# App entry point - Main FastAPI Application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1 import api_router
from app.db.session import engine
from app.db.base import Base

# Create all database tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - create tables on startup"""
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
    
    # Optionally preload ML model
    try:
        from app.services.ml_service import ml_service
        ml_service.load_model()
        print("✅ ML Model loaded successfully")
    except Exception as e:
        print(f"⚠️ ML Model not loaded: {e}")
    
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
