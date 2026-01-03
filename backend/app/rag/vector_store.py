"""
Vector store implementation for the RAG pipeline.
Supports both Chroma and FAISS for efficient similarity search.
"""

import os
import pickle
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

from ..core import get_logger, settings

logger = get_logger(__name__)


class VectorStore:
    """
    Abstract base class for vector store implementations.
    """
    
    async def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents to the vector store."""
        raise NotImplementedError
    
    async def similarity_search(
        self, 
        query_embedding: List[float], 
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        raise NotImplementedError
    
    async def delete_collection(self) -> None:
        """Delete the entire collection."""
        raise NotImplementedError


class ChromaVectorStore(VectorStore):
    """
    ChromaDB implementation of vector store.
    Provides persistent storage and efficient similarity search.
    """
    
    def __init__(self, collection_name: str = "documents"):
        if not CHROMA_AVAILABLE:
            raise ImportError("ChromaDB is not installed. Install with: pip install chromadb")
        
        self.collection_name = collection_name
        self.persist_directory = settings.chroma_persist_directory
        self.client = None
        self.collection = None
        
        # Ensure persist directory exists
        os.makedirs(self.persist_directory, exist_ok=True)
        
        self._initialize_client()
        logger.info(f"Initialized ChromaVectorStore with collection: {collection_name}")
    
    def _initialize_client(self):
        """Initialize ChromaDB client and collection."""
        try:
            # Create persistent client
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info(f"ChromaDB collection '{self.collection_name}' initialized")
            
        except Exception as e:
            logger.error(f"Error initializing ChromaDB client: {str(e)}")
            raise
    
    async def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to ChromaDB collection.
        
        Args:
            documents: List of documents with content, metadata, and embeddings
        """
        if not documents:
            return
        
        try:
            # Prepare data for ChromaDB
            ids = [doc.get("chunk_id", f"doc_{i}") for i, doc in enumerate(documents)]
            embeddings = [doc["embedding"] for doc in documents]
            contents = [doc["content"] for doc in documents]
            metadatas = [doc.get("metadata", {}) for doc in documents]
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=contents,
                metadatas=metadatas
            )
            
            logger.info(f"Added {len(documents)} documents to ChromaDB")
            
        except Exception as e:
            logger.error(f"Error adding documents to ChromaDB: {str(e)}")
            raise
    
    async def similarity_search(
        self, 
        query_embedding: List[float], 
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents in ChromaDB.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            List of similar documents with scores
        """
        try:
            # Query the collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k
            )
            
            # Format results
            documents = []
            for i in range(len(results["ids"][0])):
                distance = results["distances"][0][i]
                similarity = 1.0 - float(distance)
                doc = {
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score": similarity,
                    "distance": float(distance),
                    "chunk_id": results["ids"][0][i]
                }
                documents.append(doc)
            
            logger.info(f"Retrieved {len(documents)} documents from ChromaDB")
            return documents
            
        except Exception as e:
            logger.error(f"Error searching ChromaDB: {str(e)}")
            raise
    
    async def delete_collection(self) -> None:
        """Delete the ChromaDB collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted ChromaDB collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting ChromaDB collection: {str(e)}")
            raise


class FAISSVectorStore(VectorStore):
    """
    FAISS implementation of vector store.
    Provides high-performance similarity search for large datasets.
    """
    
    def __init__(self, dimension: int = 384, index_path: Optional[str] = None):
        if not FAISS_AVAILABLE:
            raise ImportError("FAISS is not installed. Install with: pip install faiss-cpu")
        
        self.dimension = dimension
        self.index_path = index_path or settings.faiss_index_path
        self.index = None
        self.documents = []
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        self._load_or_create_index()
        logger.info(f"Initialized FAISSVectorStore with dimension: {dimension}")
    
    def _load_or_create_index(self):
        """Load existing index or create new one."""
        try:
            if os.path.exists(self.index_path):
                # Load existing index
                self.index = faiss.read_index(self.index_path)
                
                # Load documents metadata
                metadata_path = self.index_path.replace('.index', '_metadata.pkl')
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'rb') as f:
                        self.documents = pickle.load(f)
                
                logger.info(f"Loaded existing FAISS index from {self.index_path}")
            else:
                # Create new index
                self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
                self.documents = []
                logger.info("Created new FAISS index")
                
        except Exception as e:
            logger.error(f"Error loading/creating FAISS index: {str(e)}")
            raise
    
    def _save_index(self):
        """Save index and metadata to disk."""
        try:
            # Save index
            faiss.write_index(self.index, self.index_path)
            
            # Save documents metadata
            metadata_path = self.index_path.replace('.index', '_metadata.pkl')
            with open(metadata_path, 'wb') as f:
                pickle.dump(self.documents, f)
            
            logger.info(f"Saved FAISS index to {self.index_path}")
            
        except Exception as e:
            logger.error(f"Error saving FAISS index: {str(e)}")
            raise
    
    async def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to FAISS index.
        
        Args:
            documents: List of documents with content, metadata, and embeddings
        """
        if not documents:
            return
        
        try:
            # Prepare embeddings
            embeddings = np.array([doc["embedding"] for doc in documents]).astype('float32')
            
            # Normalize embeddings for cosine similarity
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            embeddings = embeddings / norms
            
            # Add to index
            start_idx = len(self.documents)
            self.index.add(embeddings)
            
            # Store document metadata
            for i, doc in enumerate(documents):
                doc_copy = doc.copy()
                doc_copy["index_id"] = start_idx + i
                self.documents.append(doc_copy)
            
            # Save index
            self._save_index()
            
            logger.info(f"Added {len(documents)} documents to FAISS index")
            
        except Exception as e:
            logger.error(f"Error adding documents to FAISS: {str(e)}")
            raise
    
    async def similarity_search(
        self, 
        query_embedding: List[float], 
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents in FAISS index.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            List of similar documents with scores
        """
        try:
            # Prepare query embedding
            query = np.array([query_embedding]).astype('float32')
            
            # Normalize for cosine similarity
            query = query / np.linalg.norm(query, axis=1, keepdims=True)
            
            # Search
            scores, indices = self.index.search(query, min(k, len(self.documents)))
            
            # Format results
            documents = []
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0 and idx < len(self.documents):
                    doc = self.documents[idx].copy()
                    doc["score"] = float(score)
                    documents.append(doc)
            
            logger.info(f"Retrieved {len(documents)} documents from FAISS")
            return documents
            
        except Exception as e:
            logger.error(f"Error searching FAISS: {str(e)}")
            raise
    
    async def delete_collection(self) -> None:
        """Delete the FAISS index."""
        try:
            if os.path.exists(self.index_path):
                os.remove(self.index_path)
            
            metadata_path = self.index_path.replace('.index', '_metadata.pkl')
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            
            # Reset in-memory index
            self.index = faiss.IndexFlatIP(self.dimension)
            self.documents = []
            
            logger.info(f"Deleted FAISS index: {self.index_path}")
            
        except Exception as e:
            logger.error(f"Error deleting FAISS index: {str(e)}")
            raise


def get_vector_store() -> VectorStore:
    """
    Factory function to get the appropriate vector store based on configuration.
    
    Returns:
        VectorStore instance
    """
    store_type = settings.vector_store_type.lower()
    
    if store_type == "chroma":
        return ChromaVectorStore()
    elif store_type == "faiss":
        return FAISSVectorStore()
    else:
        raise ValueError(f"Unsupported vector store type: {store_type}")
