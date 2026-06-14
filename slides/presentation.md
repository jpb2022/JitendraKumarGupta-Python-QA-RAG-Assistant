# Python Q&A Assistant — Presentation

**Analytics Vidhya AI Engineer Assessment**

---

## Slide 1: Title

**Python Programming Q&A Assistant**

RAG-powered learning tool for data science learners

- Stack Overflow Python Q&A corpus
- Google Gemini + LangChain + ChromaDB
- FastAPI REST API

---

## Slide 2: Problem & Goal

**Problem:** Learners need accurate, grounded Python answers—not hallucinated code.

**Goal:** Build a retrieval-augmented Q&A system that:
- Answers any Python-related query
- Grounds responses in real Stack Overflow discussions
- Exposes a production-ready REST API

---

## Slide 3: Architecture

```mermaid
flowchart LR
    User[User / Client] --> API[FastAPI]
    API --> Retriever[ChromaDB Retriever]
    Retriever --> Context[Top-K Documents]
    Context --> LLM[Gemini 2.0 Flash]
    LLM --> Answer[Grounded Answer + Sources]
```

**Components:**
- Ingestion: CSV → HTML cleaning → chunked documents → embeddings
- Retrieval: semantic search (top-k=4)
- Generation: Gemini with strict system prompt

---

## Slide 4: Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **RAG over fine-tuning** | Faster to build, always updatable with new SO data |
| **ChromaDB** | Lightweight, persistent, no external DB for MVP |
| **Gemini Flash** | Low latency, cost-effective for Q&A |
| **Score-sorted answers** | Prefer highest-voted accepted answers |
| **Source citations** | Transparency for learners |

---

## Slide 5: Data Pipeline

1. Load Kaggle `Questions.csv` + `Answers.csv` (or HF fallback)
2. Merge on question ID, dedupe, sort by answer score
3. Strip HTML from SO posts
4. Embed with `text-embedding-004`
5. Store in ChromaDB (~1,500 Q&A pairs for demo)

---

## Slide 6: API Design

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Liveness + index status |
| `/ask` | POST | Question → answer + sources |

- Pydantic validation (3–2000 chars)
- 503 when index missing
- OpenAPI docs at `/docs`

---

## Slide 7: Testing Strategy

- **Unit tests:** health, validation, 503 without index
- **Integration tests:** 10 diverse Python queries
- **Edge cases tested:**
  - Very short input (422)
  - Out-of-domain questions (graceful fallback)
  - Missing index (503)

Results documented in `test_results/test_results.json`

---

## Slide 8: Sample Results

Queries tested include pandas CSV reading, decorators, GIL, exception handling.

**Quality observations:**
- Strong on common library questions (pandas, pip)
- Retrieves relevant SO threads with titles
- Occasionally verbose; prompt tuning would help
- Out-of-domain queries get honest "insufficient context" responses

---

## Slide 9: Scaling to 100+ Concurrent Users

**Latency:**
- Async FastAPI endpoints
- Connection pooling for Chroma / move to managed vector DB (Pinecone, Qdrant)
- Cache frequent queries (Redis, TTL 1h)

**Infrastructure:**
- Horizontal scaling behind load balancer
- Separate ingestion workers from API pods
- Pre-warm embedding model connections

**Cost:**
- Gemini Flash for generation; batch embeddings offline
- Rate limiting + request queuing
- Smaller `top_k` for speed-critical paths

---

## Slide 10: Future Improvements

- Hybrid search (BM25 + semantic)
- Re-ranking retrieved chunks
- User feedback loop for answer quality
- Streaming responses (SSE)
- Admin endpoint to refresh index incrementally
- Multi-language support

**Thank you**
