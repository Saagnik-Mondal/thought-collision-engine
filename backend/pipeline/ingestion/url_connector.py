<![CDATA["""
URL Connector — Fetch and extract text from web pages.
"""
import httpx
from bs4 import BeautifulSoup
from loguru import logger

class URLConnector:
    name = "url"

    async def fetch_content(self, url: str) -> str:
        """Fetch URL and extract text content."""
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            response = await client.get(url, headers={"User-Agent": "ThoughtCollisionEngine/0.1"})
            response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        logger.info("🌐 Extracted {} characters from {}", len(text), url)
        return text
]]>
