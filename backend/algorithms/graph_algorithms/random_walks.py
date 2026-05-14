<![CDATA["""
Random Walks — Explore the concept graph via random traversals.
"""
import random
from loguru import logger
from core.neo4j_client import Neo4jClient

class RandomWalks:
    name = "random_walks"

    async def walk(self, neo4j: Neo4jClient, start_id: str, steps: int = 10, walks: int = 5) -> list[list[dict]]:
        """Perform random walks from a starting node."""
        all_walks = []
        for _ in range(walks):
            path = [{"id": start_id}]
            current = start_id
            for _ in range(steps):
                neighbors = await neo4j.execute_read("""
                    MATCH (c:Concept {id: $id})-[r]-(n:Concept)
                    RETURN n.id AS id, n.name AS name, n.domain AS domain, r.weight AS weight
                """, {"id": current})
                if not neighbors:
                    break
                # Weighted random selection
                weights = [n.get("weight", 1) or 1 for n in neighbors]
                total = sum(weights)
                probs = [w/total for w in weights]
                chosen = random.choices(neighbors, weights=probs, k=1)[0]
                path.append(chosen)
                current = chosen["id"]
            all_walks.append(path)
        return all_walks
]]>
