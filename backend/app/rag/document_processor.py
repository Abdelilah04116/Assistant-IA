"""
Document processing module for the RAG pipeline.
Handles PDF parsing, text chunking, and metadata extraction.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
import PyPDF2
import aiofiles
from sentence_transformers import SentenceTransformer

from ..core import get_logger, settings

logger = get_logger(__name__)


class DocumentChunk:
    """Represents a chunk of processed document with metadata."""
    
    def __init__(
        self,
        content: str,
        metadata: Dict[str, Any],
        chunk_id: str
    ):
        self.content = content
        self.metadata = metadata
        self.chunk_id = chunk_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary format."""
        return {
            "content": self.content,
            "metadata": self.metadata,
            "chunk_id": self.chunk_id
        }


class DocumentProcessor:
    """
    Handles document ingestion, parsing, and chunking.
    Supports PDF files and plain text documents.
    """
    
    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
        logger.info(f"Initialized DocumentProcessor with chunk_size={self.chunk_size}")
    
    async def process_pdf(self, file_path: str) -> List[DocumentChunk]:
        """
        Process a PDF file and extract text chunks.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of document chunks
        """
        try:
            logger.info(f"Processing PDF: {file_path}")
            
            # Extract text from PDF
            text_content = await self._extract_pdf_text(file_path)
            
            # Create metadata
            metadata = {
                "source": file_path,
                "filename": os.path.basename(file_path),
                "file_type": "pdf",
                "total_pages": len(text_content) if isinstance(text_content, list) else 1
            }
            
            # Chunk the text
            chunks = self._chunk_text(text_content, metadata)
            
            logger.info(f"Generated {len(chunks)} chunks from {file_path}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {str(e)}")
            raise
    
    async def process_text(self, file_path: str) -> List[DocumentChunk]:
        """
        Process a plain text file and extract text chunks.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            List of document chunks
        """
        try:
            logger.info(f"Processing text file: {file_path}")
            
            # Read text content
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                text_content = await file.read()
            
            # Create metadata
            metadata = {
                "source": file_path,
                "filename": os.path.basename(file_path),
                "file_type": "text"
            }
            
            # Chunk the text
            chunks = self._chunk_text(text_content, metadata)
            
            logger.info(f"Generated {len(chunks)} chunks from {file_path}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing text file {file_path}: {str(e)}")
            raise
    
    async def _extract_pdf_text(self, file_path: str) -> str:
        """
        Extract text content from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        text_content = []
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_content.append(page_text)
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num}: {str(e)}")
                    continue
        
        return "\n\n".join(text_content)
    
    def _chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """
        Split text into chunks with overlap.
        
        Args:
            text: Text content to chunk
            metadata: Document metadata
            
        Returns:
            List of document chunks
        """
        chunks = []
        
        # Simple text chunking with overlap
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk_text = text[i:i + self.chunk_size]
            
            if chunk_text.strip():
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    "chunk_index": len(chunks),
                    "start_char": i,
                    "end_char": min(i + self.chunk_size, len(text))
                })
                
                chunk = DocumentChunk(
                    content=chunk_text,
                    metadata=chunk_metadata,
                    chunk_id=f"{metadata['filename']}_chunk_{len(chunks)}"
                )
                chunks.append(chunk)
        
        return chunks
    
    async def process_document(self, file_path: str) -> List[DocumentChunk]:
        """
        Process a document based on its file type.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            List of document chunks
        """
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.pdf':
            return await self.process_pdf(file_path)
        elif file_extension in ['.txt', '.md']:
            return await self.process_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")


class EmbeddingGenerator:
    """
    Handles text embedding generation using sentence transformers.
    """
    
    def __init__(self):
        self.model_name = settings.embedding_model
        self.device = settings.embedding_device
        self.model = None
        logger.info(f"Initialized EmbeddingGenerator with model={self.model_name}")
    
    def _load_model(self):
        """Load the embedding model lazily."""
        if self.model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info("Embedding model loaded successfully")
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        self._load_model()
        
        try:
            # Generate embeddings
            embeddings = self.model.encode(
                texts,
                batch_size=32,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            
            # Convert to list of lists
            return embeddings.tolist()
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    async def generate_single_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text string to embed
            
        Returns:
            Embedding vector
        """
        embeddings = await self.generate_embeddings([text])
        return embeddings[0] if embeddings else []
