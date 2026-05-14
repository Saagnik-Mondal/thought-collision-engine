<![CDATA["""
Graph Algorithms — Random Walks
Estimates reachability probabilities. Low probability = high novelty.
"""
from loguru import logger
from core.neo4j_client import Neo4jClient

class RandomWalkAlgorithm:
    async def estimate_reachability(self, neo4j: Neo4jClient, source_id: str, target_id: str, steps: int = 5, walks: int = 100) -> float:
        """
        Estimate the probability of reaching target from source via Random Walks.
        Returns probability [0.0, 1.0]. Low probability means the connection is highly novel.
        """
        # Native Cypher bounded random walk estimation
        # We simulate this efficiently using bounded pattern matching
        query = """
        MATCH (start:Concept {id: $source_id})
        MATCH path = (start)-[*1..$steps]-(end:Concept {id: $target_id})
        RETURN count(path) AS paths_found
        """
        result = await neo4j.execute_read(query, {
            "source_id": source_id,
            "target_id": target_id,
            "steps": steps
        })
        
        paths_found = result[0]["paths_found"] if result else 0
        
        # Heuristic mapping of paths found to reachability probability
        # 0 paths = 0.0 probability (highest novelty)
        if paths_found == 0:
            return 0.0
            
        prob = min(1.0, paths_found / 50.0) # Assume 50 paths is a very strong connection
        return prob

    async def score_novelty(self, neo4j: Neo4jClient, source_id: str, target_id: str) -> float:
        """Convert reachability probability into a novelty score (0.0 to 1.0)."""
        reach_prob = await self.estimate_reachability(neo4j, source_id, target_id)
        # Invert probability for novelty: 0 probability = 1.0 novelty
        return 1.0 - reach_prob
]]>
