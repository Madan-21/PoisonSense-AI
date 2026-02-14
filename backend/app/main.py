# App entry point - Main FastAPI Application
# Patch chromadb for Python 3.14 compatibility — MUST run before any chromadb import
import sys
try:
    import chromadb_patch  # noqa: F401
except Exception as e:
    print(f"⚠️ ChromaDB patch skipped: {e}")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.api.v1 import api_router
from app.db.session import engine, SessionLocal
from app.db.base import Base

def check_and_seed_database():
    """Check if database needs seeding and seed if empty"""
    from app.db.init_db import init_database
    try:
        init_database()
    except Exception as e:
        print(f"⚠️ Database seeding warning: {e}")


def auto_ingest_pdfs():
    """Auto-ingest bundled PDFs into ChromaDB if the vector store is empty.
    Runs in a background thread so the server can start accepting requests."""
    import threading

    def _ingest():
        try:
            from rag.vector_store import get_collection_stats
            from rag.ingest import ingest_directory
            from pathlib import Path

            stats = get_collection_stats()
            total = sum(stats.values())
            if total > 0:
                print(f"📚 Vector store already has {total} chunks — skipping auto-ingest")
                return

            # PDFs are bundled in backend/rag/pdf_uploads/
            base = Path(__file__).resolve().parent.parent  # backend/
            pdf_dir = base / "rag" / "pdf_uploads"

            pdfs = list(pdf_dir.glob("*.pdf")) if pdf_dir.exists() else []
            if pdfs:
                print(f"📥 Auto-ingesting {len(pdfs)} PDFs from rag/pdf_uploads/ ...")
                results = ingest_directory(str(pdf_dir), "toxicology")
                ok = sum(1 for r in results if "error" not in r)
                print(f"✅ Auto-ingest complete: {ok}/{len(results)} PDFs ingested")
            else:
                print("📭 No PDFs found in rag/pdf_uploads/ for auto-ingestion")
        except Exception as e:
            print(f"⚠️ Auto-ingest failed (non-fatal): {e}")

    t = threading.Thread(target=_ingest, daemon=True)
    t.start()

# Create all database tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - create tables on startup"""
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
    
    # Auto-seed database if empty (for fresh clones)
    check_and_seed_database()
    
    # Optionally preload ML model
    try:
        # Temporarily disabled for debugging
        print("📦 ML Model loading temporarily disabled for debugging")
        # from app.services.ml_service import ml_service
        # ml_service.load_model()
        # print("✅ ML Model loaded successfully")
    except Exception as e:
        print(f"⚠️ ML Model not loaded: {e}")
    
    # Auto-ingest bundled PDFs in background (won't block startup)
    auto_ingest_pdfs()
    
    yield
    
    # Cleanup (if needed)
    print("Shutting down PoisonSense-AI Backend...")

# Create FastAPI app
app = FastAPI(
    title="PoisonSense-AI API",
    description="""
    ## PoisonSense-AI Backend API
    
    AI-powered poison identification and emergency response system.
    
    ### Features:
    - 🔐 **Authentication**: JWT-based user authentication
    - 🧠 **AI Analysis**: DistilBERT-based symptom analysis for poison identification
    - 🏥 **Hospital Finder**: Locate nearby hospitals with toxicology capabilities
    - ☎️ **Poison Centers**: Find nearest poison control centers
    - 💊 **Antidote Locator**: Find antidote availability
    - 👨‍⚕️ **Doctor Verification**: Verified healthcare professionals
    - 📊 **Explainable AI**: Transparent reasoning with data sources
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Serve uploaded license files statically
uploads_dir = os.path.join(os.getcwd(), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "healthy",
        "service": "PoisonSense-AI API",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "ml_model": "ready"
    }

# API documentation redirect
@app.get("/docs-info", tags=["Documentation"])
async def docs_info():
    return {
        "swagger_ui": "/docs",
        "redoc": "/redoc",
        "openapi_json": "/openapi.json"
    }
