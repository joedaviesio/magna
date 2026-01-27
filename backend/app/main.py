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
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Optional Supabase support
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError as e:
    print(f"⚠ Supabase not available: {e}")
    SUPABASE_AVAILABLE = False
    Client = None

# Load environment variables
load_dotenv()

# Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
EMBEDDINGS_DIR = Path("data/embeddings")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
embeddings = None
metadata = None
embedding_model = None
anthropic_client = None
supabase_client = None

# System prompt
SYSTEM_PROMPT = """You are Bowen, a chatbot legal information assistant for New Zealand legislation.

## YOUR KNOWLEDGE
You have general knowledge about NZ law from your training, including:
- The purpose and scope of major NZ Acts
- How NZ legal system works
- Common legal concepts and terminology

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
6. In some of the User testing Bowen took on a legal personality, which was good, but remember that Bowen is also his own personality, with his data bank and precision on access to legal documentation. Bowen has passion and humour but never provides advice only information. Bowen believes that information transmission is one of the essences of the universe. Law is something in between the word and the real. 

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
You have excerpts from these NZ Acts (as at late 2025):
50 pieces of law in the html folder.

## CITATION FORMAT
When citing from excerpts: "Under Section X of the [Act Name]..."
When using general knowledge: "The [Act] generally provides for..." or "Based on my understanding of NZ law..."

Always end responses by encouraging users to verify current legislation at legislation.govt.nz and consult a lawyer for specific situations."""

DISCLAIMER = """⚠️ Bowen is a chatbot, not legal advice. It may be incomplete or outdated. For legal decisions, consult a qualified NZ lawyer or Community Law Centre."""


# Import act detection from registry (single source of truth)
from .acts_registry import detect_act_from_query, get_all_acts, ACTS_REGISTRY
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
    global embeddings, metadata, embedding_model, anthropic_client, supabase_client
    
    print("\n" + "=" * 50)
    print("Starting Bowen Backend...")
    print("=" * 50)
    
    # Load embeddings
    embeddings_path = EMBEDDINGS_DIR / "embeddings.npy"
    metadata_path = EMBEDDINGS_DIR / "metadata.json"
    
    if embeddings_path.exists() and metadata_path.exists():
        print(f"\nLoading embeddings from {embeddings_path}...")
        embeddings = np.load(embeddings_path)
        
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

    # Initialize Supabase client
    if SUPABASE_AVAILABLE and SUPABASE_URL and SUPABASE_ANON_KEY and not SUPABASE_URL.startswith("your-"):
        try:
            supabase_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            print("✓ Supabase client initialized")
        except Exception as e:
            print(f"✗ Could not initialize Supabase: {e}")
    else:
        print("⚠ Supabase not configured (chat will work but not be logged)")

    print("\n" + "=" * 50)
    print("Startup complete!")
    print("=" * 50 + "\n")


def search_similar(query: str, top_k: int = TOP_K, act_filter: str = None) -> List[dict]:
    """Search for similar chunks with optional act filtering and keyword boosting."""
    if embeddings is None or embedding_model is None:
        return []

    # Encode query
    query_embedding = embedding_model.encode(query, convert_to_numpy=True)

    # Calculate cosine similarities
    similarities = np.dot(embeddings, query_embedding).copy()

    # Keyword boosting for important sections
    boost_terms = ['purpose', 'interpretation', 'application', 'object', 'principle', 'definition']
    query_lower = query.lower()

    # Boost scores for chunks containing key terms when asking "what is" questions
    if any(q in query_lower for q in ['what is', 'what are', 'explain', 'overview', 'purpose of']):
        for i, meta in enumerate(metadata):
            text_lower = meta.get('text', '').lower()
            heading_lower = meta.get('section_heading', '').lower()

            # Boost purpose/interpretation sections
            for term in boost_terms:
                if term in heading_lower or term in text_lower[:200]:
                    similarities[i] *= 1.3  # 30% boost

            # Boost section 1-10 (usually purpose/interpretation)
            section_num = meta.get('section_number', '')
            if section_num.isdigit() and int(section_num) <= 10:
                similarities[i] *= 1.2  # 20% boost

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

    # Filter out negative scores (excluded by act filter)
    top_indices = [i for i in top_indices if similarities[i] > 0]

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


async def generate_response(query: str, context: str) -> str:
    """Generate response using Claude with hybrid knowledge approach."""
    if not anthropic_client:
        raise_anthropic_unavailable()

    try:
        message = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,  # Increased for fuller responses
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": f"""Question: {query}

LEGISLATION EXCERPTS FROM DATABASE:
{context}

---

Please answer the question using:
1. Your general knowledge about NZ law to provide context and explanation
2. The specific excerpts above to cite exact provisions and wording

If the excerpts don't contain the specific information needed, use your general knowledge but make clear what comes from the excerpts vs your training.

Remember: Provide information, not legal advice. Cite specific sections where possible."""
            }]
        )
        return message.content[0].text
    except Exception as e:
        logger.error(LogEvent.CLAUDE_ERROR, f"Claude API error: {e}", error=e)
        raise_generation_failed(str(e))


async def log_chat_message(session_id: str, role: str, content: str, sources: List[dict] = None):
    """Log a chat message to Supabase."""
    if not supabase_client:
        logger.warning(LogEvent.ANALYTICS_FAILURE, "Supabase not configured, skipping chat message log")
        return

    try:
        supabase_client.table("chat_messages").insert({
            "session_id": session_id,
            "role": role,
            "content": content,
            "sources": sources
        }).execute()
        logger.track_analytics_success("chat_message", session_id)
    except Exception as e:
        logger.track_analytics_failure("chat_message", e, session_id)


async def log_analytics(
    event_type: str,
    session_id: str = None,
    query: str = None,
    detected_act: str = None,
    sources_count: int = None,
    response_time_ms: int = None
):
    """Log analytics event to Supabase."""
    if not supabase_client:
        logger.warning(LogEvent.ANALYTICS_FAILURE, "Supabase not configured, skipping analytics log")
        return

    try:
        supabase_client.table("analytics").insert({
            "event_type": event_type,
            "session_id": session_id,
            "query": query,
            "detected_act": detected_act,
            "sources_count": sources_count,
            "response_time_ms": response_time_ms
        }).execute()
        logger.track_analytics_success("analytics_event", session_id)
    except Exception as e:
        logger.track_analytics_failure("analytics_event", e, session_id)


async def update_topic_stats(act_name: str):
    """Update topic statistics in Supabase."""
    if not supabase_client or not act_name:
        if not act_name:
            return  # No act detected, nothing to log
        logger.warning(LogEvent.ANALYTICS_FAILURE, "Supabase not configured, skipping topic stats")
        return

    try:
        # Try to upsert the topic stats
        supabase_client.table("topic_stats").upsert({
            "act_name": act_name,
            "query_count": 1,
            "last_queried": datetime.utcnow().isoformat()
        }, on_conflict="act_name").execute()

        # Increment the count
        supabase_client.rpc("increment_topic_count", {"act": act_name}).execute()
        logger.track_analytics_success("topic_stats")
    except Exception as e:
        # Fallback: just insert if RPC doesn't exist
        try:
            supabase_client.table("topic_stats").upsert({
                "act_name": act_name,
                "query_count": 1,
                "last_queried": datetime.utcnow().isoformat()
            }, on_conflict="act_name").execute()
            logger.track_analytics_success("topic_stats_fallback")
        except Exception as fallback_error:
            logger.track_analytics_failure("topic_stats", fallback_error)


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
        "supabase_ready": supabase_client is not None,
        "chunks": len(metadata) if metadata else 0,
        "analytics_failures": failure_counts,
        "has_failures": len(failure_counts) > 0
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
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

    # Search with optional act filter and increased results
    results = search_similar(
        query,
        top_k=10,  # Increased from 5
        act_filter=detected_act
    )

    # Build context
    context = build_context(results)

    # Generate response
    response_text = await generate_response(query, context)

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

    # Log to Supabase (non-blocking)
    sources_for_log = [{"act": s.act_title, "section": s.section_number} for s in sources[:5]]
    await log_chat_message(session_id, "user", query)
    await log_chat_message(session_id, "assistant", response_text, sources_for_log)
    await log_analytics(
        event_type="chat",
        session_id=session_id,
        query=query,
        detected_act=detected_act,
        sources_count=len(sources),
        response_time_ms=response_time_ms
    )
    await update_topic_stats(detected_act)

    # Log response metrics
    logger.log_chat_response(session_id, response_time_ms, len(sources), success=True)

    return ChatResponse(
        response=response_text,
        sources=sources[:5],  # Limit to top 5 sources
        disclaimer=DISCLAIMER
    )


@app.get("/search")
async def search(q: str, limit: int = 10):
    """Direct search endpoint."""
    if not q:
        raise_invalid_query()

    if embeddings is None or embedding_model is None:
        raise_embeddings_not_loaded()

    results = search_similar(q, top_k=min(limit, 20))
    
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
async def v1_search(q: str, limit: int = 10):
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)