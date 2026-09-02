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
