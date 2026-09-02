"""
test_query_gate.py — surface S2 (query gate).

Charter invariants G1 (legal-signal recall), G2 (casual rejection) and
G3 (follow-up continuity), plus act detection sanity.

The gate decides whether a message costs Opus tokens, so a false accept is
money and a false reject is a lost user. The table below is the contract.
"""

import pytest

# --- G1: must be accepted ----------------------------------------------------
ACCEPT_CASES = [
    ("names an act", "What does the Residential Tenancies Act say about bonds?"),
    ("names a section", "What is section 14 of the Bill of Rights?"),
    ("short section reference", "Tell me about s103 of the ERA"),
    ("plain legal concept", "What is an unjustified dismissal?"),
    ("tenancy", "My landlord kept my bond, is that legal?"),
    ("landlord entry", "Can my landlord enter without notice?"),
    ("employment", "What are my employment rights on a 90 day trial?"),
    ("privacy", "What is the purpose of the Privacy Act 2020?"),
    ("consumer", "Can I get a refund for a faulty product?"),
    ("court", "How do I take a claim to the Disputes Tribunal?"),
    ("offence", "Is that an offence under New Zealand law?"),
    ("liability", "Am I liable for the damage to the rental car?"),
    ("consent", "Do I need a resource consent to build a deck?"),
    ("penalty", "What penalty applies for late filing?"),
    ("rights", "What rights do I have if the police search my car?"),
    ("obligations", "What are my obligations as an employer?"),
    ("treaty", "How does the Treaty of Waitangi affect this?"),
    ("what is", "What is adverse possession?"),
    ("how does", "How does the Human Rights Act work?"),
    ("can I", "Can I be evicted without notice?"),
    ("statute", "Which statute covers this situation?"),
    ("legislation", "Is there legislation about noise control?"),
]

# --- G2: must be rejected ----------------------------------------------------
REJECT_CASES = [
    ("greeting", "hey"),
    ("greeting long", "hi there how are you today"),
    ("thanks", "thanks!"),
    ("thanks with laugh", "haha thanks that's great"),
    ("goodbye", "ok bye"),
    ("dev chatter", "just testing this out"),
    ("smalltalk", "nice weather today isn't it"),
    ("ack", "ok"),
    ("ack 2", "sure sounds good to me"),
    ("emoji-ish", "cool :)"),
    ("name", "my name is Joe"),
    ("compliment", "this is a really nice tool you have built here"),
]


@pytest.mark.parametrize("label,query", ACCEPT_CASES, ids=[c[0] for c in ACCEPT_CASES])
def test_g1_legal_queries_accepted(app_module, label, query):
    detected = app_module.detect_act_from_query(query)
    assert app_module._is_legal_query(query, detected), f"false reject: {query!r}"


@pytest.mark.parametrize("label,query", REJECT_CASES, ids=[c[0] for c in REJECT_CASES])
def test_g2_casual_queries_rejected(app_module, label, query):
    detected = app_module.detect_act_from_query(query)
    assert not app_module._is_legal_query(query, detected), f"false accept: {query!r}"


def test_gate_case_count():
    """The charter asks for at least 30 accept/reject cases."""
    assert len(ACCEPT_CASES) + len(REJECT_CASES) >= 30


# --- G3: follow-up continuity ------------------------------------------------

FOLLOWUP_ACCEPT = [
    "and section 6?",
    "what about part 2?",
    "tell me more about that",
    "explain that again",
    "how does that apply to me?",
    "also, what about the notice period?",
]

FOLLOWUP_REJECT = [
    "haha thanks",
    "great, cheers",
    "ok",
]


@pytest.fixture
def legal_session(app_module):
    session_id = "gate-followup-session"
    app_module.conversation_history[session_id] = [
        {"role": "user", "content": "What does the Residential Tenancies Act say about bonds?"},
        {"role": "assistant", "content": "Section 18 caps a general bond at 4 weeks' rent."},
    ]
    yield session_id
    app_module.conversation_history.pop(session_id, None)


@pytest.mark.parametrize("query", FOLLOWUP_ACCEPT)
def test_g3_followups_accepted_with_legal_history(app_module, legal_session, query):
    detected = app_module.detect_act_from_query(query)
    assert app_module._is_legal_query(query, detected, legal_session), \
        f"follow-up rejected despite legal history: {query!r}"


@pytest.mark.parametrize("query", FOLLOWUP_REJECT)
def test_g3_casual_followups_still_rejected(app_module, legal_session, query):
    detected = app_module.detect_act_from_query(query)
    assert not app_module._is_legal_query(query, detected, legal_session), \
        f"casual follow-up accepted: {query!r}"


def test_g3_followup_without_history_is_rejected(app_module):
    """Same short message, no legal history — must not retrieve."""
    assert not app_module._is_legal_query("and section 6?".replace("section", "part"),
                                          None, "no-such-session")


def test_gate_always_accepts_when_act_detected(app_module):
    assert app_module._is_legal_query("blah blah", "Residential Tenancies")


def test_long_messages_default_to_accept(app_module):
    long_message = " ".join(["word"] * 40)
    assert app_module._is_legal_query(long_message, None)


# --- act detection sanity ----------------------------------------------------

@pytest.mark.parametrize("query,expected", [
    ("What does the Residential Tenancies Act say?", "Residential Tenancies"),
    ("bond dispute with my landlord", "Residential Tenancies"),
    ("unjustified dismissal claim", "Employment Relations"),
    ("Privacy Act 2020 purpose", "Privacy"),
    ("misleading and deceptive conduct", "Fair Trading"),
])
def test_act_detection_hits(app_module, query, expected):
    assert app_module.detect_act_from_query(query) == expected


@pytest.mark.parametrize("query", [
    "hello there",
    "what time is it",
    "thanks very much",
])
def test_act_detection_no_false_positive(app_module, query):
    assert app_module.detect_act_from_query(query) is None


def test_act_detection_word_boundary(app_module):
    """'pla' must not match inside 'explain' (regression guard on the
    word-boundary matching in acts_registry.detect_act_from_query)."""
    assert app_module.detect_act_from_query("please explain") is None


# --- C-002: scored act detection ---------------------------------------------
#
# detect_act_from_query() used to return the first registry act with any keyword
# hit, in dict order, so a single generic word decided which act the answer was
# filtered to. Each case below produced a wrong citation in prod: the answer
# would silently cite the named act. `None` is the correct outcome whenever the
# evidence is only a generic or actor-naming word — retrieval then decides.

WRONG_CITATION_CASES = [
    # (query, what first-hit-wins returned, what it must return now)
    ("Who has the power to make laws in New Zealand?", "Electricity", None),
    ("What are my rights if the police arrest me?", "Policing", None),
    ("When am I allowed to use force in self defence?", "Defence", None),
    ("What protection is there against unreasonable search and seizure?",
     "Search and Surveillance", None),
    ("Are unfair contract terms banned in standard form consumer contracts?",
     "Consumer Guarantees", None),
    # From the first swarm run:
    ("Can a business charge extra for delivery?", "Criminal Procedure", None),
    ("Can I request information from a government agency?", "Public Service", None),
    ("Can a New Zealand citizen be forced to say something against their will?",
     "Citizenship", None),
    ("Can my employer check my social media without my consent?",
     "Employment Relations", None),
]


@pytest.mark.parametrize("query,was,expected", WRONG_CITATION_CASES,
                         ids=[c[0][:40] for c in WRONG_CITATION_CASES])
def test_generic_keyword_no_longer_picks_an_act(app_module, query, was, expected):
    got = app_module.detect_act_from_query(query)
    assert got == expected, (
        f"{query!r} detected {got!r}; first-hit-wins used to say {was!r}, "
        f"expected {expected!r}"
    )


# Two cases where a *stronger* competitor exists and must win outright.
STRONGER_MATCH_WINS = [
    ("What health and safety duties do company officers have?",
     "Companies", "Health and Safety at Work"),
    ("Are there specific duties that my employer must fulfill under the "
     "Health and Safety at Work Act?", "Employment Relations", "Health and Safety at Work"),
    ("Can I be charged for driving over the speed limit?",
     "Land Transport", "Land Transport"),
]


@pytest.mark.parametrize("query,was,expected", STRONGER_MATCH_WINS,
                         ids=[c[0][:40] for c in STRONGER_MATCH_WINS])
def test_multiword_match_beats_generic_single_word(app_module, query, was, expected):
    got = app_module.detect_act_from_query(query)
    assert got == expected, f"{query!r} detected {got!r}, expected {expected!r} (was {was!r})"


# Positives: these must keep detecting, or the act filter stops helping at all.
MUST_STILL_DETECT = [
    ("What does the Residential Tenancies Act say about bonds?", "Residential Tenancies"),
    ("bond dispute with my landlord", "Residential Tenancies"),
    ("How much notice to end a tenancy?", "Residential Tenancies"),
    ("RTA section 18", "Residential Tenancies"),
    ("unjustified dismissal claim", "Employment Relations"),
    ("my employer did not pay my wages", "Employment Relations"),
    ("s103 of the ERA", "Employment Relations"),
    ("What is the purpose of the Privacy Act 2020?", "Privacy"),
    ("personal information held overseas", "Privacy"),
    ("misleading and deceptive conduct", "Fair Trading"),
    ("What does the Fair Trading Act cover?", "Fair Trading"),
    ("consumer guarantees for a faulty product", "Consumer Guarantees"),
    ("What is the primary duty of care of a PCBU?", "Health and Safety at Work"),
    ("director duties under the Companies Act", "Companies"),
    ("official information request", "Official Information"),
    ("crimes act burglary", "Crimes"),
    ("resource consent for a deck", "Resource Management"),
]


@pytest.mark.parametrize("query,expected", MUST_STILL_DETECT,
                         ids=[c[0][:40] for c in MUST_STILL_DETECT])
def test_detection_positives_survive_scoring(app_module, query, expected):
    assert app_module.detect_act_from_query(query) == expected


def test_detection_positive_case_count():
    assert len(MUST_STILL_DETECT) >= 10, "C-002 asks for at least 10 positive cases"


def test_weak_keyword_alone_never_selects(app_module):
    """An act whose only evidence is an ambiguous keyword is never chosen."""
    from backend.app import acts_registry

    for keyword in sorted(acts_registry._WEAK_KEYWORDS):
        detected = acts_registry.detect_act_from_query(f"tell me about {keyword}")
        assert detected is None, (
            f"weak keyword {keyword!r} alone selected {detected!r}"
        )


def test_weak_keyword_still_contributes_once_something_strong_matches(app_module):
    """Weak keywords are not ignored — they add score to an act that already
    has real evidence."""
    from backend.app import acts_registry

    scores = {a["short_name"]: a for a in
              acts_registry.score_acts_for_query("company director liquidation")}
    assert "CA" in scores
    assert scores["CA"]["has_strong"] is True
    assert scores["CA"]["matched"] >= 3, "the weak 'company' hit should still count"


def test_ambiguous_tie_returns_none(app_module):
    """Two acts within the margin is ambiguous; no filter is safer than a
    coin flip between them."""
    from backend.app import acts_registry

    # 'human rights' is claimed by both the Human Rights Act and NZBORA.
    ranked = acts_registry.score_acts_for_query("human rights")
    assert len(ranked) >= 2
    assert ranked[0]["score"] == ranked[1]["score"], "expected a genuine tie"
    assert acts_registry.detect_act_from_query("human rights") is None


def test_detection_is_cheap(app_module):
    """Scoring every act runs on every /chat request, so it must stay fast."""
    import time
    from backend.app import acts_registry

    queries = [q for q, _ in MUST_STILL_DETECT]
    started = time.perf_counter()
    for _ in range(10):
        for q in queries:
            acts_registry.detect_act_from_query(q)
    per_call_ms = (time.perf_counter() - started) * 1000 / (10 * len(queries))
    assert per_call_ms < 5.0, f"detection cost {per_call_ms:.2f} ms/query"
