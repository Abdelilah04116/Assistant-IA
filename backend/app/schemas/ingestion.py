"""
Pydantic schemas for document ingestion.
"""

from typing import List, Dict, Any, Optional
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
import bleach


class DocumentIngestRequest(BaseModel):
    """Request schema for document ingestion."""
    filename: str = Field(..., description="Name of the uploaded file")
    file_type: str = Field(..., description="Type of file (pdf, txt, md)")
    chunk_size: Optional[int] = Field(1000, description="Text chunk size")
    chunk_overlap: Optional[int] = Field(200, description="Overlap between chunks")
    chunk_overlap: Optional[int] = Field(200, description="Overlap between chunks")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional document metadata")

    @field_validator('filename')
    def sanitize_filename(cls, v):
        return bleach.clean(v, strip=True)


class DocumentChunk(BaseModel):
    """Schema for a document chunk."""
    chunk_id: str = Field(..., description="Unique chunk identifier")
    content: str = Field(..., description="Chunk content")
    metadata: Dict[str, Any] = Field(..., description="Chunk metadata")


class IngestionResult(BaseModel):
    """Result of document ingestion."""
    filename: str = Field(..., description="Original filename")
    chunks_created: int = Field(..., description="Number of chunks created")
    processing_time: float = Field(..., description="Processing time in seconds")
    file_size: int = Field(..., description="File size in bytes")
    success: bool = Field(..., description="Whether ingestion was successful")
    error: Optional[str] = Field(None, description="Error message if any")


class BatchIngestionRequest(BaseModel):
    """Request schema for batch document ingestion."""
    documents: List[DocumentIngestRequest] = Field(..., description="List of documents to ingest")
    parallel_processing: Optional[bool] = Field(True, description="Whether to process in parallel")


class BatchIngestionResult(BaseModel):
    """Result of batch document ingestion."""
    total_documents: int = Field(..., description="Total documents processed")
    successful_ingestions: int = Field(..., description="Number of successful ingestions")
    failed_ingestions: int = Field(..., description="Number of failed ingestions")
    total_chunks_created: int = Field(..., description="Total chunks created across all documents")
    processing_time: float = Field(..., description="Total processing time in seconds")
    results: List[IngestionResult] = Field(..., description="Individual document results")


class CollectionStats(BaseModel):
    """Statistics about the document collection."""
    vector_store_type: str = Field(..., description="Type of vector store used")
    total_documents: int = Field(..., description="Total number of documents")
    total_chunks: int = Field(..., description="Total number of chunks")
    storage_size: Optional[int] = Field(None, description="Storage size in bytes")
    last_updated: str = Field(..., description="Last update timestamp")


class DeleteCollectionRequest(BaseModel):
    """Request schema for deleting the entire collection."""
    confirmation: str = Field(..., description="Confirmation text 'DELETE_ALL' required")


class SearchRequest(BaseModel):
    """Request schema for document search."""
    query: str = Field(..., description="Search query")
    k: Optional[int] = Field(5, description="Number of results to return")
    k: Optional[int] = Field(5, description="Number of results to return")
    rerank: Optional[bool] = Field(False, description="Whether to apply reranking")

    @field_validator('query')
    def sanitize_query(cls, v):
        return bleach.clean(v, strip=True)


class SearchResult(BaseModel):
    """Schema for a single search result."""
    content: str = Field(..., description="Document content")
    metadata: Dict[str, Any] = Field(..., description="Document metadata")
    score: float = Field(..., description="Similarity score")
    chunk_id: str = Field(..., description="Chunk identifier")


class SearchResponse(BaseModel):
    """Response schema for document search."""
    query: str = Field(..., description="Original search query")
    results: List[SearchResult] = Field(..., description="Search results")
    total_found: int = Field(..., description="Total number of results found")
    processing_time: float = Field(..., description="Search processing time in seconds")
