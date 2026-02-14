#!/usr/bin/env bash
# Render start script — ensures correct port binding
PORT="${PORT:-10000}"
echo "🚀 Starting PoisonSense-AI backend on port $PORT"
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
