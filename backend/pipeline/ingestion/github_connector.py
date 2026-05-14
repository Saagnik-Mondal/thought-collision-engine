<![CDATA["""
GitHub Connector — Fetch README from GitHub repositories.
"""
import httpx
from loguru import logger
from pipeline.ingestion.base import BaseConnector

class GitHubConnector(BaseConnector):
    name = "github"
    description = "Fetches repository README and metadata"
    supported_types = ["github"]

    def _parse_url(self, repo_url: str):
        parts = repo_url.rstrip("/").split("/")
        if len(parts) >= 2:
            return parts[-2], parts[-1]
        raise ValueError("Invalid GitHub URL")

    async def ingest(self, source: str, **kwargs) -> str:
        try:
            owner, repo = self._parse_url(source)
            api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(api_url, headers={"Accept": "application/vnd.github.v3.raw"})
                if response.status_code == 200:
                    return response.text
            return ""
        except Exception as e:
            logger.error("GitHub ingestion failed: {}", e)
            return ""

    async def extract_metadata(self, source: str, **kwargs) -> dict:
        try:
            owner, repo = self._parse_url(source)
            api_url = f"https://api.github.com/repos/{owner}/{repo}"
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(api_url, headers={"Accept": "application/vnd.github.v3+json"})
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "owner": owner,
                        "repo": repo,
                        "stars": data.get("stargazers_count", 0),
                        "language": data.get("language", "Unknown"),
                        "description": data.get("description", ""),
                        "updated_at": data.get("updated_at", "")
                    }
            return {}
        except Exception:
            return {}
]]>
