<![CDATA["""Rarity component — rarer concepts get higher scores."""
class RarityComponent:
    name = "rarity"
    weight = 0.15

    def score(self, collision: dict) -> float:
        # Based on inverse frequency / PageRank (lower PR = rarer)
        pr_a = collision.get("concept_a", {})
        pr_b = collision.get("concept_b", {})
        avg_pr = 0.5  # Default
        if hasattr(pr_a, "pagerank") and hasattr(pr_b, "pagerank"):
            avg_pr = (pr_a.pagerank + pr_b.pagerank) / 2
        return max(0, min(100, (1.0 - avg_pr) * 100))
]]>
