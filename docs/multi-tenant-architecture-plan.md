# Bowen Multi-Tenant Architecture Plan

## Overview

This document outlines the architecture for supporting organization-specific private instances of Bowen while maintaining a central public repository. The goal is to enable organizations to have their own login-protected version with custom data banks, while Bowen Public remains the canonical base.

---

## Current State

| Component | Current Implementation |
|-----------|----------------------|
| Storage | File-based (NumPy embeddings + JSON metadata) |
| Authentication | None (stateless, public access) |
| Data Isolation | None (single global corpus of 79 NZ Acts) |
| User Management | Session UUIDs only (analytics) |
| Deployment | Single instance (Railway/Docker) |

---

## Proposed Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Bowen Platform                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │   Bowen      │    │  Org A       │    │  Org B       │          │
│  │   Public     │    │  Instance    │    │  Instance    │          │
│  │              │    │              │    │              │          │
│  │  (No Auth)   │    │  (Auth Req)  │    │  (Auth Req)  │          │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘          │
│         │                   │                   │                   │
│         └───────────────────┼───────────────────┘                   │
│                             │                                        │
│                    ┌────────▼────────┐                              │
│                    │  API Gateway /   │                              │
│                    │  Auth Middleware │                              │
│                    └────────┬────────┘                              │
│                             │                                        │
│         ┌───────────────────┼───────────────────┐                   │
│         │                   │                   │                   │
│  ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐            │
│  │   Public    │    │   Org A     │    │   Org B     │            │
│  │  Data Bank  │    │  Data Bank  │    │  Data Bank  │            │
│  │             │    │  + Public   │    │  + Public   │            │
│  │ (79 NZ Acts)│    │             │    │             │            │
│  └─────────────┘    └─────────────┘    └─────────────┘            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Architecture Options

### Option A: Shared Database with Tenant Isolation (Recommended)

**Description**: Single deployment with multi-tenant data isolation at the database level.

**Pros**:
- Lower infrastructure cost
- Easier to maintain and deploy
- Organizations inherit public corpus automatically
- Centralized updates to public data

**Cons**:
- Requires careful data isolation
- Shared compute resources
- More complex query logic

**Implementation**:
```
PostgreSQL + pgvector
├── organizations (id, name, slug, settings)
├── users (id, org_id, email, role)
├── data_banks (id, org_id, name, is_public)
├── chunks (id, data_bank_id, text, metadata)
└── embeddings (chunk_id, vector[384])
```

### Option B: Isolated Instances per Organization

**Description**: Separate deployment per organization with shared public data synced.

**Pros**:
- Complete isolation
- Independent scaling
- Custom configuration per org

**Cons**:
- Higher infrastructure cost
- Sync complexity for public data
- More operational overhead

### Option C: Hybrid (Recommended for Scale)

**Description**: Shared public instance + dedicated instances for enterprise clients.

**Pros**:
- Flexibility based on client needs
- Can offer different SLAs
- Public instance stays lean

**Cons**:
- Two systems to maintain
- More complex routing

---

## Recommended Implementation: Option A

### Phase 1: Database Migration

Replace file-based storage with PostgreSQL + pgvector.

**Schema Design**:

```sql
-- Organizations
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,  -- e.g., "acme-corp"
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert public org (special case)
INSERT INTO organizations (id, name, slug)
VALUES ('00000000-0000-0000-0000-000000000000', 'Public', 'public');

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'member',  -- admin, member
    created_at TIMESTAMP DEFAULT NOW()
);

-- Data Banks
CREATE TABLE data_banks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,  -- TRUE for Bowen Public corpus
    created_at TIMESTAMP DEFAULT NOW()
);

-- Chunks (legislation text)
CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data_bank_id UUID REFERENCES data_banks(id),
    text TEXT NOT NULL,
    act_title VARCHAR(255),
    section_number VARCHAR(50),
    section_heading VARCHAR(255),
    section_url TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Embeddings (pgvector)
CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_id UUID REFERENCES chunks(id) ON DELETE CASCADE,
    embedding vector(384) NOT NULL
);

-- Index for vector similarity search
CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops);
```

### Phase 2: Authentication Layer

**Stack**: NextAuth.js (frontend) + FastAPI JWT (backend)

**Frontend Changes** (`/frontend`):
```
src/
├── app/
│   ├── (public)/           # Public routes (no auth)
│   │   └── page.tsx        # Bowen Public
│   ├── (protected)/        # Auth-required routes
│   │   ├── [org]/          # Org-specific pages
│   │   │   └── page.tsx
│   │   └── layout.tsx      # Auth wrapper
│   ├── login/
│   │   └── page.tsx
│   └── api/
│       └── auth/
│           └── [...nextauth]/route.ts
├── middleware.ts           # Route protection
└── lib/
    └── auth.ts             # NextAuth config
```

**Backend Changes** (`/backend`):

```python
# New files needed:
app/
├── auth/
│   ├── __init__.py
│   ├── jwt.py              # JWT creation/validation
│   ├── dependencies.py     # FastAPI dependencies
│   └── routes.py           # /auth/login, /auth/register
├── models/
│   ├── user.py
│   ├── organization.py
│   └── data_bank.py
├── middleware/
│   └── tenant.py           # Org context injection
└── database.py             # SQLAlchemy + asyncpg
```

**Auth Flow**:
```
1. User visits org URL (e.g., bowen.app/acme-corp)
2. Middleware checks authentication
3. If not authenticated → redirect to /login?org=acme-corp
4. User logs in with org credentials
5. JWT issued with claims: { user_id, org_id, role }
6. All API requests include org context
7. Search queries scoped to: public + org data banks
```

### Phase 3: Multi-Tenant API

**Endpoint Changes**:

```python
# Before (single tenant)
@app.post("/chat")
async def chat(request: ChatRequest):
    results = search_embeddings(request.message)
    ...

# After (multi-tenant)
@app.post("/chat")
async def chat(
    request: ChatRequest,
    org: Organization = Depends(get_current_org),  # From JWT or public
    user: Optional[User] = Depends(get_current_user)
):
    # Search public + org-specific data banks
    results = search_embeddings(
        query=request.message,
        data_bank_ids=get_accessible_data_banks(org, user)
    )
    ...
```

**Search Query Logic**:
```python
def get_accessible_data_banks(org: Organization, user: Optional[User]) -> List[UUID]:
    """
    Returns data bank IDs the user can search:
    - Always include public data banks
    - Include org-specific data banks if authenticated
    """
    accessible = []

    # Public data banks (Bowen Public corpus)
    public_banks = db.query(DataBank).filter(DataBank.is_public == True).all()
    accessible.extend([b.id for b in public_banks])

    # Org-specific data banks (if authenticated)
    if user and org.id != PUBLIC_ORG_ID:
        org_banks = db.query(DataBank).filter(DataBank.org_id == org.id).all()
        accessible.extend([b.id for b in org_banks])

    return accessible
```

### Phase 4: Data Bank Management

**Admin Interface** (new pages):

```
/[org]/admin/
├── data-banks/
│   ├── page.tsx            # List org data banks
│   ├── new/page.tsx        # Create new data bank
│   └── [id]/
│       ├── page.tsx        # View/edit data bank
│       └── upload/page.tsx # Upload documents
├── users/
│   └── page.tsx            # Manage org users
└── settings/
    └── page.tsx            # Org settings
```

**Document Upload Flow**:
```
1. Admin uploads PDF/HTML/DOCX
2. Backend processes document:
   a. Extract text (PyMuPDF, python-docx, BeautifulSoup)
   b. Chunk text (same logic as current chunking)
   c. Generate embeddings (sentence-transformers)
   d. Store in PostgreSQL with org context
3. New content immediately searchable
```

**API Endpoints**:
```
POST   /api/v1/admin/data-banks              # Create data bank
GET    /api/v1/admin/data-banks              # List org data banks
DELETE /api/v1/admin/data-banks/{id}         # Delete data bank
POST   /api/v1/admin/data-banks/{id}/upload  # Upload documents
GET    /api/v1/admin/data-banks/{id}/chunks  # List chunks
DELETE /api/v1/admin/chunks/{id}             # Delete chunk
```

---

## URL Structure

| URL | Description | Auth Required |
|-----|-------------|---------------|
| `bowen.app` | Public Bowen (NZ legislation) | No |
| `bowen.app/login` | Login page | No |
| `bowen.app/{org-slug}` | Org-specific instance | Yes |
| `bowen.app/{org-slug}/admin` | Org admin panel | Yes (admin role) |

**Alternative**: Subdomain-based routing
| URL | Description |
|-----|-------------|
| `bowen.app` | Public |
| `acme.bowen.app` | Org-specific |

---

## Data Flow for Org Queries

```
User Query: "What is our policy on remote work?"
                    │
                    ▼
┌─────────────────────────────────────────┐
│           Authentication                 │
│  Extract org_id from JWT/session        │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│         Data Bank Resolution            │
│  Get accessible banks:                  │
│  - Public: [NZ Legislation]             │
│  - Org: [HR Policies, Company Docs]     │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│          Vector Search                  │
│  Search embeddings WHERE                │
│  data_bank_id IN (accessible_banks)     │
│  ORDER BY cosine_similarity DESC        │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│         Claude Generation               │
│  System prompt includes:                │
│  - Org context/tone                     │
│  - Retrieved excerpts                   │
│  - Source attribution                   │
└────────────────────┬────────────────────┘
                     │
                     ▼
            Response with Sources
```

---

## Technology Stack

| Layer | Current | Proposed |
|-------|---------|----------|
| **Frontend** | Next.js 14 | Next.js 14 + NextAuth.js |
| **Backend** | FastAPI | FastAPI + SQLAlchemy |
| **Database** | JSON/NumPy files | PostgreSQL + pgvector |
| **Auth** | None | JWT + OAuth2 (optional) |
| **Vector Search** | NumPy cosine sim | pgvector (PostgreSQL) |
| **File Storage** | Local | S3/R2 (for uploads) |
| **Cache** | None | Redis (optional) |

---

## Migration Path

### Step 1: Database Setup
1. Provision PostgreSQL with pgvector extension
2. Create schema (organizations, users, data_banks, chunks, embeddings)
3. Migrate existing embeddings to PostgreSQL
4. Update backend to use SQLAlchemy + asyncpg

### Step 2: Authentication
1. Add NextAuth.js to frontend
2. Implement JWT auth in FastAPI
3. Create login/register pages
4. Add route protection middleware

### Step 3: Multi-Tenant Middleware
1. Add org context to all requests
2. Update search to filter by accessible data banks
3. Implement org-scoped API responses

### Step 4: Admin Interface
1. Build data bank management UI
2. Implement document upload + processing
3. Add user management for org admins

### Step 5: Onboarding Flow
1. Create org provisioning process
2. Build admin invitation system
3. Document upload workflow

---

## Security Considerations

1. **Data Isolation**: Queries must never return data from other orgs
2. **Row-Level Security**: Consider PostgreSQL RLS policies
3. **API Keys**: Org-specific API keys for programmatic access
4. **Audit Logging**: Track who accessed what data
5. **Encryption**: Encrypt sensitive org data at rest
6. **Rate Limiting**: Per-org rate limits to prevent abuse

---

## Cost Considerations

| Resource | Estimate |
|----------|----------|
| PostgreSQL (managed) | $15-50/month |
| Additional compute per org | Minimal (shared) |
| Storage per org | ~$0.02/GB/month |
| Embedding generation | One-time per upload |

---

## Open Questions

1. **Billing Model**: Per-seat, per-query, or flat fee?
2. **Data Retention**: How long to keep org data after subscription ends?
3. **Public Corpus Access**: Should orgs be able to disable public data?
4. **Custom Branding**: Allow orgs to customize UI/colors?
5. **SSO Integration**: Support SAML/OIDC for enterprise clients?
6. **Embedding Model**: Allow orgs to use different models?

---

## Next Steps

1. [ ] Finalize database schema design
2. [ ] Set up PostgreSQL + pgvector on Railway/Supabase
3. [ ] Implement auth layer (NextAuth.js + FastAPI JWT)
4. [ ] Migrate existing embeddings to PostgreSQL
5. [ ] Build org admin interface
6. [ ] Create first pilot org instance
7. [ ] Document onboarding process for clients
