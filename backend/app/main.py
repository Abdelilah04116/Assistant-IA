"""
Main FastAPI application for the intelligent research assistant.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core import setup_logging, get_logger, settings
from .api import chat_router, ingestion_router, health_router
from .schemas import ErrorResponse

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Intelligent Research Assistant API")
    
    # Initialize components here if needed
    try:
        # Test basic configuration
        if not settings.google_api_key:
            logger.warning("Google API key not configured")
        
        logger.info("Application startup completed")
        yield
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise
    
    # Shutdown
    logger.info("Shutting down Intelligent Research Assistant API")


# Create FastAPI application
app = FastAPI(
    title="Intelligent Research Assistant API",
    description="A multi-agent RAG-powered research assistant with document ingestion and intelligent query processing",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle uncaught exceptions globally."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
            timestamp="2024-01-01T00:00:00Z"  # Would use actual timestamp
        ).dict()
    )


# Include routers
app.include_router(chat_router)
app.include_router(ingestion_router)
app.include_router(health_router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "name": "Intelligent Research Assistant API",
        "version": "1.0.0",
        "description": "Multi-agent RAG-powered research assistant",
        "docs": "/docs",
        "health": "/health"
    }


# Ready check endpoint
@app.get("/ready")
async def ready_check():
    """Check if the application is ready to serve requests."""
    try:
        # Basic readiness check
        if not settings.google_api_key:
            raise HTTPException(
                status_code=503,
                detail="Service not ready: Google API key not configured"
            )
        
        return {"status": "ready", "timestamp": "2024-01-01T00:00:00Z"}
        
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
