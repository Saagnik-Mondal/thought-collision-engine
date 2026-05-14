<![CDATA["""
arXiv Connector — Fetch papers from arXiv API.
"""
import asyncio
from loguru import logger

class ArxivConnector:
    name = "arxiv"

    async def fetch_paper(self, arxiv_id: str) -> dict:
        """Fetch an arXiv paper by ID."""
        try:
            import arxiv
            client = arxiv.Client()
            search = arxiv.Search(id_list=[arxiv_id])
            results = list(client.results(search))
            if not results:
                raise ValueError(f"No paper found for ID: {arxiv_id}")
            paper = results[0]
            logger.info("📄 Fetched arXiv paper: {}", paper.title)
            return {
                "title": paper.title,
                "abstract": paper.summary,
                "authors": [str(a) for a in paper.authors],
                "url": str(paper.entry_id),
                "categories": paper.categories,
                "published": str(paper.published),
            }
        except ImportError:
            logger.warning("arxiv package not installed")
            return {"title": f"arXiv:{arxiv_id}", "abstract": "", "url": f"https://arxiv.org/abs/{arxiv_id}"}
]]>
