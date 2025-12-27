"""
Text Processing & Chunking
===========================
Utilities for preparing text for embedding.
"""

import hashlib
import logging
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger("rag.text_processor")


@dataclass
class ProcessedDocument:
    """A processed document ready for indexing."""
    source_type: str
    document_id: str
    filename: str
    chunks: List[str]
    metadata: Dict[str, Any]


class TextProcessor:
    """Handles text chunking and preprocessing for the RAG pipeline."""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 128):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        text = str(text).strip()
        
        if len(text) <= self.chunk_size:
            return [text] if text else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary if possible
            if end < len(text):
                for punct in ['. ', '! ', '? ', '\n']:
                    last_punct = chunk.rfind(punct)
                    if last_punct > self.chunk_size * 0.5:
                        chunk = chunk[:last_punct + 1]
                        end = start + len(chunk)
                        break
            
            # Only append non-empty chunks after stripping
            stripped_chunk = chunk.strip()
            if stripped_chunk:
                chunks.append(stripped_chunk)
            
            if end >= len(text):
                break
            
            start = end - self.chunk_overlap
        
        return chunks
    
    def prepare_for_indexing(
        self, 
        documents: List[ProcessedDocument]
    ) -> Tuple[List[str], List[dict]]:
        """
        Prepare documents and metadata for indexing.
        
        Returns:
            Tuple of (text_chunks, metadata_list)
        """
        all_chunks = []
        all_metadata = []
        
        for doc in documents:
            for chunk_idx, chunk in enumerate(doc.chunks):
                # Prepend document info to each chunk for context
                text = f"[{doc.source_type}:{doc.document_id}]\n\n{chunk}"
                all_chunks.append(text)
                
                meta = {
                    "source_type": doc.source_type,
                    "document_id": doc.document_id,
                    "filename": doc.filename,
                    "chunk_idx": chunk_idx,
                    "total_chunks": len(doc.chunks),
                    "content": text,
                    **doc.metadata
                }
                all_metadata.append(meta)
        
        logger.info(f"Prepared {len(all_chunks)} chunks from {len(documents)} documents")
        return all_chunks, all_metadata
    
    @staticmethod
    def compute_hash(text: str) -> str:
        """Compute MD5 hash of text for cache keys."""
        return hashlib.md5(text.encode()).hexdigest()[:12]

