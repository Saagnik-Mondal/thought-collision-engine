<![CDATA["""
Base Collision Algorithm Interface.
"""
from abc import ABC, abstractmethod

class BaseCollisionAlgorithm(ABC):
    name: str = "base"

    @abstractmethod
    async def discover(self, max_results: int = 20, domains: list[str] = None, config: dict = None) -> list[dict]:
        """Discover collision candidates. Returns list of raw collision dicts."""
        pass
]]>
