"""
Pydantic schemas for API request/response models.
"""

from .chat import (
    ChatRequest,
    ChatResponse,
    Citation,
    QualityScore,
    AnswerMetadata,
    WorkflowMetadata,
    ErrorResponse,
    HealthResponse
)

from .ingestion import (
    DocumentIngestRequest,
    DocumentChunk,
    IngestionResult,
    BatchIngestionRequest,
    BatchIngestionResult,
    CollectionStats,
    DeleteCollectionRequest,
    SearchRequest,
    SearchResult,
    SearchResponse
)

__all__ = [
    # Chat schemas
    "ChatRequest",
    "ChatResponse", 
    "Citation",
    "QualityScore",
    "AnswerMetadata",
    "WorkflowMetadata",
    "ErrorResponse",
    "HealthResponse",
    
    # Ingestion schemas
    "DocumentIngestRequest",
    "DocumentChunk",
    "IngestionResult",
    "BatchIngestionRequest",
    "BatchIngestionResult",
    "CollectionStats",
    "DeleteCollectionRequest",
    "SearchRequest",
    "SearchResult",
    "SearchResponse"
]
