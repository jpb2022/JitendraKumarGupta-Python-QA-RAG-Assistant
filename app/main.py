"""FastAPI application for Python Q&A Assistant."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.rag.pipeline import ask_question, is_index_ready


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=2000, examples=["How do I read a CSV file in pandas?"])


class SourceItem(BaseModel):
    title: str
    question_id: Optional[int] = None
    score: Optional[int] = None


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceItem]


class HealthResponse(BaseModel):
    status: str
    index_ready: bool


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Python Programming Q&A Assistant",
    description="RAG-powered assistant for Python questions using Stack Overflow data.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    ready = is_index_ready()
    return HealthResponse(
        status="ok" if ready else "degraded",
        index_ready=ready,
    )


@app.post("/ask", response_model=AskResponse)
async def ask(payload: AskRequest) -> AskResponse:
    if not is_index_ready():
        raise HTTPException(
            status_code=503,
            detail="Vector index not ready. Run scripts/ingest_data.py first.",
        )
    try:
        result = ask_question(payload.question)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {exc}") from exc
    return AskResponse(**result)
