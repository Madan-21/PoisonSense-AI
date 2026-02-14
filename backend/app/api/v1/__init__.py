# API v1 module
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.poison_analysis import router as analysis_router
from app.api.v1.hospitals import router as hospitals_router
from app.api.v1.poison_centers import router as centers_router
from app.api.v1.doctors import router as doctors_router
from app.api.v1.antidotes import router as antidotes_router
from app.api.v1.toxicology_labs import router as labs_router
from app.api.v1.poison_syndromes import router as syndromes_router
from app.api.v1.blog import router as blog_router
from app.api.v1.blog_community import router as blog_community_router
from app.api.v1.admin import router as admin_router
from app.api.v1.dashboards import router as dashboards_router
from app.api.v1.rag_chatbot import router as rag_router

api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(analysis_router)
api_router.include_router(hospitals_router)
api_router.include_router(centers_router)
api_router.include_router(doctors_router)
api_router.include_router(antidotes_router)
api_router.include_router(labs_router)
api_router.include_router(syndromes_router)  # Poison syndromes/toxidromes
api_router.include_router(blog_router)  # Blog submissions
api_router.include_router(blog_community_router)  # Blog community features
api_router.include_router(admin_router)  # Admin user management
api_router.include_router(dashboards_router)  # Role-based dashboards
api_router.include_router(rag_router)  # RAG Chatbot (replaces old chatbot + agentic_ai)

