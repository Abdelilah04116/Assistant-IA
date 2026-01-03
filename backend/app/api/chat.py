"""
Chat API endpoints for the intelligent research assistant.
Handles user queries and orchestrates the multi-agent workflow.
"""

import time
import uuid
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse

from ..agents import AgentOrchestrator
from ..core import get_logger
from ..schemas import ChatRequest, ChatResponse, ErrorResponse

logger = get_logger(__name__)

# Initialize router
router = APIRouter(prefix="/chat", tags=["chat"])

# Initialize orchestrator (singleton)
orchestrator = AgentOrchestrator()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a user query through the multi-agent workflow.
    
    Args:
        request: Chat request containing query and options
        
    Returns:
        Chat response with answer and citations
    """
    try:
        logger.info(f"Received chat request: {request.query[:100]}...")
        
        # Generate workflow ID
        workflow_id = request.session_id or str(uuid.uuid4())
        
        # Process query through orchestrator
        result = await orchestrator.process_query(
            query=request.query,
            workflow_id=workflow_id
        )
        
        # Convert to response model
        response = ChatResponse(
            query=result["query"],
            answer=result["answer"],
            citations=[
                {
                    "id": citation.get("id", 0),
                    "title": citation.get("title", ""),
                    "source_type": citation.get("source_type", ""),
                    "relevance_score": citation.get("relevance_score", 0.0),
                    "citation_info": citation.get("citation_info", {}),
                    "in_text_reference": citation.get("in_text_reference", "")
                }
                for citation in result.get("citations", [])
            ],
            metadata=result.get("metadata", {}),
            error=result.get("error"),
            success=result.get("success", False)
        )
        
        logger.info(f"Chat request completed successfully for workflow: {workflow_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/status/{workflow_id}")
async def get_workflow_status(workflow_id: str) -> Dict[str, Any]:
    """
    Get the status of a workflow execution.
    
    Args:
        workflow_id: Workflow ID to check
        
    Returns:
        Workflow status information
    """
    try:
        status = await orchestrator.get_workflow_status(workflow_id)
        return status
        
    except Exception as e:
        logger.error(f"Error getting workflow status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving workflow status: {str(e)}"
        )


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat response for real-time interaction.
    Note: This is a simplified streaming implementation.
    In production, you'd want to implement proper streaming from each agent.
    
    Args:
        request: Chat request
        
    Returns:
        Streaming response
    """
    async def generate_response():
        try:
            workflow_id = str(uuid.uuid4())
            
            # Send initial status
            yield f"data: {json.dumps({'type': 'start', 'workflow_id': workflow_id})}\n\n"
            
            # Process the query
            result = await orchestrator.process_query(
                query=request.query,
                workflow_id=workflow_id
            )
            
            # Send final result
            yield f"data: {json.dumps({'type': 'result', 'data': result})}\n\n"
            yield f"data: {json.dumps({'type': 'end'})}\n\n"
            
        except Exception as e:
            error_data = {
                'type': 'error',
                'error': str(e)
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.delete("/sessions/{session_id}")
async def clear_session(session_id: str) -> Dict[str, str]:
    """
    Clear session data (placeholder for session management).
    
    Args:
        session_id: Session ID to clear
        
    Returns:
        Confirmation message
    """
    # In a real implementation, you'd clear session data from storage
    logger.info(f"Clearing session: {session_id}")
    return {"message": f"Session {session_id} cleared successfully"}
