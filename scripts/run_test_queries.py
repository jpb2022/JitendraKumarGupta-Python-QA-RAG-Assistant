"""Run manual integration tests and save results."""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
DELAY_SECONDS = float(sys.argv[2]) if len(sys.argv) > 2 else 35.0

QUERIES = [
    "How do I read a CSV file using pandas?",
    "What is the difference between a list and a tuple in Python?",
    "How do I handle missing values in a pandas DataFrame?",
    "Explain Python list comprehensions with an example.",
    "How do I install packages with pip?",
    "What is a Python decorator and how do I create one?",
    "How do I merge two DataFrames in pandas?",
    "What is the GIL in Python?",
    "How do I catch exceptions in Python?",
    "How do I convert a string to an integer safely?",
][:8]

OUTPUT = Path(__file__).resolve().parent.parent / "test_results" / "test_results.json"


def main() -> None:
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "base_url": BASE_URL,
        "health": None,
        "queries": [],
    }

    with httpx.Client(timeout=120.0) as client:
        health = client.get(f"{BASE_URL}/health")
        results["health"] = health.json()

        for question in QUERIES:
            entry = {"question": question, "status_code": None, "answer": None, "sources": [], "error": None}
            try:
                response = client.post(f"{BASE_URL}/ask", json={"question": question})
                entry["status_code"] = response.status_code
                if response.status_code == 200:
                    payload = response.json()
                    entry["answer"] = payload.get("answer")
                    entry["sources"] = payload.get("sources", [])
                else:
                    entry["error"] = response.text
            except Exception as exc:
                entry["error"] = str(exc)
            results["queries"].append(entry)
            print(f"Done: {question[:60]}...")
            if question != QUERIES[-1]:
                time.sleep(DELAY_SECONDS)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Saved results to {OUTPUT}")


if __name__ == "__main__":
    main()
