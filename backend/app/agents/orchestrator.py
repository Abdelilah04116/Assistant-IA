"""
Agent Orchestrator using LangGraph.
Coordinates the multi-agent workflow for intelligent research assistance.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# LangGraph imports for orchestration
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .research_agent import ResearchAgent
from .reasoning_agent import ReasoningAgent
from .writer_agent import WriterAgent
from ..core import get_logger

logger = get_logger(__name__)


class WorkflowState:
    """
    State class for the LangGraph workflow.
    Maintains state across agent executions.
    """
    
    def __init__(self):
        self.query: str = ""
        self.research_results: Optional[Dict[str, Any]] = None
        self.reasoning_results: Optional[Dict[str, Any]] = None
        self.final_answer: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        self.start_time: datetime = datetime.now()
        self.current_step: str = "initialized"
        self.metadata: Dict[str, Any] = {}


class AgentOrchestrator:
    """
    Orchestrates the multi-agent workflow using LangGraph.
    Coordinates Research, Reasoning, and Writer agents to produce intelligent responses.
    
    Using LangGraph over CrewAI because:
    1. LangGraph provides better state management and checkpointing
    2. More flexible workflow definitions with conditional routing
    3. Better integration with LangChain ecosystem
    4. Superior error handling and recovery mechanisms
    5. More suitable for complex, multi-step reasoning workflows
    """
    
    def __init__(self):
        # Initialize agents
        self.research_agent = ResearchAgent()
        self.reasoning_agent = ReasoningAgent()
        self.writer_agent = WriterAgent()
        
        # Initialize LangGraph workflow
        self.workflow = self._create_workflow()
        
        # Initialize memory for checkpointing
        self.memory = MemorySaver()
        
        logger.info("Initialized Agent Orchestrator with LangGraph workflow")
    
    def _create_workflow(self) -> StateGraph:
        """
        Create the LangGraph workflow for agent orchestration.
        
        Returns:
            Configured StateGraph workflow
        """
        # Create workflow graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes (agents)
        workflow.add_node("research", self._research_step)
        workflow.add_node("reasoning", self._reasoning_step)
        workflow.add_node("writing", self._writing_step)
        workflow.add_node("error_handler", self._error_handler_step)
        
        # Add edges (workflow connections)
        workflow.set_entry_point("research")
        
        # Research to Reasoning
        workflow.add_edge("research", "reasoning")
        
        # Reasoning to Writing
        workflow.add_edge("reasoning", "writing")
        
        # Writing to End
        workflow.add_edge("writing", END)
        
        # Error handling
        workflow.add_conditional_edges(
            "research",
            self._check_research_results,
            {
                "success": "reasoning",
                "error": "error_handler"
            }
        )
        
        workflow.add_conditional_edges(
            "reasoning", 
            self._check_reasoning_results,
            {
                "success": "writing",
                "error": "error_handler"
            }
        )
        
        workflow.add_conditional_edges(
            "writing",
            self._check_writing_results,
            {
                "success": END,
                "error": "error_handler"
            }
        )
        
        workflow.add_edge("error_handler", END)
        
        return workflow
    
    async def _research_step(self, state: WorkflowState) -> WorkflowState:
        """Execute the research step."""
        try:
            logger.info(f"Starting research step for query: {state.query}")
            state.current_step = "research"
            
            # Prepare research input
            research_input = {
                "query": state.query,
                "max_documents": 5,
                "include_web_search": True
            }
            
            # Execute research
            state.research_results = await self.research_agent.process(research_input)
            
            logger.info("Research step completed successfully")
            return state
            
        except Exception as e:
            logger.error(f"Error in research step: {str(e)}")
            state.error = f"Research step failed: {str(e)}"
            return state
    
    async def _reasoning_step(self, state: WorkflowState) -> WorkflowState:
        """Execute the reasoning step."""
        try:
            logger.info("Starting reasoning step")
            state.current_step = "reasoning"
            
            # Prepare reasoning input
            reasoning_input = {
                "query": state.query,
                "sources": state.research_results.get("combined_sources", []),
                "context": state.research_results.get("research_summary", "")
            }
            
            # Execute reasoning
            state.reasoning_results = await self.reasoning_agent.process(reasoning_input)
            
            logger.info("Reasoning step completed successfully")
            return state
            
        except Exception as e:
            logger.error(f"Error in reasoning step: {str(e)}")
            state.error = f"Reasoning step failed: {str(e)}"
            return state
    
    async def _writing_step(self, state: WorkflowState) -> WorkflowState:
        """Execute the writing step."""
        try:
            logger.info("Starting writing step")
            state.current_step = "writing"
            
            # Prepare writing input
            writing_input = {
                "query": state.query,
                "research_results": state.research_results,
                "reasoning_results": state.reasoning_results,
                "style_preferences": {
                    "tone": "professional",
                    "length": "medium",
                    "audience": "general"
                }
            }
            
            # Execute writing
            state.final_answer = await self.writer_agent.process(writing_input)
            
            logger.info("Writing step completed successfully")
            return state
            
        except Exception as e:
            logger.error(f"Error in writing step: {str(e)}")
            state.error = f"Writing step failed: {str(e)}"
            return state
    
    async def _error_handler_step(self, state: WorkflowState) -> WorkflowState:
        """Handle errors in the workflow."""
        logger.error(f"Workflow error at step {state.current_step}: {state.error}")
        
        # Create a fallback response
        state.final_answer = {
            "final_answer": f"I apologize, but I encountered an error while processing your request: {state.error}",
            "citations": [],
            "answer_metadata": {
                "error": True,
                "error_message": state.error,
                "failed_step": state.current_step
            },
            "quality_score": {
                "overall_score": 0,
                "assessment": "Failed due to processing error"
            }
        }
        
        return state
    
    def _check_research_results(self, state: WorkflowState) -> str:
        """Check if research step was successful."""
        if state.error:
            return "error"
        if state.research_results is None:
            return "error"
        return "success"
    
    def _check_reasoning_results(self, state: WorkflowState) -> str:
        """Check if reasoning step was successful."""
        if state.error:
            return "error"
        if state.reasoning_results is None:
            return "error"
        return "success"
    
    def _check_writing_results(self, state: WorkflowState) -> str:
        """Check if writing step was successful."""
        if state.error:
            return "error"
        if state.final_answer is None:
            return "error"
        return "success"
    
    async def process_query(
        self, 
        query: str, 
        workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user query through the multi-agent workflow.
        
        Args:
            query: User query to process
            workflow_id: Optional workflow ID for tracking
            
        Returns:
            Complete workflow results
        """
        try:
            logger.info(f"Processing query through workflow: {query}")
            
            # Initialize workflow state
            state = WorkflowState()
            state.query = query
            state.metadata["workflow_id"] = workflow_id or f"workflow_{datetime.now().timestamp()}"
            
            # Compile and run workflow
            compiled_workflow = self.workflow.compile(checkpointer=self.memory)
            
            # Run the workflow
            config = {"configurable": {"thread_id": state.metadata["workflow_id"]}}
            result = await compiled_workflow.ainvoke(state, config=config)
            
            # Prepare final response
            end_time = datetime.now()
            processing_time = (end_time - result.start_time).total_seconds()
            
            response = {
                "query": query,
                "answer": result.final_answer.get("final_answer", "") if result.final_answer else "",
                "citations": result.final_answer.get("citations", []) if result.final_answer else [],
                "metadata": {
                    "workflow_id": result.metadata["workflow_id"],
                    "processing_time": processing_time,
                    "steps_completed": [
                        "research" if result.research_results else None,
                        "reasoning" if result.reasoning_results else None,
                        "writing" if result.final_answer else None
                    ],
                    "sources_used": len(result.research_results.get("combined_sources", [])) if result.research_results else 0,
                    "quality_score": result.final_answer.get("quality_score", {}).get("overall_score", 0) if result.final_answer else 0
                },
                "error": result.error,
                "success": result.error is None
            }
            
            logger.info(f"Workflow completed successfully in {processing_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Error in workflow orchestration: {str(e)}")
            return {
                "query": query,
                "answer": f"I apologize, but I encountered an unexpected error: {str(e)}",
                "citations": [],
                "metadata": {
                    "error": True,
                    "error_message": str(e)
                },
                "error": str(e),
                "success": False
            }
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get the status of a workflow execution.
        
        Args:
            workflow_id: Workflow ID to check
            
        Returns:
            Workflow status information
        """
        try:
            config = {"configurable": {"thread_id": workflow_id}}
            compiled_workflow = self.workflow.compile(checkpointer=self.memory)
            
            # Get checkpoint data
            checkpoint = await compiled_workflow.aget_state(config)
            
            return {
                "workflow_id": workflow_id,
                "current_step": checkpoint.values.get("current_step", "unknown"),
                "status": "completed" if checkpoint.next == [] else "in_progress",
                "error": checkpoint.values.get("error"),
                "metadata": checkpoint.values.get("metadata", {})
            }
            
        except Exception as e:
            logger.error(f"Error getting workflow status: {str(e)}")
            return {
                "workflow_id": workflow_id,
                "status": "error",
                "error": str(e)
            }
