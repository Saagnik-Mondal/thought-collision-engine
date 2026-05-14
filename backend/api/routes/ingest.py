<![CDATA["""
Thought Collision Engine — Ingestion API Routes

Endpoints for uploading and processing knowledge sources.
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from api.deps import get_db
from core.database import SourceRecord
from core.models import Source, SourceType, StatsResponse
from pipeline.ingestion.pdf_connector import PDFConnector
from pipeline.ingestion.url_connector import URLConnector
from pipeline.ingestion.text_connector import TextConnector
from pipeline.ingestion.arxiv_connector import ArxivConnector
from pipeline.ingestion.github_connector import GitHubConnector

router = APIRouter()


@router.post("/upload", response_model=Source)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(""),
    source_type: str = Form("pdf"),
    db: AsyncSession = Depends(get_db),
):
    """Upload a document for ingestion."""
    source_id = str(uuid.uuid4())
    file_content = await file.read()

    # Determine connector
    if source_type == "pdf":
        connector = PDFConnector()
        text = connector.extract_text(file_content)
    else:
        connector = TextConnector()
        text = file_content.decode("utf-8", errors="ignore")

    title = title or file.filename or "Untitled"
    preview = text[:500] if text else ""

    # Save to database
    record = SourceRecord(
        id=source_id,
        source_type=source_type,
        title=title,
        content_preview=preview,
        status="ingested",
    )
    db.add(record)
    await db.commit()

    logger.info("📥 Ingested document: {} ({})", title, source_type)

    return Source(
        id=source_id,
        source_type=SourceType(source_type),
        title=title,
        content_preview=preview,
        status="ingested",
    )


@router.post("/url", response_model=Source)
async def ingest_url(
    url: str,
    title: str = "",
    db: AsyncSession = Depends(get_db),
):
    """Ingest content from a URL."""
    source_id = str(uuid.uuid4())
    connector = URLConnector()

    try:
        text = await connector.fetch_content(url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {e}")

    title = title or url
    preview = text[:500] if text else ""

    record = SourceRecord(
        id=source_id,
        source_type="url",
        title=title,
        url=url,
        content_preview=preview,
        status="ingested",
    )
    db.add(record)
    await db.commit()

    logger.info("🌐 Ingested URL: {}", url)

    return Source(
        id=source_id,
        source_type=SourceType.URL,
        title=title,
        url=url,
        content_preview=preview,
        status="ingested",
    )


@router.post("/arxiv", response_model=Source)
async def ingest_arxiv(
    arxiv_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Ingest an arXiv paper by ID."""
    source_id = str(uuid.uuid4())
    connector = ArxivConnector()

    try:
        paper = await connector.fetch_paper(arxiv_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch arXiv paper: {e}")

    record = SourceRecord(
        id=source_id,
        source_type="arxiv",
        title=paper["title"],
        url=paper["url"],
        content_preview=paper["abstract"][:500],
        status="ingested",
    )
    db.add(record)
    await db.commit()

    logger.info("📄 Ingested arXiv paper: {}", paper["title"])

    return Source(
        id=source_id,
        source_type=SourceType.ARXIV,
        title=paper["title"],
        url=paper["url"],
        content_preview=paper["abstract"][:500],
        status="ingested",
    )


@router.post("/github", response_model=Source)
async def ingest_github(
    repo_url: str,
    db: AsyncSession = Depends(get_db),
):
    """Ingest a GitHub repository README."""
    source_id = str(uuid.uuid4())
    connector = GitHubConnector()

    try:
        repo_data = await connector.fetch_readme(repo_url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch GitHub repo: {e}")

    record = SourceRecord(
        id=source_id,
        source_type="github",
        title=repo_data["title"],
        url=repo_url,
        content_preview=repo_data["content"][:500],
        status="ingested",
    )
    db.add(record)
    await db.commit()

    logger.info("🐙 Ingested GitHub repo: {}", repo_data["title"])

    return Source(
        id=source_id,
        source_type=SourceType.GITHUB,
        title=repo_data["title"],
        url=repo_url,
        content_preview=repo_data["content"][:500],
        status="ingested",
    )


@router.post("/text", response_model=Source)
async def ingest_text(
    content: str,
    title: str = "Text Input",
    db: AsyncSession = Depends(get_db),
):
    """Ingest raw text content."""
    source_id = str(uuid.uuid4())
    preview = content[:500]

    record = SourceRecord(
        id=source_id,
        source_type="text",
        title=title,
        content_preview=preview,
        status="ingested",
    )
    db.add(record)
    await db.commit()

    logger.info("📝 Ingested text: {}", title)

    return Source(
        id=source_id,
        source_type=SourceType.TEXT,
        title=title,
        content_preview=preview,
        status="ingested",
    )


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
