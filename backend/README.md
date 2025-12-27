# Decarceration Lab RAG API

FastAPI backend for the RAG document analysis system.

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up Environment

Create a `.env` file from the template:

```bash
# Windows
copy env.template .env

# Mac/Linux
cp env.template .env
```

Then edit `.env` and add your Portkey API key:

```
PORTKEY_API_KEY=your_key_here
```

### 3. Run the Server

```bash
# Development mode (with auto-reload)
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### 4. View API Documentation

Open `http://localhost:8000/docs` for interactive Swagger documentation.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check and status |
| `/api/query` | POST | Query documents with natural language |
| `/api/upload` | POST | Upload a document for indexing |
| `/api/documents` | GET | List all indexed documents |

## Project Structure

```
backend/
├── main.py              # FastAPI app entry point
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── env.template         # Environment template
├── api/
│   ├── routes.py        # API route handlers
│   └── schemas.py       # Pydantic request/response models
├── rag/
│   ├── pipeline.py      # Main RAG orchestrator
│   ├── text_processor.py    # Text chunking
│   ├── document_processor.py # PDF/DOCX/TXT parsing
│   ├── index_builder.py     # FAISS index management
│   ├── retriever.py         # Semantic search
│   └── llm_gateway.py       # Portkey LLM integration
├── data/                # Stored index files (auto-created)
└── uploads/             # Temporary upload storage (auto-created)
```

## Running with Frontend

Start both servers:

```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

The frontend at `http://localhost:3000` will proxy `/api/*` requests to the backend.

## Deployment

### Railway / Render

1. Set environment variable: `PORTKEY_API_KEY`
2. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Docker (optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PORTKEY_API_KEY` | Yes | Your Portkey API key for LLM access |
| `LLM_MODEL` | No | Override default LLM model |
| `CORS_ORIGINS` | No | Comma-separated allowed origins |

