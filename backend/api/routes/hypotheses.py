<![CDATA["""
Thought Collision Engine — Hypotheses API Routes
"""

import uuid
from fastapi import APIRouter, Depends, Query, HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.deps import get_db
from core.database import HypothesisRecord, CollisionRecord
from core.models import Hypothesis
from algorithms.hypothesis.generator import HypothesisGenerator

router = APIRouter()


@router.post("/generate/{collision_id}", response_model=list[Hypothesis])
async def generate_hypotheses(collision_id: str, count: int = Query(3, ge=1, le=10), db: AsyncSession = Depends(get_db)):
    """Generate hypotheses for a specific collision."""
    result = await db.execute(select(CollisionRecord).where(CollisionRecord.id == collision_id))
    rec = result.scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Collision not found")

    generator = HypothesisGenerator()
    hypotheses = generator.generate(
        domain_a=rec.domain_a, domain_b=rec.domain_b,
        reasoning=rec.reasoning, novelty_score=rec.novelty_score,
        confidence_score=rec.confidence_score, count=count,
    )
    for h in hypotheses:
        h.collision_id = collision_id
        db.add(HypothesisRecord(id=h.id, collision_id=collision_id, title=h.title,
            hypothesis_type=h.hypothesis_type, description=h.description,
            reasoning_chain=h.reasoning_chain, potential_applications=h.potential_applications,
            novelty_score=h.novelty_score, confidence_score=h.confidence_score))
    await db.commit()
    return hypotheses


@router.get("/", response_model=list[Hypothesis])
async def list_hypotheses(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    """List generated hypotheses."""
    result = await db.execute(
        select(HypothesisRecord).order_by(HypothesisRecord.novelty_score.desc()).offset(skip).limit(limit)
    )
    return [Hypothesis(id=r.id, collision_id=r.collision_id, title=r.title,
        hypothesis_type=r.hypothesis_type, description=r.description,
        reasoning_chain=r.reasoning_chain or [], potential_applications=r.potential_applications or [],
        novelty_score=r.novelty_score, confidence_score=r.confidence_score, created_at=r.created_at)
        for r in result.scalars().all()]


@router.get("/{hypothesis_id}", response_model=Hypothesis)
async def get_hypothesis(hypothesis_id: str, db: AsyncSession = Depends(get_db)):
    """Get a single hypothesis."""
    result = await db.execute(select(HypothesisRecord).where(HypothesisRecord.id == hypothesis_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Hypothesis not found")
    return Hypothesis(id=r.id, collision_id=r.collision_id, title=r.title,
        hypothesis_type=r.hypothesis_type, description=r.description,
        reasoning_chain=r.reasoning_chain or [], potential_applications=r.potential_applications or [],
        novelty_score=r.novelty_score, confidence_score=r.confidence_score, created_at=r.created_at)
]]>
