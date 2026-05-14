<![CDATA["""
PDF Connector — Extract text from PDF documents using PyMuPDF.
"""
from loguru import logger
from pipeline.ingestion.base import BaseConnector

class PDFConnector(BaseConnector):
    name = "pdf"
    description = "Extracts text from PDF documents"
    supported_types = ["pdf"]

    async def ingest(self, source: bytes, **kwargs) -> str:
        try:
            import fitz
            doc = fitz.open(stream=source, filetype="pdf")
            text = "\n".join([page.get_text() for page in doc])
            doc.close()
            return text
        except Exception as e:
            logger.error("PDF extraction failed: {}", e)
            return ""

    async def extract_metadata(self, source: bytes, **kwargs) -> dict:
        try:
            import fitz
            doc = fitz.open(stream=source, filetype="pdf")
            meta = doc.metadata
            doc.close()
            return {
                "author": meta.get("author", "Unknown"),
                "creation_date": meta.get("creationDate", ""),
                "creator": meta.get("creator", "Unknown"),
                "pages": doc.page_count
            }
        except Exception:
            return {}
]]>
