# Plan: Address Bowen's Feedback on Legislation Processing

Based on Bowen's feedback, here are the prioritized improvements from high to low.

---

## Priority 1: Fragment Completeness (HIGH)

**Problem:** Excerpts appear truncated mid-sentence or show only section headings.

**Root Causes Identified:**
1. **Hard 5000 character limit** in `backend/scripts/parse_legislation.py:546`:
   ```python
   "text": body_text[:5000],  # Limit text length
   ```
2. **Sentence boundary detection** uses only `.!?` but legal definitions use dashes/semicolons
3. **Heading-only chunks** when section text is minimal

**Fix:**
1. Remove or increase the 5000 char limit in `parse_legislation.py` (line 546)
2. Improve sentence splitting in `chunk_legislation.py` to handle:
   - Semicolons (`;`) as sentence boundaries in legal definitions
   - Em-dashes (`—`) separating definition terms
   - Numbered subsections `(a)`, `(b)` as logical break points
3. Ensure chunks always include complete sentences (no mid-word/mid-sentence cuts)

**Files to modify:**
- `backend/scripts/parse_legislation.py` - Remove 5000 char limit
- `backend/scripts/chunk_legislation.py` - Improve sentence boundary regex

---

## Priority 2: Context Preservation (MEDIUM-HIGH)

**Problem:** Cross-references to other sections/schedules aren't available.

**What's in HTML but not extracted:**
- `<a class="extref">` links to related acts/sections
- Schedule references
- Amendment source acts

**Fix:**
1. Extract cross-references during HTML parsing:
   - Parse all `<a class="extref">` elements
   - Store as `cross_references` array in section metadata
2. Add schedule linking:
   - When a section mentions "Schedule X", extract the schedule number
   - Store as `schedule_references` in metadata
3. Propagate references to chunks for retrieval context

**Files to modify:**
- `backend/scripts/parse_legislation.py` - Add cross-reference extraction
- `backend/scripts/chunk_legislation.py` - Include references in chunk metadata

---

## Priority 3: Currency Indicators (MEDIUM)

**Problem:** No amendment dates or version indicators for reliability.

**Available in HTML but not extracted:**
- `<p class="reprint-date">Version as at 13 November 2025</p>`
- `<div class="cover-reprint-note">` with amendment summary
- `<div class="history">` with per-section amendment dates
- `<span class="deletion-status">[Repealed]</span>` status markers

**Fix:**
1. Extract act-level currency metadata:
   - `version_date` from `reprint-date` element
   - `assent_date` from cover metadata
   - `amendment_note` from `cover-reprint-note`
2. Extract section-level status:
   - `is_repealed` boolean from `deletion-status` spans
   - `amendment_history` from `history` divs (when section was inserted/amended)
3. Include in API responses for display

**Files to modify:**
- `backend/scripts/parse_legislation.py` - Extract version/amendment metadata
- `backend/app/main.py` - Include currency info in responses

---

## Priority 4: Search Optimization (LOWER)

**Problem:** Need more comprehensive coverage of key operative sections.

**Current state:**
- `key_sections.py` has ~200 topic→section mappings
- Works well but gaps exist for some acts

**Fix:**
1. Expand KEY_SECTIONS registry with:
   - More subsection detail (18A, 18B patterns)
   - Additional common query topics
   - Coverage for newer/less common acts
2. Add section type classification:
   - `purpose`, `interpretation`, `operative`, `procedural`, `penalty`
   - Enable smarter filtering based on query intent

**Files to modify:**
- `backend/app/key_sections.py` - Expand topic→section mappings

---

## Implementation Order

1. **Fragment Completeness** - Fix truncation (biggest user-visible issue)
2. **Currency Indicators** - Add version dates (quick metadata extraction)
3. **Context Preservation** - Cross-references (moderate complexity)
4. **Search Optimization** - Expand key sections (ongoing improvement)

---

## Verification

After implementation:
1. Re-run parsing: `python backend/scripts/parse_legislation.py`
2. Re-run chunking: `python backend/scripts/chunk_legislation.py`
3. Re-generate embeddings: `python backend/scripts/generate_embeddings.py`
4. Test specific problematic sections mentioned by Bowen:
   - Local Government Act 1974 s292 (was heading-only)
   - Biosecurity Act excerpt starting with "(a)"
5. Verify currency info appears in `/chat` responses
6. Test cross-reference availability via `/debug/search`
