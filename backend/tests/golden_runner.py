"""
golden_runner.py

Shared evaluation logic for the golden retrieval set (charter invariant R2).
Imported by test_golden_retrieval.py and by scripts/run_golden.py; deliberately
not named test_* so pytest does not collect it.
"""

import time
from contextlib import contextmanager


@contextmanager
def candidate_multiplier(main_module, value):
    """Temporarily change the over-fetch factor used by search_similar().

    `value=1` reproduces the pre-dedupe selection behaviour: the old code took
    `argsort(similarities)[-top_k:]` and returned those rows verbatim, so the
    set of *unique* (act, section) pairs it could deliver was exactly the set
    present in the raw top_k rows — which is what multiplier 1 yields.
    """
    if value is None:
        yield
        return
    previous = main_module.CANDIDATE_MULTIPLIER
    main_module.CANDIDATE_MULTIPLIER = value
    try:
        yield
    finally:
        main_module.CANDIDATE_MULTIPLIER = previous


@contextmanager
def duplicated_index(main_module, factor):
    """Temporarily tile the loaded index `factor` times.

    This reproduces the shape of the deployed corpus, where rebuild_all_chunks()
    re-ingested its own output so every chunk is present ~10-12 times as an
    identical (act_title, section_number, text) row with an identical embedding.
    Block tiling (whole corpus repeated) matches how the duplicates actually
    arose. See NOTES-duplication.md.
    """
    if not factor or factor <= 1:
        yield
        return
    import numpy as np

    original_embeddings = main_module.embeddings
    original_metadata = main_module.metadata
    main_module.embeddings = np.tile(np.asarray(original_embeddings), (factor, 1))
    main_module.metadata = list(original_metadata) * factor
    try:
        yield
    finally:
        main_module.embeddings = original_embeddings
        main_module.metadata = original_metadata


def unique_pairs(results):
    """(act_title, section_number) pairs in result order, duplicates removed."""
    seen = []
    for r in results:
        pair = (r["act_title"], (r["section_number"] or "").strip())
        if pair not in seen:
            seen.append(pair)
    return seen


def evaluate_entry(main_module, entry, top_k=6):
    """Run one golden question down the same path /chat takes."""
    question = entry["question"]
    started = time.perf_counter()
    detected_act = main_module.detect_act_from_query(question)
    results = main_module.search_similar(question, top_k=top_k, act_filter=detected_act)
    elapsed_ms = (time.perf_counter() - started) * 1000.0

    pairs = unique_pairs(results)
    expected = (entry["act"], entry["section"])
    rank = pairs.index(expected) + 1 if expected in pairs else None

    return {
        "question": question,
        "expected_act": entry["act"],
        "expected_section": entry["section"],
        "detected_act": detected_act,
        "hit": rank is not None,
        "rank": rank,
        "unique_returned": len(pairs),
        "rows_returned": len(results),
        "got": pairs,
        "elapsed_ms": elapsed_ms,
    }


def evaluate_all(main_module, entries, top_k=6, multiplier=None, duplicate=None):
    with duplicated_index(main_module, duplicate):
        with candidate_multiplier(main_module, multiplier):
            return [evaluate_entry(main_module, e, top_k=top_k) for e in entries]


def format_table(rows, title):
    """Render a compact pass/fail table for the report."""
    out = [title, "=" * len(title)]
    out.append(f"{'#':>3}  {'hit':<4} {'rank':>4}  {'act':<38} {'sec':<5} question")
    for i, r in enumerate(rows, 1):
        out.append(
            "%3d  %-4s %4s  %-38s %-5s %s" % (
                i,
                "PASS" if r["hit"] else "FAIL",
                r["rank"] if r["rank"] else "-",
                r["expected_act"][:38],
                r["expected_section"],
                r["question"][:70],
            )
        )
    passed = sum(1 for r in rows if r["hit"])
    lat = sorted(r["elapsed_ms"] for r in rows)
    p95 = lat[max(0, int(len(lat) * 0.95) - 1)] if lat else 0.0
    out.append("")
    out.append("passed %d/%d (%.1f%%)  |  latency mean %.1f ms, p95 %.1f ms, max %.1f ms" % (
        passed, len(rows), 100.0 * passed / max(1, len(rows)),
        sum(lat) / max(1, len(lat)), p95, max(lat) if lat else 0.0,
    ))
    return "\n".join(out)


def summary(rows):
    lat = sorted(r["elapsed_ms"] for r in rows)
    return {
        "total": len(rows),
        "passed": sum(1 for r in rows if r["hit"]),
        "failed": sum(1 for r in rows if not r["hit"]),
        "p95_ms": lat[max(0, int(len(lat) * 0.95) - 1)] if lat else 0.0,
        "max_ms": max(lat) if lat else 0.0,
    }
