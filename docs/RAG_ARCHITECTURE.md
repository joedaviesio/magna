# Bowen Public — RAG Architecture

How the system works, end to end. Two halves: an **offline ingestion pipeline**
that turns NZ legislation into a searchable vector store, and an **online RAG
runtime** that answers questions against it.

---

## 1. System map

```
                            ┌─────────────────────────────────────┐
                            │            USER (browser)            │
                            └───────────────────┬─────────────────-┘
                                                │ HTTPS
                                                ▼
        ┌───────────────────────────────────────────────────────────────────┐
        │  FRONTEND  — Next.js (App Router)        host: Netlify              │
        │  chat.tsx · ChatInput.tsx · useChat.ts · lib/api.ts                 │
        └───────────────────────────┬───────────────────────────────────────-┘
                                    │  POST /api/v1/chat/stream  (SSE)
                                    │  GET  /acts   ·  DELETE /session/{id}
                                    ▼
        ┌───────────────────────────────────────────────────────────────────┐
        │  BACKEND  — FastAPI / uvicorn            host: Railway (Docker)     │
        │                                                                    │
        │   ┌─ retrieval ─────────┐   ┌─ generation ──────────────────────┐  │
        │   │ search_similar()    │   │ Anthropic Messages API (stream)   │──┼──► api.anthropic.com
        │   │  cosine + boosting  │   │ model: claude-opus-4-6            │  │
        │   └─────────┬──────────-┘   └───────────────────────────────────┘  │
        │             │ reads (mmap)                                          │
        └─────────────┼─────────────────────────────────────────────────────-┘
                      ▼
        ┌───────────────────────────────────────────────────────────────────┐
        │  VECTOR STORE  (flat files, no DB)                                  │
        │  embeddings.npy  ·  metadata.json  ·  config.json                   │
        │  pulled at Docker build from a GitHub Release (NOT git LFS)         │
        └───────────────────────────────────────────────────────────────────┘
                      ▲
                      │ produced offline by the ingestion pipeline
        ┌─────────────┴─────────────────────────────────────────────────────-┐
        │  legislation.govt.nz  ──►  batch_ingest.py  ──►  vector store        │
        └───────────────────────────────────────────────────────────────────┘
```

There is **no vector database** — retrieval is a single NumPy matrix multiply
over a memory-mapped array. Simple, cheap, and the reason embeddings file size
matters so much (see §7).

---

## 2. Offline: the ingestion pipeline

Run manually per batch: `python backend/scripts/batch_ingest.py --batch N`.
Driven by `data/expansion-manifest.json` (acts grouped into batches of ~10).

```
  expansion-manifest.json
        │  for each act in batch:
        ▼
  ┌──────────────┐   2s delay   ┌──────────────┐   ┌──────────────┐
  │ download_html│─────────────►│ parse_       │──►│ chunk_       │
  │              │              │ legislation  │   │ legislation  │
  │ GET .../whole│              │  HTML→JSON   │   │ JSON→chunks  │
  │ .html        │              │  (sections)  │   │ 512 tok,     │
  └──────┬───────┘              └──────┬───────┘   │ 50 overlap   │
         │ skips repealed /            │           └──────┬───────┘
         │ already-downloaded          │                  │
         ▼                             ▼                  ▼
  data/raw/html/*.html   data/processed/json/*   data/processed/chunks/
                                                       *_chunks.json
         │ also registers act in:                       │
         ├── acts_registry.py  (ACTS_REGISTRY)          │
         └── parse_legislation.py (ACT_METADATA)        │
                                                        ▼
                              ┌──────────────────────────────────────┐
                              │ rebuild_all_chunks()                  │
                              │  concat ALL *_chunks.json → one file  │
                              │  → data/processed/chunks/             │
                              │       all_chunks.json                 │
                              └───────────────────┬──────────────────-┘
                                                  ▼
                              ┌──────────────────────────────────────┐
                              │ generate_embeddings.py                │
                              │  all-MiniLM-L6-v2, 384-dim, batched   │
                              │  (skipped with --skip-embeddings)     │
                              └───────────────────┬──────────────────-┘
                                                  ▼
                          data/embeddings/  embeddings.npy
                                            metadata.json   (text trunc 1000 chars)
                                            config.json
```

**Key properties**

- **Idempotent / resumable.** Already-downloaded HTML and already-registered
  acts are skipped; manifest progress is saved per-act. Safe to re-run.
- **In-force whole-acts only.** `download_html` skips anything flagged repealed,
  and amendments/regulations without a consolidated `whole.html` page just fail
  to download (this is why a "200-act" target lands at ~198).
- **Embeddings are all-or-nothing.** `generate_embeddings.py` rebuilds the
  *entire* `embeddings.npy` from `all_chunks.json` every time — there is no
  incremental update. Hence the multi-batch strategy: ingest with
  `--skip-embeddings`, regenerate once at the end.
- **`rebuild_all_chunks()` globs `*_chunks.json`** — a stray/misnamed chunk file
  gets double-counted into the index (one such file currently exists).

Files: `backend/scripts/batch_ingest.py`, `parse_legislation.py`,
`chunk_legislation.py`, `generate_embeddings.py`.

---

## 3. Online: the RAG query flow

```
 BROWSER                         BACKEND  /chat/stream  (backend/app/main.py:1064)
 ───────                         ──────────────────────────────────────────────────

 user types ─► ChatInput
   handleSubmit (preventDefault)
   onSend(text)
        │
   useChat.send                  ① guards: embeddings? model? anthropic? loaded
   POST /api/v1/chat/stream  ──► ② detect_act_from_query(query)      acts_registry
   (SSE, session_id)                  → act short_name | None
        │                        ③ _is_legal_query(query,...)        main.py:887
        │                            regex legal-signals + act + follow-up shape
        │                            │
        │                            ├─ NO  → skip retrieval, context = "casual"
        │                            │
        │                            └─ YES ▼
        │                        ④ search_similar(query, top_k=6,    main.py:383
        │                            act_filter=detected_act)
        │                              • encode query (MiniLM)
        │                              • cosine = embeddings · q  (mmap matmul)
        │                              • heuristic boosting (see §4)
        │                              • drop < MIN_SIMILARITY (0.25)
        │                              • argsort → top-k chunks
        │                        ⑤ build_context()  group by Act → markdown
        │                           find_matching_references()  (Te Tiriti essay)
        │                           attachments → PDF text / image blocks
        │                        ⑥ _build_claude_messages()          main.py:577
        │                            system = SYSTEM_PROMPT (Bowen persona)
        │                            history = conversation_history[sid] (≤10 turns)
        │                            user   = QUESTION + EXCERPTS + refs + docs
        │                        ⑦ anthropic.messages.stream(opus-4-6)
        │                            │
   onToken  ◄── data:{type:token} ◄─┤  (each text delta, SSE)
   (append to last msg)             │
        │                           ▼  stream ends
   onDone   ◄── data:{type:done, sources[≤3], disclaimer}
   (attach sources)             ⑧ _store_history(sid)  + log_query()
        │
   onError  ◄── data:{type:error, error}   (on any exception)
```

Non-streaming `/chat` (main.py:923) exists with the same shape; the frontend
uses only the streaming path.

### Frontend chat screen (wireframe)

```
┌─────────────────────────────────────────────────────────┐
│  [M][K]  Bowen PUBLIC                       ● Online      │  sticky header
├─────────────────────────────────────────────────────────┤
│                                                           │
│        Ask Bowen about New Zealand Law                    │  empty state
│        A public and free service ...                      │  (messages == 0)
│                                                           │
│     ┌──────┐ ┌──────┐ ┌──────────────┐                    │
│     │ 198  │ │36,956│ │  1,361,971   │   ◄ {acts.length}   │  stats: live /acts
│     │ Acts │ │ Sec. │ │   Chunks     │     else FALLBACK   │  count, else 89
│     └──────┘ └──────┘ └──────────────┘                     │
│        [ ✦ Legislation Coverage ▾ ]   [ ♥ Support ]        │
│                                                           │
│  ─────────────────  (after first message)  ────────────-  │
│   user: "what's the max bond?"                            │
│   assistant: Under s18 RTA … ▌(streaming)                 │
│      ▸ Sources: Residential Tenancies Act 1986 · s18 …    │
├─────────────────────────────────────────────────────────┤
│  [📎]  Ask about NZ law...                      [ Send ▶] │  fixed input
│        Not legal advice · disclaimer                       │
└─────────────────────────────────────────────────────────┘
```

State lives in `useChat.ts`: session UUID in `localStorage`; on mount it
**wipes** stored messages and DELETEs the backend session (fresh start every
load). Acts count comes from `/acts`, falling back to the bundled
`FALLBACK_LEGISLATION` list (currently 89) if the call fails.

---

## 4. Retrieval scoring detail (`search_similar`)

The "smart" part of the RAG. Pure NumPy + hand-tuned heuristics — no reranker.

```
 query ─► MiniLM encode ─► q (384-d)

 similarities = embeddings · q          # cosine (vectors are normalized)

 for each chunk i with raw_score ≥ 0.25:               # MIN_SIMILARITY floor
     boost = 1.0
     × key-section boost      (topic → known important sections)
     × 1.3  if overview Q ("what is/explain") & heading∈{purpose,
            interpretation,application,object,principle,definition}
     × 1.2  if overview Q & section_number ≤ 10
     × 1.1  if chunk has a real section number
     × 1.4  if a query term (>3 chars) appears in section heading
     boost = min(boost, 2.5)                            # MAX_BOOST cap
     similarities[i] = raw_score × boost

 if act_filter:  similarities[non-matching acts] = -1   # hard exclude
 top_indices = argsort(similarities)[-k:][::-1]
 keep only those still ≥ 0.25
```

Tunable constants (top of `main.py`):

| Const | Value | Meaning |
|---|---|---|
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | 384-dim sentence encoder |
| `TOP_K` | 5 | default retrieved chunks (chat uses 6, shows ≤3 sources) |
| `MIN_SIMILARITY` | 0.25 | discard floor |
| `MAX_BOOST` | 2.5 | boost cap |
| `MAX_HISTORY` | 10 | conversation turns kept in memory |
| chunking | 512 tok / 50 overlap / 50 min | `chunk_legislation.py` |

---

## 5. Prompt assembly

The model never sees raw chunks — they're wrapped (`_build_claude_messages`,
main.py:577):

```
system: SYSTEM_PROMPT            ── "You are Bowen…" persona + rules (main.py:165)

messages: [ …conversation_history[session_id]  (≤10 turns, ≤4 if attachments) ,
            { role: user, content:
                USER'S QUESTION: <query>
                ---
                LEGISLATION EXCERPTS FROM DATABASE: <build_context()>
                [CURATED SCHOLARLY REFERENCES: …]   (Te Tiriti essay, keyword-matched)
                [UPLOADED DOCUMENT TEXT: …]          (PDF extract)
                + answer instructions (cite sections, info-not-advice)
              [ + image blocks if images uploaded → multimodal ] } ]

max_tokens: 1750  (2500 when attachments present)
```

Conversation memory is **in-process only** (`conversation_history` dict) — it
does not survive a backend restart and is not shared across instances.

---

## 6. Key files

| Concern | File |
|---|---|
| API, retrieval, generation, RAG loop | `backend/app/main.py` |
| Act registry + query→act detection | `backend/app/acts_registry.py` |
| Ingestion orchestrator | `backend/scripts/batch_ingest.py` |
| HTML → structured JSON | `backend/scripts/parse_legislation.py` |
| JSON → token chunks | `backend/scripts/chunk_legislation.py` |
| Chunks → embeddings | `backend/scripts/generate_embeddings.py` |
| Chat UI + streaming client | `frontend/src/components/chat.tsx`, `lib/api.ts`, `hooks/useChat.ts` |
| Ingestion plan/state | `data/expansion-manifest.json` |
| Deploy (backend) | `Dockerfile`, `backend/railway.toml` |
| Deploy (frontend) | `frontend/netlify.toml` |

---

## 7. Known constraints & gaps

Cross-referenced from earlier investigation — not part of the happy path but
load-bearing for operations:

- **Embeddings file size vs. GitHub Release 2 GB cap.** After the 198-act
  expansion `embeddings.npy` ≈ 4 GB (float32). The Dockerfile pulls it from a
  GitHub *Release* (free, but 2 GB/file hard limit). This blocks shipping the
  new data until it's float16 + sharded, or moved to external object storage.
- **Git LFS bloat.** `.gitattributes` LFS-tracks the regenerated artifacts even
  though deploy uses Releases — pure dead weight; local `.git/lfs` ≈ 8 GB and
  growing every regeneration.
- **Silent send-failure UX.** `useChat.send` drops the user message on failure
  and reverts to the welcome screen where the error banner isn't rendered —
  failures look like a crash. See `known-issue-silent-send-failure`.
- **API URL not in repo.** `NEXT_PUBLIC_API_URL` defaults to
  `http://localhost:8105`; must be set in Netlify. `ALLOWED_ORIGINS` (CORS)
  defaults to localhost-only; must be set on Railway.
- **No rate limiting** on `/chat/stream` — open Anthropic spend exposure.
- **Model pinned in code** to `claude-opus-4-6` (`generate_response_stream`),
  not configurable via env.
- **Conversation memory is in-process** — lost on restart, not multi-instance
  safe.
```
