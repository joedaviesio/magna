# Pilot Organisation Implementation Plan

## Overview

Minimal implementation to get the first organisation running on Bowen with their own private data bank alongside the public NZ legislation corpus.

**Scope**: Manual data processing, basic auth, tenant-aware search. No admin UI or self-service features.

---

## Pilot Requirements

| Requirement | Implementation |
|-------------|----------------|
| Org-specific login | Email/password auth with JWT |
| Private data bank | Org's documents chunked and embedded |
| Combined search | Query searches org data + public corpus |
| Separate URL | `bowen.app/[org-slug]` or subdomain |
| Basic UI | Same chat interface, org branding minimal |

---

## Implementation Checklist

### 1. Database Setup

- [ ] Provision PostgreSQL instance (Railway/Supabase)
- [ ] Enable pgvector extension
- [ ] Create schema:
  ```sql
  -- Core tables
  organizations (id, name, slug, settings)
  users (id, org_id, email, password_hash, role)
  data_banks (id, org_id, name, is_public)
  chunks (id, data_bank_id, text, metadata fields...)
  embeddings (id, chunk_id, vector)
  ```
- [ ] Seed public org + public data bank record
- [ ] Migrate existing NZ legislation embeddings to PostgreSQL

### 2. Backend Auth

- [ ] Add dependencies: `python-jose`, `passlib`, `bcrypt`
- [ ] Create auth module:
  ```
  app/auth/
  ├── jwt.py          # Token create/verify
  ├── password.py     # Hash/verify passwords
  ├── dependencies.py # get_current_user, get_current_org
  └── routes.py       # POST /auth/login
  ```
- [ ] Add auth middleware to protected routes
- [ ] Update `/chat` endpoint to accept org context

### 3. Frontend Auth

- [ ] Install NextAuth.js (or simple JWT approach)
- [ ] Create login page at `/login`
- [ ] Add auth context/provider
- [ ] Create protected route wrapper
- [ ] Store JWT in httpOnly cookie or secure storage
- [ ] Add org slug to API requests

### 4. Pilot Org Data Processing

- [ ] Receive documents from pilot org
- [ ] Process documents:
  - Extract text (PDF/DOCX/HTML)
  - Clean and normalize
  - Chunk using existing chunking logic
- [ ] Generate embeddings with sentence-transformers
- [ ] Insert into database with org's data_bank_id

### 5. Multi-Tenant Search

- [ ] Update search function to accept data_bank_ids
- [ ] Modify query to filter embeddings by accessible banks
- [ ] Ensure public corpus always included for authenticated users
- [ ] Test isolation (org A cannot see org B's data)

### 6. Frontend Routing

- [ ] Add dynamic route: `/[org-slug]/page.tsx`
- [ ] Fetch org config on page load
- [ ] Apply minimal org branding (logo, name in header)
- [ ] Redirect unauthenticated users to login

---

## Database Schema (Pilot Scope)

```sql
-- Organisations
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Public org (ID fixed for easy reference)
INSERT INTO organizations (id, name, slug)
VALUES ('00000000-0000-0000-0000-000000000000', 'Bowen Public', 'public');

-- Pilot org
INSERT INTO organizations (name, slug)
VALUES ('[Pilot Org Name]', '[pilot-slug]');

-- Users (pilot org admins/members)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'member',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Data banks
CREATE TABLE data_banks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Public data bank (NZ legislation)
INSERT INTO data_banks (org_id, name, is_public)
VALUES ('00000000-0000-0000-0000-000000000000', 'NZ Legislation', TRUE);

-- Chunks
CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data_bank_id UUID REFERENCES data_banks(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    act_title VARCHAR(255),
    section_number VARCHAR(50),
    section_heading VARCHAR(255),
    section_url TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Embeddings with pgvector
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_id UUID REFERENCES chunks(id) ON DELETE CASCADE,
    embedding vector(384) NOT NULL
);

-- Index for fast similarity search
CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

---

## API Changes

### New Endpoints

```
POST /auth/login
  Body: { email, password }
  Returns: { access_token, user, org }

GET /auth/me
  Headers: Authorization: Bearer <token>
  Returns: { user, org }
```

### Modified Endpoints

```
POST /chat
  Headers: Authorization: Bearer <token> (optional)
  Body: { message, session_id? }

  Behaviour:
  - No auth → search public data banks only
  - With auth → search public + org's data banks
```

---

## File Changes Summary

### Backend

```
backend/app/
├── auth/
│   ├── __init__.py
│   ├── jwt.py
│   ├── password.py
│   ├── dependencies.py
│   └── routes.py
├── database.py              # SQLAlchemy setup
├── models/
│   ├── __init__.py
│   ├── organization.py
│   ├── user.py
│   ├── data_bank.py
│   ├── chunk.py
│   └── embedding.py
├── main.py                  # Add auth routes, update /chat
└── requirements.txt         # Add: sqlalchemy, asyncpg, pgvector, python-jose, passlib, bcrypt
```

### Frontend

```
frontend/src/
├── app/
│   ├── login/
│   │   └── page.tsx
│   ├── [org]/
│   │   └── page.tsx
│   └── page.tsx             # Public Bowen (unchanged)
├── components/
│   └── auth-provider.tsx
├── lib/
│   ├── auth.ts
│   └── api.ts               # Add auth headers
└── middleware.ts            # Route protection
```

---

## Pilot Data Processing Workflow

```
1. Receive documents from pilot org
   └── Formats: PDF, DOCX, HTML, TXT

2. Extract text
   └── Tools: PyMuPDF (PDF), python-docx (DOCX), BeautifulSoup (HTML)

3. Clean text
   ├── Remove headers/footers
   ├── Normalize whitespace
   └── Handle special characters

4. Chunk documents
   ├── Use existing chunking logic from scripts/chunk_legislation.py
   ├── Chunk size: ~500-1000 tokens
   └── Preserve document/section metadata

5. Generate embeddings
   ├── Model: all-MiniLM-L6-v2 (same as public corpus)
   └── Script: Adapt scripts/generate_embeddings.py

6. Insert into database
   ├── Create data_bank record for pilot org
   ├── Insert chunks with data_bank_id
   └── Insert embeddings linked to chunks

7. Verify
   ├── Test search returns org documents
   └── Confirm public corpus still accessible
```

---

## Testing Checklist

- [ ] Public Bowen (`/`) works without auth
- [ ] Pilot org URL (`/[org-slug]`) requires login
- [ ] Login with valid credentials succeeds
- [ ] Login with invalid credentials fails
- [ ] Authenticated queries return org + public results
- [ ] Unauthenticated queries return public results only
- [ ] Org A user cannot access org B data
- [ ] Session persists across page refreshes
- [ ] Logout clears session

---

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/bowen

# Auth
JWT_SECRET_KEY=<generate-secure-key>
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# Existing
ANTHROPIC_API_KEY=...
SUPABASE_URL=...  # Optional, for analytics
SUPABASE_KEY=...
```

---

## Rollout Steps

1. **Set up database** - Create PostgreSQL instance, run schema
2. **Migrate public corpus** - Move existing embeddings to database
3. **Deploy backend changes** - Auth + multi-tenant search
4. **Deploy frontend changes** - Login page + protected routes
5. **Create pilot org** - Insert org record, create user accounts
6. **Process pilot data** - Chunk and embed org documents
7. **Test end-to-end** - Verify combined search works
8. **Hand off to pilot org** - Provide login credentials, gather feedback

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Auth flow works | Login/logout functional |
| Search accuracy | Org docs appear in relevant queries |
| Data isolation | No cross-org data leakage |
| Performance | Response time <3s |
| Pilot feedback | Org confirms utility for their use case |

---

## Post-Pilot Improvements (Phase 2)

Based on pilot feedback, prioritise:
- [ ] Admin UI for data bank management
- [ ] Document upload interface
- [ ] Custom branding per org
- [ ] User management (invite team members)
- [ ] Usage analytics dashboard

---

## Notes

- Keep auth simple for pilot - email/password, no OAuth yet
- Manual data processing is fine - learn what formats orgs typically have
- Get feedback on search quality - may need to tune chunking or boosting
- Document any pain points for automation later
