# rag/ingest_pdfs.py

import os
from backend.services.rag_service import ingest_pdf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE_DIR, "pdfs")

def main():
    if not os.path.exists(PDF_DIR):
        print(f"PDF directory not found: {PDF_DIR}")
        return

    for fname in os.listdir(PDF_DIR):
        if not fname.lower().endswith(".pdf"):
            continue
        path = os.path.join(PDF_DIR, fname)
        print(f"Ingesting: {path}")
        ingest_pdf(path, metadata={"category": "faq"})
    print("Done.")

if __name__ == "__main__":
    main()
