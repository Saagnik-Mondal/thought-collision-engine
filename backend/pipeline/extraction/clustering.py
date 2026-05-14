<![CDATA["""
Concept Clustering — Group related concepts using HDBSCAN.
"""
import numpy as np
from loguru import logger

class ConceptClusterer:
    def cluster(self, embeddings: dict[str, list[float]], min_cluster_size: int = 3) -> dict[str, int]:
        """Cluster concept embeddings and return concept_id -> cluster_id mapping."""
        if len(embeddings) < min_cluster_size:
            return {cid: 0 for cid in embeddings}

        ids = list(embeddings.keys())
        vectors = np.array([embeddings[cid] for cid in ids])

        try:
            import hdbscan
            clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, metric="cosine")
            labels = clusterer.fit_predict(vectors)
        except ImportError:
            from sklearn.cluster import KMeans
            n_clusters = max(2, len(ids) // 5)
            labels = KMeans(n_clusters=n_clusters, random_state=42, n_init=10).fit_predict(vectors)

        mapping = dict(zip(ids, [int(l) for l in labels]))
        n_clusters = len(set(labels) - {-1})
        logger.info("Clustered {} concepts into {} groups", len(ids), n_clusters)
        return mapping
]]>
