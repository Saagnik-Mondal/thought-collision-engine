<![CDATA["""
Thought Collision Engine — API Dependencies

FastAPI dependency injection for database sessions and services.
"""

from core.database import async_session, AsyncSession
from core.neo4j_client import neo4j_client
from core.vector_store import vector_store


async def get_db() -> AsyncSession:
    """Get an async PostgreSQL session."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_neo4j():
    """Get the Neo4j client."""
    return neo4j_client


async def get_vector_store():
    """Get the ChromaDB vector store."""
    return vector_store
]]>
