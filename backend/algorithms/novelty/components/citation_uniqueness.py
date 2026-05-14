<![CDATA["""
Citation Uniqueness Component for Novelty Scoring.
Checks if the concepts have ever co-occurred in the same source.
"""
from core.neo4j_client import Neo4jClient

class CitationUniquenessComponent:
    name = "citation_uniqueness"
    
    def __init__(self, neo4j: Neo4jClient):
        self.neo4j = neo4j
        
    async def score(self, concept_a_id: str, concept_b_id: str) -> float:
        """
        Returns novelty score (0.0 to 1.0).
        1.0 if they share NO common Source documents.
        Lower if they frequently appear together.
        """
        query = """
        MATCH (s:Source)-[:HAS_CONCEPT]->(a:Concept {id: $id_a})
        MATCH (s)-[:HAS_CONCEPT]->(b:Concept {id: $id_b})
        RETURN count(DISTINCT s) AS intersection_count
        """
        result = await self.neo4j.execute_read(query, {"id_a": concept_a_id, "id_b": concept_b_id})
        
        count = result[0]["intersection_count"] if result else 0
        
        if count == 0:
            return 1.0
        
        # Decay novelty rapidly if they co-occur
        score = max(0.0, 1.0 - (count * 0.2))
        return round(score, 3)

    def explain(self, score: float) -> str:
        if score == 1.0:
            return "Have never been cited or mentioned together in any ingested document."
        elif score > 0.0:
            return "Have rarely appeared together in the same context."
        else:
            return "Frequently co-occur in the same documents."
]]>
