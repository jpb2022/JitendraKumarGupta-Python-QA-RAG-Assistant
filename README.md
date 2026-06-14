# Python Programming Q&A Assistant

AI-powered RAG system that answers Python programming questions using Stack Overflow Q&A data and Google Gemini.

## Live Demo

> Deploy using Render/Railway/Hugging Face and add your URL here.

## Features

- **RAG pipeline** — LangChain + ChromaDB + Google Gemini embeddings & chat
- **FastAPI REST API** — `POST /ask` and `GET /health`
- **Stack Overflow data** — Kaggle [Python Questions](https://www.kaggle.com/datasets/stackoverflow/pythonquestions) or Hugging Face fallback sample
- **Automated tests** — pytest suite + integration query runner

## Architecture

```
User → FastAPI (/ask) → Retriever (ChromaDB) → Gemini LLM → Grounded Answer
                              ↑
                    Stack Overflow Q&A index
```

## Setup

### 1. Clone and install

```bash
git clone <your-repo-url>
cd Assignment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and set GOOGLE_API_KEY
```

### 3. Prepare data (optional — auto-fallback)

Download from Kaggle and place in `data/raw/`:

- `Questions.csv`
- `Answers.csv`

```bash
kaggle datasets download -d stackoverflow/pythonquestions -p data/raw --unzip
```

If Kaggle files are missing, ingestion uses a Hugging Face Stack Overflow sample filtered for Python tags.

### 4. Build the vector index

```bash
python scripts/ingest_data.py --limit 1500
```

### 5. Run the API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://127.0.0.1:8000/docs for Swagger UI.

## API Endpoints

### `GET /health`

```json
{"status": "ok", "index_ready": true}
```

### `POST /ask`

**Request:**

```json
{"question": "How do I read a CSV file using pandas?"}
```

**Response:**

```json
{
  "question": "How do I read a CSV file using pandas?",
  "answer": "...",
  "sources": [{"title": "...", "question_id": 123, "score": 45}]
}
```

## Testing

```bash
pytest tests/ -v
```

Run 10 integration queries (server must be running):

```bash
python scripts/run_test_queries.py http://127.0.0.1:8000
```

Results are saved to `test_results/test_results.json`.

## Deployment (Render / Railway)

1. Push repo to GitHub
2. Set `GOOGLE_API_KEY` in platform environment variables
3. Build command: `pip install -r requirements.txt && python scripts/ingest_data.py --limit 1000`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Or use the included `Dockerfile`.

## Project Structure

```
app/
  main.py           # FastAPI app
  config.py         # Settings
  rag/
    ingest.py       # Data loading & indexing
    pipeline.py     # RAG chain
scripts/
  ingest_data.py    # CLI ingestion
  run_test_queries.py
tests/
  test_api.py
test_results/
slides/
  presentation.md
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GOOGLE_API_KEY` | Google Gemini API key |
| `GEMINI_MODEL` | Chat model (default: `gemini-2.0-flash`) |
| `GEMINI_EMBEDDING_MODEL` | Embedding model |
| `CHROMA_PERSIST_DIR` | Vector store path |
| `TOP_K` | Retrieved documents count |

## License

Assessment project for Analytics Vidhya AI Engineer role.
