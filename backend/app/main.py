# App entry point — Vercel-compatible FastAPI with mangum
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1 import api_router
from app.db.session import engine
from app.db.base import Base


def check_and_seed_database():
    """Check if database needs seeding and seed if empty"""
    from app.db.init_db import init_database
    try:
        init_database()
    except Exception as e:
        print(f"⚠️ Database seeding warning: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — create tables + seed on startup."""
    # Create database tables (including pgvector extension)
    from sqlalchemy import text as sa_text
    with engine.connect() as conn:
        conn.execute(sa_text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

    # Auto-seed database if empty (demo users, poisons, hospitals, etc.)
    check_and_seed_database()

    yield
    print("Shutting down PoisonSense-AI Backend...")


# Create FastAPI app
app = FastAPI(
    title="PoisonSense-AI API",
    description="AI-powered poison identification and emergency response system.",
    version="1.0.0",
    lifespan=lifespan,
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


# Health check endpoints
@app.get("/", tags=["Health"])
async def root():
    return {"status": "healthy", "service": "PoisonSense-AI API", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "database": "connected", "ml_model": "ready"}


@app.get("/docs-info", tags=["Documentation"])
async def docs_info():
    return {"swagger_ui": "/docs", "redoc": "/redoc", "openapi_json": "/openapi.json"}


# ── Mangum handler for Vercel serverless ───────────────────────────────
from mangum import Mangum  # noqa: E402

handler = Mangum(app, lifespan="auto")
