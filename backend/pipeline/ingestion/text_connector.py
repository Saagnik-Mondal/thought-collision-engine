<![CDATA["""
Text Connector — Process raw text input.
"""
from pipeline.ingestion.base import BaseConnector

class TextConnector(BaseConnector):
    name = "text"
    description = "Processes raw text input"
    supported_types = ["text"]

    async def ingest(self, source: str | bytes, **kwargs) -> str:
        if isinstance(source, bytes):
            return source.decode("utf-8", errors="ignore")
        return source

    async def extract_metadata(self, source: str | bytes, **kwargs) -> dict:
        text = await self.ingest(source)
        return {
            "word_count": len(text.split()),
            "char_count": len(text)
        }
]]>
