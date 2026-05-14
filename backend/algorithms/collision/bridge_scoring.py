<![CDATA["""
Bridge Scoring — Score based on bridge node potential.
"""
from core.neo4j_client import Neo4jClient

class BridgeScorer:
    name = "bridge_scoring"

    async def score(self, neo4j: Neo4jClient, id_a: str, id_b: str) -> float:
        """Score based on whether the pair would create a valuable bridge."""
        # Check community membership
        result = await neo4j.execute_read("""
            MATCH (a:Concept {id: $id_a}), (b:Concept {id: $id_b})
            RETURN a.community_id AS comm_a, b.community_id AS comm_b,
                   a.domain AS domain_a, b.domain AS domain_b
        """, {"id_a": id_a, "id_b": id_b})

        if not result:
            return 0.5

        r = result[0]
        score = 0.5

        # Different communities = higher bridge score
        if r.get("comm_a") is not None and r.get("comm_b") is not None:
            if r["comm_a"] != r["comm_b"]:
                score += 0.3

        # Different domains = higher score
        if r.get("domain_a") and r.get("domain_b"):
            if r["domain_a"] != r["domain_b"]:
                score += 0.2

        return min(1.0, score)
]]>
