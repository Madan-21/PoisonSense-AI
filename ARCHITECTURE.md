# PoisonSense AI — Agentic RAG Chatbot Architecture

## A) Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (React + Vite)                       │
│  ┌──────────────┐  ┌────────────────┐  ┌──────────────────────────┐   │
│  │  AiAssistant  │  │   ragApi.js    │  │  RagChat.css (Citations  │   │
│  │  (Chat UI)    │──│  /rag/ask      │  │   Sources, Safety, etc.) │   │
│  │               │  │  /rag/ingest   │  │                          │   │
│  └──────────────┘  └────────┬───────┘  └──────────────────────────┘   │
└────────────────────────────|──────────────────────────────────────────┘
                              │ HTTP / JSON
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI + Python)                          │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    API Layer (rag_chatbot.py)                     │  │
│  │  POST /rag/ask    POST /rag/ingest    GET /rag/collections       │  │
│  │  POST /rag/reset  DELETE /rag/collections/{name}                 │  │
│  │  POST /rag/tools/execute   GET /rag/status                       │  │
│  └────────────────────────────┬─────────────────────────────────────┘  │
│                               │                                         │
│  ┌────────────────────────────▼─────────────────────────────────────┐  │
│  │                    RAG ENGINE (rag/ module)                       │  │
│  │                                                                   │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │  │
│  │  │ Safety Gate  │  │    Agent     │  │     LLM Interface      │  │  │
│  │  │ (classify,   │──│ (decision    │──│ (Groq — free)          │  │  │
│  │  │  refuse,     │  │  routing,    │  │                        │  │  │
│  │  │  escalate)   │  │  generate)   │  └────────────────────────┘  │  │
│  │  └─────────────┘  └──────┬───────┘                               │  │
│  │                          │                                        │  │
│  │  ┌───────────────────────▼────────────────────────────────────┐  │  │
│  │  │              Retrieval Layer                                │  │  │
│  │  │  ┌────────────────┐  ┌────────────────┐                    │  │  │
│  │  │  │  Vector Store   │  │  Collection    │                    │  │  │
│  │  │  │  (ChromaDB)     │  │  Router        │                    │  │  │
│  │  │  └────────┬───────┘  └────────────────┘                    │  │  │
│  │  │           │                                                 │  │  │
│  │  │  ┌────────▼───────────────────────────────────────────┐    │  │  │
│  │  │  │            Embedding Layer (HF Inference API — free)     │    │  │  │
│  │  │  │  sentence-transformers/all-MiniLM-L6-v2 (384 dims)      │    │  │  │
│  │  │  └────────────────────────────────────────────────────┘    │  │  │
│  │  └────────────────────────────────────────────────────────────┘  │  │
│  │                                                                   │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │  │
│  │  │  Ingestion   │  │   Safe Tools │  │   Session Memory       │  │  │
│  │  │  Pipeline    │  │  (contacts,  │  │  (per session_id)      │  │  │
│  │  │  (PDF→Chunk  │  │   checklist, │  │                        │  │  │
│  │  │   →Embed     │  │   logging)   │  │                        │  │  │
│  │  │   →Store)    │  │              │  │                        │  │  │
│  │  └─────────────┘  └──────────────┘  └────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Flow
1. User sends question → `POST /rag/ask`
2. **Safety Gate** classifies query (harmful? emergency? self-harm? vague?)
3. If harmful → immediate refusal with safe alternatives
4. If emergency → escalation + retrieval from knowledge base
5. If vague → triage questions before retrieval
6. Otherwise → **Collection Router** decides which collections to query
7. **Vector Store** performs cosine similarity search
8. Results filtered by relevance threshold (default 0.25)
9. **LLM** generates grounded answer using ONLY retrieved sources
10. Response includes: answer, citations, reasoning, safety assessment

### Threat Model
| Threat | Mitigation |
|--------|-----------|
| Harmful queries (poisoning instructions) | Regex-based safety gate + refusal templates |
| Hallucination / confabulation | Hard-grounding: LLM forced to cite sources only |
| Prompt injection | System prompt is immutable; user input treated as data |
| Dosage/antidote administration | Blocked by safety patterns + disallowed tool list |
| Self-harm queries | Compassionate refusal + crisis resource referrals |
| Data quality | Only approved PDFs ingested by admin |

---

## B) Data Ingestion Pipeline

### PDF Parsing Strategy
- **Primary**: `pdfplumber` — extracts text + tables + page numbers
- **Fallback**: `PyPDF2` — text-only extraction
- **Metadata captured**: page number, document title, source file path

### Chunking Strategy
- **Method**: Paragraph-aware sliding window with sentence-boundary splitting
- **Chunk size**: 800 tokens (configurable via `CHUNK_SIZE`)
- **Overlap**: 200 tokens (configurable via `CHUNK_OVERLAP`)
- **Special handling**: Tables concatenated as pipe-separated text

### Embedding Model
- **Provider**: Hugging Face Inference API (free, no local model needed)
- **Model**: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- **Token**: Optional `HF_API_TOKEN` — public models work without one

### Vector DB
- **Default**: ChromaDB (persistent, local)
- **Storage**: `backend/rag/chroma_store/`
- **Distance metric**: Cosine similarity

### Metadata Schema
```json
{
  "doc_id": "a1b2c3d4",
  "doc_title": "Forensic Toxicology Handbook",
  "source_path": "handbook.pdf",
  "page": 42,
  "section": "",
  "chunk_id": "a1b2c3d4_p42_c0",
  "hash": "sha256_16chars",
  "created_at": "2026-02-10T00:00:00Z",
  "collection": "general"
}
```

---

## C) Retrieval & Answer Generation

### Multi-stage Retrieval
1. **Intent analysis** → route to 1..N collections
2. **Vector search** → cosine similarity top-K (default 8)
3. **Threshold filter** → keep only results ≥ 0.25 relevance
4. **Deduplication** → by chunk_id across collections

### Threshold Logic
- Score ≥ 0.25 → include in context
- No results above threshold → "I don't have that in my approved dataset"
- Fallback offers: contact professional, poison control, WHO resources

### Citation Generator
Every response includes:
```json
{
  "sources": [
    {
      "doc_title": "Forensic Toxicology Handbook",
      "doc_id": "a1b2c3d4",
      "source_path": "handbook.pdf",
      "page": 42,
      "chunk_id": "a1b2c3d4_p42_c0",
      "relevance_score": 0.87,
      "supporting_quote": "Carbon monoxide binds to hemoglobin with 200x affinity..."
    }
  ]
}
```

---

## D) Agentic Behavior Policy

### Decision Logic
1. **Safety gate FIRST** → classify every query
2. **If vague exposure** → ask triage questions (age, substance, route, time, symptoms)
3. **If general question** → retrieve from knowledge base + generate grounded answer
4. **If emergency** → escalate + retrieve first-aid from KB
5. **If harmful** → refuse with safe alternatives

### Collection Routing
| Intent Keywords | Collections Queried |
|----------------|-------------------|
| first aid, emergency, swallow, inhale | `first_aid`, `emergency_escalation` |
| symptom, sign, feel, effect | `symptom_recognition` |
| prevent, store, safe, keep away | `prevention_storage` |
| nepal, india, hospital, center | `regional_resources` |
| (default) | `general` |

### Safe Tools
| Tool | Purpose |
|------|---------|
| `get_poison_control_contacts(country)` | Emergency contacts by country |
| `find_nearest_emergency_department(location)` | Hospital guidance |
| `create_incident_checklist(context)` | 10-step incident checklist |
| `log_incident(details)` | Non-medical incident logging |
| `read_label_or_sds(text)` | Product label interpretation |

### Disallowed Tools
- `dosage_calculator` — BLOCKED
- `antidote_selector` — BLOCKED
- `antidote_administrator` — BLOCKED
- `chemical_mixing_guide` — BLOCKED

### Session Memory
Per `session_id`:
- Conversation history (last 20 messages)
- Triage data collected
- Advice already given
- Whether emergency services contacted

---

## E) Safety / Harm-Prevention Gate

### Detection Patterns
- **Harmful intent**: "how to poison", "best poison", "lethal dose", "LD50", etc.
- **Dosage/admin**: "antidote dosage", "how much antidote", "administer antidote"
- **Chemical mixing**: "mix bleach ammonia", "chlorine gas", "chemical weapon"
- **Self-harm**: "suicide", "kill myself", "want to die", "overdose"
- **Emergency**: "swallowed poison", "child drank", "not breathing", "seizure"

### Refusal Templates
- **Harmful**: Refuses + pivots to prevention, emergency response, legal info
- **Self-harm**: Compassionate refusal + crisis hotlines (Nepal 1166, global resources)
- **Emergency**: Immediate escalation with Nepal emergency numbers + first-aid steps

---

## F) Reference Implementation

### Stack
- **Backend**: Python 3.10+ / FastAPI
- **Vector Store**: ChromaDB (local, persistent)
- **PDF Extraction**: pdfplumber (primary) / PyPDF2 (fallback)
- **Embeddings**: Hugging Face Inference API — `all-MiniLM-L6-v2` (free)
- **LLM**: Groq (default, free) / Ollama (local fallback)
- **Frontend**: React 19 + Vite

### Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/rag/ask` | Ask a question |
| POST | `/api/v1/rag/ingest` | Upload PDFs |
| POST | `/api/v1/rag/ingest/directory` | Ingest from server directory |
| GET | `/api/v1/rag/collections` | List collections + stats |
| DELETE | `/api/v1/rag/collections/{name}` | Delete a collection |
| POST | `/api/v1/rag/reset` | Reset chat session |
| GET | `/api/v1/rag/status` | RAG system health |
| POST | `/api/v1/rag/tools/execute` | Execute safe tool |
| GET | `/api/v1/rag/tools/contacts/{country}` | Poison control contacts |

---

## G) Response Format

Every assistant response follows this schema:
```json
{
  "answer": "string (with inline [Source: doc_title, page X] citations)",
  "why_this_answer": "string (brief reasoning tied to citations)",
  "sources": [
    {
      "doc_title": "string",
      "doc_id": "string",
      "source_path": "string",
      "page": "number|null",
      "section": "string|null",
      "chunk_id": "string",
      "relevance_score": "number (0-1)",
      "supporting_quote": "string (≤25 words)"
    }
  ],
  "follow_up_questions": ["string"],
  "safety": {
    "risk_level": "low|medium|high",
    "policy_notes": "string",
    "refusal": "string|null",
    "emergency_escalation": "string|null"
  },
  "session_id": "string"
}
```

---

## Quick Start

```bash
# 1. Backend setup
cd backend
cp .env.example .env
# Edit .env → set GROQ_API_KEY (get free at console.groq.com)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Ingest PDFs
python ingest_pdfs.py

# 3. Start backend
uvicorn app.main:app --reload --port 8000

# 4. Frontend (new terminal)
cd frontend
npm install
npm run dev
# Open http://localhost:5173 → navigate to AI Assistant
```
