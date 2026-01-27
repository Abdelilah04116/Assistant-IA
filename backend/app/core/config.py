"""
Configuration management for the intelligent research assistant.
Handles environment variables and application settings.
"""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)
    
    # Security Configuration
    secret_key: str = Field(default="dev_secret_key", env="SECRET_KEY")
    rate_limit: str = Field(default="60/minute", env="RATE_LIMIT")
    
    # Google Gemini Configuration
    google_api_key: str = Field(..., env="GOOGLE_API_KEY")
    
    # Vector Store Configuration
    vector_store_type: str = Field(default="chroma", env="VECTOR_STORE_TYPE")
    chroma_persist_directory: str = Field(default="./data/vector_store", env="CHROMA_PERSIST_DIRECTORY")
    faiss_index_path: str = Field(default="./data/vector_store/faiss.index", env="FAISS_INDEX_PATH")
    
    # Embedding Configuration
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", 
        env="EMBEDDING_MODEL"
    )
    embedding_device: str = Field(default="cpu", env="EMBEDDING_DEVICE")
    
    # Document Processing
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    max_documents_per_query: int = Field(default=5, env="MAX_DOCUMENTS_PER_QUERY")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # CORS Configuration
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"], 
        env="ALLOWED_ORIGINS"
    )
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
# Global settings instance
settings = Settings()
