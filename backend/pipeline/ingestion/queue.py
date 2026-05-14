<![CDATA["""
Thought Collision Engine — Ingestion Queue
Asynchronous queue for background processing of ingested documents.
"""
import asyncio
from typing import Any
from loguru import logger
from core.events import event_bus
from core.database import get_db, SourceRecord
from pipeline.ingestion.pdf_connector import PDFConnector
from pipeline.ingestion.url_connector import URLConnector
from pipeline.ingestion.arxiv_connector import ArxivConnector
from pipeline.ingestion.github_connector import GitHubConnector
from pipeline.ingestion.text_connector import TextConnector
from sqlalchemy.future import select

class IngestionQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.connectors = {
            "pdf": PDFConnector(),
            "url": URLConnector(),
            "arxiv": ArxivConnector(),
            "github": GitHubConnector(),
            "text": TextConnector(),
        }
        self.worker_task = None

    async def start_worker(self):
        """Start the background worker task."""
        if not self.worker_task:
            self.worker_task = asyncio.create_task(self._worker())
            logger.info("Ingestion Queue worker started.")

    async def stop_worker(self):
        """Stop the background worker."""
        if self.worker_task:
            self.worker_task.cancel()
            self.worker_task = None

    async def add_job(self, source_id: str, source_type: str, source_data: Any, title: str):
        """Add a job to the queue and publish a requested event."""
        job = {
            "source_id": source_id,
            "source_type": source_type,
            "source_data": source_data,
            "title": title
        }
        await self.queue.put(job)
        await event_bus.publish(f"ingestion.requested.{source_id}", job)
        logger.info(f"Added ingestion job {source_id} to queue.")

    async def _worker(self):
        """Background worker that processes the queue."""
        while True:
            try:
                job = await self.queue.get()
                await self._process_job(job)
                self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Queue worker error: {e}")

    async def _process_job(self, job: dict):
        """Process a single ingestion job."""
        source_id = job["source_id"]
        source_type = job["source_type"]
        source_data = job["source_data"]

        await event_bus.publish(f"ingestion.started.{source_id}", {"source_id": source_id, "status": "processing"})
        
        connector = self.connectors.get(source_type)
        if not connector:
            await self._fail_job(source_id, f"Unsupported source type: {source_type}")
            return

        try:
            # Extract Metadata
            metadata = await connector.extract_metadata(source_data)
            await event_bus.publish(f"ingestion.metadata_extracted.{source_id}", {"source_id": source_id, "metadata": metadata})

            # Extract Text
            text = await connector.ingest(source_data)
            
            # Validate
            is_valid, msg = connector.validate(text, metadata)
            if not is_valid:
                await self._fail_job(source_id, f"Validation failed: {msg}")
                return

            metadata["word_count"] = len(text.split())
            
            # Update Database
            async for session in get_db():
                stmt = select(SourceRecord).where(SourceRecord.id == source_id)
                result = await session.execute(stmt)
                record = result.scalar_one_or_none()
                if record:
                    record.content_preview = text[:500] + "..." if len(text) > 500 else text
                    record.status = "completed"
                    record.metadata_ = metadata
                    await session.commit()
                break # Only need one session

            await event_bus.publish(f"ingestion.completed.{source_id}", {
                "source_id": source_id, 
                "status": "completed",
                "metadata": metadata
            })
            logger.info(f"Successfully processed ingestion job {source_id}")

        except Exception as e:
            await self._fail_job(source_id, str(e))

    async def _fail_job(self, source_id: str, error_msg: str):
        """Handle a failed job."""
        logger.error(f"Job {source_id} failed: {error_msg}")
        async for session in get_db():
            stmt = select(SourceRecord).where(SourceRecord.id == source_id)
            result = await session.execute(stmt)
            record = result.scalar_one_or_none()
            if record:
                record.status = "failed"
                await session.commit()
            break
        await event_bus.publish(f"ingestion.failed.{source_id}", {"source_id": source_id, "error": error_msg})

ingestion_queue = IngestionQueue()
]]>
