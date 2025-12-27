"""
Pydantic Schemas
=================
Request and response models for the API.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ============================================================================
# Query Schemas
# ============================================================================

class QueryRequest(BaseModel):
    """Request body for document queries."""
    query: str = Field(..., min_length=1, max_length=2000, description="The question to ask")
    k: Optional[int] = Field(None, ge=1, le=20, description="Number of documents to retrieve")
    filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the main themes in the uploaded documents?",
                "k": 4
            }
        }


class Citation(BaseModel):
    """A citation reference."""
    index: int
    document_id: str
    filename: str
    chunk: str
    score: float


class QueryResponse(BaseModel):
    """Response from a query."""
    answer: str
    citations: List[Citation]
    success: bool
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Based on the documents...",
                "citations": [
                    {
                        "index": 1,
                        "document_id": "abc123",
                        "filename": "research.pdf",
                        "chunk": "1/5",
                        "score": 0.85
                    }
                ],
                "success": True,
                "error": None
            }
        }


# ============================================================================
# Document Schemas
# ============================================================================

class DocumentInfo(BaseModel):
    """Information about an indexed document."""
    document_id: str
    filename: str
    chunks: int
    char_count: int
    status: str = "ready"


class UploadResponse(BaseModel):
    """Response from document upload."""
    success: bool
    document: Optional[DocumentInfo] = None
    error: Optional[str] = None


class DocumentListResponse(BaseModel):
    """List of all indexed documents."""
    documents: List[DocumentInfo]
    total_chunks: int


# ============================================================================
# Status Schemas
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    index_ready: bool
    document_count: int
    supported_types: List[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "index_ready": True,
                "document_count": 150,
                "supported_types": [".txt", ".pdf", ".docx"]
            }
        }

