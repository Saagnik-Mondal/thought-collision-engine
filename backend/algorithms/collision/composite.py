<![CDATA["""
Composite Collision Algorithm — Scalable Candidate Generation and Orchestration.
"""
from loguru import logger
from core.neo4j_client import Neo4jClient
from core.vector_store import VectorStore
from core.models import Concept
from algorithms.collision.semantic_distance import SemanticDistanceScorer
from algorithms.graph_algorithms.pagerank import PageRankAlgorithm
from algorithms.graph_algorithms.community_detection import CommunityDetection
from algorithms.graph_algorithms.shortest_paths import ShortestPathAlgorithm
from algorithms.graph_algorithms.random_walks import RandomWalkAlgorithm

class CompositeCollisionAlgorithm:
    name = "composite_v2"

    def __init__(self, neo4j: Neo4jClient, vector_store: VectorStore):
        self.neo4j = neo4j
        self.vs = vector_store
        self.semantic_scorer = SemanticDistanceScorer(vector_store)
        self.pagerank = PageRankAlgorithm()
        self.community = CommunityDetection()
        self.shortest_path = ShortestPathAlgorithm()
        self.random_walk = RandomWalkAlgorithm()

    async def prepare_graph(self):
        """Run necessary background graph algorithms."""
        await self.pagerank.run(self.neo4j)
        await self.community.run(self.neo4j)

    async def discover(self, max_results: int = 20, config: dict = None) -> list[dict]:
        """Scalable Discovery: Seeds -> Vector Search -> Graph Scoring."""
        config = config or {}
        w_semantic = config.get("weight_semantic", 0.4)
        w_structural = config.get("weight_structural", 0.3)
        w_bridge = config.get("weight_bridge", 0.3)

        # 1. Get High Centrality Seed Concepts
        seeds = await self.pagerank.get_top_concepts(self.neo4j, limit=20)
        if not seeds:
            logger.warning("No seeds found. Have you ingested and built the graph?")
            return []

        candidates = []
        seen_pairs = set()

        # 2. Iterate seeds and fetch sweet-spot semantic candidates
        for seed in seeds:
            seed_id = seed["id"]
            
            sweet_spot_matches = await self.semantic_scorer.get_sweet_spot_candidates(seed_id, top_k=10)
            
            for match in sweet_spot_matches:
                match_id = match["id"]
                
                # Deduplicate A-B and B-A
                pair_key = tuple(sorted([seed_id, match_id]))
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)
                
                # 3. Run heavy graph algorithms on this curated pair
                semantic_score = match["semantic_score"]
                
                # Structural Score (Average of Shortest Path Novelty and Random Walk Novelty)
                sp_score = await self.shortest_path.score_novelty(self.neo4j, seed_id, match_id)
                rw_score = await self.random_walk.score_novelty(self.neo4j, seed_id, match_id)
                structural_score = (sp_score + rw_score) / 2.0
                
                # Bridge Score (Are they in different Louvain communities?)
                is_bridge = await self.community.are_bridge_nodes(self.neo4j, seed_id, match_id)
                bridge_score = 1.0 if is_bridge else 0.0

                # 4. Composite Scoring
                composite = (
                    (w_semantic * semantic_score) + 
                    (w_structural * structural_score) + 
                    (w_bridge * bridge_score)
                )
                
                # If they are from the same domain, penalize heavily
                if seed.get("domain") and seed.get("domain") == match.get("domain"):
                    composite *= 0.5
                    
                confidence = min(100.0, composite * 100 * 0.9)

                if composite > 0.4:
                    candidates.append({
                        "concept_a": Concept(id=seed_id, name=seed["name"], node_type="concept", domain=seed.get("domain", "")),
                        "concept_b": Concept(id=match_id, name=match["name"], node_type="concept", domain=match.get("domain", "")),
                        "reasoning": self._generate_reasoning(seed, match, semantic_score, structural_score, is_bridge),
                        "composite_score": composite,
                        "confidence": confidence,
                        "semantic_distance": semantic_score,
                        "graph_distance": structural_score,
                        "bridge_score": bridge_score,
                    })

        # Sort by best collision
        candidates.sort(key=lambda x: x["composite_score"], reverse=True)
        return candidates[:max_results]

    def _generate_reasoning(self, seed: dict, match: dict, sem_s: float, struct_s: float, is_bridge: bool) -> str:
        parts = [f"Found a highly novel collision between '{seed['name']}' and '{match['name']}'."]
        if is_bridge:
            parts.append("They belong to completely separate knowledge communities, making this a powerful Bridge.")
        if struct_s > 0.8:
            parts.append("They are structurally distant in the graph with no direct inferred path.")
        if sem_s > 0.8:
            parts.append("Yet, they sit in the exact 'Sweet Spot' of semantic similarity, indicating hidden transferable mechanics.")
        return " ".join(parts)
]]>
