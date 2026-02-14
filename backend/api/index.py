# Vercel serverless entry point
# This file is the single entry point for all API routes on Vercel.

import sys
import os

# Ensure the backend directory is on the Python path
# so that `from app.main import handler` works regardless
# of whether Vercel root is repo-root or backend/
backend_dir = os.path.join(os.path.dirname(__file__), "..")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import handler  # mangum handler wrapping the FastAPI app
