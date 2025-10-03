from __future__ import annotations

import sys
from pathlib import Path

from langchain.schema import Document
from .rag_chain import load_text_files, build_index

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m app.ingest <data_path>")
        raise SystemExit(1)
    data_path = Path(sys.argv[1]).resolve()
    if not data_path.exists():
        print(f"Path not found: {data_path}")
        raise SystemExit(1)

    docs = load_text_files([data_path])
    if not docs:
        print("No .txt or .md files found to ingest.")
        raise SystemExit(1)

    build_index(docs)
    print(f"Indexed {len(docs)} chunks. Index saved in storage/faiss_index/.")

if __name__ == "__main__":
    main()
