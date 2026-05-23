<div align="center">

# 🧪 PoisonSense AI

**An AI-powered poison emergency and clinical support platform for Nepal**

*Connecting patients, doctors, and hospitals — powered by RAG, built on a free stack*

---

## 📖 About

PoisonSense AI is a full-stack web platform designed to address Nepal's poison emergency response gap. It combines a **RAG-powered clinical AI assistant**, **role-based dashboards** for patients, doctors, hospital admins, and reviewers, a **poison information database**, and **location-based hospital discovery** — all in one platform.

Originally named *PoisonCare*, the project was built by a team of four students as a full-stack AI application with a Nepal-only focus.

> ⚠️ **Nepal-specific**: Hospital data, location services, and clinical context are tailored for Nepal.

---

## ✨ Features

### 🤖 AI Assistant
- RAG-powered chatbot grounded in clinical toxicology PDFs
- Per-user scoped chat history
- Answers overhauled for clinical accuracy and safety

### 👥 Role-Based Platform
| Role | Capabilities |
|---|---|
| **Patient** | AI chat, find nearby hospitals, poison information |
| **Doctor** | Clinical dashboard, case review |
| **Hospital Admin** | Linked hospital management (e.g. Bir Hospital) |
| **Reviewer** | Case and content review dashboard |

### 🗺️ Location Services
- Find nearby hospitals and poison treatment centres in Nepal

### 💊 Poison Information
- Antidotes directory
- Poison Labs listings
- Educational blog

### 🔐 Authentication
- OTP-based signup and login

### 📊 Custom NLP Model
- Scraped poison dataset (Dipesh)
- Trained custom classification model for poison identification

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│              Frontend (React)               │
│  Patient | Doctor | Hospital | Reviewer     │
│         Deployed: Vercel / GitHub Pages     │
└───────────────────┬─────────────────────────┘
                    │ REST API
┌───────────────────▼─────────────────────────┐
│           Backend (FastAPI / ASGI)          │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │           RAG Pipeline              │    │
│  │  Query → HF Embed → pgvector search │    │
│  │  Top-k chunks → Groq LLM → Answer   │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  Auth | Roles | Blog | Hospital | Location  │
└──────┬─────────────────┬────────────────────┘
       │                 │
┌──────▼──────┐   ┌──────▼──────────────────┐
│  Supabase   │   │   HuggingFace Inference  │
│  pgvector   │   │   API (Embeddings)       │
│  (vectors + │   └─────────────────────────┘
│   user data)│
└─────────────┘
```

**Document Ingestion**
```
Toxicology PDFs → Chunk → HF Embed → Supabase pgvector
(run via ingest_remote.py)
```

---

## 🛠️ Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| **LLM** | [Groq](https://console.groq.com) | Replaced OpenAI — free tier |
| **Embeddings** | [HuggingFace Inference API](https://huggingface.co/inference-api) | Free, no local GPU needed |
| **Vector DB** | [Supabase](https://supabase.com) + pgvector | Replaced ChromaDB for remote deployment |
| **Backend** | FastAPI (native ASGI) | Removed Mangum for Vercel compatibility |
| **Frontend** | React + HashRouter | GitHub Pages + Vercel |
| **Auth** | OTP-based | Custom implementation |
| **NLP Model** | Custom (Dipesh) | Scraped + trained poison dataset |
| **CI/CD** | GitHub Actions | Auto-deploy to GitHub Pages |
| **Containerization** | Docker Compose | Local development |

> 💸 **Entirely free to run** — no OpenAI, no paid embeddings, no paid vector DB.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker (optional)
- [Supabase](https://supabase.com) project with pgvector enabled
- [Groq API key](https://console.groq.com)
- [HuggingFace token](https://huggingface.co/settings/tokens)

### 1. Clone the repo

```bash
git clone https://github.com/Madan-21/PoisonSense-AI.git
cd PoisonSense-AI
```

### 2. Configure environment variables

Create a `.env` file in `backend/`:

```env
GROQ_API_KEY=your_groq_api_key
HF_TOKEN=your_huggingface_token
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
```

### 3. Run with Docker (recommended)

```bash
docker-compose up --build
```

### 4. Or run manually

**Backend:**
```bash
cd backend
pip install -r requirements.txt
bash ../start_backend.sh
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## 📄 Ingesting Documents

Place your toxicology PDFs in the `Pdf's/` folder, then run:

```bash
python ingest_remote.py
```

This chunks the PDFs, generates embeddings via HuggingFace, and stores them in Supabase pgvector.

> **Note:** Keep PDFs under ~5MB total to avoid OOM issues on free-tier hosting.

---

## 🗂️ Project Structure

```
PoisonSense-AI/
├── .github/workflows/      # CI/CD — GitHub Pages deploy
├── Pdf's/                  # Clinical toxicology PDF knowledge base
├── backend/                # FastAPI app (RAG, auth, roles, blog)
├── frontend/               # React app (all role dashboards)
├── docker-compose.yml      # Docker orchestration
├── ingest_remote.py        # PDF ingestion script (Supabase pgvector)
├── start_backend.sh        # Backend startup script
├── package.json            # Root JS dependencies
└── vercel.json             # Vercel deployment config
```

---


## ⚠️ Disclaimer

PoisonSense AI is a **clinical decision-support tool** and does not replace professional medical advice. In a poison emergency, always contact emergency services immediately.

**Nepal Poison Helpline:** 16600185066  
**Bir Hospital Emergency:** +977-1-4221119

---

## 📜 License

This project does not currently have a license. All rights reserved by the contributors.
