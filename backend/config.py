"""
Configuration & Environment Setup
==================================
Centralized configuration for the RAG system.
"""

import os
import logging
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
from functools import lru_cache

# ============================================================================
# LOGGING SETUP
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("rag")


@dataclass
class Config:
    """Central configuration for the RAG system."""
    
    # Data paths
    data_dir: str = "./data"
    uploads_dir: str = "./uploads"
    index_filename: str = "index.faiss"
    metadata_filename: str = "metadata.json"
    
    # Embedding model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384
    
    # Chunking parameters
    chunk_size: int = 512
    chunk_overlap: int = 128
    
    # Retrieval parameters
    retrieval_k: int = 4
    max_context_chars: int = 3000
    
    # LLM configuration
    llm_model: str = "@first-integrati-db9427/gemini-2.5-flash-lite"
    llm_max_tokens: int = 512
    
    # API keys
    portkey_api_key: Optional[str] = field(default=None, repr=False)
    
    # Server settings
    cors_origins: list = field(default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"])
    
    @property
    def index_path(self) -> Path:
        return Path(self.data_dir) / self.index_filename
    
    @property
    def metadata_path(self) -> Path:
        return Path(self.data_dir) / self.metadata_filename
    
    @property
    def uploads_path(self) -> Path:
        return Path(self.uploads_dir)
    
    def load_api_keys(self):
        """Load API keys from environment variables."""
        self.portkey_api_key = os.getenv('PORTKEY_API_KEY')
        
        if not self.portkey_api_key:
            logger.warning("⚠️ No PORTKEY_API_KEY found in environment variables")
        else:
            logger.info("✓ Loaded Portkey API key from environment")
    
    def ensure_directories(self):
        """Create required directories if they don't exist."""
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        Path(self.uploads_dir).mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Data directory: {self.data_dir}")
        logger.info(f"✓ Uploads directory: {self.uploads_dir}")
    
    def validate(self) -> bool:
        """Validate configuration."""
        if not self.portkey_api_key:
            logger.warning("API key missing - LLM calls will fail")
            return False
        return True


@lru_cache()
def get_config() -> Config:
    """Get singleton config instance."""
    config = Config()
    config.load_api_keys()
    config.ensure_directories()
    return config

