"""
API Routes
===========
FastAPI route definitions.
"""

import logging
import shutil
import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, BackgroundTasks

from .schemas import (
    QueryRequest, QueryResponse, Citation,
    UploadResponse, DocumentInfo, DocumentListResponse,
    HealthResponse
)
from ..rag import RAGPipeline
from ..config import Config, get_config

logger = logging.getLogger("api.routes")

# Create router
router = APIRouter()

# Global pipeline instance (initialized in main.py)
_pipeline: RAGPipeline = None


def get_pipeline() -> RAGPipeline:
    """Dependency to get the RAG pipeline."""
    if _pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    return _pipeline


def set_pipeline(pipeline: RAGPipeline):
    """Set the global pipeline instance."""
    global _pipeline
    _pipeline = pipeline


# ============================================================================
# Health & Status
# ============================================================================

@router.get("/health", response_model=HealthResponse, tags=["Status"])
async def health_check(pipeline: RAGPipeline = Depends(get_pipeline)):
    """Check the health status of the API."""
    return HealthResponse(
        status="healthy",
        index_ready=pipeline.is_ready,
        document_count=pipeline.document_count,
        supported_types=pipeline.supported_file_types
    )


# ============================================================================
# Query Endpoint
# ============================================================================

@router.post("/query", response_model=QueryResponse, tags=["Query"])
async def query_documents(
    request: QueryRequest,
    pipeline: RAGPipeline = Depends(get_pipeline)
):
    """
    Query the indexed documents using natural language.
    
    The system will:
    1. Search for relevant document chunks
    2. Use the LLM to generate an answer based on the context
    3. Return the answer with citations
    """
    try:
        result = pipeline.query(
            question=request.query,
            k=request.k,
            filters=request.filters
        )
        
        citations = [Citation(**c) for c in result.citations]
        
        return QueryResponse(
            answer=result.answer,
            citations=citations,
            success=result.success,
            error=result.error
        )
        
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Document Upload
# ============================================================================

@router.post("/upload", response_model=UploadResponse, tags=["Documents"])
async def upload_document(
    file: UploadFile = File(...),
    config: Config = Depends(get_config),
    pipeline: RAGPipeline = Depends(get_pipeline)
):
    """
    Upload a document for indexing.
    
    Supported formats: PDF, DOCX, TXT
    Maximum size: 50MB
    """
    # Validate file type
    suffix = Path(file.filename).suffix.lower()
    if suffix not in pipeline.supported_file_types:
        return UploadResponse(
            success=False,
            error=f"Unsupported file type: {suffix}. Supported: {pipeline.supported_file_types}"
        )
    
    # Validate file size (50MB max)
    max_size = 50 * 1024 * 1024
    content = await file.read()
    if len(content) > max_size:
        return UploadResponse(
            success=False,
            error=f"File too large. Maximum size: 50MB"
        )
    
    # Save to temp file
    temp_filename = f"{uuid.uuid4()}{suffix}"
    temp_path = Path(config.uploads_dir) / temp_filename
    
    try:
        with open(temp_path, "wb") as f:
            f.write(content)
        
        # Process and index
        result = pipeline.process_and_index_file(
            file_path=temp_path,
            original_filename=file.filename,
            save=True
        )
        
        return UploadResponse(
            success=True,
            document=DocumentInfo(
                document_id=result["document_id"],
                filename=result["filename"],
                chunks=result["chunks"],
                char_count=result["char_count"],
                status="ready"
            )
        )
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        return UploadResponse(
            success=False,
            error=str(e)
        )
        
    finally:
        # Clean up temp file
        if temp_path.exists():
            temp_path.unlink()


@router.get("/documents", response_model=DocumentListResponse, tags=["Documents"])
async def list_documents(pipeline: RAGPipeline = Depends(get_pipeline)):
    """List all indexed documents."""
    
    if not pipeline.is_ready:
        return DocumentListResponse(documents=[], total_chunks=0)
    
    # Get unique documents from metadata
    seen_docs = {}
    for meta in pipeline.index_builder.metadata:
        doc_id = meta.get("document_id")
        if doc_id and doc_id not in seen_docs:
            seen_docs[doc_id] = {
                "document_id": doc_id,
                "filename": meta.get("filename", "Unknown"),
                "chunks": meta.get("total_chunks", 1),
                "char_count": meta.get("char_count", 0),
                "status": "ready"
            }
    
    documents = [DocumentInfo(**doc) for doc in seen_docs.values()]
    
    return DocumentListResponse(
        documents=documents,
        total_chunks=pipeline.document_count
    )


@router.delete("/documents/{document_id}", tags=["Documents"])
async def delete_document(document_id: str):
    """
    Delete a document from the index.
    
    Note: This is not yet implemented. Deleting from FAISS requires rebuilding the index.
    """
    raise HTTPException(
        status_code=501, 
        detail="Document deletion not yet implemented. Requires index rebuild."
    )

