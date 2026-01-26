# Dual Search Feature Expansion Plan

This document outlines the architecture and implementation plan for expanding Bowen to support two distinctive search features:

1. **Legislation Search** - 100 most common NZ laws
2. **South Island Plans Search** - Regional and District plans

---

## Executive Summary

The current Bowen implementation uses a single vector store for 9 NZ Acts. This expansion will:

- Scale legislation coverage from 9 to ~100 Acts
- Add a second knowledge domain for South Island planning documents
- Implement domain-aware routing to direct queries appropriately
- Maintain a unified chat interface with domain indicators

---

## 1. Data Sources

### 1.1 Legislation (100 Acts)

| Category | Count | Examples |
|----------|-------|----------|
| Core/Constitutional | 5 | Constitution Act, Electoral Act, Public Service Act |
| Business & Commercial | 15 | Companies Act, Fair Trading Act, Financial Markets Conduct Act |
| Employment & Health | 12 | Employment Relations Act, Health and Safety at Work Act |
| Property & Land | 10 | Property Law Act, Unit Titles Act, Resource Management Act |
| Criminal & Justice | 8 | Crimes Act, Sentencing Act, Family Violence Act |
| Environment & Conservation | 12 | Conservation Act, Biosecurity Act, Climate Change Response Act |
| Health & Social | 10 | Health Act, Privacy Act, Accident Compensation Act |
| Transport & Infrastructure | 8 | Land Transport Act, Building Act |
| Other | 20 | Various domain-specific Acts |

**Source:** `docs/legislation.csv` (93 Acts listed)

### 1.2 South Island Plans

| Region | Plan Count | Types |
|--------|------------|-------|
| Southland | 8 | Regional plans (air, coastal, water, pest, marine) |
| Canterbury | 12 | 2 Regional + 10 District plans |
| West Coast | 5 | Regional plans |
| Otago | 5 | District plans |
| Nelson Tasman | 2 | District plans |
| Marlborough | 1 | Combined District/Regional plan |

**Source:** `docs/southislandplans.csv` (34 plans listed)

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ Domain      │  │ Chat        │  │ Source Attribution      │ │
│  │ Selector    │  │ Interface   │  │ (Legislation/Plans)     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY                                 │
│  POST /api/v1/chat     { message, domain?, session_id }         │
│  GET  /api/v1/search   { q, domain, limit }                     │
│  GET  /api/v1/domains  List available domains                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    QUERY ROUTER                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  1. Explicit domain selection (user chose)                │  │
│  │  2. Domain detection from query keywords                  │  │
│  │  3. Multi-domain search (if ambiguous)                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                    │                       │
                    ▼                       ▼
┌───────────────────────────┐   ┌───────────────────────────────┐
│   LEGISLATION DOMAIN      │   │   PLANNING DOMAIN             │
│  ┌─────────────────────┐  │   │  ┌─────────────────────────┐  │
│  │ Vector Store        │  │   │  │ Vector Store            │  │
│  │ (100 Acts)          │  │   │  │ (34 Plans)              │  │
│  │ ~300K chunks        │  │   │  │ ~150K chunks            │  │
│  └─────────────────────┘  │   │  └─────────────────────────┘  │
│  ┌─────────────────────┐  │   │  ┌─────────────────────────┐  │
│  │ Legislation         │  │   │  │ Planning                │  │
│  │ Registry            │  │   │  │ Registry                │  │
│  └─────────────────────┘  │   │  └─────────────────────────┘  │
│  ┌─────────────────────┐  │   │  ┌─────────────────────────┐  │
│  │ System Prompt       │  │   │  │ System Prompt           │  │
│  │ (Legal focus)       │  │   │  │ (Planning focus)        │  │
│  └─────────────────────┘  │   │  └─────────────────────────┘  │
└───────────────────────────┘   └───────────────────────────────┘
                    │                       │
                    └───────────┬───────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RESPONSE GENERATOR                            │
│  - Claude API with domain-specific system prompts               │
│  - Source attribution with domain labels                        │
│  - Cross-domain awareness (e.g., RMA relates to District Plans) │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Model Changes

### 3.1 Domain Registry

```python
# backend/app/domain_registry.py

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel

class Domain(str, Enum):
    LEGISLATION = "legislation"
    PLANNING = "planning"

class DomainConfig(BaseModel):
    id: Domain
    name: str
    description: str
    keywords: List[str]
    embeddings_path: str
    metadata_path: str
    system_prompt: str

DOMAIN_REGISTRY: Dict[Domain, DomainConfig] = {
    Domain.LEGISLATION: DomainConfig(
        id=Domain.LEGISLATION,
        name="NZ Legislation",
        description="100 most common New Zealand Acts and statutes",
        keywords=["act", "law", "legislation", "statute", "section", "legal"],
        embeddings_path="data/embeddings/legislation/embeddings.npy",
        metadata_path="data/embeddings/legislation/metadata.json",
        system_prompt=LEGISLATION_SYSTEM_PROMPT
    ),
    Domain.PLANNING: DomainConfig(
        id=Domain.PLANNING,
        name="South Island Plans",
        description="Regional and District plans for South Island councils",
        keywords=["plan", "district", "regional", "council", "zone", "resource consent", "land use"],
        embeddings_path="data/embeddings/planning/embeddings.npy",
        metadata_path="data/embeddings/planning/metadata.json",
        system_prompt=PLANNING_SYSTEM_PROMPT
    )
}
```

### 3.2 Updated Chunk Metadata

```python
# Legislation chunk metadata
{
    "id": "chunk_hash",
    "domain": "legislation",
    "text": "...",
    "act_title": "Resource Management Act 1991",
    "act_short_name": "RMA",
    "act_year": 1991,
    "section_number": "5",
    "section_heading": "Purpose",
    "section_url": "https://...",
    "chunk_index": 0,
    "total_chunks": 5
}

# Planning chunk metadata
{
    "id": "chunk_hash",
    "domain": "planning",
    "text": "...",
    "plan_name": "Christchurch District Plan",
    "plan_type": "District Plan",
    "region": "Canterbury",
    "authority": "Christchurch City Council",
    "chapter": "Residential",
    "rule_number": "14.5.2.1",
    "rule_heading": "Permitted Activities",
    "plan_url": "https://...",
    "chunk_index": 0,
    "total_chunks": 3
}
```

### 3.3 Database Schema Updates

```sql
-- Add domain tracking to existing tables
ALTER TABLE chat_messages ADD COLUMN domain TEXT DEFAULT 'legislation';
ALTER TABLE analytics ADD COLUMN domain TEXT DEFAULT 'legislation';

-- New table for domain-specific stats
CREATE TABLE domain_stats (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    domain TEXT NOT NULL,
    query_count INTEGER DEFAULT 0,
    avg_response_time_ms INTEGER,
    last_queried TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(domain)
);

-- Planning-specific stats
CREATE TABLE plan_stats (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    plan_name TEXT NOT NULL,
    region TEXT NOT NULL,
    query_count INTEGER DEFAULT 1,
    last_queried TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(plan_name)
);
```

---

## 4. API Changes

### 4.1 Updated Endpoints

```python
# POST /api/v1/chat
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    domain: Optional[Domain] = None  # NEW: explicit domain selection

class ChatResponse(BaseModel):
    response: str
    sources: List[Source]
    domain: Domain  # NEW: which domain was used
    disclaimer: str

# GET /api/v1/search
@app.get("/api/v1/search")
async def search(
    q: str,
    domain: Optional[Domain] = None,  # NEW: filter by domain
    limit: int = 10
):
    ...

# GET /api/v1/domains
@app.get("/api/v1/domains")
async def list_domains():
    """List all available search domains."""
    return {
        "domains": [
            {
                "id": d.id,
                "name": d.name,
                "description": d.description
            }
            for d in DOMAIN_REGISTRY.values()
        ]
    }
```

### 4.2 Source Model Updates

```python
class LegislationSource(BaseModel):
    domain: str = "legislation"
    act_title: str
    section_number: str
    section_heading: str
    url: str
    excerpt: str
    score: float

class PlanningSource(BaseModel):
    domain: str = "planning"
    plan_name: str
    plan_type: str
    region: str
    authority: str
    chapter: Optional[str]
    rule_number: Optional[str]
    url: str
    excerpt: str
    score: float

# Union type for response
Source = Union[LegislationSource, PlanningSource]
```

---

## 5. Query Router Implementation

```python
# backend/app/query_router.py

from typing import List, Tuple
from .domain_registry import Domain, DOMAIN_REGISTRY

class QueryRouter:
    """Routes queries to appropriate domain(s) based on content analysis."""

    def __init__(self):
        self.domain_keywords = {
            domain: config.keywords
            for domain, config in DOMAIN_REGISTRY.items()
        }

    def detect_domain(self, query: str) -> Tuple[Domain, float]:
        """
        Detect the most likely domain for a query.
        Returns (domain, confidence) tuple.
        """
        query_lower = query.lower()
        scores = {}

        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            scores[domain] = score

        # Legislation-specific patterns
        if any(pattern in query_lower for pattern in [
            "act ", "section ", "s.", "ss.", "what is the law",
            "legal requirement", "statute"
        ]):
            scores[Domain.LEGISLATION] += 2

        # Planning-specific patterns
        if any(pattern in query_lower for pattern in [
            "district plan", "regional plan", "zone", "permitted activity",
            "resource consent", "building height", "setback", "subdivision",
            "christchurch", "queenstown", "dunedin", "canterbury", "otago"
        ]):
            scores[Domain.PLANNING] += 2

        # Cross-domain detection (RMA relates to both)
        if "rma" in query_lower or "resource management" in query_lower:
            # Could be asking about the Act OR how it applies in plans
            if any(p in query_lower for p in ["plan", "council", "consent"]):
                scores[Domain.PLANNING] += 1
            else:
                scores[Domain.LEGISLATION] += 1

        best_domain = max(scores, key=scores.get)
        confidence = scores[best_domain] / (sum(scores.values()) + 1)

        return best_domain, confidence

    def should_search_both(self, query: str, confidence: float) -> bool:
        """Determine if we should search both domains."""
        # Low confidence = search both
        if confidence < 0.4:
            return True

        # Explicit cross-domain questions
        cross_domain_patterns = [
            "how does the .* apply to",
            "what does .* say about planning",
            "legislation and plans"
        ]
        return any(p in query.lower() for p in cross_domain_patterns)
```

---

## 6. Frontend Changes

### 6.1 Domain Selector Component

```typescript
// frontend/src/components/DomainSelector.tsx

interface DomainSelectorProps {
  selectedDomain: Domain | null;
  onDomainChange: (domain: Domain | null) => void;
}

export function DomainSelector({ selectedDomain, onDomainChange }: DomainSelectorProps) {
  return (
    <div className="flex gap-2 mb-4">
      <button
        onClick={() => onDomainChange(null)}
        className={`px-4 py-2 rounded-lg ${
          selectedDomain === null
            ? 'bg-navy text-white'
            : 'bg-slate-100 text-slate-600'
        }`}
      >
        All
      </button>
      <button
        onClick={() => onDomainChange('legislation')}
        className={`px-4 py-2 rounded-lg ${
          selectedDomain === 'legislation'
            ? 'bg-blue-600 text-white'
            : 'bg-slate-100 text-slate-600'
        }`}
      >
        Legislation
      </button>
      <button
        onClick={() => onDomainChange('planning')}
        className={`px-4 py-2 rounded-lg ${
          selectedDomain === 'planning'
            ? 'bg-green-600 text-white'
            : 'bg-slate-100 text-slate-600'
        }`}
      >
        SI Plans
      </button>
    </div>
  );
}
```

### 6.2 Updated Source Display

```typescript
// frontend/src/components/Sources.tsx

function SourceCard({ source }: { source: Source }) {
  const isLegislation = source.domain === 'legislation';

  return (
    <div className={`p-4 rounded-lg border ${
      isLegislation ? 'border-blue-200 bg-blue-50' : 'border-green-200 bg-green-50'
    }`}>
      <div className="flex items-center gap-2 mb-2">
        <span className={`text-xs px-2 py-0.5 rounded ${
          isLegislation ? 'bg-blue-200 text-blue-800' : 'bg-green-200 text-green-800'
        }`}>
          {isLegislation ? 'Legislation' : 'Plan'}
        </span>
        {isLegislation ? (
          <span className="font-medium">{source.act_title}</span>
        ) : (
          <span className="font-medium">{source.plan_name}</span>
        )}
      </div>

      {isLegislation ? (
        <p className="text-sm text-slate-600">
          Section {source.section_number}: {source.section_heading}
        </p>
      ) : (
        <p className="text-sm text-slate-600">
          {source.chapter} - {source.rule_number}
        </p>
      )}

      <p className="text-sm mt-2">{source.excerpt}</p>
    </div>
  );
}
```

---

## 7. Data Ingestion Pipeline

### 7.1 Folder Structure

```
data/
├── raw/
│   ├── legislation/           # XML files from legislation.govt.nz
│   │   ├── resource-management-act-1991.xml
│   │   ├── crimes-act-1961.xml
│   │   └── ... (100 Acts)
│   │
│   └── planning/              # PDFs/HTML from council websites
│       ├── canterbury/
│       │   ├── christchurch-district-plan.pdf
│       │   └── ...
│       ├── otago/
│       │   ├── queenstown-lakes-district-plan.pdf
│       │   └── ...
│       └── ...
│
├── processed/
│   ├── legislation/
│   │   └── chunks.json
│   └── planning/
│       └── chunks.json
│
└── embeddings/
    ├── legislation/
    │   ├── embeddings.npy
    │   ├── metadata.json
    │   └── config.json
    └── planning/
        ├── embeddings.npy
        ├── metadata.json
        └── config.json
```

### 7.2 Ingestion Scripts

```python
# backend/scripts/ingest_plans.py

"""
Ingestion script for South Island planning documents.
Handles PDFs and HTML from council websites.
"""

import os
from pathlib import Path
from typing import List, Dict
import fitz  # PyMuPDF for PDF parsing
from bs4 import BeautifulSoup
import json

PLANS_CSV = Path("docs/southislandplans.csv")
RAW_DIR = Path("data/raw/planning")
OUTPUT_DIR = Path("data/processed/planning")

def parse_district_plan_pdf(pdf_path: Path, plan_info: Dict) -> List[Dict]:
    """Parse a district plan PDF into chunks."""
    chunks = []
    doc = fitz.open(pdf_path)

    current_chapter = ""
    current_rule = ""

    for page_num, page in enumerate(doc):
        text = page.get_text()

        # Detect chapter headings (usually bold, larger font)
        # This is simplified - real implementation would use font analysis
        if text.startswith("Chapter"):
            current_chapter = text.split("\n")[0]

        # Detect rule numbers (e.g., "14.5.2.1")
        rule_match = re.search(r"(\d+\.\d+\.\d+\.\d+)", text)
        if rule_match:
            current_rule = rule_match.group(1)

        # Chunk the text (simplified)
        for para in text.split("\n\n"):
            if len(para.strip()) > 50:  # Skip tiny fragments
                chunks.append({
                    "text": para.strip(),
                    "domain": "planning",
                    "plan_name": plan_info["Plan Name"],
                    "plan_type": plan_info["Plan Type"],
                    "region": plan_info["Region/Territory"],
                    "authority": plan_info["Authority"],
                    "chapter": current_chapter,
                    "rule_number": current_rule,
                    "page": page_num + 1,
                    "source_file": str(pdf_path)
                })

    return chunks

def main():
    # Load plans list
    plans = pd.read_csv(PLANS_CSV)

    all_chunks = []
    for _, plan in plans.iterrows():
        plan_dir = RAW_DIR / plan["Region/Territory"].lower().replace(" ", "-")
        # Find matching PDF/HTML
        # ... processing logic ...

    # Save chunks
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_DIR / "chunks.json", "w") as f:
        json.dump(all_chunks, f, indent=2)

    print(f"Processed {len(all_chunks)} chunks from {len(plans)} plans")
```

---

## 8. System Prompts

### 8.1 Legislation Prompt (existing, expanded)

```python
LEGISLATION_SYSTEM_PROMPT = """You are Bowen, an AI legal information assistant for New Zealand legislation.

## YOUR KNOWLEDGE
You have access to 100 New Zealand Acts covering:
- Constitutional and electoral law
- Business and commercial law
- Employment and workplace law
- Property and land law
- Criminal and justice law
- Environmental and conservation law
- Health and social services law
- Transport and infrastructure law

## CRITICAL RULES
1. You provide INFORMATION only, NOT legal advice
2. Cite specific sections when available
3. Distinguish between excerpts and general knowledge
4. Always recommend consulting a lawyer for specific situations

## CITATION FORMAT
"Under Section X of the [Act Name]..."
"Based on my understanding of NZ law..."
"""
```

### 8.2 Planning Prompt (new)

```python
PLANNING_SYSTEM_PROMPT = """You are Bowen, an AI assistant for South Island planning documents.

## YOUR KNOWLEDGE
You have access to Regional and District Plans for:
- Canterbury (including Christchurch, Selwyn, Waimakariri, etc.)
- Otago (including Queenstown Lakes, Dunedin, Central Otago)
- Southland (Environment Southland regional plans)
- West Coast (regional plans)
- Nelson Tasman
- Marlborough

## PLAN TYPES
- **Regional Plans**: Cover air, water, coastal, pest management at regional level
- **District Plans**: Cover land use, zoning, building rules at council level

## CRITICAL RULES
1. You provide INFORMATION only, NOT planning advice
2. Plans change frequently - always recommend checking the council website
3. Cite specific chapters and rules when available
4. Note which council/authority the plan belongs to
5. Explain that resource consent may be required

## CITATION FORMAT
"According to the [Plan Name], Chapter [X], Rule [Y]..."
"The [Council] District Plan states..."
"Note: This information should be verified with [Council] as plans are updated regularly."

## COMMON QUERIES
- Zoning questions (residential, commercial, rural)
- Permitted vs controlled vs discretionary activities
- Building heights, setbacks, site coverage
- Subdivision rules
- Heritage and character overlays
"""
```

---

## 9. Implementation Phases

### Phase 1: Infrastructure (Week 1-2)
- [ ] Set up domain registry architecture
- [ ] Create separate embedding directories
- [ ] Update database schema
- [ ] Implement query router

### Phase 2: Legislation Expansion (Week 3-4)
- [ ] Download remaining ~90 Acts from legislation.govt.nz
- [ ] Update chunking script for scale
- [ ] Generate embeddings for full legislation corpus
- [ ] Update acts registry with all 100 Acts
- [ ] Test retrieval quality

### Phase 3: Planning Ingestion (Week 5-7)
- [ ] Source planning documents from councils
- [ ] Build PDF/HTML parsing pipeline
- [ ] Handle different document formats per council
- [ ] Generate planning embeddings
- [ ] Create plans registry

### Phase 4: Frontend Updates (Week 8)
- [ ] Add domain selector UI
- [ ] Update source display for dual domains
- [ ] Add domain indicators to messages
- [ ] Update empty state with domain info

### Phase 5: Testing & Refinement (Week 9-10)
- [ ] Cross-domain query testing
- [ ] Retrieval quality evaluation
- [ ] User testing
- [ ] Performance optimization
- [ ] Documentation

---

## 10. Technical Considerations

### 10.1 Embedding Storage

With ~450K total chunks (300K legislation + 150K planning):

| Option | Pros | Cons |
|--------|------|------|
| Separate NumPy files | Simple, fast load per domain | Memory if loading both |
| Single NumPy + domain filter | Unified search possible | Larger memory footprint |
| pgvector (Supabase) | SQL queries, scalable | Network latency |
| Pinecone/Weaviate | Managed, scalable | Cost, vendor lock-in |

**Recommendation:** Start with separate NumPy files, migrate to pgvector when scaling.

### 10.2 Document Sourcing

| Source | Legislation | Planning |
|--------|-------------|----------|
| Format | XML (structured) | PDF/HTML (varied) |
| API | legislation.govt.nz | None (manual download) |
| Updates | Official, versioned | Council-dependent |
| Licensing | Open (NZGOAL) | Varies by council |

### 10.3 Cross-Domain Queries

Some queries naturally span both domains:
- "What does the RMA say about district plans?" (Legislation about Planning)
- "How do I comply with Building Act requirements in Christchurch?" (Both)

**Strategy:**
1. Detect cross-domain intent
2. Search both domains
3. Present results with clear domain labels
4. Let Claude synthesize across domains

---

## 11. Success Metrics

| Metric | Target |
|--------|--------|
| Legislation coverage | 100 Acts |
| Planning coverage | 34 South Island plans |
| Query routing accuracy | >90% |
| Response time (p95) | <3s |
| Retrieval relevance (human eval) | >4/5 |
| User domain preference tracking | Implemented |

---

## 12. Future Expansion

Once dual-search is stable, potential additions:

1. **North Island Plans** - Expand planning coverage nationwide
2. **Case Law** - Add NZLII case database
3. **Regulations** - Add secondary legislation (SRs)
4. **Treaty Documents** - Waitangi Tribunal reports
5. **Building Code** - Detailed compliance documents

---

## Appendix A: Data Source URLs

### Legislation
- Primary: https://legislation.govt.nz/subscribe
- API Docs: https://www.pco.govt.nz/open-data/
- Format: XML (Akoma Ntoso)

### South Island Plans
| Region | URL |
|--------|-----|
| Canterbury (ECan) | https://www.ecan.govt.nz/your-region/plans-strategies-and-bylaws/ |
| Christchurch | https://districtplan.ccc.govt.nz/ |
| Queenstown Lakes | https://www.qldc.govt.nz/planning/district-plan/ |
| Dunedin | https://www.dunedin.govt.nz/council/district-plan |
| Environment Southland | https://www.es.govt.nz/environment/plans-and-strategies |
| West Coast | https://www.wcrc.govt.nz/plans-and-strategies |
| Nelson | https://www.nelson.govt.nz/nelson-plan/ |
| Tasman | https://www.tasman.govt.nz/my-region/plans-and-strategies/ |
| Marlborough | https://www.marlborough.govt.nz/your-council/resource-management-policy-and-plans |

---

## Appendix B: Sample Queries by Domain

### Legislation Only
- "What is the maximum bond under the Residential Tenancies Act?"
- "What are the director duties under the Companies Act?"
- "How much notice is required for dismissal under the ERA?"

### Planning Only
- "What are the permitted building heights in Christchurch residential zones?"
- "Can I build a tiny house in Queenstown?"
- "What activities are permitted in Canterbury's rural zone?"

### Cross-Domain
- "What does the RMA require councils to include in district plans?"
- "How do Building Act requirements apply in Dunedin heritage areas?"
- "What legislation governs Southland's coastal plan?"
