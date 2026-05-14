<![CDATA["""
Concept Diversity Component for Novelty Scoring.
Measures the Jaccard Distance of the surrounding domain neighborhoods.
"""
from core.neo4j_client import Neo4jClient

class ConceptDiversityComponent:
    name = "concept_diversity"
    
    def __init__(self, neo4j: Neo4jClient):
        self.neo4j = neo4j
        
    async def score(self, concept_a_id: str, concept_b_id: str) -> float:
        """
        Returns novelty score (0.0 to 1.0).
        Calculates Jaccard Distance (1 - Jaccard Index) of 1-hop neighbor domains.
        Completely non-overlapping domain neighborhoods = 1.0 diversity.
        """
        query = """
        MATCH (a:Concept {id: $id})-[]-(neighbor:Concept)
        WHERE neighbor.domain IS NOT NULL AND neighbor.domain <> ''
        RETURN collect(DISTINCT neighbor.domain) AS domains
        """
        
        res_a = await self.neo4j.execute_read(query, {"id": concept_a_id})
        res_b = await self.neo4j.execute_read(query, {"id": concept_b_id})
        
        domains_a = set(res_a[0]["domains"]) if res_a and res_a[0]["domains"] else set()
        domains_b = set(res_b[0]["domains"]) if res_b and res_b[0]["domains"] else set()
        
        if not domains_a and not domains_b:
            return 0.5 # Unknown diversity
            
        intersection = domains_a.intersection(domains_b)
        union = domains_a.union(domains_b)
        
        if not union:
            return 0.5
            
        jaccard_index = len(intersection) / len(union)
        jaccard_distance = 1.0 - jaccard_index
        return round(jaccard_distance, 3)

    def explain(self, score: float) -> str:
        if score > 0.8:
            return "Belong to completely distinct intellectual neighborhoods with no overlapping domains."
        elif score > 0.4:
            return "Have partially overlapping domain neighborhoods."
        else:
            return "Are surrounded by identical fields of study."
]]>
