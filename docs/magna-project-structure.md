# Magna - Project Structure

## Folder Structure

```
magna/
│
├── README.md                    # Project overview and setup instructions
├── .env.example                 # Environment variables template
├── .env                         # Your actual env vars (git ignored)
├── .gitignore                   # Git ignore file
├── package.json                 # Root package.json (if using monorepo)
│
├── /docs                        # Documentation
│   ├── project-plan.csv         # Your project plan
│   ├── architecture.md          # System architecture notes
│   └── pitch-deck.pptx          # Pitch materials (when ready)
│
├── /data                        # Legislation data
│   ├── /raw                     # Raw XML files from legislation.govt.nz
│   │   ├── residential-tenancies-act-1986.xml
│   │   ├── employment-relations-act-2000.xml
│   │   ├── companies-act-1993.xml
│   │   ├── consumer-guarantees-act-1993.xml
│   │   ├── property-law-act-2007.xml
│   │   ├── fair-trading-act-1986.xml
│   │   ├── privacy-act-2020.xml
│   │   ├── building-act-2004.xml
│   │   ├── contract-commercial-law-act-2017.xml
│   │   └── resource-management-act-1991.xml
│   │
│   ├── /processed               # Chunked and processed documents
│   │   └── chunks.json          # Processed chunks with metadata
│   │
│   └── /embeddings              # Vector embeddings (if storing locally)
│       └── embeddings.pkl       # Serialized embeddings
│
├── /backend                     # Python backend (FastAPI + RAG)
│   ├── requirements.txt         # Python dependencies
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Configuration and settings
│   │
│   ├── /app
│   │   ├── __init__.py
│   │   ├── /api
│   │   │   ├── __init__.py
│   │   │   └── routes.py        # API endpoints (/chat, /health)
│   │   │
│   │   ├── /core
│   │   │   ├── __init__.py
│   │   │   ├── rag.py           # RAG pipeline (retrieval + generation)
│   │   │   ├── embeddings.py    # Embedding generation
│   │   │   ├── vectorstore.py   # Vector store operations
│   │   │   └── prompts.py       # System prompts and templates
│   │   │
│   │   ├── /services
│   │   │   ├── __init__.py
│   │   │   └── claude.py        # Claude API integration
│   │   │
│   │   └── /utils
│   │       ├── __init__.py
│   │       ├── parser.py        # XML legislation parser
│   │       └── chunker.py       # Text chunking utilities
│   │
│   └── /scripts
│       ├── ingest_legislation.py    # Script to process raw XML
│       ├── generate_embeddings.py   # Script to create embeddings
│       └── test_rag.py              # Test the RAG pipeline
│
├── /frontend                    # Next.js frontend
│   ├── package.json
│   ├── next.config.js
│   ├── tsconfig.json            # If using TypeScript
│   ├── tailwind.config.js       # Tailwind CSS config
│   ├── postcss.config.js
│   │
│   ├── /public
│   │   ├── favicon.ico
│   │   └── /images
│   │       └── logo.svg
│   │
│   ├── /src
│   │   ├── /app                 # Next.js App Router
│   │   │   ├── layout.tsx       # Root layout
│   │   │   ├── page.tsx         # Home page (chat interface)
│   │   │   └── globals.css      # Global styles
│   │   │
│   │   ├── /components
│   │   │   ├── Chat.tsx         # Main chat component (your prototype)
│   │   │   ├── Message.tsx      # Individual message component
│   │   │   ├── Sources.tsx      # Sources/citations panel
│   │   │   ├── Disclaimer.tsx   # Disclaimer modal
│   │   │   └── Header.tsx       # Header component
│   │   │
│   │   ├── /hooks
│   │   │   └── useChat.ts       # Chat state management hook
│   │   │
│   │   ├── /lib
│   │   │   └── api.ts           # API client for backend
│   │   │
│   │   └── /types
│   │       └── index.ts         # TypeScript types
│   │
│   └── /styles
│       └── fonts.css            # Font imports
│
└── /scripts                     # Utility scripts
    ├── download_legislation.sh  # Download XML from data.govt.nz
    └── setup.sh                 # Initial setup script
```

---

## Key Files to Create First

### 1. `.env.example`
```env
# Claude API
ANTHROPIC_API_KEY=your_api_key_here

# Optional: Vector DB (if using cloud)
# PINECONE_API_KEY=your_key
# PINECONE_ENVIRONMENT=your_env

# App settings
ENVIRONMENT=development
DEBUG=true
```

### 2. `.gitignore`
```
# Environment
.env
.env.local

# Python
__pycache__/
*.py[cod]
venv/
.venv/

# Node
node_modules/
.next/
out/

# Data (large files)
data/raw/*.xml
data/embeddings/*.pkl

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

### 3. `backend/requirements.txt`
```
fastapi==0.109.0
uvicorn==0.27.0
anthropic==0.18.0
python-dotenv==1.0.0
langchain==0.1.0
langchain-anthropic==0.1.0
chromadb==0.4.22
lxml==5.1.0
pydantic==2.5.0
httpx==0.26.0
```

### 4. `frontend/package.json`
```json
{
  "name": "magna-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.1.0",
    "react": "^18",
    "react-dom": "^18"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "autoprefixer": "^10",
    "postcss": "^8",
    "tailwindcss": "^3.4",
    "typescript": "^5"
  }
}
```

---

## Quick Start Commands

```bash
# 1. Create project folder
mkdir magna && cd magna

# 2. Create folder structure
mkdir -p docs data/{raw,processed,embeddings} backend/{app/{api,core,services,utils},scripts} frontend/{public/images,src/{app,components,hooks,lib,types},styles} scripts

# 3. Initialize backend
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# 4. Initialize frontend
cd ../frontend
npm install

# 5. Run development servers
# Terminal 1 (backend):
cd backend && uvicorn main:app --reload --port 8000

# Terminal 2 (frontend):
cd frontend && npm run dev
```

---

## Migration Checklist

- [ ] Create folder structure
- [ ] Copy `nz-legal-assistant-prototype.jsx` → `frontend/src/components/Chat.tsx`
- [ ] Copy `nz-legal-assistant-project-plan.csv` → `docs/project-plan.csv`
- [ ] Create `.env` with your Anthropic API key
- [ ] Download 10 Acts XML files to `data/raw/`
- [ ] Set up backend with Claude API integration
- [ ] Connect frontend to backend API

---

## Next Steps After Migration

1. **Get Claude API key** from console.anthropic.com
2. **Download legislation XML** from data.govt.nz
3. **Build the ingestion pipeline** (parse XML → chunk → embed)
4. **Implement RAG in backend** (retrieve chunks → call Claude)
5. **Connect frontend** to backend API
6. **Deploy** to Vercel (frontend) + Railway/Fly.io (backend)
