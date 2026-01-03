"""
Retrieval module for the RAG pipeline.
Handles document retrieval and ranking for query processing.
"""

import asyncio
from typing import List, Dict, Any, Optional
import numpy as np

from .document_processor import EmbeddingGenerator
from .vector_store import get_vector_store, VectorStore
from ..core import get_logger, settings

logger = get_logger(__name__)


class DocumentRetriever:
    """
    Handles document retrieval using embeddings and vector similarity search.
    Supports both dense retrieval and optional reranking.
    """
    
    def __init__(self):
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = get_vector_store()
        self.max_documents = settings.max_documents_per_query
        logger.info("Initialized DocumentRetriever")
    
    async def retrieve(
        self, 
        query: str, 
        k: Optional[int] = None,
        rerank: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a given query.
        
        Args:
            query: User query string
            k: Number of documents to retrieve (defaults to settings)
            rerank: Whether to apply reranking
            
        Returns:
            List of retrieved documents with scores and metadata
        """
        if k is None:
            k = self.max_documents
        
        try:
            logger.info(f"Retrieving documents for query: {query[:100]}...")
            
            # Generate query embedding
            query_embedding = await self.embedding_generator.generate_single_embedding(query)
            
            if not query_embedding:
                logger.warning("Failed to generate query embedding")
                return []
            
            # Retrieve similar documents
            documents = await self.vector_store.similarity_search(
                query_embedding=query_embedding,
                k=k
            )
            
            # Apply reranking if requested
            if rerank and len(documents) > 1:
                documents = await self._rerank_documents(query, documents)
            
            # Filter out documents with very low similarity scores
            filtered_documents = [
                doc for doc in documents 
                if doc.get("score", 0) > 0.1  # Threshold for relevance
            ]
            
            logger.info(f"Retrieved {len(filtered_documents)} relevant documents")
            return filtered_documents
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            raise
    
    async def _rerank_documents(
        self, 
        query: str, 
        documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents based on query relevance.
        Uses a simple keyword-based reranking for now.
        
        Args:
            query: Original query
            documents: List of retrieved documents
            
        Returns:
            Reranked list of documents
        """
        try:
            # Extract keywords from query (simple approach)
            query_terms = set(query.lower().split())
            
            # Calculate relevance scores for each document
            reranked_docs = []
            for doc in documents:
                content = doc.get("content", "").lower()
                
                # Count term matches
                term_matches = sum(1 for term in query_terms if term in content)
                
                # Calculate term density
                term_density = term_matches / len(query_terms) if query_terms else 0
                
                # Combine with original similarity score
                original_score = doc.get("score", 0)
                combined_score = 0.7 * original_score + 0.3 * term_density
                
                doc_copy = doc.copy()
                doc_copy["rerank_score"] = combined_score
                reranked_docs.append(doc_copy)
            
            # Sort by combined score
            reranked_docs.sort(key=lambda x: x["rerank_score"], reverse=True)
            
            logger.info(f"Reranked {len(documents)} documents")
            return reranked_docs
            
        except Exception as e:
            logger.error(f"Error reranking documents: {str(e)}")
            return documents  # Return original documents if reranking fails
    
    async def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of documents to add
        """
        if not documents:
            return
        
        try:
            # Generate embeddings for all documents
            texts = [doc["content"] for doc in documents]
            embeddings = await self.embedding_generator.generate_embeddings(texts)
            
            # Add embeddings to documents
            for i, doc in enumerate(documents):
                doc["embedding"] = embeddings[i]
            
            # Add to vector store
            await self.vector_store.add_documents(documents)
            
            logger.info(f"Added {len(documents)} documents to vector store")
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise
    
    async def get_document_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific document by its chunk ID.
        
        Args:
            chunk_id: Unique identifier for the document chunk
            
        Returns:
            Document if found, None otherwise
        """
        try:
            # This is a simplified implementation
            # In a production system, you might want to maintain an index
            # for efficient ID-based lookups
            
            # For now, we'll use a similarity search with a dummy embedding
            # and filter by chunk_id
            dummy_embedding = [0.0] * 384  # Default embedding dimension
            
            documents = await self.vector_store.similarity_search(
                query_embedding=dummy_embedding,
                k=1000  # Retrieve many to find the specific one
            )
            
            for doc in documents:
                if doc.get("chunk_id") == chunk_id:
                    return doc
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving document by ID: {str(e)}")
            return None
    
    async def delete_all_documents(self) -> None:
        """Delete all documents from the vector store."""
        try:
            await self.vector_store.delete_collection()
            logger.info("Deleted all documents from vector store")
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            raise
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the document collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            # This is a simplified implementation
            # In practice, you'd want to maintain these stats separately
            
            dummy_embedding = [0.0] * 384
            documents = await self.vector_store.similarity_search(
                query_embedding=dummy_embedding,
                k=1  # Just to check if collection exists
            )
            
            return {
                "vector_store_type": settings.vector_store_type,
                "status": "active" if documents else "empty"
            }
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {
                "vector_store_type": settings.vector_store_type,
                "status": "error",
                "error": str(e)
            }
