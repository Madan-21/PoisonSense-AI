# Environment, secrets
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # App
    APP_NAME: str = "PoisonSense AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./poisonsense.db"
    
    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"]
    
    # ML Model paths
    ML_MODEL_PATH: str = "app/ml/models"
    ML_DATA_PATH: str = "app/ml/data"
    
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
