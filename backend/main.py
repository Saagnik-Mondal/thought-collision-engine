<![CDATA["""
Thought Collision Engine — FastAPI Application Entry Point

Main application factory with CORS, lifespan management, and route registration.
"""

import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from config import settings
from api.router import api_router
from core.database import init_db, close_db
from core.neo4j_client import neo4j_client
from core.vector_store import vector_store


# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG" if settings.debug else "INFO",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    logger.info("🧠 Starting Thought Collision Engine v{}", settings.app_version)

    # Initialize databases
    await init_db()
    logger.info("✅ PostgreSQL connected")

    try:
        await neo4j_client.connect()
        logger.info("✅ Neo4j connected")
    except Exception as e:
        logger.warning("⚠️ Neo4j not available (running in degraded mode): {}", e)

    try:
        vector_store.connect()
        logger.info("✅ ChromaDB connected")
    except Exception as e:
        logger.warning("⚠️ ChromaDB not available (running in degraded mode): {}", e)

    logger.info("🚀 All systems ready — Engine is live!")

    yield

    # Shutdown
    logger.info("🛑 Shutting down Thought Collision Engine...")
    await neo4j_client.close()
    await close_db()
    logger.info("👋 Shutdown complete.")


# Create application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Discover hidden relationships between ideas across unrelated domains.",
    lifespan=lifespan,
)

# CORS — allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router, prefix="/api")


@app.get("/", tags=["root"])
async def root():
    """Root endpoint — health check."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "message": "🧠 Thought Collision Engine is running.",
    }


@app.get("/health", tags=["root"])
async def health_check():
    """Detailed health check for all services."""
    neo4j_healthy = await neo4j_client.is_healthy()
    pg_healthy = True  # If we got here, FastAPI is up
    chroma_healthy = vector_store.is_healthy()

    return {
        "status": "healthy" if all([neo4j_healthy, pg_healthy, chroma_healthy]) else "degraded",
        "services": {
            "fastapi": {"status": "healthy"},
            "postgresql": {"status": "healthy" if pg_healthy else "unhealthy"},
            "neo4j": {"status": "healthy" if neo4j_healthy else "unhealthy"},
            "chromadb": {"status": "healthy" if chroma_healthy else "unhealthy"},
        },
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.debug,
    )
]]>
