# Environment, secrets — Vercel-safe (no local .env auto-create)
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List
import os

class Settings(BaseSettings):
    # App
    APP_NAME: str = "PoisonSense AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database — Postgres via DATABASE_URL env var (Supabase / Neon / etc.)
    DATABASE_URL: str = "postgresql://localhost/poisonsense"

    # JWT Authentication
    SECRET_KEY: str = "change-me-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "https://madan-21.github.io",
    ]

    # ML Model paths (kept for compatibility, not used on Vercel)
    ML_MODEL_PATH: str = "app/ml/models"
    ML_DATA_PATH: str = "app/ml/data"

    # File Upload — S3-compatible (Supabase Storage)
    STORAGE_BUCKET: str = "uploads"
    SUPABASE_URL: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None
    # Legacy local path (for local dev fallback only)
    LICENSE_UPLOAD_DIR: str = "uploads/licenses"

    # External APIs (optional)
    GOOGLE_MAPS_API_KEY: Optional[str] = None

    # Email Settings (SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "PoisonSense AI <noreply@poisonsense.ai>"
    EMAIL_FROM_NAME: str = "PoisonSense AI"

    # OTP Settings
    OTP_EXPIRE_MINUTES: int = 10

    # ── RAG / LLM Settings ─────────────────────────────────────
    LLM_PROVIDER: str = "groq"
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Embeddings — Hugging Face Inference API (free, no local model, Vercel-safe)
    HF_API_TOKEN: Optional[str] = None  # optional — public models work without a token
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSIONS: int = 384

    # RAG tuning
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 200
    TOP_K: int = 8
    RELEVANCE_THRESHOLD: float = 0.25

    # Treat empty strings as None for optional fields
    @field_validator(
        "SMTP_USER", "SMTP_PASSWORD", "GOOGLE_MAPS_API_KEY",
        "GROQ_API_KEY", "HF_API_TOKEN",
        "SUPABASE_URL", "SUPABASE_SERVICE_KEY",
        mode="before",
    )
    @classmethod
    def empty_str_to_none(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()
