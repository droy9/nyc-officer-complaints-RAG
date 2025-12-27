"""
RAG Pipeline Orchestrator
==========================
Main orchestrator that ties together all RAG components.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional, List

from .text_processor import TextProcessor, ProcessedDocument
from .document_processor import DocumentProcessor
from .index_builder import IndexBuilder
from .retriever import Retriever, RetrievalResult
from .llm_gateway import LLMGateway, LLMResponse, SYSTEM_PROMPTS

logger = logging.getLogger("rag.pipeline")


@dataclass
class RAGResponse:
    """Complete response from the RAG pipeline."""
    answer: str
    citations: List[dict]
    sources: List[dict]
    llm_response: dict
    success: bool = True
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "answer": self.answer,
            "citations": self.citations,
            "sources": self.sources,
            "llm": self.llm_response,
            "success": self.success,
            "error": self.error
        }


class RAGPipeline:
    """Main orchestrator for the RAG system."""
    
    def __init__(
        self,
        embedding_model: str,
        embedding_dim: int,
        llm_api_key: Optional[str],
        llm_model: str,
        llm_max_tokens: int = 512,
        chunk_size: int = 512,
        chunk_overlap: int = 128,
        retrieval_k: int = 4,
        max_context_chars: int = 3000,
        index_path: Optional[str] = None,
        metadata_path: Optional[str] = None
    ):
        # Initialize components
        self.text_processor = TextProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        self.document_processor = DocumentProcessor(self.text_processor)
        
        self.index_builder = IndexBuilder(
            embedding_model=embedding_model,
            embedding_dim=embedding_dim
        )
        
        self.retriever = Retriever(
            index_builder=self.index_builder,
            retrieval_k=retrieval_k,
            max_context_chars=max_context_chars
        )
        
        self.llm_gateway = LLMGateway(
            api_key=llm_api_key,
            model=llm_model,
            max_tokens=llm_max_tokens
        )
        
        self.index_path = index_path
        self.metadata_path = metadata_path
        
        self._is_initialized = False
        
        # Try to load existing index
        if index_path and metadata_path:
            self.load_index()
    
    def load_index(self) -> bool:
        """Load existing index from disk."""
        if self.index_path and self.metadata_path:
            if Path(self.index_path).exists() and Path(self.metadata_path).exists():
                success = self.index_builder.load(self.index_path, self.metadata_path)
                if success:
                    self._is_initialized = True
                    logger.info("✓ Pipeline loaded from existing index")
                return success
        return False
    
    def save_index(self):
        """Save current index to disk."""
        if self.index_path and self.metadata_path:
            self.index_builder.save(self.index_path, self.metadata_path)
    
    def process_and_index_file(
        self, 
        file_path: Path, 
        original_filename: str,
        metadata: Optional[Dict[str, Any]] = None,
        save: bool = True
    ) -> dict:
        """
        Process a single file and add it to the index.
        
        Returns:
            Dict with document_id and chunk count
        """
        # Process file
        processed_doc = self.document_processor.process_file(
            file_path=file_path,
            original_filename=original_filename,
            metadata=metadata
        )
        
        # Prepare for indexing
        chunks, chunk_metadata = self.text_processor.prepare_for_indexing([processed_doc])
        
        # Add to index
        self.index_builder.add_documents(chunks, chunk_metadata)
        self._is_initialized = True
        
        # Save if requested
        if save and self.index_path and self.metadata_path:
            self.save_index()
        
        return {
            "document_id": processed_doc.document_id,
            "filename": processed_doc.filename,
            "chunks": len(processed_doc.chunks),
            "char_count": processed_doc.metadata.get("char_count", 0)
        }
    
    def query(
        self, 
        question: str, 
        k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        system_prompt_key: str = "default"
    ) -> RAGResponse:
        """Process a user query through the full RAG pipeline."""
        
        if not self._is_initialized:
            return RAGResponse(
                answer="No documents have been indexed yet. Please upload some documents first.",
                citations=[],
                sources=[],
                llm_response={},
                success=False,
                error="Pipeline not initialized - no documents indexed"
            )
        
        logger.info(f"Processing query: {question[:50]}...")
        
        # Retrieve relevant documents
        try:
            results = self.retriever.retrieve(question, k=k, filters=filters)
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return RAGResponse(
                answer="",
                citations=[],
                sources=[],
                llm_response={},
                success=False,
                error=f"Retrieval failed: {e}"
            )
        
        if not results:
            return RAGResponse(
                answer="No relevant information found in the indexed documents for your query.",
                citations=[],
                sources=[],
                llm_response={"content": "", "success": True},
                success=True
            )
        
        # Build context and generate response
        context_block = self.retriever.get_context_block(results)
        citations = self.retriever.get_citations(results)
        
        system_prompt = SYSTEM_PROMPTS.get(system_prompt_key, SYSTEM_PROMPTS["default"])
        
        user_prompt = (
            f"QUESTION: {question}\n\n"
            f"CONTEXT:\n{context_block}\n\n"
            f"Provide a comprehensive answer based on the context above. "
            f"Reference specific documents when possible."
        )
        
        llm_response = self.llm_gateway.generate(system_prompt, user_prompt)
        
        # Build source list
        sources = [r.to_dict() for r in results]
        
        return RAGResponse(
            answer=llm_response.content,
            citations=citations,
            sources=sources,
            llm_response=llm_response.to_dict(),
            success=llm_response.success,
            error=llm_response.error
        )
    
    @property
    def is_ready(self) -> bool:
        """Check if pipeline is ready to handle queries."""
        return self._is_initialized and self.index_builder.is_ready
    
    @property
    def document_count(self) -> int:
        """Return number of indexed document chunks."""
        return self.index_builder.document_count
    
    @property
    def supported_file_types(self) -> list:
        """Return list of supported file types."""
        return self.document_processor.supported_types

