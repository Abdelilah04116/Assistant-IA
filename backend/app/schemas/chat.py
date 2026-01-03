"""
Pydantic schemas for chat and query processing.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""
    query: str = Field(..., description="User query or question")
    session_id: Optional[str] = Field(None, description="Session ID for conversation tracking")
    max_documents: Optional[int] = Field(5, description="Maximum documents to retrieve")
    include_web_search: Optional[bool] = Field(True, description="Include web search in research")
    style_preferences: Optional[Dict[str, Any]] = Field(None, description="Writing style preferences")


class Citation(BaseModel):
    """Citation information schema."""
    id: int = Field(..., description="Citation ID")
    title: str = Field(..., description="Source title")
    source_type: str = Field(..., description="Type of source (internal/web)")
    relevance_score: float = Field(..., description="Relevance score")
    citation_info: Dict[str, Any] = Field(..., description="Detailed citation information")
    in_text_reference: str = Field(..., description="In-text reference format")


class QualityScore(BaseModel):
    """Quality assessment schema."""
    overall_score: int = Field(..., description="Overall quality score (0-100)")
    metrics: Dict[str, Any] = Field(..., description="Quality metrics")
    assessment: str = Field(..., description="Quality assessment text")


class AnswerMetadata(BaseModel):
    """Metadata about the generated answer."""
    query: str = Field(..., description="Original query")
    sources_used: int = Field(..., description="Number of sources used")
    word_count: int = Field(..., description="Word count of answer")
    generation_timestamp: str = Field(..., description="Timestamp of generation")


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    query: str = Field(..., description="Original query")
    answer: str = Field(..., description="Generated answer")
    citations: List[Citation] = Field(..., description="List of citations")
    metadata: Dict[str, Any] = Field(..., description="Response metadata")
    error: Optional[str] = Field(None, description="Error message if any")
    success: bool = Field(..., description="Whether the request was successful")


class WorkflowMetadata(BaseModel):
    """Workflow execution metadata."""
    workflow_id: str = Field(..., description="Unique workflow identifier")
    processing_time: float = Field(..., description="Processing time in seconds")
    steps_completed: List[Optional[str]] = Field(..., description="Completed workflow steps")
    sources_used: int = Field(..., description="Number of sources used")
    quality_score: int = Field(..., description="Answer quality score")


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    timestamp: str = Field(..., description="Error timestamp")


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    uptime: float = Field(..., description="Service uptime in seconds")
    components: Dict[str, str] = Field(..., description="Component status")
