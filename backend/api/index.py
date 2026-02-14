# Vercel serverless entry point
# This file is the single entry point for all API routes on Vercel.

from app.main import handler  # mangum handler wrapping the FastAPI app
