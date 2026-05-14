<![CDATA["""
Thought Collision Engine — PostgreSQL Database

Async SQLAlchemy connection with session management.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, JSON
from datetime import datetime

from config import settings


# Create async engine
engine = create_async_engine(
    settings.postgres_url,
    echo=settings.debug,
    pool_size=10,
    max_overflow=20,
)

# Session factory
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


# ─── ORM Models ──────────────────────────────────────────────────────────────


class SourceRecord(Base):
    """Tracks ingested knowledge sources."""
    __tablename__ = "sources"

    id = Column(String, primary_key=True)
    source_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=True)
    content_preview = Column(Text, default="")
    concept_count = Column(Integer, default=0)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata_ = Column("metadata", JSON, default=dict)


class CollisionRecord(Base):
    """Persisted collision discoveries."""
    __tablename__ = "collisions"

    id = Column(String, primary_key=True)
    concept_a_id = Column(String, nullable=False)
    concept_b_id = Column(String, nullable=False)
    domain_a = Column(String, default="")
    domain_b = Column(String, default="")
    reasoning = Column(Text, default="")
    novelty_score = Column(Float, default=0.0)
    confidence_score = Column(Float, default=0.0)
    semantic_distance = Column(Float, default=0.0)
    graph_distance = Column(Float, default=0.0)
    bridge_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata_ = Column("metadata", JSON, default=dict)


class HypothesisRecord(Base):
    """Persisted hypotheses."""
    __tablename__ = "hypotheses"

    id = Column(String, primary_key=True)
    collision_id = Column(String, nullable=False)
    title = Column(String, default="")
    hypothesis_type = Column(String, default="research")
    description = Column(Text, default="")
    reasoning_chain = Column(JSON, default=list)
    potential_applications = Column(JSON, default=list)
    novelty_score = Column(Float, default=0.0)
    confidence_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class ExperimentRecord(Base):
    """Persisted experiment runs."""
    __tablename__ = "experiments"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    config = Column(JSON, default=dict)
    metrics = Column(JSON, default=dict)
    duration_seconds = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


# ─── Database Lifecycle ──────────────────────────────────────────────────────


async def init_db():
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Dispose of the engine."""
    await engine.dispose()


async def get_session() -> AsyncSession:
    """Get an async database session."""
    async with async_session() as session:
        yield session
]]>
