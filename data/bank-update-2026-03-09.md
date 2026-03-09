# Bank Update — 9 March 2026

Next 10 acts to pipe through the Bowen ingestion pipeline.
Fills gaps in criminal, family, civil procedure, and professional law.

## Acts to Add

| # | Short Code | Full Title | Year | URL |
|---|---|---|---|---|
| 1 | SA | Sentencing Act | 2002 | https://www.legislation.govt.nz/act/public/2002/0009/latest/DLM135342.html |
| 2 | CPA | Criminal Procedure Act | 2011 | https://www.legislation.govt.nz/act/public/2011/0081/latest/DLM3359902.html |
| 3 | EVA | Evidence Act | 2006 | https://www.legislation.govt.nz/act/public/2006/0069/latest/DLM393462.html |
| 4 | BAIL | Bail Act | 2000 | https://www.legislation.govt.nz/act/public/2000/0038/latest/DLM68380.html |
| 5 | COCA | Care of Children Act | 2004 | https://www.legislation.govt.nz/act/public/2004/0090/latest/DLM317233.html |
| 6 | PRA | Property (Relationships) Act | 1976 | https://www.legislation.govt.nz/act/public/1976/0166/latest/DLM440945.html |
| 7 | LA | Limitation Act | 2010 | https://www.legislation.govt.nz/act/public/2010/0110/latest/DLM2033101.html |
| 8 | LCA | Lawyers and Conveyancers Act | 2006 | https://www.legislation.govt.nz/act/public/2006/0001/latest/DLM364939.html |
| 9 | SSA | Search and Surveillance Act | 2012 | https://www.legislation.govt.nz/act/public/2012/0024/latest/DLM2136536.html |
| 10 | PPPR | Protection of Personal and Property Rights Act | 1988 | https://www.legislation.govt.nz/act/public/1988/0004/latest/DLM126528.html |

## Rationale

- **Criminal law** (SA, CPA, EVA, BAIL): Core criminal statutes — sentencing, procedure, evidence, and bail. Currently no criminal procedure coverage.
- **Family law** (COCA, PRA): Care of children and relationship property. Complements existing Family Violence Act and Family Court Act.
- **Civil procedure** (LA): Limitation periods affect nearly every civil claim. Fundamental gap.
- **Legal profession** (LCA): Governs lawyers and conveyancers — relevant to many user queries about legal obligations.
- **Police powers** (SSA): Search and surveillance — bridges criminal and civil rights law.
- **Personal rights** (PPPR): Enduring powers of attorney, welfare guardians — high public interest.

## Pipeline Steps

1. Download HTML from legislation.govt.nz URLs above
2. Parse with `backend/scripts/parse_legislation.py`
3. Chunk with `backend/scripts/chunk_legislation.py`
4. Add entries to `backend/app/acts_registry.py`
5. Regenerate embeddings with `backend/scripts/generate_embeddings.py`
6. Verify via `/api/v1/acts` endpoint
