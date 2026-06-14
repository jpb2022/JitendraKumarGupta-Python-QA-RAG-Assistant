"""Quick direct RAG tests (no HTTP server needed)."""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.rag.pipeline import ask_question, is_index_ready  # noqa: E402

QUERIES = [
    "How do I read a CSV file using pandas?",
    "What is the difference between a list and a tuple in Python?",
    "How do I handle missing values in a pandas DataFrame?",
    "Explain Python list comprehensions with an example.",
    "How do I install packages with pip?",
    "What is a Python decorator and how do I create one?",
    "How do I merge two DataFrames in pandas?",
    "What is the GIL in Python?",
]

OUTPUT = PROJECT_ROOT / "test_results" / "test_results.json"


def main() -> None:
    if not is_index_ready():
        print("Run: python scripts/ingest_data.py")
        sys.exit(1)

    results = {"timestamp": datetime.now(timezone.utc).isoformat(), "mode": "direct", "queries": []}
    for i, q in enumerate(QUERIES):
        entry = {"question": q, "status_code": 200, "answer": None, "sources": [], "error": None}
        try:
            r = ask_question(q)
            entry["answer"] = r["answer"]
            entry["sources"] = r["sources"]
        except Exception as exc:
            entry["status_code"] = 500
            entry["error"] = str(exc)
        results["queries"].append(entry)
        print(f"[{i+1}/8] OK" if entry["answer"] else f"[{i+1}/8] FAIL")
        if i < len(QUERIES) - 1:
            time.sleep(5)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    main()
