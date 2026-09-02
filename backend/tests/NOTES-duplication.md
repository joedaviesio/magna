# Why the corpus is ~10x duplicated

_Analysis only — no pipeline was run and no data file was modified. C-001 §6._

**Summary.** Two independent mechanisms stack. The dominant one (~9.9x) is a
self-referential glob in `rebuild_all_chunks()`: `all_chunks.json` matches the
pattern `*_chunks.json`, so every rebuild re-ingests the previous build's own
output. The minor one (~1.09x) is the unanchored `prov` class regex in the HTML
parser, which emits one record per *nested* provision `div` as well as the
section itself.

    2,619,279 rows in metadata.json
      ÷ 265,795 chunks actually on disk across the 197 per-act files   = 9.855x   (mechanism 1)
      ÷ 243,095 distinct (act_title, section_number, text)             = 1.093x   (mechanism 2)
      → 10.78x overall

---

## Mechanism 1 — `all_chunks.json` re-ingests itself (~9.9x, dominant)

`backend/scripts/batch_ingest.py:263`:

```python
chunk_files = sorted(PROCESSED_CHUNKS_DIR.glob("*_chunks.json"))
```

`all_chunks.json` — the *output* of this function — matches `*_chunks.json`
(`*` binds to `all`). It lives in the same directory, so each rebuild reads it
back in as though it were one more per-act file. Sorted, it lands at position 1,
immediately after `accident-compensation-act-2001_chunks.json`.

Let `A` be the first act's chunks and `R` the rest. The recurrence is:

```
all_1 = A + R
all_2 = A + all_1 + R = A + (A + R) + R
all_3 = A + all_2 + R = A + A + A + R + R + R
...
all_k = k copies of A, then the accumulated remainder
```

so the earliest acts accumulate one extra copy per batch run and later-added
acts accumulate fewer — which is why the average multiplicity (9.86x) sits below
the maximum (12x).

### Evidence

1. **The glob really does match its own output.**

   ```
   glob *_chunks.json matches: 198
   all_chunks.json in glob?    True
   position of all_chunks.json: 1
   per-act files:              197
   ```

2. **Size ratio.** Per-act files total 286,196,140 bytes; `all_chunks.json` is
   2,808,694,471 bytes — **9.81x** the material it is supposedly a concatenation
   of.

3. **Count ratio.** The 197 per-act files hold 265,795 chunks. `metadata.json`
   (generated 1:1 from `all_chunks.json` by `generate_embeddings.py`) holds
   2,619,279 rows — **9.855x**.

4. **The repeats are consecutive and evenly spaced, exactly as the recurrence
   predicts.** Scanning `metadata.json` for the id of its very first row
   (`0d10395fc604`, Accident Compensation Act 2001 s1 Title) finds **12**
   occurrences, at byte offsets

   ```
   2, 2428777, 4857552, 7286327, 9715102, 12143877,
   14572652, 17001427, 19430202, 21858977, 24287752, 26716527
   ```

   i.e. 12 back-to-back copies of the whole Accident Compensation block
   (~2.43 MB each) before the second act begins. Twelve generations of rebuild,
   and the first act carries all twelve.

5. **Nothing new appears after the first pass.** Building
   `backend/tests/fixtures/mini` streamed all 2,619,279 rows for 10 target acts:
   all 10,790 distinct rows were found within the first 500,000 rows; the
   remaining 2.1 M rows contributed **zero** new distinct rows and 130,321
   duplicates.

`generate_embeddings.py:46` reads `all_chunks.json` and writes one embedding and
one metadata row per element, so the duplication passes through untouched into
`embeddings.npy` and `metadata.json`.

## Mechanism 2 — nested `prov` divs in the parser (~1.09x, secondary)

`backend/scripts/parse_legislation.py:1042`:

```python
sections = soup.find_all('div', class_=re.compile(r'prov'))
```

`find_all` is recursive and the regex is unanchored, so it matches the section's
own `div.prov` **and** every descendant whose class merely contains `prov`
(`prov-body`, nested subsection provisions, and so on). Each match becomes a
separate record in the act JSON, carrying overlapping text.

`chunk_section()` then faithfully emits chunks for each record, so the overlap
reaches the index. Contrary to the original hypothesis in the commission,
`chunk_section` itself is not at fault — it is 1 section-record → N chunks and
never re-emits.

### Evidence

`data/processed/json/residential-tenancies-1986.json`:

```
sections:                       2030      (the RTA has ~450 real sections)
unique (num, heading, text):    1899
unique text:                    1715
empty section_number:           1643 of 2030
empty heading:                  1058 of 2030
```

Records 171-176 are the giveaway — one real section followed by its own
sub-fragments:

```
171  '18'  '18 General bonds'  925 chars  '(1) A landlord may require payment of a bond (a general bond)...'
172  ''    '(a)'               922 chars  '(1) A landlord may require payment of a bond (a general bond)...'
173  ''    ''                  181 chars  '(1) A landlord may require payment of a bond (a general bond)...'
174  ''    ''                  211 chars  '(2) If the landlord lawfully increases the amount of the rent...'
```

The first two rows of `metadata.json` show the same shape reaching the index:
id `0d10395fc604` (`"1 Title\n\nThis Act is the Accident Compensation Act 2001."`,
section_number `"1"`) is immediately followed by two copies of id `df5fe6d8e610`
(the same sentence with no heading and **no section number**).

Note the collateral damage: 81% of RTA records carry an empty `section_number`,
so they can never be cited as a section even when they are retrieved.

---

## Proposed fix points for the next regeneration

**Primary — one line, `backend/scripts/batch_ingest.py:263`:**

```python
# before
chunk_files = sorted(PROCESSED_CHUNKS_DIR.glob("*_chunks.json"))
# after
chunk_files = sorted(f for f in PROCESSED_CHUNKS_DIR.glob("*_chunks.json")
                     if f.name != "all_chunks.json")
```

This alone takes the corpus from 2,619,279 rows to ~265,795 — a 9.9x cut in
embeddings size, metadata RAM and search time, which is also the Railway RAM
problem that parked the expansion.

**Belt and braces — one line in `generate_embeddings.py`,** after the chunks are
loaded (line ~54), so no future pipeline bug can put duplicates in the index:

```python
chunks = list({(c["metadata"].get("act_title", ""),
                c["metadata"].get("section_number", ""),
                c["text"]): c for c in chunks}.values())
```

**Secondary — parser, `parse_legislation.py:1042`,** to stop nested provisions
becoming their own records. The narrow change is to keep only top-level
provisions:

```python
sections = [d for d in soup.find_all('div', class_=re.compile(r'prov'))
            if not d.find_parent('div', class_=re.compile(r'prov'))]
```

This one changes what text is indexed, so it needs a retrieval re-baseline
against `backend/tests/golden/retrieval.json` before it ships — the sub-fragment
records currently do carry some of the golden hits.

## Runtime mitigation already in place

`search_similar()` now over-fetches `top_k * CANDIDATE_MULTIPLIER` (12)
candidates and drops duplicates on `(act_title, section_number, text)` before
truncating to `top_k`. On a 12x-duplicated index that lifts the golden set from
27/55 to 37/55 and restores `/chat` from one source to three. It is a mitigation,
not a cure: the wasted RAM, disk and search time remain until the data is
regenerated.
