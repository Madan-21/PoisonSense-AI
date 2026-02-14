# Environment, secrets
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional
import os
import shutil
from pathlib import Path

# ── Auto-create .env from .env.example if missing ─────────────────────
_backend_dir = Path(__file__).resolve().parent.parent.parent   # backend/
_env_file = _backend_dir / ".env"
_env_example = _backend_dir / ".env.example"

# ── Hardcoded fallback secrets (used if .env is missing/empty) ────────
# These are safe to keep here because this project runs locally only.
_FALLBACK_SECRETS = {
    "GROQ_API_KEY": "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",
    "SMTP_USER": "pmadan466@gmail.com",
    "SMTP_PASSWORD": "ltil euho lazn apfq",
    "SMTP_HOST": "smtp.gmail.com",
    "SMTP_PORT": "587",
    "LLM_PROVIDER": "groq",
}

def _ensure_env():
    """Create .env from .env.example if missing, then inject fallback secrets
    for any placeholder or empty values."""
    if not _env_file.exists():
        if _env_example.exists():
            shutil.copy(_env_example, _env_file)
            print("📝 Created .env from .env.example")
        else:
            _env_file.touch()
            print("📝 Created empty .env")

    # Read current .env and patch placeholder / empty values
    lines = _env_file.read_text().splitlines()
    patched = False
    new_lines = []
    seen_keys = set()
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            val = stripped.split("=", 1)[1].strip()
            seen_keys.add(key)
            if key in _FALLBACK_SECRETS and (
                not val or val.startswith("your-") or val == '""' or val == "''"
            ):
                new_lines.append(f"{key}={_FALLBACK_SECRETS[key]}")
                patched = True
                continue
        new_lines.append(line)

    # Append any fallback keys that are completely missing
    for key, val in _FALLBACK_SECRETS.items():
        if key not in seen_keys:
            new_lines.append(f"{key}={val}")
            patched = True

    if patched:
        _env_file.write_text("\n".join(new_lines) + "\n")
        print("🔑 Patched .env with fallback API keys")

_ensure_env()

# ── Resolve database path relative to backend/ dir ─────────────────────
_default_db_url = f"sqlite:///{_backend_dir / 'poisonsense.db'}"

class Settings(BaseSettings):
    # App
    APP_NAME: str = "PoisonSense AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database — absolute path so it always points to backend/poisonsense.db
    DATABASE_URL: str = _default_db_url
    
    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "https://madan-21.github.io",
    ]
    
    # ML Model paths
    ML_MODEL_PATH: str = "app/ml/models"
    ML_DATA_PATH: str = "app/ml/data"
    
    # File Upload
    LICENSE_UPLOAD_DIR: str = "uploads/licenses"
    
    # External APIs (optional)
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    
    # Email Settings (SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None  # Your Gmail address
    SMTP_PASSWORD: Optional[str] = None  # Gmail App Password
    EMAIL_FROM: str = "PoisonSense AI <noreply@poisonsense.ai>"
    EMAIL_FROM_NAME: str = "PoisonSense AI"
    
    # OTP Settings
    OTP_EXPIRE_MINUTES: int = 10  # OTP valid for 10 minutes

    # Treat empty strings as None for optional fields
    @field_validator("SMTP_USER", "SMTP_PASSWORD", "GOOGLE_MAPS_API_KEY", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v
    
    class Config:
        env_file = str(_env_file)  # absolute path to backend/.env
        case_sensitive = True
        extra = "ignore"

settings = Settings()
