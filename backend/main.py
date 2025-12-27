"""
NYC Police Accountability RAG API
===================================
FastAPI server for the RAG document analysis system.

Run with:
    uvicorn main:app --reload --port 8000
    
Or:
    python main.py
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_config, logger
from rag import RAGPipeline
from api.routes import router, set_pipeline

# ============================================================================
# Application Lifespan
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown logic."""
    config = get_config()
    
    logger.info("=" * 60)
    logger.info("Starting RAG API Server")
    logger.info("=" * 60)
    
    # Initialize the RAG pipeline
    pipeline = RAGPipeline(
        embedding_model=config.embedding_model,
        embedding_dim=config.embedding_dim,
        llm_api_key=config.portkey_api_key,
        llm_model=config.llm_model,
        llm_max_tokens=config.llm_max_tokens,
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap,
        retrieval_k=config.retrieval_k,
        max_context_chars=config.max_context_chars,
        index_path=str(config.index_path),
        metadata_path=str(config.metadata_path)
    )
    
    # Set the pipeline for routes
    set_pipeline(pipeline)
    
    logger.info(f"Pipeline ready: {pipeline.is_ready}")
    logger.info(f"Indexed documents: {pipeline.document_count}")
    logger.info(f"Supported file types: {pipeline.supported_file_types}")
    logger.info("=" * 60)
    
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down RAG API Server")


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Decarceration Lab RAG API",
    description="""
Document Study & Reference API powered by RAG (Retrieval-Augmented Generation).

## Features

- **Document Upload**: Upload PDF, DOCX, or TXT files for indexing
- **Semantic Search**: Query documents using natural language
- **AI-Powered Answers**: Get answers generated from your document corpus

## Usage

1. Upload documents via `/api/upload`
2. Query your documents via `/api/query`
3. Check status via `/api/health`
    """,
    version="1.0.0",
    lifespan=lifespan
)

# ============================================================================
# CORS Middleware
# ============================================================================

config = get_config()

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins + ["*"],  # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Routes
# ============================================================================

# Include API routes with /api prefix
app.include_router(router, prefix="/api")


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Decarceration Lab RAG API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


# ============================================================================
# Run with Python directly
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

