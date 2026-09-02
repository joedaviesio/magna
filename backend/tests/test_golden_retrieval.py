"""
test_golden_retrieval.py — charter invariant R2 (golden hits).

Every golden entry is run down the same path /chat takes:
    detect_act_from_query(q) -> search_similar(q, top_k=6, act_filter=...)

Entries recorded in golden/baseline.json as `expected_pass` are a regression
lock and must keep passing. Entries recorded as `known_misses` are xfail
(non-strict), so a retrieval improvement shows up as XPASS rather than
breaking the build — update the baseline when that happens.
"""

import json
from pathlib import Path

import pytest

import golden_runner

BASELINE_PATH = Path(__file__).parent / "golden" / "baseline.json"
with open(BASELINE_PATH, encoding="utf-8") as _fh:
    BASELINE = json.load(_fh)

EXPECTED_PASS = set(BASELINE["expected_pass"])
KNOWN_MISSES = {m["question"]: m for m in BASELINE["known_misses"]}

with open(Path(__file__).parent / "golden" / "retrieval.json", encoding="utf-8") as _fh:
    GOLDEN = json.load(_fh)

TOP_K = GOLDEN["header"]["top_k"]


def _params():
    for entry in GOLDEN["entries"]:
        marks = []
        if entry["question"] in KNOWN_MISSES:
            miss = KNOWN_MISSES[entry["question"]]
            marks.append(pytest.mark.xfail(
                reason="known miss at baseline (detected_act=%s)" % miss.get("detected_act"),
                strict=False,
            ))
        yield pytest.param(entry, marks=marks,
                           id="%s-s%s" % (entry["act"].split()[0][:12], entry["section"]))


def test_golden_file_shape():
    assert GOLDEN["header"]["entry_count"] == len(GOLDEN["entries"])
    assert len(GOLDEN["entries"]) >= 40, "the charter requires at least 40 golden entries"
    for entry in GOLDEN["entries"]:
        assert set(entry) == {"question", "act", "section", "notes"}
        assert entry["question"] and entry["act"] and entry["section"]
    questions = [e["question"] for e in GOLDEN["entries"]]
    assert len(questions) == len(set(questions)), "duplicate golden questions"


def test_golden_sections_exist_in_fixture(app_module):
    """A golden entry citing a section absent from the index is a bad entry,
    not a retrieval failure."""
    present = {(row["act_title"], row["section_number"].strip())
               for row in app_module.metadata}
    missing = [(e["act"], e["section"]) for e in GOLDEN["entries"]
               if (e["act"], e["section"]) not in present]
    assert not missing, f"golden entries cite sections not in the fixture: {missing}"


@pytest.mark.golden
@pytest.mark.parametrize("entry", list(_params()))
def test_golden_entry(app_module, entry):
    result = golden_runner.evaluate_entry(app_module, entry, top_k=TOP_K)
    assert result["hit"], (
        "expected (%s, s%s) in top-%d unique results; detected_act=%r, got %s"
        % (entry["act"], entry["section"], TOP_K, result["detected_act"], result["got"])
    )


@pytest.mark.golden
def test_golden_pass_rate_not_regressed(app_module):
    rows = golden_runner.evaluate_all(app_module, GOLDEN["entries"], top_k=TOP_K)
    passed = sum(1 for r in rows if r["hit"])
    print("\n" + golden_runner.format_table(rows, "Golden retrieval set (current)"))
    assert passed >= BASELINE["passed"], (
        f"golden pass count regressed: {passed} < baseline {BASELINE['passed']}"
    )


@pytest.mark.golden
def test_expected_pass_entries_all_hit(app_module):
    """Explicit regression lock over the recorded passing set."""
    failures = []
    for entry in GOLDEN["entries"]:
        if entry["question"] not in EXPECTED_PASS:
            continue
        result = golden_runner.evaluate_entry(app_module, entry, top_k=TOP_K)
        if not result["hit"]:
            failures.append((entry["act"], entry["section"], result["got"]))
    assert not failures, f"entries that passed at baseline now fail: {failures}"


@pytest.mark.golden
@pytest.mark.slow
def test_dedupe_restores_golden_hits_on_duplicated_corpus(app_module):
    """The demo-visible defect, end to end.

    On a 12x-duplicated corpus the pre-change selection collapses the result
    list onto a single section and the golden pass count drops. With the
    result-level dedupe the pass count returns to the deduplicated baseline.
    """
    subset = GOLDEN["entries"]
    with golden_runner.duplicated_index(app_module, 12):
        with golden_runner.candidate_multiplier(app_module, 1):
            before = golden_runner.evaluate_all(app_module, subset, top_k=TOP_K)
        after = golden_runner.evaluate_all(app_module, subset, top_k=TOP_K)

    before_passed = sum(1 for r in before if r["hit"])
    after_passed = sum(1 for r in after if r["hit"])
    print(f"\nduplicated corpus: before dedupe {before_passed}/{len(subset)}, "
          f"after dedupe {after_passed}/{len(subset)}")

    assert after_passed > before_passed, "dedupe did not recover any golden hits"
    assert after_passed == BASELINE["passed"], (
        "dedupe should fully restore the deduplicated baseline "
        f"({after_passed} vs {BASELINE['passed']})"
    )


@pytest.mark.golden
def test_golden_latency_within_budget(app_module):
    budget = GOLDEN["header"]["latency_budget_ms"]
    rows = golden_runner.evaluate_all(app_module, GOLDEN["entries"], top_k=TOP_K)
    stats = golden_runner.summary(rows)
    assert stats["p95_ms"] <= budget["per_query_p95"], (
        f"p95 {stats['p95_ms']:.1f} ms over budget {budget['per_query_p95']} ms"
    )
    assert stats["max_ms"] <= budget["per_query_max"], (
        f"max {stats['max_ms']:.1f} ms over budget {budget['per_query_max']} ms"
    )
