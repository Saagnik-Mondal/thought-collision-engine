<![CDATA["""
Concept Clustering — Group related concepts using HDBSCAN.
"""
import numpy as np
from loguru import logger

class ConceptClusterer:
    def cluster(self, embeddings_dict: dict[str, list[float]], min_cluster_size: int = 3) -> dict[str, int]:
        """
        Cluster concept embeddings using HDBSCAN.
        Returns a mapping of concept_id -> cluster_id.
        Cluster ID -1 indicates noise (unclustered).
        """
        if len(embeddings_dict) < min_cluster_size:
            logger.info("Not enough items to cluster.")
            return {cid: 0 for cid in embeddings_dict}

        ids = list(embeddings_dict.keys())
        vectors = np.array([embeddings_dict[cid] for cid in ids])

        try:
            import hdbscan
            # metric="euclidean" is standard for HDBSCAN, but for embeddings cosine is better. 
            # If hdbscan doesn't support cosine natively, euclidean on normalized vectors is equivalent.
            clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, metric="euclidean")
            
            # Normalize vectors for Euclidean to mimic Cosine distance
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            # Avoid division by zero
            norms[norms == 0] = 1e-9
            normalized_vectors = vectors / norms

            labels = clusterer.fit_predict(normalized_vectors)
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            logger.info(f"HDBSCAN Clustered {len(ids)} concepts into {n_clusters} groups. (-1 is noise)")
            
            return dict(zip(ids, [int(l) for l in labels]))

        except ImportError:
            logger.warning("HDBSCAN not found. Falling back to KMeans.")
            from sklearn.cluster import KMeans
            n_clusters = max(2, len(ids) // 5)
            labels = KMeans(n_clusters=n_clusters, random_state=42, n_init=10).fit_predict(vectors)
            return dict(zip(ids, [int(l) for l in labels]))
        except Exception as e:
            logger.error(f"Clustering failed: {e}")
            return {cid: 0 for cid in ids}
]]>
