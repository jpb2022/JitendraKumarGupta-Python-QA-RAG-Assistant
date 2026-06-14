"""API tests for Python Q&A Assistant."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("GOOGLE_API_KEY", "test-key-for-unit-tests")

from app.main import app  # noqa: E402
from app.rag.pipeline import is_index_ready  # noqa: E402

client = TestClient(app)

MOCK_ANSWER = {
    "question": "test",
    "answer": "Use pandas.read_csv('file.csv') to load a CSV file.",
    "sources": [{"title": "How to read a CSV file using pandas", "question_id": 1, "score": 99}],
}


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "index_ready" in data
    assert data["status"] in ("ok", "degraded")


def test_ask_validation_empty_question():
    response = client.post("/ask", json={"question": "ab"})
    assert response.status_code == 422


def test_ask_without_index_returns_503():
    if is_index_ready():
        pytest.skip("Index exists; skipping 503 test")
    response = client.post("/ask", json={"question": "How do I use list comprehensions?"})
    assert response.status_code == 503


@pytest.mark.skipif(not is_index_ready(), reason="Vector index not built")
@patch("app.main.ask_question", return_value=MOCK_ANSWER)
def test_ask_returns_answer(_mock):
    response = client.post(
        "/ask",
        json={"question": "How do I read a CSV file using pandas?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["answer"]) > 20
    assert isinstance(data["sources"], list)


@pytest.mark.skipif(not is_index_ready(), reason="Vector index not built")
@patch("app.main.ask_question", return_value=MOCK_ANSWER)
def test_ask_includes_sources(_mock):
    response = client.post(
        "/ask",
        json={"question": "What is a Python decorator?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["sources"]) >= 1
    assert "title" in data["sources"][0]
