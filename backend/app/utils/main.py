#!/usr/bin/env python3
"""
main.py

FastAPI backend for Magna - NZ Legal Assistant
Uses numpy-based vector search and Claude API.

Run from magna root:
    cd ~/Desktop/magna
    uvicorn backend.app.main:app --reload --port 8000
"""

import os
import json
import numpy as np
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
EMBEDDINGS_DIR = Path("data/embeddings")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5

# Pydantic models
class ChatRequest(BaseModel):
    message: str

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

# Initialize FastAPI
app = FastAPI(
    title="Magna - NZ Legal Assistant",
    description="AI-powered legal information retrieval for New Zealand legislation",
    version="0.1.0"
)

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

# System prompt
SYSTEM_PROMPT = """You are Magna, an AI legal information assistant for New Zealand legislation. 

CRITICAL RULES:
1. You provide INFORMATION only, NOT legal advice
2. ALWAYS cite specific sections (e.g., "Section 12 of the Residential Tenancies Act 1986")
3. If information isn't in the context, say so clearly
4. Use plain language to explain legal concepts
5. For "Can I do X?" questions, explain what the legislation SAYS, don't give advice

RESPONSE FORMAT:
- Start with a direct answer based on the legislation
- Cite specific sections
- Explain in plain language
- Note any exceptions or conditions
- Keep responses concise but complete

You have access to: Residential Tenancies Act 1986, Employment Relations Act 2000, Companies Act 1993, Fair Trading Act 1986, Property Law Act 2007, Privacy Act 2020, Building Act 2004, Contract and Commercial Law Act 2017, Resource Management Act 1991."""

DISCLAIMER = """⚠️ Magna is an AI Chat bot, NOT legal advice. It may be incomplete or outdated. For legal decisions, consult a qualified NZ lawyer or Community Law Centre."""


@app.on_event("startup")
async def startup():
    """Load models and data on startup."""
    global embeddings, metadata, embedding_model, anthropic_client
    
    print("\n" + "=" * 50)
    print("Starting Magna Backend...")
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
    
    print("\n" + "=" * 50)
    print("Startup complete!")
    print("=" * 50 + "\n")


def search_similar(query: str, top_k: int = TOP_K) -> List[dict]:
    """Search for similar chunks using cosine similarity."""
    if embeddings is None or embedding_model is None:
        return []
    
    # Encode query
    query_embedding = embedding_model.encode(query, convert_to_numpy=True)
    
    # Calculate cosine similarities
    similarities = np.dot(embeddings, query_embedding)
    
    # Get top-k indices
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    
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
    """Build context string from search results."""
    if not results:
        return "No relevant legislation found."
    
    parts = []
    for i, r in enumerate(results, 1):
        header = f"[Source {i}: {r['act_title']}"
        if r['section_number']:
            header += f", Section {r['section_number']}"
        if r['section_heading']:
            header += f" - {r['section_heading']}"
        header += "]"
        parts.append(f"{header}\n{r['text']}")
    
    return "\n\n---\n\n".join(parts)


async def generate_response(query: str, context: str) -> str:
    """Generate response using Claude."""
    if not anthropic_client:
        return "I'm sorry, but the AI service is not available. Please check the API key configuration."
    
    try:
        message = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": f"""Based on these excerpts from New Zealand legislation, answer the question.

LEGISLATION EXCERPTS:
{context}

QUESTION: {query}

Provide a helpful response based on the legislation above. Cite specific sections."""
            }]
        )
        return message.content[0].text
    except Exception as e:
        print(f"Claude API error: {e}")
        return f"I encountered an error generating a response. Please try again."


@app.get("/")
async def root():
    return {
        "name": "Magna - NZ Legal Assistant",
        "version": "0.1.0",
        "status": "running",
        "chunks_loaded": len(metadata) if metadata else 0
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "embeddings_loaded": embeddings is not None,
        "model_loaded": embedding_model is not None,
        "anthropic_ready": anthropic_client is not None,
        "chunks": len(metadata) if metadata else 0
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint."""
    query = request.message.strip()
    
    if not query:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Search for relevant chunks
    results = search_similar(query, top_k=TOP_K)
    
    # Build context
    context = build_context(results)
    
    # Generate response
    response_text = await generate_response(query, context)
    
    # Format sources
    sources = []
    seen = set()
    for r in results:
        key = f"{r['act_title']}:{r['section_number']}"
        if key not in seen:
            seen.add(key)
            sources.append(Source(
                act_title=r['act_title'],
                section_number=r['section_number'],
                section_heading=r['section_heading'],
                url=r['section_url'] or r['act_url'],
                excerpt=r['text'][:200] + "..." if len(r['text']) > 200 else r['text'],
                score=r['score']
            ))
    
    return ChatResponse(
        response=response_text,
        sources=sources,
        disclaimer=DISCLAIMER
    )


@app.get("/search")
async def search(q: str, limit: int = 10):
    """Direct search endpoint."""
    if not q:
        raise HTTPException(status_code=400, detail="Query 'q' is required")
    
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
    """List all available acts."""
    if not metadata:
        return {"acts": []}
    
    acts = {}
    for m in metadata:
        title = m.get("act_title", "Unknown")
        if title not in acts:
            acts[title] = {
                "title": title,
                "short_name": m.get("act_short_name", ""),
                "url": m.get("act_url", "")
            }
    
    return {"acts": list(acts.values())}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)