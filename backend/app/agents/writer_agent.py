"""
Writer Agent for the multi-agent system.
Synthesizes final answers with proper citations and clear structure.
"""

import asyncio
from typing import Dict, Any, List, Optional
import json

from .base_agent import BaseAgent
from ..core import get_logger

logger = get_logger(__name__)


class WriterAgent(BaseAgent):
    """
    Writer Agent responsible for:
    - Synthesizing final answers from research and reasoning
    - Producing clear, structured, and actionable responses
    - Properly citing sources used in the answer
    - Ensuring answer quality and coherence
    """
    
    def __init__(self):
        super().__init__(
            name="Writer Agent",
            model_name="gemini-pro",
            temperature=0.4,  # Balanced temperature for clear yet engaging writing
            max_tokens=2500
        )
        
        logger.info("Initialized Writer Agent")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process writing task by synthesizing research and reasoning results.
        
        Args:
            input_data: Dictionary containing:
                - query: Original user query
                - research_results: Results from research agent
                - reasoning_results: Results from reasoning agent
                - style_preferences: Writing style preferences (optional)
                
        Returns:
            Dictionary containing:
                - final_answer: Synthesized answer
                - citations: List of citations used
                - answer_metadata: Metadata about the answer
                - quality_score: Quality assessment score
        """
        try:
            self.log_processing_start(input_data)
            
            # Validate input
            if not await self.validate_input(input_data):
                raise ValueError("Invalid input data for Writer Agent")
            
            query = input_data.get("query", "")
            research_results = input_data.get("research_results", {})
            reasoning_results = input_data.get("reasoning_results", {})
            style_preferences = input_data.get("style_preferences", {})
            
            if not query:
                raise ValueError("Query is required for writing")
            
            logger.info(f"Starting answer synthesis for query: {query}")
            
            # Step 1: Extract and organize information
            organized_info = await self._organize_information(
                research_results, reasoning_results
            )
            
            # Step 2: Generate structured answer
            structured_answer = await self._generate_structured_answer(
                query, organized_info, style_preferences
            )
            
            # Step 3: Format citations
            citations = await self._format_citations(organized_info)
            
            # Step 4: Quality assessment
            quality_score = await self._assess_answer_quality(
                query, structured_answer, organized_info
            )
            
            # Step 5: Final formatting
            final_answer = await self._format_final_answer(
                structured_answer, citations
            )
            
            result = {
                "final_answer": final_answer,
                "structured_answer": structured_answer,
                "citations": citations,
                "answer_metadata": {
                    "query": query,
                    "sources_used": len(organized_info.get("sources", [])),
                    "word_count": len(final_answer.split()),
                    "generation_timestamp": "2024-01-01T00:00:00Z"  # Would use actual timestamp
                },
                "quality_score": quality_score,
                "organized_info": organized_info
            }
            
            self.log_processing_end(result)
            return result
            
        except Exception as e:
            logger.error(f"Error in Writer Agent processing: {str(e)}")
            raise
    
    async def _organize_information(
        self, 
        research_results: Dict[str, Any], 
        reasoning_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Organize information from research and reasoning results.
        
        Args:
            research_results: Results from research agent
            reasoning_results: Results from reasoning agent
            
        Returns:
            Organized information dictionary
        """
        # Extract sources from research results
        sources = research_results.get("combined_sources", [])
        research_summary = research_results.get("research_summary", "")
        
        # Extract reasoning information
        query_analysis = reasoning_results.get("query_analysis", {})
        key_insights = reasoning_results.get("key_insights", [])
        answer_outline = reasoning_results.get("answer_outline", {})
        reasoning_steps = reasoning_results.get("reasoning_steps", [])
        
        # Organize by relevance and source type
        organized_sources = []
        for source in sources:
            organized_sources.append({
                "content": source.get("content", ""),
                "title": source.get("metadata", {}).get("filename", "Unknown"),
                "source_type": source.get("source_type", "unknown"),
                "relevance_score": source.get("score", 0),
                "citation_info": self._extract_citation_info(source)
            })
        
        return {
            "sources": organized_sources,
            "research_summary": research_summary,
            "query_analysis": query_analysis,
            "key_insights": key_insights,
            "answer_outline": answer_outline,
            "reasoning_steps": reasoning_steps
        }
    
    async def _generate_structured_answer(
        self, 
        query: str, 
        organized_info: Dict[str, Any], 
        style_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a structured answer based on organized information.
        
        Args:
            query: Original query
            organized_info: Organized information from research and reasoning
            style_preferences: Writing style preferences
            
        Returns:
            Structured answer dictionary
        """
        # Determine writing style
        tone = style_preferences.get("tone", "professional")
        length = style_preferences.get("length", "medium")
        audience = style_preferences.get("audience", "general")
        
        # Prepare context for LLM
        context = self._prepare_writing_context(organized_info)
        
        messages = [
            {
                "role": "system",
                "content": f"You are an expert writer and researcher. Write a comprehensive, "
                          f"well-structured answer to the user's query. Use a {tone} tone, "
                          f"aim for {length} length, and target a {audience} audience. "
                          f"Include proper citations and ensure the answer is accurate, "
                          f"clear, and actionable. Structure your response with clear headings, "
                          f"bullet points where appropriate, and a logical flow."
            },
            {
                "role": "user",
                "content": f"Query: {query}\n\n"
                          f"Context and Information:\n{context}\n\n"
                          f"Write a comprehensive answer:"
            }
        ]
        
        answer_content = await self._call_llm(messages)
        
        # Extract sections from the answer
        sections = self._extract_answer_sections(answer_content)
        
        return {
            "content": answer_content,
            "sections": sections,
            "tone": tone,
            "length": length,
            "audience": audience
        }
    
    def _prepare_writing_context(self, organized_info: Dict[str, Any]) -> str:
        """
        Prepare context information for writing.
        
        Args:
            organized_info: Organized information
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # Add key insights
        if organized_info.get("key_insights"):
            insights_text = "\n".join([
                f"- {insight.get('insight', '')}"
                for insight in organized_info["key_insights"]
            ])
            context_parts.append(f"Key Insights:\n{insights_text}")
        
        # Add answer outline
        if organized_info.get("answer_outline"):
            outline = organized_info["answer_outline"]
            outline_text = f"Introduction: {outline.get('introduction', '')}\n"
            
            if outline.get("main_points"):
                outline_text += "Main Points:\n"
                for point in outline["main_points"]:
                    outline_text += f"- {point.get('point', '')}\n"
            
            outline_text += f"Conclusion: {outline.get('conclusion', '')}"
            context_parts.append(f"Answer Outline:\n{outline_text}")
        
        # Add top sources
        if organized_info.get("sources"):
            top_sources = organized_info["sources"][:5]  # Top 5 sources
            sources_text = "\n".join([
                f"Source {i+1}: {source.get('title', 'Unknown')} - "
                f"{source.get('content', '')[:200]}..."
                for i, source in enumerate(top_sources)
            ])
            context_parts.append(f"Key Sources:\n{sources_text}")
        
        return "\n\n".join(context_parts)
    
    def _extract_answer_sections(self, answer_content: str) -> List[Dict[str, Any]]:
        """
        Extract sections from the answer content.
        
        Args:
            answer_content: Full answer content
            
        Returns:
            List of sections with titles and content
        """
        sections = []
        lines = answer_content.split('\n')
        current_section = {"title": "Introduction", "content": []}
        
        for line in lines:
            line = line.strip()
            
            # Check if it's a heading (starts with # or **)
            if line.startswith('#') or (line.startswith('**') and line.endswith('**')):
                # Save previous section
                if current_section["content"]:
                    current_section["content"] = "\n".join(current_section["content"])
                    sections.append(current_section)
                
                # Start new section
                title = line.lstrip('#').strip().strip('*').strip()
                current_section = {"title": title, "content": []}
            else:
                current_section["content"].append(line)
        
        # Add final section
        if current_section["content"]:
            current_section["content"] = "\n".join(current_section["content"])
            sections.append(current_section)
        
        return sections
    
    async def _format_citations(self, organized_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format citations from the organized information.
        
        Args:
            organized_info: Organized information with sources
            
        Returns:
            List of formatted citations
        """
        citations = []
        sources = organized_info.get("sources", [])
        
        for i, source in enumerate(sources):
            citation = {
                "id": i + 1,
                "title": source.get("title", "Unknown Source"),
                "source_type": source.get("source_type", "unknown"),
                "relevance_score": source.get("relevance_score", 0),
                "citation_info": source.get("citation_info", {}),
                "in_text_reference": f"[{i + 1}]"
            }
            citations.append(citation)
        
        return citations
    
    async def _assess_answer_quality(
        self, 
        query: str, 
        structured_answer: Dict[str, Any], 
        organized_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess the quality of the generated answer.
        
        Args:
            query: Original query
            structured_answer: Generated structured answer
            organized_info: Information used to generate answer
            
        Returns:
            Quality assessment dictionary
        """
        answer_content = structured_answer.get("content", "")
        sources_count = len(organized_info.get("sources", []))
        
        # Simple quality metrics
        word_count = len(answer_content.split())
        has_citations = "[1]" in answer_content or "[Source" in answer_content
        has_structure = len(structured_answer.get("sections", [])) > 1
        
        # Quality scoring (0-100)
        quality_score = 50  # Base score
        
        # Add points for various quality factors
        if word_count > 100:
            quality_score += 10
        if word_count > 300:
            quality_score += 10
        if has_citations:
            quality_score += 15
        if has_structure:
            quality_score += 10
        if sources_count > 0:
            quality_score += min(sources_count * 2, 15)
        
        quality_score = min(quality_score, 100)
        
        return {
            "overall_score": quality_score,
            "metrics": {
                "word_count": word_count,
                "sources_used": sources_count,
                "has_citations": has_citations,
                "has_structure": has_structure
            },
            "assessment": self._get_quality_assessment(quality_score)
        }
    
    def _get_quality_assessment(self, score: int) -> str:
        """Get quality assessment based on score."""
        if score >= 90:
            return "Excellent - Comprehensive, well-structured, and well-cited answer"
        elif score >= 75:
            return "Good - Solid answer with room for minor improvements"
        elif score >= 60:
            return "Acceptable - Basic answer that addresses the query"
        else:
            return "Needs Improvement - Answer lacks depth or proper structure"
    
    async def _format_final_answer(
        self, 
        structured_answer: Dict[str, Any], 
        citations: List[Dict[str, Any]]
    ) -> str:
        """
        Format the final answer with citations.
        
        Args:
            structured_answer: Structured answer content
            citations: List of citations
            
        Returns:
            Formatted final answer
        """
        content = structured_answer.get("content", "")
        
        # Add citations section if citations exist
        if citations:
            citations_section = "\n\n## Sources\n\n"
            for citation in citations:
                citations_section += f"{citation['in_text_reference']} {citation['title']}\n"
            
            content += citations_section
        
        return content
    
    def _extract_citation_info(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """Extract citation information from a source."""
        metadata = source.get("metadata", {})
        return {
            "filename": metadata.get("filename", "Unknown"),
            "source": metadata.get("source", "Unknown"),
            "chunk_id": source.get("chunk_id", "Unknown"),
            "url": metadata.get("url", "")
        }
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data for writing processing.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not await super().validate_input(input_data):
            return False
        
        # Check for required fields
        query = input_data.get("query")
        if not query or not isinstance(query, str):
            return False
        
        # Check that at least one of research_results or reasoning_results exists
        research_results = input_data.get("research_results")
        reasoning_results = input_data.get("reasoning_results")
        
        if not research_results and not reasoning_results:
            return False
        
        return True
