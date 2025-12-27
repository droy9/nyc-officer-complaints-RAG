"""
Embedding & Index Building
===========================
Handles embedding generation and FAISS index management.
"""

import json
import logging
import time
from pathlib import Path
from typing import List, Optional

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

logger = logging.getLogger("rag.index_builder")


class IndexBuilder:
    """Builds and manages the FAISS vector index."""
    
    def __init__(self, embedding_model: str, embedding_dim: int):
        self.embedding_model_name = embedding_model
        self.embedding_dim = embedding_dim
        self.model: Optional[SentenceTransformer] = None
        self.index: Optional[faiss.Index] = None
        self.metadata: List[dict] = []
    
    def load_embedding_model(self) -> SentenceTransformer:
        """Load the embedding model (lazy loading)."""
        if self.model is None:
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.model = SentenceTransformer(self.embedding_model_name)
            logger.info("✓ Embedding model loaded")
        return self.model
    
    def embed_documents(
        self, 
        documents: List[str], 
        batch_size: int = 256,
        show_progress: bool = True
    ) -> np.ndarray:
        """Embed documents in batches for memory efficiency."""
        model = self.load_embedding_model()
        
        all_embeddings = []
        total_batches = (len(documents) + batch_size - 1) // batch_size
        
        start_time = time.time()
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            if show_progress and batch_num % 10 == 0:
                elapsed = time.time() - start_time
                rate = i / elapsed if elapsed > 0 else 0
                logger.info(
                    f"Embedding batch {batch_num}/{total_batches} "
                    f"({rate:.0f} docs/sec)"
                )
            
            embeddings = model.encode(
                batch,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False
            )
            all_embeddings.append(embeddings)
        
        result = np.vstack(all_embeddings)
        
        elapsed = time.time() - start_time
        logger.info(
            f"✓ Embedded {len(documents)} documents in {elapsed:.1f}s "
            f"({len(documents)/elapsed:.0f} docs/sec)"
        )
        
        return result
    
    def embed_query(self, query: str) -> np.ndarray:
        """Embed a single query."""
        model = self.load_embedding_model()
        return model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        ).astype(np.float32)
    
    def build_index(
        self, 
        documents: List[str], 
        metadata: List[dict],
        use_ivf: bool = False,
        nlist: int = 100
    ) -> faiss.Index:
        """Build a FAISS index from documents."""
        if len(documents) != len(metadata):
            raise ValueError(
                f"Document count ({len(documents)}) != metadata count ({len(metadata)})"
            )
        
        # Generate embeddings
        embeddings = self.embed_documents(documents)
        dim = embeddings.shape[1]
        
        # Create index
        if use_ivf and len(documents) > 10000:
            logger.info(f"Building IVF index with {nlist} clusters")
            quantizer = faiss.IndexFlatIP(dim)
            self.index = faiss.IndexIVFFlat(quantizer, dim, nlist)
            self.index.train(embeddings)
            self.index.nprobe = min(10, nlist)
        else:
            logger.info("Building Flat index (exact search)")
            self.index = faiss.IndexFlatIP(dim)
        
        # Add embeddings
        self.index.add(embeddings.astype(np.float32))
        self.metadata = metadata
        
        logger.info(f"✓ Built index with {self.index.ntotal} vectors")
        
        return self.index
    
    def add_documents(self, documents: List[str], metadata: List[dict]):
        """Add new documents to an existing index."""
        if self.index is None:
            # Create new index
            return self.build_index(documents, metadata)
        
        # Embed new documents
        embeddings = self.embed_documents(documents)
        
        # Add to index
        self.index.add(embeddings.astype(np.float32))
        self.metadata.extend(metadata)
        
        logger.info(f"✓ Added {len(documents)} documents. Total: {self.index.ntotal}")
    
    def save(self, index_path: str, metadata_path: str):
        """Save index and metadata to disk."""
        if self.index is None:
            raise ValueError("No index to save. Call build_index() first.")
        
        Path(index_path).parent.mkdir(parents=True, exist_ok=True)
        
        faiss.write_index(self.index, str(index_path))
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata, f)
        
        logger.info(f"✓ Saved index to {index_path}")
        logger.info(f"✓ Saved metadata to {metadata_path}")
    
    def load(self, index_path: str, metadata_path: str) -> bool:
        """Load index and metadata from disk."""
        try:
            self.index = faiss.read_index(str(index_path))
            with open(metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            
            logger.info(
                f"✓ Loaded index with {self.index.ntotal} vectors "
                f"and {len(self.metadata)} metadata entries"
            )
            return True
            
        except FileNotFoundError as e:
            logger.warning(f"Index files not found: {e}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted metadata file: {e}")
            self.index = None
            self.metadata = []
            return False
        except PermissionError as e:
            logger.error(f"Permission denied accessing index files: {e}")
            return False
        except Exception as e:
            # Catch FAISS errors and other unexpected issues
            logger.error(f"Failed to load index: {type(e).__name__}: {e}")
            self.index = None
            self.metadata = []
            return False
    
    @property
    def is_ready(self) -> bool:
        """Check if index is loaded and ready."""
        return self.index is not None and self.index.ntotal > 0
    
    @property
    def document_count(self) -> int:
        """Return number of indexed documents."""
        return self.index.ntotal if self.index else 0

