"""
Base agent class for the multi-agent system.
Provides common functionality and interface for all specialized agents.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

from ..core import get_logger, settings

logger = get_logger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the multi-agent system.
    Provides common functionality including LLM integration and logging.
    """
    
    def __init__(
        self, 
        name: str,
        model_name: str = "gemini-pro",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ):
        """
        Initialize the base agent.
        
        Args:
            name: Agent name for identification
            model_name: Google Gemini model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        """
        self.name = name
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=settings.google_api_key
        )
        
        logger.info(f"Initialized agent: {name} with model: {model_name}")
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return results.
        Must be implemented by subclasses.
        
        Args:
            input_data: Input data for processing
            
        Returns:
            Processing results
        """
        pass
    
    async def _call_llm(
        self, 
        messages: List[Dict[str, str]], 
        response_format: Optional[str] = None
    ) -> str:
        """
        Call the language model with a list of messages.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            response_format: Optional format hint for the response
            
        Returns:
            LLM response text
        """
        try:
            # Convert message dictionaries to LangChain message objects
            langchain_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    langchain_messages.append(SystemMessage(content=msg["content"]))
                elif msg["role"] == "user":
                    langchain_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    langchain_messages.append(AIMessage(content=msg["content"]))
            
            # Add response format instruction if provided
            if response_format:
                format_message = SystemMessage(
                    content=f"Please respond in the following format: {response_format}"
                )
                langchain_messages.insert(0, format_message)
            
            # Call the model
            response = await self.llm.ainvoke(langchain_messages)
            
            logger.info(f"LLM call successful for agent: {self.name}")
            return response.content
            
        except Exception as e:
            logger.error(f"Error calling LLM for agent {self.name}: {str(e)}")
            raise
    
    def _format_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Format retrieved documents into a context string.
        
        Args:
            documents: List of retrieved documents
            
        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant documents found."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            source = metadata.get("source", "Unknown source")
            
            context_parts.append(
                f"Document {i} (Source: {source}):\n{content}\n"
            )
        
        return "\n".join(context_parts)
    
    def _extract_citations(self, documents: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Extract citation information from documents.
        
        Args:
            documents: List of documents
            
        Returns:
            List of citation dictionaries
        """
        citations = []
        for doc in documents:
            metadata = doc.get("metadata", {})
            citation = {
                "source": metadata.get("source", "Unknown source"),
                "filename": metadata.get("filename", "Unknown file"),
                "chunk_id": doc.get("chunk_id", "Unknown chunk"),
                "score": str(doc.get("score", 0))
            }
            citations.append(citation)
        
        return citations
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data before processing.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Basic validation - can be overridden by subclasses
        return isinstance(input_data, dict) and input_data is not None
    
    def log_processing_start(self, input_data: Dict[str, Any]) -> None:
        """Log the start of processing."""
        logger.info(f"Agent {self.name} starting processing")
    
    def log_processing_end(self, result: Dict[str, Any]) -> None:
        """Log the end of processing."""
        logger.info(f"Agent {self.name} completed processing successfully")
