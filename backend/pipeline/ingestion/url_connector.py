<![CDATA["""
URL Connector — Fetch and extract text from web pages.
"""
import httpx
from bs4 import BeautifulSoup
from loguru import logger
from pipeline.ingestion.base import BaseConnector

class URLConnector(BaseConnector):
    name = "url"
    description = "Fetches and extracts text from web pages"
    supported_types = ["url"]

    async def ingest(self, source: str, **kwargs) -> str:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            response = await client.get(source, headers={"User-Agent": "ThoughtCollisionEngine/0.1"})
            response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)

    async def extract_metadata(self, source: str, **kwargs) -> dict:
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
                response = await client.get(source, headers={"User-Agent": "ThoughtCollisionEngine/0.1"})
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string if soup.title else "Unknown"
            description = ""
            desc_tag = soup.find("meta", attrs={"name": "description"})
            if desc_tag and "content" in desc_tag.attrs:
                description = desc_tag["content"]
            return {"url": source, "title": title, "description": description}
        except Exception:
            return {"url": source}
]]>
