<![CDATA["""
GitHub Connector — Fetch README from GitHub repositories.
"""
import httpx
from loguru import logger

class GitHubConnector:
    name = "github"

    async def fetch_readme(self, repo_url: str) -> dict:
        """Fetch README from a GitHub repository."""
        # Extract owner/repo from URL
        parts = repo_url.rstrip("/").split("/")
        if len(parts) >= 2:
            owner, repo = parts[-2], parts[-1]
        else:
            raise ValueError(f"Invalid GitHub URL: {repo_url}")

        api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(api_url, headers={"Accept": "application/vnd.github.v3.raw"})
            if response.status_code == 200:
                content = response.text
            else:
                content = f"Failed to fetch README (status {response.status_code})"

        logger.info("🐙 Fetched GitHub README for {}/{}", owner, repo)
        return {"title": f"{owner}/{repo}", "content": content}
]]>
