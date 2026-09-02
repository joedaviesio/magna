#!/usr/bin/env python3
"""Bowen Public test swarm runner — charter v1 (tests/SWARM-CHARTER.md).

Generates probe questions with a local Ollama model, fires them at a LOCAL backend
(port 8105, stubbed LLM), checks the deterministic invariants, writes DIGEST.md.

Usage:
  swarm_run.py --backend http://localhost:8105 --acts-file <acts.json> \
               --golden <retrieval.json> --model qwen2.5-coder:32b --per-act 3

Hard constraints enforced here: only localhost targets; never touches ~/bpct; never edits the repo.
"""
import argparse, json, os, re, statistics, sys, time, urllib.request, urllib.parse, datetime, pathlib

FORBIDDEN_HOSTS = ("railway.app", "bowenpublic.com", "anthropic.com")

def load_gate(repo_root):
    """Import the real gate + act detection from the repo under test (no server, no network)."""
    os.environ.setdefault("BOWEN_STUB_LLM", "1"); os.environ.setdefault("HF_HUB_OFFLINE", "1")
    sys.path.insert(0, repo_root)
    from backend.app import main as m
    from backend.app.acts_registry import detect_act_from_query
    return m._is_legal_query, m._LEGAL_SIGNALS, detect_act_from_query
MIN_SIMILARITY, MAX_BOOST = 0.25, 2.5

def http_json(url, payload=None, timeout=120):
    for h in FORBIDDEN_HOSTS:
        if h in url:
            raise SystemExit(f"KILL: forbidden host in {url}")
    req = urllib.request.Request(url, data=json.dumps(payload).encode() if payload else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

def ollama(model, prompt, timeout=300):
    out = http_json("http://localhost:11434/api/generate",
                    {"model": model, "prompt": prompt, "stream": False, "options": {"temperature": 0.9}}, timeout)
    return out.get("response", "")

def gen_probes(model, act_title, n):
    prompt = (f"You write test questions for a New Zealand legal information tool. Write {n} distinct plain-language "
              f"questions an ordinary person might ask that should be answered from the '{act_title}'. "
              f"Also write 1 casual message with NO legal or law-related words at all (a greeting, thanks, or small talk about weather/food, under 10 words). "
              f"Reply ONLY with a JSON object: {{\"legal\": [..], \"casual\": [..]}}.")
    txt = ollama(model, prompt)
    m = re.search(r"\{.*\}", txt, re.S)
    try:
        d = json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        d = {}
    return [q for q in d.get("legal", []) if isinstance(q, str)][:n], [q for q in d.get("casual", []) if isinstance(q, str)][:1]

def check_search(backend, q, expect_act=None):
    t = time.time()
    res = http_json(f"{backend}/search?q={urllib.parse.quote(q)}&limit=10")
    dt = time.time() - t
    results = res.get("results", [])
    findings = []
    keys = [(r["act_title"], r["section_number"], r["text"]) for r in results]
    dup = len(keys) - len(set(keys))
    if dup:
        findings.append(("R1", f"{dup} duplicate (act,section,text) rows in {len(keys)} results"))
    scores = [r["score"] for r in results]
    if scores != sorted(scores, reverse=True):
        findings.append(("R4", "scores not descending"))
    if any((not isinstance(s, (int, float))) or s != s or s < MIN_SIMILARITY for s in scores):
        findings.append(("R4", f"score below floor/non-finite: {scores}"))
    if expect_act and results and not any(expect_act.lower() in r["act_title"].lower() for r in results):
        findings.append(("R2/R3", f"expected act '{expect_act}' absent; got {sorted(set(r['act_title'] for r in results))[:3]}"))
    return findings, dt, results

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="http://localhost:8105")
    ap.add_argument("--acts-file", required=True, help="JSON list of act titles to probe (from /acts, saved locally)")
    ap.add_argument("--golden", help="backend/tests/golden/retrieval.json (optional)")
    ap.add_argument("--model", default="qwen2.5-coder:32b")
    ap.add_argument("--per-act", type=int, default=3)
    ap.add_argument("--max-acts", type=int, default=20)
    ap.add_argument("--charter-version", default="v1")
    ap.add_argument("--repo", required=True, help="repo root under test (worktree) — used to import the gate in-process")
    a = ap.parse_args()
    if not a.backend.startswith("http://localhost") and not a.backend.startswith("http://127.0.0.1"):
        raise SystemExit("KILL: backend must be localhost")

    run_dir = pathlib.Path.home() / ".cache/bowen-swarm/runs" / datetime.date.today().isoformat()
    run_dir.mkdir(parents=True, exist_ok=True)
    is_legal, LEGAL_RE, detect_act = load_gate(a.repo)
    health = http_json(f"{a.backend}/health")
    acts = json.load(open(a.acts_file))[: a.max_acts]
    items, latencies, noise, n_probe = [], [], 0, 0
    log = open(run_dir / "probes.jsonl", "a")

    for act in acts:
        legal, casual = gen_probes(a.model, act, a.per_act)
        for q in legal:
            n_probe += 1
            try:
                f, dt, results = check_search(a.backend, q, expect_act=act.rsplit(" Act", 1)[0])
            except Exception as e:
                f, dt, results = [("A1", f"request failed: {e}")], 0, []
            latencies.append(dt)
            log.write(json.dumps({"act": act, "q": q, "findings": f, "dt": dt, "n": len(results)}) + "\n")
            for inv, msg in f:
                items.append({"inv": inv, "q": q, "act": act, "msg": msg})
        # Gate (G1/G2) and act detection (D1) are checked in-process — deterministic functions.
        for q in legal:
            n_probe += 1
            det = detect_act(q)
            if not is_legal(q, det):
                items.append({"inv": "G1", "q": q, "act": act, "msg": "gate rejected a legal question"})
            if det and det.lower() not in act.lower():
                items.append({"inv": "D1", "q": q, "act": act, "msg": f"detected act '{det}' (expected {act.rsplit(' Act',1)[0]})"})
        for c in casual:
            if LEGAL_RE.search(c):
                noise += 1  # generator wrote a "casual" message containing legal vocabulary — not a gate defect
                continue
            n_probe += 1
            if is_legal(c, detect_act(c)):
                items.append({"inv": "G2", "q": c, "act": act, "msg": "gate accepted a casual message"})

    if a.golden and os.path.exists(a.golden):
        for g in json.load(open(a.golden)).get("entries", []):
            n_probe += 1
            f, dt, results = check_search(a.backend, g["question"], expect_act=g["act"])
            hit = any(r["act_title"] == g["act"] and str(r["section_number"]).strip() == str(g["section"]).strip() for r in results)
            if not hit:
                items.append({"inv": "R2", "q": g["question"], "act": g["act"], "msg": f"expected s{g['section']} not in top-10"})

    sev = {"R2": 0, "R2/R3": 0, "D1": 0, "R1": 1, "A1": 2, "R4": 2, "G1": 3, "G2": 3}
    items.sort(key=lambda i: sev.get(i["inv"], 9))
    # collapse repeats of the same invariant+act into one line with a count
    seen, digest, suppressed = {}, [], 0
    for i in items:
        k = (i["inv"], i["act"], i["msg"].split(" ")[0])
        if k in seen:
            seen[k]["count"] += 1; suppressed += 1
        else:
            i["count"] = 1; seen[k] = i; digest.append(i)
    p95 = statistics.quantiles(latencies, n=20)[-1] if len(latencies) >= 20 else (max(latencies) if latencies else 0)
    with open(run_dir / "DIGEST.md", "w") as d:
        d.write(f"# Swarm digest — {datetime.date.today()}\n\n")
        d.write(f"charter {a.charter_version} · backend {a.backend} · chunks {health.get('chunks')} · model {a.model} · probes {n_probe} · acts {len(acts)} · search p95 {p95:.2f}s\n\n")
        d.write("## Items (max 10, by severity)\n\n")
        for i in digest[:10]:
            d.write(f"- **{i['inv']}** ×{i['count']} — {i['act']} — `{i['q'][:120]}` — {i['msg']}\n")
        d.write(f"\n## Appendix\n\n{max(0, len(digest) - 10)} further items in probes.jsonl. Repeats collapsed: {suppressed}. Generator noise dropped: {noise}. Fixture acts: {len(acts)}.\n")
    print(f"wrote {run_dir / 'DIGEST.md'} — {len(digest)} items, {n_probe} probes, p95 {p95:.2f}s")

if __name__ == "__main__":
    main()
