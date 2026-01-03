"""
Research Agent for the multi-agent system.
Handles information retrieval from both internal documents and external sources.
"""

import asyncio
import httpx
from typing import Dict, Any, List, Optional
import json

from .base_agent import BaseAgent
from ..rag import DocumentRetriever
from ..core import get_logger

logger = get_logger(__name__)


class ResearchAgent(BaseAgent):
    """
    Research Agent responsible for gathering information from multiple sources:
    - Internal document search using RAG
    - External web search via APIs
    - Source validation and ranking
    """
    
    def __init__(self):
        super().__init__(
            name="Research Agent",
            model_name="gemini-pro",
            temperature=0.3,  # Lower temperature for more factual responses
            max_tokens=1500
        )
        self.document_retriever = DocumentRetriever()
        self.web_search_enabled = True  # Can be configured
        
        logger.info("Initialized Research Agent")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process research request by gathering information from multiple sources.
        
        Args:
            input_data: Dictionary containing:
                - query: Research question/topic
                - max_documents: Maximum documents to retrieve (optional)
                - include_web_search: Whether to include web search (optional)
                
        Returns:
            Dictionary containing:
                - internal_documents: Retrieved internal documents
                - web_results: Web search results (if enabled)
                - combined_sources: All sources with metadata
                - research_summary: Brief summary of findings
        """
        try:
            self.log_processing_start(input_data)
            
            # Validate input
            if not await self.validate_input(input_data):
                raise ValueError("Invalid input data for Research Agent")
            
            query = input_data.get("query", "")
            max_documents = input_data.get("max_documents", 5)
            include_web_search = input_data.get("include_web_search", self.web_search_enabled)
            
            if not query:
                raise ValueError("Query is required for research")
            
            logger.info(f"Starting research for query: {query}")
            
            # Parallel research from multiple sources
            tasks = []
            
            # Internal document search
            tasks.append(self._search_internal_documents(query, max_documents))
            
            # Web search (if enabled)
            if include_web_search:
                tasks.append(self._web_search(query))
            
            # Execute all research tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            internal_docs = results[0] if not isinstance(results[0], Exception) else []
            web_results = results[1] if len(results) > 1 and not isinstance(results[1], Exception) else []
            
            # Combine and rank sources
            combined_sources = self._combine_sources(internal_docs, web_results)
            
            # Generate research summary
            research_summary = await self._generate_research_summary(query, combined_sources)
            
            result = {
                "internal_documents": internal_docs,
                "web_results": web_results,
                "combined_sources": combined_sources,
                "research_summary": research_summary,
                "query": query,
                "total_sources": len(combined_sources)
            }
            
            self.log_processing_end(result)
            return result
            
        except Exception as e:
            logger.error(f"Error in Research Agent processing: {str(e)}")
            raise
    
    async def _search_internal_documents(
        self, 
        query: str, 
        max_documents: int
    ) -> List[Dict[str, Any]]:
        """
        Search internal documents using the RAG system.
        
        Args:
            query: Search query
            max_documents: Maximum documents to retrieve
            
        Returns:
            List of retrieved documents with metadata
        """
        try:
            logger.info(f"Searching internal documents for: {query}")
            
            documents = await self.document_retriever.retrieve(
                query=query,
                k=max_documents,
                rerank=True
            )
            
            # Add source type information
            for doc in documents:
                doc["source_type"] = "internal"
                doc["retrieval_method"] = "semantic_search"
            
            logger.info(f"Found {len(documents)} internal documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error searching internal documents: {str(e)}")
            return []
    
    async def _web_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform web search for additional information.
        Note: This is a simplified implementation. In production, you'd use
        proper web search APIs like Google Search API, Bing Search API, etc.
        
        Args:
            query: Search query
            
        Returns:
            List of web search results
        """
        try:
            logger.info(f"Performing web search for: {query}")
            
            # This is a placeholder implementation
            # In production, integrate with actual web search APIs
            web_results = await self._mock_web_search(query)
            
            logger.info(f"Found {len(web_results)} web search results")
            return web_results
            
        except Exception as e:
            logger.error(f"Error in web search: {str(e)}")
            return []
    
    async def _mock_web_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Mock web search implementation for demonstration.
        Replace with actual web search API integration.
        
        Args:
            query: Search query
            
        Returns:
            Mock web search results
        """
        # This is a simplified mock implementation
        # In production, integrate with real web search APIs
        
        mock_results = [
            {
                "title": f"Web search result for: {query}",
                "url": "https://example.com/search-result",
                "snippet": f"This is a mock web search result for the query: {query}. "
                          "In production, this would contain actual search results from "
                          "web search APIs like Google, Bing, or specialized search engines.",
                "source_type": "web",
                "retrieval_method": "web_search",
                "score": 0.8
            }
        ]
        
        return mock_results
    
    def _combine_sources(
        self, 
        internal_docs: List[Dict[str, Any]], 
        web_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Combine and rank sources from different retrieval methods.
        
        Args:
            internal_docs: Internal document results
            web_results: Web search results
            
        Returns:
            Combined and ranked list of sources
        """
        combined = internal_docs + web_results
        
        # Sort by score (descending)
        combined.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        # Add ranking information
        for i, source in enumerate(combined, 1):
            source["rank"] = i
            source["relevance_score"] = source.get("score", 0)
        
        return combined
    
    async def _generate_research_summary(
        self, 
        query: str, 
        sources: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a brief summary of research findings.
        
        Args:
            query: Original research query
            sources: Retrieved sources
            
        Returns:
            Research summary
        """
        if not sources:
            return f"No relevant information found for query: {query}"
        
        # Prepare sources summary
        sources_summary = []
        for i, source in enumerate(sources[:5], 1):  # Limit to top 5 for summary
            if source.get("source_type") == "internal":
                content = source.get("content", "")[:200] + "..." if len(source.get("content", "")) > 200 else source.get("content", "")
                sources_summary.append(f"Source {i} (Internal): {content}")
            else:
                snippet = source.get("snippet", source.get("title", ""))
                sources_summary.append(f"Source {i} (Web): {snippet}")
        
        sources_text = "\n".join(sources_summary)
        
        # Generate summary using LLM
        messages = [
            {
                "role": "system",
                "content": "You are a research assistant. Based on the provided sources, "
                          "generate a concise summary of the key findings related to the query. "
                          "Focus on the most relevant and important information."
            },
            {
                "role": "user",
                "content": f"Query: {query}\n\nSources:\n{sources_text}\n\n"
                          f"Provide a brief summary of the key findings:"
            }
        ]
        
        summary = await self._call_llm(messages)
        return summary
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data for research processing.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not await super().validate_input(input_data):
            return False
        
        # Check for required query field
        query = input_data.get("query")
        if not query or not isinstance(query, str):
            return False
        
        return True
