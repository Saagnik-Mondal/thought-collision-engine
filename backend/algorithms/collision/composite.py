<![CDATA["""
Composite Collision Algorithm — Combines all scoring methods.

This is the primary collision discovery algorithm that orchestrates
graph distance, semantic distance, and bridge scoring to find
the most novel and potentially useful conceptual collisions.
"""
from itertools import combinations
from loguru import logger
from core.neo4j_client import Neo4jClient
from core.vector_store import VectorStore
from core.models import Concept
from algorithms.collision.graph_distance import GraphDistanceScorer
from algorithms.collision.semantic_distance import SemanticDistanceScorer
from algorithms.collision.bridge_scoring import BridgeScorer

class CompositeCollisionAlgorithm:
    name = "composite"

    def __init__(self, neo4j: Neo4jClient, vector_store: VectorStore):
        self.neo4j = neo4j
        self.vs = vector_store
        self.graph_scorer = GraphDistanceScorer()
        self.semantic_scorer = SemanticDistanceScorer()
        self.bridge_scorer = BridgeScorer()

    async def discover(self, max_results: int = 20, domains: list[str] = None, config: dict = None) -> list[dict]:
        """Discover collision candidates across the concept graph."""
        config = config or {}
        w_graph = config.get("weight_graph", 0.3)
        w_semantic = config.get("weight_semantic", 0.4)
        w_bridge = config.get("weight_bridge", 0.3)

        # Get all concepts
        where = ""
        params = {"limit": 200}
        if domains:
            where = "WHERE c.domain IN $domains"
            params["domains"] = domains

        nodes = await self.neo4j.execute_read(f"""
            MATCH (c:Concept) {where}
            RETURN c.id AS id, c.name AS name, c.node_type AS node_type,
                   c.domain AS domain, c.description AS description
            ORDER BY c.pagerank DESC
            LIMIT $limit
        """, params)

        if len(nodes) < 2:
            return []

        # Score all pairs from different domains
        candidates = []
        pairs = list(combinations(nodes, 2))
        logger.info("Evaluating {} concept pairs for collisions", len(pairs))

        for node_a, node_b in pairs:
            # Skip same-domain pairs (less novel)
            if node_a.get("domain") and node_a["domain"] == node_b.get("domain"):
                continue

            id_a, id_b = node_a["id"], node_b["id"]

            # Score components
            graph_score = await self.graph_scorer.score(self.neo4j, id_a, id_b)
            semantic_score = self.semantic_scorer.score(self.vs, id_a, id_b)
            bridge_score = await self.bridge_scorer.score(self.neo4j, id_a, id_b)

            composite = (w_graph * graph_score + w_semantic * semantic_score + w_bridge * bridge_score)
            confidence = min(100, composite * 100 * 0.85)

            if composite > 0.4:  # Threshold
                concept_a = Concept(id=id_a, name=node_a["name"],
                    node_type=node_a.get("node_type", "concept"), domain=node_a.get("domain", ""))
                concept_b = Concept(id=id_b, name=node_b["name"],
                    node_type=node_b.get("node_type", "concept"), domain=node_b.get("domain", ""))

                reasoning = self._generate_reasoning(node_a, node_b, graph_score, semantic_score, bridge_score)

                candidates.append({
                    "concept_a": concept_a, "concept_b": concept_b,
                    "domain_a": node_a.get("domain", ""), "domain_b": node_b.get("domain", ""),
                    "reasoning": reasoning,
                    "composite_score": composite,
                    "confidence": confidence,
                    "semantic_distance": semantic_score,
                    "graph_distance": graph_score,
                    "bridge_score": bridge_score,
                })

        # Sort by composite score
        candidates.sort(key=lambda x: x["composite_score"], reverse=True)
        logger.info("Found {} collision candidates above threshold", len(candidates))
        return candidates[:max_results]

    def _generate_reasoning(self, node_a: dict, node_b: dict, graph_s: float, semantic_s: float, bridge_s: float) -> str:
        """Generate human-readable reasoning for the collision."""
        name_a, name_b = node_a["name"], node_b["name"]
        domain_a = node_a.get("domain", "unknown")
        domain_b = node_b.get("domain", "unknown")

        parts = [f"'{name_a}' ({domain_a}) and '{name_b}' ({domain_b}) are concepts from different domains"]
        if graph_s > 0.7:
            parts.append("that are far apart in the knowledge graph, suggesting no previously known connection")
        if semantic_s > 0.6:
            parts.append("yet share hidden semantic similarities that suggest transferable principles")
        if bridge_s > 0.7:
            parts.append("and connecting them would bridge separate knowledge communities")
        parts.append(". This collision has high potential for novel cross-domain insights.")
        return " ".join(parts)
]]>
