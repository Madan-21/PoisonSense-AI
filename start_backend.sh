#!/bin/bash
# PoisonSense AI — Backend Start Script
# Starts the FastAPI backend with the RAG chatbot

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"

cd "$BACKEND_DIR"

echo "═══════════════════════════════════════════"
echo "  PoisonSense AI — Backend Server"
echo "═══════════════════════════════════════════"

# Check for .env
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "📝 Created .env — please set your GROQ_API_KEY in backend/.env"
    else
        echo "❌ No .env.example found either. Create backend/.env with your API keys."
        exit 1
    fi
fi

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet 2>&1 | tail -1

echo ""
echo "🚀 Starting server on http://localhost:8000"
echo "📚 API docs at http://localhost:8000/docs"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
