"""Data ingestion for Stack Overflow Python Q&A."""

from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Iterable

import pandas as pd
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

from app.config import PROJECT_ROOT, get_settings


def clean_html(text: str) -> str:
    if not isinstance(text, str) or not text.strip():
        return ""
    if "<" not in text and ">" not in text:
        return re.sub(r"\s+", " ", text).strip()
    soup = BeautifulSoup(text, "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()
    cleaned = soup.get_text(separator=" ")
    cleaned = html.unescape(cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _load_kaggle_csvs(data_dir: Path) -> pd.DataFrame | None:
    questions_path = data_dir / "Questions.csv"
    answers_path = data_dir / "Answers.csv"
    if not questions_path.exists() or not answers_path.exists():
        return None

    questions = pd.read_csv(questions_path, encoding="latin-1", low_memory=False)
    answers = pd.read_csv(answers_path, encoding="latin-1", low_memory=False)

    merged = questions.merge(
        answers,
        left_on="Id",
        right_on="ParentId",
        suffixes=("_question", "_answer"),
    )
    merged = merged.sort_values("Score_answer", ascending=False)
    merged = merged.drop_duplicates(subset=["Id"], keep="first")
    return merged


def _load_bundled_sample(limit: int) -> pd.DataFrame:
    sample_path = PROJECT_ROOT / "data" / "sample" / "sample_qa.json"
    if not sample_path.exists():
        raise FileNotFoundError(
            "No Kaggle CSVs found and bundled sample missing. "
            "Run: python scripts/create_sample_data.py "
            "or download Kaggle data to data/raw/."
        )
    records = pd.read_json(sample_path)
    return records.head(limit)


def build_documents(df: pd.DataFrame) -> list[Document]:
    documents: list[Document] = []
    for _, row in df.iterrows():
        title = clean_html(str(row.get("Title", "")))
        question_body = clean_html(str(row.get("Body_question", row.get("Body", ""))))
        answer_body = clean_html(str(row.get("Body_answer", "")))
        if not answer_body:
            continue

        page_content = (
            f"Question: {title}\n\n"
            f"Question details: {question_body}\n\n"
            f"Answer: {answer_body}"
        )
        if len(page_content) < 80:
            continue

        documents.append(
            Document(
                page_content=page_content[:8000],
                metadata={
                    "question_id": int(row["Id"]),
                    "title": title[:200],
                    "score": int(row.get("Score_answer", 0) or 0),
                    "source": "stackoverflow_python",
                },
            )
        )
    return documents


def load_qa_documents(
    *,
    limit: int = 3000,
    data_dir: Path | None = None,
) -> list[Document]:
    data_dir = data_dir or PROJECT_ROOT / "data" / "raw"
    df = _load_kaggle_csvs(data_dir)
    if df is None:
        df = _load_bundled_sample(limit)
    else:
        df = df.head(limit)
    return build_documents(df)


def ingest_to_chroma(
    documents: Iterable[Document],
    *,
    reset: bool = True,
) -> Chroma:
    settings = get_settings()
    persist_dir = settings.chroma_path
    persist_dir.mkdir(parents=True, exist_ok=True)

    if reset and persist_dir.exists():
        import shutil

        shutil.rmtree(persist_dir, ignore_errors=True)
        persist_dir.mkdir(parents=True, exist_ok=True)

    embeddings = GoogleGenerativeAIEmbeddings(
        model=settings.gemini_embedding_model,
        google_api_key=settings.google_api_key,
    )

    docs = list(documents)
    if not docs:
        raise ValueError("No documents available for ingestion.")

    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=settings.collection_name,
        persist_directory=str(persist_dir),
    )
    return vectorstore
