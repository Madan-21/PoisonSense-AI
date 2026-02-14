#!/usr/bin/env bash
# Render Build Script — installs CPU-only PyTorch (smaller) then other deps
set -o errexit

echo "📦 Installing CPU-only PyTorch first (smaller than GPU version)..."
pip install torch --index-url https://download.pytorch.org/whl/cpu

echo "📦 Installing remaining dependencies..."
pip install -r requirements.txt
