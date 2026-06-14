"""RAG pipeline for Python Q&A."""

from __future__ import annotations

import time
from functools import lru_cache

from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from app.config import get_settings

SYSTEM_PROMPT = """You are a helpful Python programming tutor for data science learners.
Answer the user's question using ONLY the provided Stack Overflow context.
If the context does not contain enough information, say so clearly and provide general Python guidance.
Always include a short code example when relevant.
Cite the question title from the context when possible."""

USER_PROMPT = """Context from Stack Overflow:
{context}

Question: {question}

Provide a clear, accurate, grounded answer:"""


def _format_docs(docs) -> str:
    parts = []
    for i, doc in enumerate(docs, start=1):
        title = doc.metadata.get("title", "Unknown")
        parts.append(f"[{i}] {title}\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


@lru_cache
def get_vectorstore() -> Chroma:
    settings = get_settings()
    embeddings = GoogleGenerativeAIEmbeddings(
        model=settings.gemini_embedding_model,
        google_api_key=settings.google_api_key,
    )
    return Chroma(
        collection_name=settings.collection_name,
        embedding_function=embeddings,
        persist_directory=str(settings.chroma_path),
    )


def get_retriever():
    settings = get_settings()
    return get_vectorstore().as_retriever(search_kwargs={"k": settings.top_k})


def build_rag_chain():
    settings = get_settings()
    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=0.2,
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", USER_PROMPT),
        ]
    )
    retriever = get_retriever()

    chain = (
        {
            "context": retriever | _format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain


def ask_question(question: str, *, max_retries: int = 3) -> dict:
    retriever = get_retriever()
    source_docs = retriever.invoke(question)
    chain = build_rag_chain()

    last_error = None
    for attempt in range(max_retries):
        try:
            answer = chain.invoke(question)
            break
        except Exception as exc:
            last_error = exc
            message = str(exc)
            if "429" in message or "ResourceExhausted" in message:
                wait_seconds = 35 * (attempt + 1)
                time.sleep(wait_seconds)
                continue
            raise
    else:
        raise last_error  # type: ignore[misc]

    sources = [
        {
            "title": doc.metadata.get("title", ""),
            "question_id": doc.metadata.get("question_id"),
            "score": doc.metadata.get("score"),
        }
        for doc in source_docs
    ]
    return {"question": question, "answer": answer, "sources": sources}


def is_index_ready() -> bool:
    settings = get_settings()
    return settings.chroma_path.exists() and any(settings.chroma_path.iterdir())
