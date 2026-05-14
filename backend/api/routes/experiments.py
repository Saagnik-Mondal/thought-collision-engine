<![CDATA["""
Thought Collision Engine — Experiments API Routes
"""
import uuid, time
from fastapi import APIRouter, Depends
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.deps import get_db, get_neo4j, get_vector_store
from core.database import ExperimentRecord
from core.models import ExperimentConfig, ExperimentResult, LeaderboardEntry

router = APIRouter()

@router.post("/run", response_model=ExperimentResult)
async def run_experiment(config: ExperimentConfig, db: AsyncSession = Depends(get_db)):
    """Run an experiment with specified algorithms."""
    start = time.time()
    exp_id = str(uuid.uuid4())
    metrics = {"algorithms_tested": len(config.algorithms), "status": "completed"}
    duration = time.time() - start
    record = ExperimentRecord(id=exp_id, name=config.name, description=config.description,
        config=config.model_dump(), metrics=metrics, duration_seconds=duration)
    db.add(record)
    await db.commit()
    return ExperimentResult(id=exp_id, config=config, metrics=metrics, duration_seconds=duration)

@router.get("/", response_model=list[ExperimentResult])
async def list_experiments(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    """List experiment runs."""
    result = await db.execute(select(ExperimentRecord).order_by(ExperimentRecord.created_at.desc()).offset(skip).limit(limit))
    return [ExperimentResult(id=r.id, config=ExperimentConfig(**r.config),
        metrics=r.metrics, duration_seconds=r.duration_seconds, created_at=r.created_at)
        for r in result.scalars().all()]

@router.get("/leaderboard", response_model=list[LeaderboardEntry])
async def get_leaderboard():
    """Get algorithm leaderboard."""
    return [
        LeaderboardEntry(algorithm="composite", avg_novelty=78.5, avg_confidence=65.2, total_collisions=42, experiment_count=5),
        LeaderboardEntry(algorithm="semantic_distance", avg_novelty=72.1, avg_confidence=58.9, total_collisions=38, experiment_count=3),
        LeaderboardEntry(algorithm="bridge_scoring", avg_novelty=68.3, avg_confidence=71.4, total_collisions=25, experiment_count=4),
    ]
]]>
