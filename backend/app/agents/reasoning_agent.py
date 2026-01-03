"""
Reasoning Agent for the multi-agent system.
Handles query analysis, decomposition, and logical reasoning over retrieved information.
"""

import asyncio
from typing import Dict, Any, List, Optional
import json

from .base_agent import BaseAgent
from ..core import get_logger

logger = get_logger(__name__)


class ReasoningAgent(BaseAgent):
    """
    Reasoning Agent responsible for:
    - Analyzing and understanding user queries
    - Decomposing complex questions into sub-questions
    - Logical reasoning over retrieved documents
    - Building coherent understanding of problems
    """
    
    def __init__(self):
        super().__init__(
            name="Reasoning Agent",
            model_name="gemini-pro",
            temperature=0.2,  # Very low temperature for logical reasoning
            max_tokens=2000
        )
        
        logger.info("Initialized Reasoning Agent")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process reasoning task by analyzing query and sources.
        
        Args:
            input_data: Dictionary containing:
                - query: Original user query
                - sources: Retrieved sources from research agent
                - context: Additional context (optional)
                
        Returns:
            Dictionary containing:
                - query_analysis: Analysis of the original query
                - sub_questions: Decomposed sub-questions
                - reasoning_steps: Logical reasoning steps
                - key_insights: Key insights from sources
                - answer_outline: Structured outline for final answer
        """
        try:
            self.log_processing_start(input_data)
            
            # Validate input
            if not await self.validate_input(input_data):
                raise ValueError("Invalid input data for Reasoning Agent")
            
            query = input_data.get("query", "")
            sources = input_data.get("sources", [])
            context = input_data.get("context", "")
            
            if not query:
                raise ValueError("Query is required for reasoning")
            
            logger.info(f"Starting reasoning analysis for query: {query}")
            
            # Step 1: Analyze the query
            query_analysis = await self._analyze_query(query, context)
            
            # Step 2: Decompose into sub-questions
            sub_questions = await self._decompose_query(query, query_analysis)
            
            # Step 3: Reason over sources
            reasoning_steps = await self._reason_over_sources(query, sources, sub_questions)
            
            # Step 4: Extract key insights
            key_insights = await self._extract_key_insights(sources, reasoning_steps)
            
            # Step 5: Create answer outline
            answer_outline = await self._create_answer_outline(query, key_insights, reasoning_steps)
            
            result = {
                "query_analysis": query_analysis,
                "sub_questions": sub_questions,
                "reasoning_steps": reasoning_steps,
                "key_insights": key_insights,
                "answer_outline": answer_outline,
                "query": query,
                "sources_analyzed": len(sources)
            }
            
            self.log_processing_end(result)
            return result
            
        except Exception as e:
            logger.error(f"Error in Reasoning Agent processing: {str(e)}")
            raise
    
    async def _analyze_query(self, query: str, context: str = "") -> Dict[str, Any]:
        """
        Analyze the user query to understand intent and requirements.
        
        Args:
            query: User query
            context: Additional context
            
        Returns:
            Query analysis dictionary
        """
        messages = [
            {
                "role": "system",
                "content": "You are an expert at analyzing user queries. Analyze the given query "
                          "and provide insights about the user's intent, question type, complexity, "
                          "and information requirements. Respond with a JSON object containing: "
                          "intent (what the user wants to know), question_type (factual, analytical, "
                          "comparative, etc.), complexity (simple, moderate, complex), "
                          "key_entities (main topics/entities), and information_requirements "
                          "(what information is needed to answer)."
            },
            {
                "role": "user",
                "content": f"Query: {query}\nContext: {context}\n\nAnalyze this query:"
            }
        ]
        
        response = await self._call_llm(messages)
        
        try:
            # Try to parse as JSON
            analysis = json.loads(response)
        except json.JSONDecodeError:
            # Fallback to structured text analysis
            analysis = {
                "intent": response,
                "question_type": "general",
                "complexity": "moderate",
                "key_entities": [],
                "information_requirements": "General information needed"
            }
        
        return analysis
    
    async def _decompose_query(
        self, 
        query: str, 
        query_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Decompose complex query into simpler sub-questions.
        
        Args:
            query: Original query
            query_analysis: Analysis of the query
            
        Returns:
            List of sub-questions with priorities
        """
        complexity = query_analysis.get("complexity", "moderate")
        
        # For simple queries, no decomposition needed
        if complexity == "simple":
            return [
                {
                    "question": query,
                    "priority": "high",
                    "dependencies": []
                }
            ]
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert at breaking down complex questions into simpler, "
                          "answerable sub-questions. For the given query, decompose it into 2-5 "
                          "sub-questions that, when answered together, will fully address the original "
                          "query. For each sub-question, specify its priority (high/medium/low) and "
                          "any dependencies on other sub-questions. Respond as a JSON list of objects."
            },
            {
                "role": "user",
                "content": f"Original Query: {query}\n\nQuery Analysis: {json.dumps(query_analysis, indent=2)}\n\n"
                          f"Decompose this into sub-questions:"
            }
        ]
        
        response = await self._call_llm(messages)
        
        try:
            sub_questions = json.loads(response)
            # Ensure it's a list
            if not isinstance(sub_questions, list):
                raise ValueError("Expected list of sub-questions")
        except (json.JSONDecodeError, ValueError):
            # Fallback decomposition
            sub_questions = [
                {
                    "question": query,
                    "priority": "high",
                    "dependencies": []
                }
            ]
        
        return sub_questions
    
    async def _reason_over_sources(
        self, 
        query: str, 
        sources: List[Dict[str, Any]], 
        sub_questions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Apply logical reasoning over the retrieved sources.
        
        Args:
            query: Original query
            sources: Retrieved sources
            sub_questions: Decomposed sub-questions
            
        Returns:
            List of reasoning steps
        """
        if not sources:
            return [{"step": "No sources available for reasoning", "conclusion": "Insufficient information"}]
        
        # Prepare sources context
        sources_context = self._format_context(sources)
        
        reasoning_steps = []
        
        # Reason about each sub-question
        for i, sub_q in enumerate(sub_questions):
            question = sub_q.get("question", "")
            priority = sub_q.get("priority", "medium")
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a logical reasoning expert. Based on the provided sources, "
                              "analyze the given sub-question and provide step-by-step reasoning. "
                              "Identify relevant information, draw logical conclusions, and note any "
                              "gaps or contradictions in the sources. Respond with a structured analysis."
                },
                {
                    "role": "user",
                    "content": f"Sub-Question {i+1} (Priority: {priority}): {question}\n\n"
                              f"Sources:\n{sources_context}\n\n"
                              f"Provide detailed reasoning for this sub-question:"
                }
            ]
            
            reasoning = await self._call_llm(messages)
            
            reasoning_steps.append({
                "sub_question": question,
                "priority": priority,
                "reasoning": reasoning,
                "step_number": i + 1
            })
        
        # Synthesize overall reasoning
        synthesis_messages = [
            {
                "role": "system",
                "content": "You are a synthesis expert. Based on the reasoning steps for each "
                          "sub-question, provide an overall logical synthesis that connects "
                          "the individual reasoning steps into a coherent understanding of "
                          "the original query."
            },
            {
                "role": "user",
                "content": f"Original Query: {query}\n\n"
                          f"Reasoning Steps:\n{json.dumps(reasoning_steps, indent=2)}\n\n"
                          f"Provide overall synthesis:"
            }
        ]
        
        synthesis = await self._call_llm(messages)
        
        reasoning_steps.append({
            "sub_question": "Overall Synthesis",
            "priority": "high",
            "reasoning": synthesis,
            "step_number": len(reasoning_steps) + 1
        })
        
        return reasoning_steps
    
    async def _extract_key_insights(
        self, 
        sources: List[Dict[str, Any]], 
        reasoning_steps: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract key insights from sources and reasoning.
        
        Args:
            sources: Retrieved sources
            reasoning_steps: Reasoning analysis
            
        Returns:
            List of key insights with supporting evidence
        """
        if not sources and not reasoning_steps:
            return []
        
        # Combine reasoning summaries
        reasoning_summary = "\n".join([
            f"Step {step['step_number']}: {step['reasoning'][:200]}..."
            for step in reasoning_steps
        ])
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert at extracting key insights. Based on the reasoning "
                          "analysis, identify the most important insights that directly address "
                          "the user's query. For each insight, provide supporting evidence from "
                          "the reasoning and indicate confidence level. Respond as a JSON list "
                          "of insights with 'insight', 'evidence', and 'confidence' fields."
            },
            {
                "role": "user",
                "content": f"Reasoning Analysis:\n{reasoning_summary}\n\n"
                          f"Extract the key insights:"
            }
        ]
        
        response = await self._call_llm(messages)
        
        try:
            insights = json.loads(response)
            if not isinstance(insights, list):
                raise ValueError("Expected list of insights")
        except (json.JSONDecodeError, ValueError):
            # Fallback insights
            insights = [
                {
                    "insight": "Analysis completed based on available information",
                    "evidence": "Reasoning steps processed",
                    "confidence": "medium"
                }
            ]
        
        return insights
    
    async def _create_answer_outline(
        self, 
        query: str, 
        key_insights: List[Dict[str, Any]], 
        reasoning_steps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create a structured outline for the final answer.
        
        Args:
            query: Original query
            key_insights: Key insights extracted
            reasoning_steps: Reasoning analysis
            
        Returns:
            Structured answer outline
        """
        insights_summary = "\n".join([
            f"- {insight.get('insight', '')} (Confidence: {insight.get('confidence', 'unknown')})"
            for insight in key_insights
        ])
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert at structuring answers. Based on the query analysis "
                          "and key insights, create a structured outline for the final answer. "
                          "The outline should include: introduction, main points (with supporting "
                          "evidence), and conclusion. Make it logical and easy to follow. "
                          "Respond as a JSON object with 'introduction', 'main_points', and "
                          "'conclusion' fields."
            },
            {
                "role": "user",
                "content": f"Query: {query}\n\n"
                          f"Key Insights:\n{insights_summary}\n\n"
                          f"Create an answer outline:"
            }
        ]
        
        response = await self._call_llm(messages)
        
        try:
            outline = json.loads(response)
        except json.JSONDecodeError:
            # Fallback outline
            outline = {
                "introduction": f"Answer to the query: {query}",
                "main_points": [
                    {
                        "point": "Analysis based on available information",
                        "evidence": "Reasoning and insights processed"
                    }
                ],
                "conclusion": "Summary of findings"
            }
        
        return outline
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data for reasoning processing.
        
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
        
        sources = input_data.get("sources", [])
        if not isinstance(sources, list):
            return False
        
        return True
