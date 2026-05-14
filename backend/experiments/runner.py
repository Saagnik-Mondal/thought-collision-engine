<![CDATA["""
Experiment Runner — Benchmarks different algorithm configurations.
"""
from loguru import logger
from core.neo4j_client import neo4j_client
from core.vector_store import vector_store
from algorithms.collision.composite import CompositeCollisionAlgorithm

class ExperimentRunner:
    def __init__(self):
        self.engine = CompositeCollisionAlgorithm(neo4j_client, vector_store)
        self.results = []

    async def run_benchmarks(self):
        """Run the collision engine with various weight configurations."""
        logger.info("Starting Collision Engine Benchmarks...")
        
        # Prepare Graph (PageRank, Louvain)
        await self.engine.prepare_graph()
        
        configs = [
            {"name": "Balanced", "weight_semantic": 0.33, "weight_structural": 0.33, "weight_bridge": 0.33},
            {"name": "Semantic Heavy", "weight_semantic": 0.7, "weight_structural": 0.15, "weight_bridge": 0.15},
            {"name": "Structural Heavy", "weight_structural": 0.7, "weight_semantic": 0.15, "weight_bridge": 0.15},
            {"name": "Bridge Heavy", "weight_bridge": 0.7, "weight_semantic": 0.15, "weight_structural": 0.15},
        ]
        
        self.results = []
        for conf in configs:
            logger.info(f"Running config: {conf['name']}")
            candidates = await self.engine.discover(max_results=10, config=conf)
            
            # Metric: Average Composite Score of top 10
            avg_score = sum(c["composite_score"] for c in candidates) / max(1, len(candidates))
            
            self.results.append({
                "config_name": conf["name"],
                "candidates_found": len(candidates),
                "avg_novelty_score": round(avg_score, 3),
                "top_collision": candidates[0]["reasoning"] if candidates else "None"
            })
            
        logger.info("Benchmarks complete.")
        return self.results

experiment_runner = ExperimentRunner()
]]>
