<![CDATA["""
Thought Collision Engine — Collisions API Routes

Endpoints for discovering and managing conceptual collisions.
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from api.deps import get_db, get_neo4j, get_vector_store
from core.database import CollisionRecord
from core.models import Collision, CollisionRequest, Concept
from core.neo4j_client import Neo4jClient
from core.vector_store import VectorStore
from algorithms.collision.composite import CompositeCollisionAlgorithm
from algorithms.novelty.scorer import NoveltyScorer

router = APIRouter()


@router.post("/discover", response_model=list[Collision])
async def discover_collisions(
    request: CollisionRequest,
    db: AsyncSession = Depends(get_db),
    neo4j: Neo4jClient = Depends(get_neo4j),
    vs: VectorStore = Depends(get_vector_store),
):
    """Run collision discovery algorithm to find hidden connections."""
    logger.info("💥 Running collision discovery (algorithm={}, min_novelty={})",
                request.algorithm, request.min_novelty)

    # Initialize algorithm
    algorithm = CompositeCollisionAlgorithm(neo4j=neo4j, vector_store=vs)
    scorer = NoveltyScorer()

    # Discover collisions
    raw_collisions = await algorithm.discover(
        max_results=request.max_results,
        domains=request.domains,
        config=request.config,
    )

    # Score and filter
    collisions = []
    for raw in raw_collisions:
        novelty = scorer.score(raw)
        if novelty >= request.min_novelty:
            collision = Collision(
                id=str(uuid.uuid4()),
                concept_a=raw["concept_a"],
                concept_b=raw["concept_b"],
                domain_a=raw.get("domain_a", ""),
                domain_b=raw.get("domain_b", ""),
                reasoning=raw.get("reasoning", ""),
                novelty_score=novelty,
                confidence_score=raw.get("confidence", 0),
                semantic_distance=raw.get("semantic_distance", 0),
                graph_distance=raw.get("graph_distance", 0),
                bridge_score=raw.get("bridge_score", 0),
            )
            collisions.append(collision)

            # Persist
            record = CollisionRecord(
                id=collision.id,
                concept_a_id=collision.concept_a.id,
                concept_b_id=collision.concept_b.id,
                domain_a=collision.domain_a,
                domain_b=collision.domain_b,
                reasoning=collision.reasoning,
                novelty_score=collision.novelty_score,
                confidence_score=collision.confidence_score,
                semantic_distance=collision.semantic_distance,
                graph_distance=collision.graph_distance,
                bridge_score=collision.bridge_score,
            )
            db.add(record)

    await db.commit()

    # Sort by novelty
    collisions.sort(key=lambda c: c.novelty_score, reverse=True)

    logger.info("💥 Found {} collisions above threshold", len(collisions))
    return collisions[:request.max_results]


@router.get("/", response_model=list[Collision])
async def list_collisions(
    skip: int = 0,
    limit: int = 20,
    min_novelty: float = 0,
    db: AsyncSession = Depends(get_db),
    neo4j: Neo4jClient = Depends(get_neo4j),
):
    """List previously discovered collisions."""
    query = select(CollisionRecord).where(
        CollisionRecord.novelty_score >= min_novelty
    ).order_by(
        CollisionRecord.novelty_score.desc()
    ).offset(skip).limit(limit)

    result = await db.execute(query)
    records = result.scalars().all()

    collisions = []
    for r in records:
        # Fetch concept details from Neo4j
        concept_a_data = await neo4j.execute_read(
            "MATCH (c:Concept {id: $id}) RETURN c.id AS id, c.name AS name, c.node_type AS node_type, c.domain AS domain",
            {"id": r.concept_a_id}
        )
        concept_b_data = await neo4j.execute_read(
            "MATCH (c:Concept {id: $id}) RETURN c.id AS id, c.name AS name, c.node_type AS node_type, c.domain AS domain",
            {"id": r.concept_b_id}
        )

        concept_a = Concept(
            id=r.concept_a_id,
            name=concept_a_data[0]["name"] if concept_a_data else "Unknown",
            node_type=concept_a_data[0].get("node_type", "concept") if concept_a_data else "concept",
            domain=concept_a_data[0].get("domain", "") if concept_a_data else "",
        )
        concept_b = Concept(
            id=r.concept_b_id,
            name=concept_b_data[0]["name"] if concept_b_data else "Unknown",
            node_type=concept_b_data[0].get("node_type", "concept") if concept_b_data else "concept",
            domain=concept_b_data[0].get("domain", "") if concept_b_data else "",
        )

        collisions.append(Collision(
            id=r.id,
            concept_a=concept_a,
            concept_b=concept_b,
            domain_a=r.domain_a,
            domain_b=r.domain_b,
            reasoning=r.reasoning,
            novelty_score=r.novelty_score,
            confidence_score=r.confidence_score,
            semantic_distance=r.semantic_distance,
            graph_distance=r.graph_distance,
            bridge_score=r.bridge_score,
            created_at=r.created_at,
        ))

    return collisions


@router.get("/stats")
async def collision_stats(db: AsyncSession = Depends(get_db)):
    """Get collision discovery statistics."""
    total = await db.execute(select(func.count(CollisionRecord.id)))
    avg_novelty = await db.execute(select(func.avg(CollisionRecord.novelty_score)))
    max_novelty = await db.execute(select(func.max(CollisionRecord.novelty_score)))

    return {
        "total_collisions": total.scalar() or 0,
        "avg_novelty_score": round(avg_novelty.scalar() or 0, 2),
        "max_novelty_score": round(max_novelty.scalar() or 0, 2),
    }
]]>
