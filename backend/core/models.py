<![CDATA["""
Thought Collision Engine — Pydantic Models

All request/response schemas and domain models.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ─── Enums ────────────────────────────────────────────────────────────────────


class SourceType(str, Enum):
    PDF = "pdf"
    ARXIV = "arxiv"
    URL = "url"
    GITHUB = "github"
    TEXT = "text"


class NodeType(str, Enum):
    CONCEPT = "concept"
    ENTITY = "entity"
    DOMAIN = "domain"
    IDEA = "idea"
    TOPIC = "topic"


class EdgeType(str, Enum):
    SEMANTIC = "semantic"
    INFERRED = "inferred"
    CITATION = "citation"
    CO_OCCURRENCE = "co_occurrence"
    HIERARCHICAL = "hierarchical"


# ─── Source Documents ─────────────────────────────────────────────────────────


class SourceCreate(BaseModel):
    """Request to ingest a new document."""
    source_type: SourceType
    title: str = ""
    url: Optional[str] = None
    content: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class Source(BaseModel):
    """A knowledge source document."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_type: SourceType
    title: str
    url: Optional[str] = None
    content_preview: str = ""
    concept_count: int = 0
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)


# ─── Concepts & Nodes ────────────────────────────────────────────────────────


class ConceptCreate(BaseModel):
    """Request to create a concept node."""
    name: str
    node_type: NodeType = NodeType.CONCEPT
    domain: str = ""
    description: str = ""
    source_id: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class Concept(BaseModel):
    """A concept/idea node in the knowledge graph."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    node_type: NodeType
    domain: str = ""
    description: str = ""
    source_ids: list[str] = Field(default_factory=list)
    embedding: Optional[list[float]] = None
    pagerank: float = 0.0
    centrality: float = 0.0
    community_id: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)


# ─── Relationships / Edges ───────────────────────────────────────────────────


class Relationship(BaseModel):
    """An edge in the knowledge graph."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str
    target_id: str
    edge_type: EdgeType
    weight: float = 1.0
    label: str = ""
    metadata: dict = Field(default_factory=dict)


# ─── Collisions ──────────────────────────────────────────────────────────────


class Collision(BaseModel):
    """A discovered conceptual collision between two distant concepts."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    concept_a: Concept
    concept_b: Concept
    domain_a: str = ""
    domain_b: str = ""
    reasoning: str = ""
    novelty_score: float = 0.0
    confidence_score: float = 0.0
    semantic_distance: float = 0.0
    graph_distance: float = 0.0
    bridge_score: float = 0.0
    hypotheses: list[Hypothesis] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)


class CollisionRequest(BaseModel):
    """Request to discover collisions."""
    min_novelty: float = 50.0
    max_results: int = 20
    domains: Optional[list[str]] = None
    algorithm: str = "composite"
    config: dict = Field(default_factory=dict)


# ─── Hypotheses ───────────────────────────────────────────────────────────────


class Hypothesis(BaseModel):
    """A generated hypothesis from a collision."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    collision_id: str = ""
    title: str = ""
    hypothesis_type: str = "research"  # research, startup, insight, combination
    description: str = ""
    reasoning_chain: list[str] = Field(default_factory=list)
    potential_applications: list[str] = Field(default_factory=list)
    novelty_score: float = 0.0
    confidence_score: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ─── Graph Visualization ─────────────────────────────────────────────────────


class GraphNode(BaseModel):
    """Node data for frontend graph visualization."""
    id: str
    name: str
    node_type: str
    domain: str = ""
    val: float = 1.0  # Node size
    color: Optional[str] = None
    community_id: Optional[int] = None
    pagerank: float = 0.0


class GraphLink(BaseModel):
    """Edge data for frontend graph visualization."""
    source: str
    target: str
    edge_type: str
    weight: float = 1.0
    label: str = ""


class GraphData(BaseModel):
    """Complete graph for visualization."""
    nodes: list[GraphNode] = Field(default_factory=list)
    links: list[GraphLink] = Field(default_factory=list)
    stats: dict = Field(default_factory=dict)


# ─── Experiments ──────────────────────────────────────────────────────────────


class ExperimentConfig(BaseModel):
    """Configuration for running an experiment."""
    name: str
    description: str = ""
    algorithms: list[str] = Field(default_factory=list)
    embedding_model: str = "all-MiniLM-L6-v2"
    scoring_weights: dict = Field(default_factory=dict)
    max_collisions: int = 50


class ExperimentResult(BaseModel):
    """Results from an experiment run."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    config: ExperimentConfig
    collisions: list[Collision] = Field(default_factory=list)
    metrics: dict = Field(default_factory=dict)
    duration_seconds: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LeaderboardEntry(BaseModel):
    """A leaderboard entry for algorithm comparison."""
    algorithm: str
    avg_novelty: float = 0.0
    avg_confidence: float = 0.0
    total_collisions: int = 0
    top_collision_score: float = 0.0
    experiment_count: int = 0


# ─── API Responses ────────────────────────────────────────────────────────────


class PaginatedResponse(BaseModel):
    """Generic paginated response."""
    items: list = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    has_next: bool = False


class StatsResponse(BaseModel):
    """Dashboard statistics."""
    total_concepts: int = 0
    total_relationships: int = 0
    total_sources: int = 0
    total_collisions: int = 0
    total_hypotheses: int = 0
    domains: list[str] = Field(default_factory=list)
    top_concepts: list[dict] = Field(default_factory=list)
    recent_collisions: list[dict] = Field(default_factory=list)


# Forward reference resolution
Collision.model_rebuild()
]]>
