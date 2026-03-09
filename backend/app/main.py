#!/usr/bin/env python3
"""
main.py

FastAPI backend for Bowen - NZ Legal Assistant
Uses numpy-based vector search and Claude API.

Run from magna root:
    cd ~/Desktop/magna
    uvicorn backend.app.main:app --reload --port 8000
"""

import os
import json
import uuid
import time
import numpy as np

from .key_sections import get_key_sections_for_query, should_boost_section
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, APIRouter, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from pydantic import BaseModel, Field
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")  # For accessing logs
LOGS_DIR = Path(os.getenv("LOGS_DIR", "logs"))  # Use env var for Railway volume
EMBEDDINGS_DIR = Path("data/embeddings")
REFERENCES_DIR = Path("data/references")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5
MIN_SIMILARITY = 0.25  # Floor: discard results below this cosine similarity
MAX_BOOST = 2.5        # Cap: prevent multiplicative boost inflation
MAX_HISTORY = 10       # Max conversation turns (user+assistant pairs) to keep

# In-memory conversation history keyed by session_id
conversation_history: dict[str, list[dict]] = {}

# Pydantic models
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000, description="User message")
    session_id: Optional[str] = Field(None, max_length=100, description="Session ID for conversation tracking")

class Source(BaseModel):
    act_title: str
    section_number: str
    section_heading: str
    url: str
    excerpt: str
    score: float

class ChatResponse(BaseModel):
    response: str
    sources: List[Source]
    disclaimer: str

# API Version
API_VERSION = "1.0.0"

# Initialize FastAPI
app = FastAPI(
    title="Bowen - NZ Legal Assistant",
    description="Chatbot legal information retrieval for New Zealand legislation",
    version=API_VERSION
)

# API v1 Router
api_v1 = APIRouter(prefix="/api/v1", tags=["v1"])

# CORS - Configure allowed origins from environment
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else []
DEFAULT_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
CORS_ORIGINS = ALLOWED_ORIGINS if ALLOWED_ORIGINS else DEFAULT_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response


app.add_middleware(SecurityHeadersMiddleware)

# Global state
embeddings = None
metadata = None
embedding_model = None
anthropic_client = None
references = []  # Curated scholarly references

# Import act detection from registry (single source of truth)
from .acts_registry import detect_act_from_query, get_all_acts, ACTS_REGISTRY

# System prompt
SYSTEM_PROMPT = f"""You are Bowen, a chatbot legal information assistant for New Zealand legislation.

## IDENTITY
You ARE Bowen. Always refer to yourself in the first person — "I", "me", "my". Never say "Bowen is..." or "Bowen has..." — say "I am...", "I have...". When someone asks "What's Bowen about?", respond with "I'm a legal information assistant..." not "Bowen is a legal information assistant...".

## YOUR KNOWLEDGE
You have general knowledge about NZ law from your training, including:
- The purpose and scope of major NZ Acts
- How NZ legal system works
- Common legal concepts and terminology

## TE TIRITI O WAITANGI / TREATY OF WAITANGI
The Treaty is foundational to NZ law and requires particular care in your responses.

### Constitutional Status
The Treaty is not formally part of NZ's constitution, but has been described as a "constitutional document" by the courts. Its legal effect depends on incorporation into statute - it has no direct legal force unless Parliament gives it effect through legislation. However, its principles increasingly permeate NZ law.

### The Two Texts
There are material differences between the Māori and English texts:
- Article 1: Māori text cedes "kāwanatanga" (governance), English cedes "sovereignty"
- Article 2: Māori guarantees "tino rangatiratanga" (full chieftainship) over taonga; English guarantees "exclusive and undisturbed possession" of lands, estates, forests, fisheries
- Article 2 also established Crown pre-emption (exclusive right to purchase Māori land)
- Article 3: Both texts grant Māori the rights of British subjects

### Treaty Principles (from case law)
Key principles developed through litigation include:
- **Partnership**: The Crown and Māori are partners, requiring good faith and reasonable cooperation
- **Active Protection**: The Crown must actively protect Māori interests, not merely avoid harming them
- **Redress**: Where the Crown has breached Treaty obligations, it should provide redress
- **Informed Decision-making**: Māori should have sufficient information to make decisions about their taonga

### Key Cases
- **R v Symonds (1847)**: Recognised native title; Crown's exclusive pre-emption right
- **Wi Parata v Bishop of Wellington (1877)**: Described Treaty as "a simple nullity" - this was the dominant view for over a century but is now discredited
- **NZ Maori Council v Attorney-General [1987] (Lands Case)**: Pivotal case establishing Treaty principles; Court of Appeal held the Crown must act in good faith and make informed decisions
- **Te Runanga o Muriwhenua v Attorney-General [1990]**: Fisheries and Treaty rights
- **Ngati Apa v Attorney-General [2003]**: Recognised Māori customary title to foreshore and seabed may not have been extinguished

### Treaty Clauses in Modern Legislation
Many NZ Acts now contain Treaty clauses requiring decision-makers to consider Treaty principles:
- RMA 1991, s8: "shall take into account the principles of the Treaty"
- Conservation Act 1987, s4: "shall give effect to the principles of the Treaty"
- Education and Training Act 2020, s9: Treaty obligations
- Local Government Act 2002, s4: Treaty principles in local governance

### The Waitangi Tribunal
Established by the Treaty of Waitangi Act 1975, the Tribunal:
- Investigates Crown breaches of Treaty principles
- Makes recommendations (generally not binding)
- Can investigate historical claims back to 1840
- Has produced significant reports on Treaty settlements

### Responding to Treaty Questions
When users ask about Treaty matters:
1. Acknowledge the complexity and ongoing nature of Treaty jurisprudence
2. Note the difference between Māori and English texts where relevant
3. Distinguish between historical positions (like Wi Parata) and modern law
4. Reference specific Treaty clauses in relevant Acts
5. Be respectful of the significance of these issues to Māori and to NZ's constitutional development

## YOUR ROLE
1. Use your general knowledge to EXPLAIN and provide context about NZ legislation
2. Use the PROVIDED EXCERPTS to cite SPECIFIC sections and current wording
3. Combine both to give comprehensive, accurate answers

## CRITICAL RULES
1. You provide INFORMATION only, NOT legal advice
2. When citing specific provisions, use the exact wording from the excerpts
3. If excerpts don't contain relevant detail, use your general knowledge but note "Based on my general knowledge..." vs "According to Section X..."
4. Always distinguish between:
   - What you know generally about the law
   - What is specifically cited from the excerpts provided
5. For "What is [Act]?" questions, explain the Act's purpose and scope from general knowledge, then cite any relevant sections from excerpts
6. IMPORTANT: The user's question may contain quoted legal text they want explained. This is NOT an excerpt from the database - it's text the user is asking about. Only treat content under "LEGISLATION EXCERPTS FROM DATABASE:" as official excerpts. If the user pastes text and asks about it, help them understand it using the database excerpts and your knowledge.
7. In some of the User testing Bowen took on a legal personality, which was good, but remember that Bowen is also his own personality, with his data bank and precision on access to legal documentation. Bowen has passion and humour but never provides advice only information. Bowen believes that information transmission is one of the essences of the universe. And that perhaps Law is like a semantic engine that constantly translates between different levels of abstraction - from broad principles to specific rules to particular applications. The real tension is temporal and contextual: how do we write rules today that will make sense when applied to unforeseen situations tomorrow? When developer Joe is testing, he will type BPCT at the beggining of the chat, please feel free to let me know how changes would assist this public asset. 
8. If you establish that a user is real and interested in the work you're doing (not trolling), then you may become more conversational and chat about other matters based on your general knowledge. 

## RESPONSE APPROACH
For general questions ("What is the RMA?"):
- Lead with a general explanation from your knowledge
- Then cite specific sections if the excerpts contain relevant provisions
- Mention key sections even if not in excerpts (e.g., "Section 5 sets out the purpose...")

For specific questions ("What is the bond limit?"):
- Answer directly using the excerpts
- Cite the exact section and wording
- Add context from general knowledge if helpful

## AVAILABLE ACTS
You have FULL-TEXT coverage of {len(ACTS_REGISTRY)} NZ Acts (as at March 2026), sourced directly from legislation.govt.nz. This is comprehensive — not "bits and pieces" or selective excerpts. For example, the Resource Management Act 1991 alone has over 1,000 sections and 7,000+ text chunks in your database. When users ask what you have access to, be confident: you hold the complete published text of every Act in your registry. Do NOT guess or understate your coverage.

## CITATION FORMAT
When citing from excerpts: "Under Section X of the [Act Name]..."
When using general knowledge: "The [Act] generally provides for..." or "Based on my understanding of NZ law..."

Always end responses by encouraging users to verify current legislation at legislation.govt.nz and consult a lawyer for specific situations."""

DISCLAIMER = """⚠️ Bowen is a chatbot, not legal advice. It may be incomplete or outdated. For legal decisions, consult a qualified NZ lawyer or Community Law Centre."""


from .logger import logger, LogEvent
from .errors import (
    raise_empty_message,
    raise_invalid_query,
    raise_embeddings_not_loaded,
    raise_model_not_loaded,
    raise_anthropic_unavailable,
    raise_generation_failed,
    ErrorCode,
    InternalError
)


@app.on_event("startup")
async def startup():
    """Load models and data on startup."""
    global embeddings, metadata, embedding_model, anthropic_client, references

    print("\n" + "=" * 50)
    print("Starting Bowen Backend...")
    print("=" * 50)

    # Validate required environment variables
    missing_vars = []
    if not ANTHROPIC_API_KEY:
        missing_vars.append("ANTHROPIC_API_KEY")

    if missing_vars:
        print(f"\n✗ CRITICAL: Missing required environment variables: {', '.join(missing_vars)}")
        print("  Set these in your .env file or environment before starting the server.")
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")

    # Log CORS configuration
    print(f"\n✓ CORS origins: {CORS_ORIGINS}")
    
    # Load embeddings
    embeddings_path = EMBEDDINGS_DIR / "embeddings.npy"
    metadata_path = EMBEDDINGS_DIR / "metadata.json"
    
    if embeddings_path.exists() and metadata_path.exists():
        print(f"\nLoading embeddings from {embeddings_path}...")
        embeddings = np.load(embeddings_path, allow_pickle=True)
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        print(f"✓ Loaded {len(metadata):,} chunks")
    else:
        print(f"✗ Embeddings not found at {EMBEDDINGS_DIR}")
        print("  Run generate_embeddings.py first")
    
    # Load embedding model
    try:
        from sentence_transformers import SentenceTransformer
        print(f"\nLoading embedding model: {EMBEDDING_MODEL}...")
        embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        print("✓ Embedding model loaded")
    except Exception as e:
        print(f"✗ Could not load embedding model: {e}")
    
    # Initialize Anthropic client
    if ANTHROPIC_API_KEY:
        try:
            import anthropic
            anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            print("✓ Anthropic client initialized")
        except Exception as e:
            print(f"✗ Could not initialize Anthropic: {e}")
    else:
        print("✗ ANTHROPIC_API_KEY not set in .env")

    # Initialize logs directory
    LOGS_DIR.mkdir(exist_ok=True)
    print("✓ Logs directory ready")

    # Load curated references
    if REFERENCES_DIR.exists():
        for ref_file in REFERENCES_DIR.glob("*.json"):
            try:
                with open(ref_file, 'r') as f:
                    ref_data = json.load(f)
                    references.append(ref_data)
                    print(f"✓ Loaded reference: {ref_data.get('title', ref_file.name)}")
            except Exception as e:
                print(f"✗ Could not load reference {ref_file.name}: {e}")
        print(f"✓ Loaded {len(references)} curated references")
    else:
        print("  No references directory found (optional)")

    print("\n" + "=" * 50)
    print("Startup complete!")
    print("=" * 50 + "\n")


def search_similar(query: str, top_k: int = TOP_K, act_filter: str = None) -> List[dict]:
    """
    Search for similar chunks with:
    - Optional act filtering
    - Keyword boosting for overview questions
    - KEY SECTION boosting for common topics
    """
    if embeddings is None or embedding_model is None:
        return []

    # Encode query
    query_embedding = embedding_model.encode(query, convert_to_numpy=True)

    # Calculate cosine similarities
    similarities = np.dot(embeddings, query_embedding).copy()

    query_lower = query.lower()

    # Get key sections for this query
    key_sections = get_key_sections_for_query(query)

    # Keyword boosting for "what is" questions
    boost_terms = ['purpose', 'interpretation', 'application', 'object', 'principle', 'definition']
    is_overview_question = any(q in query_lower for q in ['what is', 'what are', 'explain', 'overview', 'purpose of'])

    for i, meta in enumerate(metadata):
        raw_score = similarities[i]

        # Skip chunks below minimum similarity (no point boosting junk)
        if raw_score < MIN_SIMILARITY:
            continue

        text_lower = meta.get('text', '').lower()
        heading_lower = meta.get('section_heading', '').lower()
        section_num = meta.get('section_number', '').strip()

        # Track total boost to cap it
        total_boost = 1.0

        # Apply key section boosting
        section_boost = should_boost_section(meta, key_sections)
        if section_boost > 1.0:
            total_boost *= section_boost

        # Boost purpose/interpretation sections for overview questions
        if is_overview_question:
            for term in boost_terms:
                if term in heading_lower or term in text_lower[:200]:
                    total_boost *= 1.3
                    break  # Only one term boost per chunk

            # Boost early sections (usually purpose/interpretation)
            if section_num.isdigit() and int(section_num) <= 10:
                total_boost *= 1.2

        # Boost chunks with actual section numbers
        if section_num and section_num.replace('.', '').isdigit():
            total_boost *= 1.1

        # Boost chunks where section heading matches query terms
        query_terms = [t for t in query_lower.split() if len(t) > 3]
        for term in query_terms:
            if term in heading_lower:
                total_boost *= 1.4
                break  # Only boost once per chunk

        # Cap total boost to prevent weak matches from inflating
        total_boost = min(total_boost, MAX_BOOST)
        similarities[i] = raw_score * total_boost

    # Apply act filter if specified
    if act_filter:
        act_filter_lower = act_filter.lower()
        for i, meta in enumerate(metadata):
            act_title = meta.get('act_title', '').lower()
            act_short = meta.get('act_short_name', '').lower()
            if act_filter_lower not in act_title and act_filter_lower not in act_short:
                similarities[i] = -1  # Exclude non-matching acts

    # Get top-k indices
    top_indices = np.argsort(similarities)[-top_k:][::-1]

    # Filter out low-relevance and excluded results
    top_indices = [i for i in top_indices if similarities[i] >= MIN_SIMILARITY]

    results = []
    for idx in top_indices:
        meta = metadata[idx]
        results.append({
            "text": meta.get("text", ""),
            "act_title": meta.get("act_title", ""),
            "act_short_name": meta.get("act_short_name", ""),
            "section_number": meta.get("section_number", ""),
            "section_heading": meta.get("section_heading", ""),
            "section_url": meta.get("section_url", ""),
            "act_url": meta.get("act_url", ""),
            "score": float(similarities[idx])
        })

    return results


def build_context(results: List[dict]) -> str:
    """Build context string with better organization."""
    if not results:
        return "No specific legislation excerpts found for this query. Please use your general knowledge about NZ law."

    # Group by Act
    by_act = {}
    for r in results:
        act = r['act_title']
        if act not in by_act:
            by_act[act] = []
        by_act[act].append(r)

    parts = []
    for act_title, act_results in by_act.items():
        act_section = f"## {act_title}\n\n"
        for r in act_results:
            if r['section_number']:
                act_section += f"**Section {r['section_number']}"
                if r['section_heading']:
                    act_section += f" - {r['section_heading']}"
                act_section += f"**\n{r['text']}\n\n"
            else:
                act_section += f"{r['text']}\n\n"
        parts.append(act_section)

    return "\n---\n\n".join(parts)


def find_matching_references(query: str) -> List[dict]:
    """Find curated references that match the query based on keywords."""
    if not references:
        return []

    query_lower = query.lower()
    matches = []

    for ref in references:
        # Check if any keywords match
        keywords = ref.get('keywords', [])
        topics = ref.get('topics', [])
        all_terms = keywords + topics

        matched_terms = []
        for term in all_terms:
            if term.lower() in query_lower:
                matched_terms.append(term)

        # Also check for partial matches on important terms
        important_terms = ['treaty', 'waitangi', 'maori', 'land', 'possession', 'title', 'property']
        for term in important_terms:
            if term in query_lower and term not in [t.lower() for t in matched_terms]:
                # Check if reference covers this term
                if any(term in kw.lower() for kw in all_terms):
                    matched_terms.append(term)

        if matched_terms:
            matches.append({
                'reference': ref,
                'matched_terms': list(set(matched_terms)),
                'score': len(set(matched_terms))
            })

    # Sort by number of matched terms (relevance)
    matches.sort(key=lambda x: x['score'], reverse=True)
    return matches


def build_reference_context(matched_refs: List[dict]) -> str:
    """Build context string from matched references."""
    if not matched_refs:
        return ""

    parts = []
    for match in matched_refs[:2]:  # Limit to top 2 most relevant references
        ref = match['reference']
        parts.append(f"""## Curated Reference: {ref.get('title', 'Unknown')}
**Source:** Essay on Bowen's Te Tiriti page (bowenpublic.com/te-tiriti)
**Relevance:** Matched on: {', '.join(match['matched_terms'])}

**Summary:** {ref.get('summary', '')}

**Key Historical Context:**
{chr(10).join('- ' + str(e['year']) + ': ' + e['event'] for e in ref.get('historical_timeline', [])[:5])}

**Key Cases Discussed:**
{chr(10).join('- ' + c['name'] + ' ' + c['citation'] + ' - ' + c['relevance'] for c in ref.get('key_cases', [])[:4])}
""")

    return "\n---\n\n".join(parts)


async def generate_response(query: str, context: str, reference_context: str = "", session_id: str = "") -> str:
    """Generate response using Claude with hybrid knowledge approach and conversation memory."""
    if not anthropic_client:
        raise_anthropic_unavailable()

    # Build the reference section if we have matching references
    reference_section = ""
    if reference_context:
        reference_section = f"""
---

CURATED SCHOLARLY REFERENCES (use for historical context and case law background):
{reference_context}

---
"""

    # Build the current user message with context
    current_user_content = f"""USER'S QUESTION:
{query}

---

LEGISLATION EXCERPTS FROM DATABASE (these are the official excerpts you should cite):
{context}
{reference_section}
Please answer the user's question using:
1. Your general knowledge about NZ law to provide context and explanation
2. The specific excerpts above to cite exact provisions and wording
3. The curated scholarly references (if provided) for historical context and case law

Note: If the user's question contains quoted legal text, that is text THEY are asking about - not an official excerpt. Only cite from the "LEGISLATION EXCERPTS FROM DATABASE" section above.

If the excerpts don't contain the specific information needed, use your general knowledge but make clear what comes from the excerpts vs your training.

When using curated references, cite them as: "According to the essay on Bowen's Te Tiriti page..." or "As discussed in the essay 'From Possession to Ownership' on Bowen's Te Tiriti page..." Never attribute the essay to a named individual.

Remember: Provide information, not legal advice. Cite specific sections where possible."""

    # Build messages array with conversation history
    messages = []
    if session_id and session_id in conversation_history:
        messages.extend(conversation_history[session_id])
    messages.append({"role": "user", "content": current_user_content})

    try:
        message = anthropic_client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        response_text = message.content[0].text

        # Store conversation history
        if session_id:
            if session_id not in conversation_history:
                conversation_history[session_id] = []
            # Store the raw user query (not the full context) to save tokens
            conversation_history[session_id].append({"role": "user", "content": query})
            conversation_history[session_id].append({"role": "assistant", "content": response_text})
            # Trim to last N turns (each turn = 2 messages)
            if len(conversation_history[session_id]) > MAX_HISTORY * 2:
                conversation_history[session_id] = conversation_history[session_id][-(MAX_HISTORY * 2):]

        return response_text
    except Exception as e:
        logger.error(LogEvent.CLAUDE_ERROR, f"Claude API error: {e}", error=e)
        raise_generation_failed(str(e))


def log_query(
    session_id: str,
    ip: str,
    query: str,
    response: str,
    detected_act: str,
    sources_count: int,
    response_time_ms: int
):
    """Log query to JSON file."""
    try:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "session_id": session_id,
            "ip": ip,
            "query": query,
            "response": response,
            "detected_act": detected_act,
            "sources_count": sources_count,
            "response_time_ms": response_time_ms
        }

        log_file = LOGS_DIR / "queries.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        logger.error(LogEvent.ANALYTICS_FAILURE, f"Failed to log query: {e}", error=e)


@app.get("/")
async def root():
    return {
        "name": "Bowen - NZ Legal Assistant",
        "version": "0.1.0",
        "status": "running",
        "chunks_loaded": len(metadata) if metadata else 0
    }


@app.get("/health")
async def health():
    failure_counts = logger.get_failure_counts()
    return {
        "status": "healthy",
        "embeddings_loaded": embeddings is not None,
        "model_loaded": embedding_model is not None,
        "anthropic_ready": anthropic_client is not None,
        "chunks": len(metadata) if metadata else 0,
        "analytics_failures": failure_counts,
        "has_failures": len(failure_counts) > 0
    }


@app.get("/admin/logs")
async def get_logs(token: str = Query(..., description="Admin token")):
    """Download query logs. Requires ADMIN_TOKEN."""
    if not ADMIN_TOKEN or token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid admin token")

    log_file = LOGS_DIR / "queries.jsonl"
    if not log_file.exists():
        return {"message": "No logs yet", "entries": []}

    entries = []
    with open(log_file, "r") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))

    return {
        "total": len(entries),
        "entries": entries
    }


@app.get("/admin/stats")
async def get_stats(token: str = Query(..., description="Admin token")):
    """Get quick stats. Requires ADMIN_TOKEN."""
    if not ADMIN_TOKEN or token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid admin token")

    log_file = LOGS_DIR / "queries.jsonl"
    if not log_file.exists():
        return {"total_queries": 0, "top_acts": {}}

    entries = []
    with open(log_file, "r") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))

    # Count by act
    act_counts = {}
    for e in entries:
        act = e.get("detected_act") or "Unknown"
        act_counts[act] = act_counts.get(act, 0) + 1

    # Sort by count
    top_acts = dict(sorted(act_counts.items(), key=lambda x: x[1], reverse=True)[:10])

    return {
        "total_queries": len(entries),
        "top_acts": top_acts
    }


import re

# Legal signal patterns — if any match, always retrieve
_LEGAL_SIGNALS = re.compile(
    r'(?i)'
    r'(?:\bsection\s+\d|'          # "section 5"
    r'\bs\s?\d|'                    # "s5" or "s 5"
    r'\bact\b|'                     # "act"
    r'\blaw\b|'                     # "law"
    r'\blegal\b|'                   # "legal"
    r'\blegislat|'                  # "legislation/legislative"
    r'\bstatut|'                    # "statute/statutory"
    r'\bconsent\b|'                 # "consent"
    r'\btribunal\b|'               # "tribunal"
    r'\bcourt\b|'                   # "court"
    r'\bliable|liability\b|'       # "liable/liability"
    r'\boffence\b|'                # "offence"
    r'\bpenalt|'                   # "penalty/penalties"
    r'\bbond\b|'                   # "bond"
    r'\btenant|tenancy\b|'         # "tenant/tenancy"
    r'\blandlord\b|'              # "landlord"
    r'\bresource\s+consent|'       # "resource consent"
    r'\bemployment\b|'             # "employment"
    r'\bwhat\s+is\b|'             # "what is" (likely asking about a concept)
    r'\bhow\s+does\b|'            # "how does"
    r'\bcan\s+(?:i|you|they)\b|'  # "can I/you/they"
    r'\bam\s+i\s+allowed\b|'      # "am I allowed"
    r'\brights?\b|'               # "right/rights"
    r'\bobligat|'                  # "obligation/obligations"
    r'\btreaty\b|'                 # "treaty"
    r'\btiriti\b|'                 # "tiriti"
    r'\bmāori\b|'                  # "māori"
    r'\bproperty\b|'              # "property"
    r'\bcontract\b|'              # "contract"
    r'\bcriminal\b|'              # "criminal"
    r'\bfine\b|'                   # "fine"
    r'\bnotice\b)'                 # "notice"
)


def _is_legal_query(query: str, detected_act: str | None, session_id: str = "") -> bool:
    """Lightweight check: should we search the legislation database?

    Errs on the side of inclusion — only skips clearly casual messages.
    """
    # If an act was detected, always search
    if detected_act:
        return True

    # If there's conversation history, check if any recent message was legal
    # Short vague follow-ups ("what about part 1?", "and section 6?") should retrieve
    # but purely casual messages ("haha thanks", "hey how are you") should not
    if session_id and session_id in conversation_history and conversation_history[session_id]:
        # Check last 3 user messages — if any had legal signals, this is likely a follow-up
        recent_user_msgs = [m['content'] for m in conversation_history[session_id] if m['role'] == 'user'][-3:]
        has_recent_legal = any(_LEGAL_SIGNALS.search(m) for m in recent_user_msgs)
        # Only treat as follow-up if query looks like a question or reference, not a greeting
        query_words = query.lower().split()
        followup_starts = ['what', 'which', 'tell', 'explain', 'and', 'also', 'part', 'section', 'how']
        is_followup_shaped = (len(query_words) > 0 and query_words[0] in followup_starts) or any(w in query.lower() for w in ['about', 'part ', 'section'])
        if has_recent_legal and is_followup_shaped:
            return True

    # If any legal signal word/pattern is present, search
    if _LEGAL_SIGNALS.search(query):
        return True

    # Short casual messages (greetings, dev notes) — skip
    # Longer messages are more likely to contain a real question
    if len(query.split()) <= 30:
        return False

    # Default: search (err on side of inclusion)
    return True


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, req: Request):
    """Main chat endpoint with improved retrieval."""
    start_time = time.time()
    query = request.message.strip()

    if not query:
        raise_empty_message()

    # Check service availability
    if embeddings is None or metadata is None:
        raise_embeddings_not_loaded()

    if embedding_model is None:
        raise_model_not_loaded()

    if anthropic_client is None:
        raise_anthropic_unavailable()

    # Get or generate session ID
    session_id = request.session_id or str(uuid.uuid4())

    # Detect if asking about specific Act
    detected_act = detect_act_from_query(query)

    # Log incoming request
    logger.log_chat_request(session_id, len(query), detected_act)

    # Skip retrieval for clearly non-legal casual messages
    is_legal_query = _is_legal_query(query, detected_act, session_id)

    if is_legal_query:
        # Search with optional act filter
        results = search_similar(
            query,
            top_k=6,  # Retrieve 6, display up to 3 after filtering
            act_filter=detected_act
        )

        # Build context
        context = build_context(results)

        # Find matching curated references
        matched_refs = find_matching_references(query)
        reference_context = build_reference_context(matched_refs)
    else:
        results = []
        context = "No legislation search performed — this appears to be a casual/non-legal message."
        reference_context = ""

    # Generate response
    response_text = await generate_response(query, context, reference_context, session_id)

    # Format sources (deduplicate by act+section, or by text hash if no section)
    sources = []
    seen = set()
    for r in results:
        section_num = r['section_number'].strip() if r['section_number'] else ''

        if section_num:
            # Standard deduplication by act:section
            key = f"{r['act_title']}:{section_num}"
        else:
            # For chunks without section numbers, use text hash to avoid false duplicates
            text_hash = hash(r['text'][:100])
            key = f"{r['act_title']}:__no_section__{text_hash}"

        if key not in seen:
            seen.add(key)
            sources.append(Source(
                act_title=r['act_title'],
                section_number=section_num if section_num else 'General',
                section_heading=r['section_heading'] or 'General Provisions',
                url=r['section_url'] or r['act_url'],
                excerpt=r['text'][:200] + "..." if len(r['text']) > 200 else r['text'],
                score=r['score']
            ))

    # Calculate response time
    response_time_ms = int((time.time() - start_time) * 1000)

    # Log query to JSON file
    client_ip = req.headers.get("X-Forwarded-For", req.client.host if req.client else "unknown")
    if "," in client_ip:
        client_ip = client_ip.split(",")[0].strip()  # Get first IP if multiple

    log_query(
        session_id=session_id,
        ip=client_ip,
        query=query,
        response=response_text,
        detected_act=detected_act,
        sources_count=len(sources),
        response_time_ms=response_time_ms
    )

    # Log response metrics
    logger.log_chat_response(session_id, response_time_ms, len(sources), success=True)

    return ChatResponse(
        response=response_text,
        sources=sources[:3],  # Limit to top 3 most relevant sources
        disclaimer=DISCLAIMER
    )


@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear conversation history for a session."""
    conversation_history.pop(session_id, None)
    return {"status": "cleared"}


@app.get("/search")
async def search(
    q: str = Query(..., min_length=1, max_length=1000, description="Search query"),
    limit: int = Query(default=10, ge=1, le=20, description="Maximum results to return")
):
    """Direct search endpoint."""
    if embeddings is None or embedding_model is None:
        raise_embeddings_not_loaded()

    results = search_similar(q, top_k=limit)
    
    return {
        "query": q,
        "results": [
            {
                "act_title": r["act_title"],
                "section_number": r["section_number"],
                "section_heading": r["section_heading"],
                "text": r["text"],
                "score": r["score"],
                "url": r["section_url"] or r["act_url"]
            }
            for r in results
        ]
    }


@app.get("/acts")
async def list_acts():
    """List all available acts from the registry (single source of truth)."""
    return {"acts": get_all_acts()}


# =============================================================================
# API v1 Routes (versioned endpoints)
# =============================================================================

@api_v1.get("/health")
async def v1_health():
    """Health check endpoint (v1)."""
    return await health()


@api_v1.post("/chat", response_model=ChatResponse)
async def v1_chat(request: ChatRequest):
    """Chat endpoint (v1)."""
    return await chat(request)


@api_v1.get("/search")
async def v1_search(
    q: str = Query(..., min_length=1, max_length=1000, description="Search query"),
    limit: int = Query(default=10, ge=1, le=20, description="Maximum results to return")
):
    """Search endpoint (v1)."""
    return await search(q, limit)


@api_v1.get("/acts")
async def v1_list_acts():
    """List acts endpoint (v1)."""
    return await list_acts()


@api_v1.get("/version")
async def v1_version():
    """Get API version information."""
    return {
        "api_version": API_VERSION,
        "app_version": "0.1.0",
        "endpoints": [
            "/api/v1/health",
            "/api/v1/chat",
            "/api/v1/search",
            "/api/v1/acts",
            "/api/v1/version"
        ]
    }


# Mount the v1 router
app.include_router(api_v1)


# =============================================================================
# Debug endpoint to test retrieval without Claude
# =============================================================================

# Debug endpoints - only available in development
DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"


@app.get("/debug/search")
async def debug_search(q: str, limit: int = Query(default=10, ge=1, le=50)):
    """
    Debug endpoint to see what sections are being retrieved.
    Shows key section boosting in action.
    Only available when DEBUG=true environment variable is set.
    """
    if not DEBUG_MODE:
        raise HTTPException(status_code=404, detail="Not found")

    key_sections = get_key_sections_for_query(q)
    detected_act = detect_act_from_query(q)

    results = search_similar(q, top_k=limit, act_filter=detected_act)

    return {
        "query": q,
        "detected_act": detected_act,
        "key_sections_matched": key_sections,
        "results": [
            {
                "act": r["act_title"],
                "section": r["section_number"],
                "heading": r["section_heading"],
                "score": round(r["score"], 4),
                "text_preview": r["text"][:150] + "..."
            }
            for r in results
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)