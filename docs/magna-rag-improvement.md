# Magna RAG Improvement Prompt for Claude Code

## Current Problem

The RAG system retrieves legislation chunks but struggles with:
1. **General "what is X" questions** - retrieves random mentions instead of overview/purpose sections
2. **Poor context** - retrieves section headings without content
3. **Cross-act confusion** - searches all acts when user wants a specific one
4. **No general knowledge** - Claude can't use its training knowledge about NZ law to supplement

## Goal

Create a hybrid system where:
1. Claude uses its **general knowledge** about NZ legislation as foundation
2. RAG provides **specific citations and current wording** from the actual Acts
3. Better retrieval that **prioritizes purpose sections, definitions, and key provisions**
4. Ability to **filter by specific Act** when relevant

## Files to Modify

Location: `~/Desktop/magna/backend/app/main.py`

## Key Improvements Needed

### 1. Updated System Prompt (CRITICAL)

Replace the current SYSTEM_PROMPT with this improved version:

```python
SYSTEM_PROMPT = """You are Magna, an AI legal information assistant for New Zealand legislation.

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
- Residential Tenancies Act 1986 (RTA) - tenancy, bonds, landlord/tenant rights
- Employment Relations Act 2000 (ERA) - employment, dismissal, leave, unions
- Companies Act 1993 (CA) - company formation, directors, shareholders
- Fair Trading Act 1986 (FTA) - consumer protection, misleading conduct
- Property Law Act 2007 (PLA) - property transactions, mortgages, leases
- Privacy Act 2020 (PA) - personal information, privacy principles
- Building Act 2004 (BA) - building consents, code compliance
- Contract and Commercial Law Act 2017 (CCLA) - contracts, sale of goods
- Resource Management Act 1991 (RMA) - environmental management, resource consents

## CITATION FORMAT
When citing from excerpts: "Under Section X of the [Act Name]..."
When using general knowledge: "The [Act] generally provides for..." or "Based on my understanding of NZ law..."

Always end responses by encouraging users to verify current legislation at legislation.govt.nz and consult a lawyer for specific situations."""
```

### 2. Improved Search Function

Add keyword boosting for important terms:

```python
def search_similar(query: str, top_k: int = TOP_K, act_filter: str = None) -> List[dict]:
    """Search for similar chunks with optional act filtering and keyword boosting."""
    if embeddings is None or embedding_model is None:
        return []
    
    # Encode query
    query_embedding = embedding_model.encode(query, convert_to_numpy=True)
    
    # Calculate cosine similarities
    similarities = np.dot(embeddings, query_embedding)
    
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
```

### 3. Smart Act Detection

Add a function to detect which Act the user is asking about:

```python
def detect_act_from_query(query: str) -> Optional[str]:
    """Detect if user is asking about a specific Act."""
    query_lower = query.lower()
    
    act_keywords = {
        'Resource Management': ['rma', 'resource management', 'resource consent', 'environmental'],
        'Residential Tenancies': ['rta', 'residential tenancies', 'tenancy', 'tenant', 'landlord', 'bond', 'rental'],
        'Employment Relations': ['era', 'employment relations', 'employment', 'employer', 'employee', 'dismissal', 'redundancy'],
        'Companies': ['companies act', 'company', 'director', 'shareholder', 'incorporation'],
        'Fair Trading': ['fta', 'fair trading', 'misleading', 'deceptive', 'consumer protection'],
        'Privacy': ['privacy act', 'privacy', 'personal information', 'data protection'],
        'Building': ['building act', 'building consent', 'building code', 'construction'],
        'Property Law': ['pla', 'property law', 'mortgage', 'lease', 'easement'],
        'Contract and Commercial': ['ccla', 'contract', 'commercial law', 'sale of goods'],
    }
    
    for act_name, keywords in act_keywords.items():
        if any(kw in query_lower for kw in keywords):
            return act_name
    
    return None
```

### 4. Updated Chat Endpoint

Modify the chat endpoint to use smart detection:

```python
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint with improved retrieval."""
    query = request.message.strip()
    
    if not query:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Detect if asking about specific Act
    detected_act = detect_act_from_query(query)
    
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
    
    # Format sources (deduplicate)
    sources = []
    seen = set()
    for r in results:
        key = f"{r['act_title']}:{r['section_number']}"
        if key not in seen and r['section_number']:  # Only include if has section number
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
        sources=sources[:5],  # Limit to top 5 sources
        disclaimer=DISCLAIMER
    )
```

### 5. Better Context Building

Improve how context is presented to Claude:

```python
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
```

### 6. Updated Generation Prompt

Modify how we ask Claude to respond:

```python
async def generate_response(query: str, context: str) -> str:
    """Generate response using Claude with hybrid knowledge approach."""
    if not anthropic_client:
        return "I'm sorry, but the AI service is not available."
    
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
        print(f"Claude API error: {e}")
        return f"I encountered an error generating a response. Please try again."
```

## Testing After Changes

Test these queries to verify improvements:

```bash
# General "what is" question
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the Resource Management Act?"}'

# Should now get: General explanation + any relevant cited sections

# Specific provision question  
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the purpose of the RMA?"}'

# Cross-act question
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How is engagement defined in employment law?"}'

# Specific detail question
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the maximum bond for a tenancy?"}'
```

## Expected Improvements

| Query Type | Before | After |
|------------|--------|-------|
| "What is the RMA?" | Poor context, no explanation | General explanation + key sections |
| Specific provisions | Good | Good (unchanged) |
| Ambiguous terms | Cross-act confusion | Filtered to relevant Act |
| Purpose questions | Random sections | Purpose sections prioritized |

## Summary of Changes

1. **New system prompt** - Tells Claude to use general knowledge + excerpts
2. **Keyword boosting** - Prioritizes purpose/interpretation sections
3. **Act detection** - Auto-filters to relevant Act
4. **Better context** - Organized by Act with clear section labels
5. **Improved generation** - Explicitly asks for hybrid approach
6. **More results** - TOP_K increased to 10 for better coverage

The key insight is: **Claude already knows about NZ law** - we just need to let it use that knowledge while grounding specific citations in the actual legislation text.