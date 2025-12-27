"""
Retrieval Engine
=================
Handles semantic search with caching, filtering, and metrics.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

import numpy as np

from .index_builder import IndexBuilder
from .text_processor import TextProcessor

logger = logging.getLogger("rag.retriever")


@dataclass
class RetrievalResult:
    """A single retrieval result with score and metadata."""
    score: float
    content: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "content": self.content,
            "metadata": self.metadata
        }


@dataclass
class RetrievalMetrics:
    """Metrics for a retrieval operation."""
    query: str
    num_results: int
    top_score: float
    avg_score: float
    retrieval_time_ms: float
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))


class Retriever:
    """Semantic retrieval engine with caching and filtering support."""
    
    def __init__(
        self, 
        index_builder: IndexBuilder, 
        retrieval_k: int = 4,
        max_context_chars: int = 3000
    ):
        self.index_builder = index_builder
        self.retrieval_k = retrieval_k
        self.max_context_chars = max_context_chars
        self._query_cache: Dict[str, np.ndarray] = {}
        self.metrics_history: List[RetrievalMetrics] = []
    
    def _embed_query(self, query: str) -> np.ndarray:
        """Embed a query with caching."""
        cache_key = TextProcessor.compute_hash(query)
        
        if cache_key not in self._query_cache:
            embedding = self.index_builder.embed_query(query)
            self._query_cache[cache_key] = embedding
            
            # Limit cache size
            if len(self._query_cache) > 1000:
                oldest_key = next(iter(self._query_cache))
                del self._query_cache[oldest_key]
        
        return self._query_cache[cache_key]
    
    def retrieve(
        self,
        query: str,
        k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        min_score: float = 0.0
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: The search query
            k: Number of results to return
            filters: Optional metadata filters
            min_score: Minimum similarity score threshold
            
        Returns:
            List of RetrievalResult objects sorted by score
        """
        k = k or self.retrieval_k
        start_time = time.time()
        
        if not self.index_builder.is_ready:
            logger.warning("Index not ready - returning empty results")
            return []
        
        # Embed query
        query_embedding = self._embed_query(query)
        
        # Search with over-retrieval if filtering
        search_k = k * 3 if filters else k
        distances, indices = self.index_builder.index.search(query_embedding, search_k)
        
        results = []
        for idx, score in zip(indices[0], distances[0]):
            if idx == -1:
                continue
            
            if score < min_score:
                continue
            
            metadata = self.index_builder.metadata[idx]
            
            # Apply filters
            if filters:
                match = all(
                    metadata.get(key) == value 
                    for key, value in filters.items()
                )
                if not match:
                    continue
            
            content = metadata.get("content", f"[Record: {metadata.get('document_id', idx)}]")
            
            results.append(RetrievalResult(
                score=float(score),
                content=content[:self.max_context_chars],
                metadata=metadata
            ))
            
            if len(results) >= k:
                break
        
        # Record metrics
        elapsed_ms = (time.time() - start_time) * 1000
        metrics = RetrievalMetrics(
            query=query[:100],
            num_results=len(results),
            top_score=results[0].score if results else 0.0,
            avg_score=sum(r.score for r in results) / len(results) if results else 0.0,
            retrieval_time_ms=elapsed_ms
        )
        self.metrics_history.append(metrics)
        
        logger.info(
            f"Retrieved {len(results)} results in {elapsed_ms:.1f}ms "
            f"(top score: {metrics.top_score:.3f})"
        )
        
        return results
    
    def get_context_block(
        self, 
        results: List[RetrievalResult],
        include_scores: bool = False
    ) -> str:
        """Format retrieval results as a context block for the LLM."""
        blocks = []
        for i, result in enumerate(results, 1):
            header = f"[{i}] Document: {result.metadata.get('filename', 'Unknown')}"
            if include_scores:
                header += f" (relevance: {result.score:.2f})"
            blocks.append(f"{header}\n{result.content}")
        
        return "\n\n---\n\n".join(blocks)
    
    def get_citations(self, results: List[RetrievalResult]) -> List[dict]:
        """Generate citation list for results."""
        citations = []
        for i, result in enumerate(results, 1):
            meta = result.metadata
            citations.append({
                "index": i,
                "document_id": meta.get("document_id", "N/A"),
                "filename": meta.get("filename", "Unknown"),
                "chunk": f"{meta.get('chunk_idx', 0)+1}/{meta.get('total_chunks', 1)}",
                "score": round(result.score, 3)
            })
        return citations
    
    def clear_cache(self):
        """Clear the query embedding cache."""
        self._query_cache.clear()
        logger.info("Query cache cleared")

