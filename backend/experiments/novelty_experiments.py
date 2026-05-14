<![CDATA["""
Novelty Experiments — Benchmarking the Novelty Scorer with different configurations.
"""
import asyncio
from loguru import logger
from core.neo4j_client import neo4j_client
from core.vector_store import vector_store
from algorithms.novelty.scorer import NoveltyScorer

async def run_novelty_experiment():
    logger.info("Starting Novelty Engine Experiment...")

    # Define test configurations
    configs = [
        {"name": "Balanced Novelty", "weights": None}, # Uses default
        {"name": "Hyper-Structural Novelty", "weights": {
            "semantic_distance": 0.1, "rarity": 0.1, 
            "graph_separation": 0.4, "citation_uniqueness": 0.1, "concept_diversity": 0.3
        }},
        {"name": "Hyper-Semantic Novelty", "weights": {
            "semantic_distance": 0.6, "rarity": 0.1, 
            "graph_separation": 0.1, "citation_uniqueness": 0.1, "concept_diversity": 0.1
        }}
    ]
    
    # We need mock IDs that actually exist in your DB, or we just evaluate mock pairs.
    # For this experiment script, we assume we fetch two high-centrality nodes from the DB.
    nodes = await neo4j_client.get_all_nodes(limit=2)
    
    if len(nodes) < 2:
        logger.error("Not enough nodes in Neo4j to run experiment. Ingest documents first.")
        return
        
    node_a, node_b = nodes[0]["id"], nodes[1]["id"]
    name_a, name_b = nodes[0]["name"], nodes[1]["name"]
    
    logger.info(f"Evaluating Novelty between '{name_a}' and '{name_b}'...")

    for conf in configs:
        logger.info(f"\n--- Running Configuration: {conf['name']} ---")
        scorer = NoveltyScorer(neo4j_client, vector_store, weights=conf["weights"])
        
        result = await scorer.evaluate(node_a, node_b)
        logger.info(f"Final Novelty Score: {result['novelty_score']}")
        logger.info(f"Explanation:\n{result['explanation']}")

if __name__ == "__main__":
    asyncio.run(run_novelty_experiment())
]]>
