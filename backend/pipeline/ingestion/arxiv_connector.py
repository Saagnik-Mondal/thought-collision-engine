<![CDATA["""
arXiv Connector — Fetch papers from arXiv API.
"""
from loguru import logger
from pipeline.ingestion.base import BaseConnector

class ArxivConnector(BaseConnector):
    name = "arxiv"
    description = "Fetches abstracts and metadata from arXiv"
    supported_types = ["arxiv"]

    async def ingest(self, source: str, **kwargs) -> str:
        try:
            import arxiv
            client = arxiv.Client()
            search = arxiv.Search(id_list=[source])
            results = list(client.results(search))
            if not results:
                return ""
            return results[0].summary
        except Exception as e:
            logger.error("arXiv ingestion failed: {}", e)
            return ""

    async def extract_metadata(self, source: str, **kwargs) -> dict:
        try:
            import arxiv
            client = arxiv.Client()
            search = arxiv.Search(id_list=[source])
            results = list(client.results(search))
            if not results:
                return {}
            paper = results[0]
            return {
                "title": paper.title,
                "authors": [str(a) for a in paper.authors],
                "url": str(paper.entry_id),
                "categories": paper.categories,
                "published": str(paper.published),
            }
        except Exception:
            return {}
]]>
