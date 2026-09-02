# Bowen Public — Test Swarm Charter v1

_Authored by the project director, 2026-09-02; v1.1 same day after swarm run 3 (added D1, corrected G2 cost). Swarm digests are judged against this document. Changes to this charter are a director decision, not a swarm or engineer decision._

## 1. Purpose

Cheap local language models (the "swarm") continuously generate probes against the **deterministic** surfaces of the Bowen backend and report anomalies to the engineer as periodic digests. The swarm exists to find retrieval, gating, and API-contract regressions before users or funders do. It does not evaluate answer prose quality (that is an LLM-layer concern, out of scope for v1).

## 2. Surfaces under test (v1)

| # | Surface | Entry point | Why |
|---|---|---|---|
| S1 | Retrieval | `search_similar()` in `backend/app/main.py`, via `GET /search` and `GET /api/v1/search` | The product's core promise: the right act and section for a plain-language question |
| S2 | Query gate | `_is_legal_query()`, `has_registry_signal()` and `detect_act_from_query()` | False rejects skip retrieval entirely (the answer then has no citations); false accepts cost only ~30 ms of search — `/chat` calls the model either way |
| S3 | API contracts | `/health`, `/acts`, `/search`, `/chat`, `/chat/stream` (SSE framing), `/api/v1/*` mirrors, error shapes from `errors.py`, attachment validation | Frontend and future org pilots depend on these shapes |

Out of scope for v1: answer quality, Stripe endpoints, admin endpoints, the frontend, anything requiring a real Anthropic call.

## 3. Invariants probed

Each probe asserts one or more of the following. A digest item must name the invariant it believes is violated.

- **R1 Uniqueness.** No two results in a single `/search` response share the same `(act_title, section_number, text)`. _(Known-violated on the deployed `v1.0-data`: every section appears 4–7 times. Tracked as a defect; the swarm reports counts, not repeats.)_
- **R2 Golden hits.** For every entry in `backend/tests/golden/retrieval.json`, the expected `(act, section)` appears in the top-k **unique** results.
- **R3 Act filter honoured.** When `detect_act_from_query()` returns an act, every returned result belongs to that act.
- **R4 Score sanity.** Scores are finite, descending, and every returned score ≥ `MIN_SIMILARITY` (0.25). Boosted scores never exceed `raw × MAX_BOOST` (2.5).
- **R5 Latency.** `/search` p95 under the local budget recorded in the golden file header (set by the engineer after baseline; prod currently measures ~3–4 s).
- **G1 Legal-signal recall.** Questions that name an act, a section, or an obviously legal concept are accepted by the gate.
- **G2 Casual rejection.** Greetings, thanks, dev chatter under 30 words are rejected. (Low severity: a false accept costs a search, not tokens.)
- **D1 Act selection.** When `detect_act_from_query()` selects an act, that act is the one the question is about; ambiguous single keywords never select an act alone. Gate acceptance (G1) must not depend on act selection.
- **G3 Follow-up continuity.** With legal history in the session, short follow-ups ("and section 6?") are accepted.
- **A1 Shape stability.** Every endpoint's success and error JSON matches the recorded schema snapshot; `/chat/stream` emits `token…` then exactly one `done` event carrying `sources` and `disclaimer`, or one `error` event.
- **A2 Validation.** Oversize messages (>5000 chars), >3 attachments, disallowed content types, and empty messages return 4xx with the documented error code, never 5xx.
- **A3 Mirror parity.** `/api/v1/X` and `/X` return identical bodies for identical inputs.

## 4. Hard constraints (non-negotiable)

1. **Stubbed Anthropic client only.** The swarm runs against a local backend started with the stub enabled. No probe may reach `api.anthropic.com`. Any digest containing evidence of a real completion is a charter breach and the run is killed.
2. **Never against production.** Target is `http://localhost:8105` (the registered backend port) only. Probes carrying the Railway or bowenpublic.com hostnames are rejected at the harness boundary.
3. **Never in the trust repo.** The swarm has no read or write access to `~/bpct`. Probe generators receive only this charter, the golden file, `acts_registry.py` titles, and the OpenAPI schema.
4. **No writes to the product repo.** The swarm writes only to its own run directory (`~/.cache/bowen-swarm/runs/<date>/`). It never edits code, data, or tests; proposals go in the digest.
5. **Data source.** Retrieval probes run over the pinned release cache (`~/.cache/bowen-data/<release>/`), never over the uncommitted expansion artifacts in the working tree.
6. **Model.** `qwen2.5-coder:32b` via local Ollama (fallback `qwen3.8:27b`). No paid model generates probes. Opus tokens are spent only by the engineer, on triage.

## 5. Digest format and cadence

- **Cadence:** one digest per run; runs at most daily while the harness is new, weekly once stable. Never a live firehose to the engineer.
- **Location:** `~/.cache/bowen-swarm/runs/<date>/DIGEST.md`; the director copies notable items into hq.
- **Format:** (1) run header: charter version, data release, backend commit, model, probe counts by surface; (2) at most **10** items ranked by severity, each with: invariant, minimal reproducing request, observed vs expected, first-seen run; (3) a "still open from last run" list; (4) a "noise suppressed" count with one example. Anything that does not fit is an appendix, not a digest item.
- **Severity:** `demo-visible` (a funder would notice) → `wrong-citation` (D1, R2) → `contract-break` → `gate-miss` (G1) → `cosmetic` (G2).

## 6. Success and kill criteria

**Success (charter v1 achieved when all hold for two consecutive runs):**
- Zero false-positive digest items after engineer triage (every item reproduces).
- Golden-set coverage ≥ 3 questions per act for the 20 most-queried acts in the query logs.
- Every `demo-visible` item found by the swarm reached the engineer before it was reported by a human.

**Kill the run immediately if:**
- Any real Anthropic call, any prod hostname, or any `~/bpct` path appears in run logs.
- Digest false-positive rate exceeds 50% for two runs (the generator is producing noise; fix the generator before resuming).
- Local backend RSS exceeds 6 GB or a run exceeds 2 hours (something is loading the wrong data).

## 7. Prerequisites (owned by the engineer, tracked in hq commission C-001)

The harness under `backend/tests/` with the golden file, the data-directory override, the stub client switch, and the fixture builder. The swarm does not start until C-001 is accepted by the director.
