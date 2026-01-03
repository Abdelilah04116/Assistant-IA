"""
Document ingestion API endpoints.
Handles document upload, processing, and vector storage.
"""

import os
import time
import asyncio
from typing import List, Dict, Any
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse

from ..rag import DocumentProcessor, DocumentRetriever
from ..core import get_logger, settings
from ..schemas import (
    DocumentIngestRequest,
    IngestionResult,
    BatchIngestionResult,
    CollectionStats,
    DeleteCollectionRequest,
    SearchRequest,
    SearchResponse,
    SearchResult
)

logger = get_logger(__name__)

# Initialize router
router = APIRouter(prefix="/ingestion", tags=["ingestion"])

# Initialize components
document_processor = DocumentProcessor()
document_retriever = DocumentRetriever()


@router.post("/upload", response_model=IngestionResult)
async def upload_document(
    file: UploadFile = File(...),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    metadata: str = Form("{}")
) -> IngestionResult:
    """
    Upload and ingest a single document.
    
    Args:
        file: Uploaded file
        chunk_size: Text chunk size
        chunk_overlap: Overlap between chunks
        metadata: JSON string of additional metadata
        
    Returns:
        Ingestion result with statistics
    """
    try:
        start_time = time.time()
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Get file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in ['.pdf', '.txt', '.md']:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_extension}. Supported types: .pdf, .txt, .md"
            )
        
        # Save uploaded file temporarily
        temp_dir = "./data/temp"
        os.makedirs(temp_dir, exist_ok=True)
        temp_file_path = os.path.join(temp_dir, file.filename)
        
        try:
            # Save uploaded file
            with open(temp_file_path, "wb") as temp_file:
                content = await file.read()
                temp_file.write(content)
            
            # Parse metadata
            try:
                import json
                additional_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                additional_metadata = {}
            
            # Process document
            chunks = await document_processor.process_document(temp_file_path)
            
            # Add documents to vector store
            documents_to_add = []
            for chunk in chunks:
                doc = {
                    "content": chunk.content,
                    "metadata": {**chunk.metadata, **additional_metadata},
                    "chunk_id": chunk.chunk_id
                }
                documents_to_add.append(doc)
            
            await document_retriever.add_documents(documents_to_add)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            result = IngestionResult(
                filename=file.filename,
                chunks_created=len(chunks),
                processing_time=processing_time,
                file_size=len(content),
                success=True
            )
            
            logger.info(f"Successfully ingested {file.filename}: {len(chunks)} chunks")
            return result
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting document {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error ingesting document: {str(e)}"
        )


@router.post("/batch", response_model=BatchIngestionResult)
async def batch_upload(
    files: List[UploadFile] = File(...),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    parallel_processing: bool = Form(True)
) -> BatchIngestionResult:
    """
    Upload and ingest multiple documents.
    
    Args:
        files: List of uploaded files
        chunk_size: Text chunk size
        chunk_overlap: Overlap between chunks
        parallel_processing: Whether to process files in parallel
        
    Returns:
        Batch ingestion results
    """
    try:
        start_time = time.time()
        
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        results = []
        
        if parallel_processing:
            # Process files in parallel
            tasks = []
            for file in files:
                task = upload_document(file, chunk_size, chunk_overlap, "{}")
                tasks.append(task)
            
            # Wait for all tasks to complete
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    results.append(IngestionResult(
                        filename=files[i].filename,
                        chunks_created=0,
                        processing_time=0,
                        file_size=0,
                        success=False,
                        error=str(result)
                    ))
                else:
                    results.append(result)
        else:
            # Process files sequentially
            for file in files:
                try:
                    result = await upload_document(file, chunk_size, chunk_overlap, "{}")
                    results.append(result)
                except Exception as e:
                    results.append(IngestionResult(
                        filename=file.filename,
                        chunks_created=0,
                        processing_time=0,
                        file_size=0,
                        success=False,
                        error=str(e)
                    ))
        
        # Calculate batch statistics
        total_processing_time = time.time() - start_time
        successful_ingestions = sum(1 for r in results if r.success)
        failed_ingestions = len(results) - successful_ingestions
        total_chunks_created = sum(r.chunks_created for r in results)
        
        batch_result = BatchIngestionResult(
            total_documents=len(files),
            successful_ingestions=successful_ingestions,
            failed_ingestions=failed_ingestions,
            total_chunks_created=total_chunks_created,
            processing_time=total_processing_time,
            results=results
        )
        
        logger.info(f"Batch ingestion completed: {successful_ingestions}/{len(files)} successful")
        return batch_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch ingestion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error in batch ingestion: {str(e)}"
        )


@router.get("/stats", response_model=CollectionStats)
async def get_collection_stats() -> CollectionStats:
    """
    Get statistics about the document collection.
    
    Returns:
        Collection statistics
    """
    try:
        stats = await document_retriever.get_collection_stats()
        
        # This is a simplified implementation
        # In production, you'd want to track actual document counts
        collection_stats = CollectionStats(
            vector_store_type=stats.get("vector_store_type", "unknown"),
            total_documents=0,  # Would be tracked in production
            total_chunks=0,     # Would be tracked in production
            storage_size=None,  # Would be calculated in production
            last_updated=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        return collection_stats
        
    except Exception as e:
        logger.error(f"Error getting collection stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving collection stats: {str(e)}"
        )


@router.delete("/collection")
async def delete_collection(request: DeleteCollectionRequest) -> Dict[str, str]:
    """
    Delete the entire document collection.
    
    Args:
        request: Delete collection request with confirmation
        
    Returns:
        Confirmation message
    """
    try:
        if request.confirmation != "DELETE_ALL":
            raise HTTPException(
                status_code=400,
                detail="Confirmation must be exactly 'DELETE_ALL'"
            )
        
        await document_retriever.delete_all_documents()
        
        logger.info("Document collection deleted successfully")
        return {"message": "Document collection deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting collection: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting collection: {str(e)}"
        )


@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest) -> SearchResponse:
    """
    Search documents in the collection.
    
    Args:
        request: Search request with query and parameters
        
    Returns:
        Search results
    """
    try:
        start_time = time.time()
        
        # Retrieve documents
        documents = await document_retriever.retrieve(
            query=request.query,
            k=request.k,
            rerank=request.rerank
        )
        
        # Convert to response format
        results = []
        for doc in documents:
            result = SearchResult(
                content=doc.get("content", ""),
                metadata=doc.get("metadata", {}),
                score=doc.get("score", 0.0),
                chunk_id=doc.get("chunk_id", "")
            )
            results.append(result)
        
        processing_time = time.time() - start_time
        
        search_response = SearchResponse(
            query=request.query,
            results=results,
            total_found=len(results),
            processing_time=processing_time
        )
        
        logger.info(f"Search completed: {len(results)} results for query: {request.query[:50]}...")
        return search_response
        
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error searching documents: {str(e)}"
        )
