#!/usr/bin/env python3
"""
Ingest PDFs into the deployed PoisonSense-AI backend.
Uploads each PDF to the /api/v1/rag/ingest endpoint.

Usage:
    python3 ingest_remote.py https://poison-sense-ai.vercel.app ./Pdf\'s/
"""

import sys
import os
import requests
from pathlib import Path


def ingest_pdfs(api_url: str, pdf_dir: str):
    """Upload all PDFs from pdf_dir to the deployed backend."""
    endpoint = f"{api_url.rstrip('/')}/api/v1/rag/ingest"
    pdf_path = Path(pdf_dir)

    if not pdf_path.exists():
        print(f"❌ Directory not found: {pdf_dir}")
        sys.exit(1)

    pdfs = sorted(pdf_path.glob("*.pdf"))
    if not pdfs:
        print(f"❌ No PDFs found in: {pdf_dir}")
        sys.exit(1)

    print(f"📁 Found {len(pdfs)} PDFs in {pdf_dir}")
    print(f"🌐 Target: {endpoint}\n")

    for i, pdf in enumerate(pdfs, 1):
        print(f"[{i}/{len(pdfs)}] Uploading: {pdf.name} ({pdf.stat().st_size // 1024} KB)...")
        try:
            with open(pdf, "rb") as f:
                resp = requests.post(
                    endpoint,
                    files=[("files", (pdf.name, f, "application/pdf"))],
                    data={"collection": "toxicology"},
                    timeout=120,  # PDFs can take a while
                )
            if resp.status_code == 200:
                result = resp.json()
                for r in result.get("results", []):
                    if "error" in r:
                        print(f"  ⚠️  Error: {r['error']}")
                    else:
                        print(f"  ✅ {r.get('doc_title', pdf.name)} → {r.get('chunks_created', '?')} chunks")
            else:
                print(f"  ❌ HTTP {resp.status_code}: {resp.text[:200]}")
        except requests.exceptions.Timeout:
            print(f"  ⏰ Timeout — file may be too large for serverless. Skipping.")
        except Exception as e:
            print(f"  ❌ Error: {e}")

    print("\n🎉 Ingestion complete! Check /api/v1/rag/collections for stats.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 ingest_remote.py <API_URL> <PDF_DIR>")
        print("Example: python3 ingest_remote.py https://poison-sense-ai.vercel.app ./Pdf's/")
        sys.exit(1)

    ingest_pdfs(sys.argv[1], sys.argv[2])
