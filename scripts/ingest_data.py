"""Ingest Stack Overflow Python Q&A into ChromaDB."""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.rag.ingest import ingest_to_chroma, load_qa_documents  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest Stack Overflow data into ChromaDB")
    parser.add_argument("--limit", type=int, default=1500, help="Max Q&A pairs to ingest")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "raw",
        help="Directory containing Questions.csv and Answers.csv from Kaggle",
    )
    parser.add_argument("--no-reset", action="store_true", help="Do not wipe existing index")
    args = parser.parse_args()

    print(f"Loading up to {args.limit} Q&A pairs...")
    documents = load_qa_documents(limit=args.limit, data_dir=args.data_dir)
    print(f"Prepared {len(documents)} documents.")

    print("Building vector index (this may take several minutes)...")
    ingest_to_chroma(documents, reset=not args.no_reset)
    print("Ingestion complete.")


if __name__ == "__main__":
    main()
