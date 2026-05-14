<![CDATA["""
Thought Collision Engine — Ingestion API Routes

Endpoints for uploading and processing knowledge sources.
"""

import uuid
import asyncio
from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, BackgroundTasks
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from api.deps import get_db, get_current_user
from core.database import SourceRecord
from core.models import Source, SourceType, StatsResponse
from pipeline.ingestion.queue import ingestion_queue

router = APIRouter()

# Start the queue worker on startup
@router.on_event("startup")
async def startup_event():
    await ingestion_queue.start_worker()

@router.on_event("shutdown")
async def shutdown_event():
    await ingestion_queue.stop_worker()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    source_type: str = Form("pdf"),
    db: AsyncSession = Depends(get_db)
):
    """Upload a document (PDF, TXT) and queue for processing."""
    source_id = str(uuid.uuid4())
    content = await file.read()
    
    record = SourceRecord(
        id=source_id,
        title=title,
        source_type=source_type,
        status="pending"
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    await ingestion_queue.add_job(source_id, source_type, content, title)
    return {"message": "Job queued", "source": record}


@router.post("/url")
async def ingest_url(url: str, title: str = "Web Page", db: AsyncSession = Depends(get_db)):
    """Queue a web page for ingestion."""
    source_id = str(uuid.uuid4())
    record = SourceRecord(
        id=source_id, title=title, source_type="url", url=url, status="pending"
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    await ingestion_queue.add_job(source_id, "url", url, title)
    return {"message": "Job queued", "source": record}


@router.post("/arxiv")
async def ingest_arxiv(arxiv_id: str, db: AsyncSession = Depends(get_db)):
    """Queue an arXiv paper for ingestion."""
    source_id = str(uuid.uuid4())
    record = SourceRecord(
        id=source_id, title=f"arXiv: {arxiv_id}", source_type="arxiv", url=arxiv_id, status="pending"
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    await ingestion_queue.add_job(source_id, "arxiv", arxiv_id, f"arXiv: {arxiv_id}")
    return {"message": "Job queued", "source": record}


@router.post("/github")
async def ingest_github(repo_url: str, db: AsyncSession = Depends(get_db)):
    """Queue a GitHub repository README for ingestion."""
    source_id = str(uuid.uuid4())
    record = SourceRecord(
        id=source_id, title=repo_url, source_type="github", url=repo_url, status="pending"
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    await ingestion_queue.add_job(source_id, "github", repo_url, repo_url)
    return {"message": "Job queued", "source": record}


@router.post("/text")
async def ingest_text(
    content: str,
    title: str = "Text Input",
    db: AsyncSession = Depends(get_db),
):
    """Queue raw text content for ingestion."""
    source_id = str(uuid.uuid4())
    record = SourceRecord(
        id=source_id, title=title, source_type="text", status="pending"
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    await ingestion_queue.add_job(source_id, "text", content, title)
    return {"message": "Job queued", "source": record}


@router.get("/sources", response_model=list[Source])
async def list_sources(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """List all ingested sources."""
    result = await db.execute(
        select(SourceRecord).offset(skip).limit(limit).order_by(SourceRecord.created_at.desc())
    )
    records = result.scalars().all()

    return [
        Source(
            id=r.id,
            source_type=SourceType(r.source_type),
            title=r.title,
            url=r.url,
            content_preview=r.content_preview,
            concept_count=r.concept_count,
            status=r.status,
            created_at=r.created_at,
        )
        for r in records
    ]


@router.get("/stats")
async def ingestion_stats(db: AsyncSession = Depends(get_db)):
    """Get ingestion statistics."""
    total = await db.execute(select(func.count(SourceRecord.id)))
    by_type = await db.execute(
        select(SourceRecord.source_type, func.count(SourceRecord.id))
        .group_by(SourceRecord.source_type)
    )

    return {
        "total_sources": total.scalar() or 0,
        "by_type": {row[0]: row[1] for row in by_type.all()},
    }
]]>
