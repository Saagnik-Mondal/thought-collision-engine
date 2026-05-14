<![CDATA["""
Algorithm Comparator — Compare results across experiments.
"""
class AlgorithmComparator:
    def compare(self, results: list[dict]) -> dict:
        """Compare experiment results and rank algorithms."""
        rankings = {}
        for result in results:
            for algo, metrics in result.get("results", {}).items():
                if algo not in rankings:
                    rankings[algo] = {"total_novelty": 0, "runs": 0}
                rankings[algo]["total_novelty"] += metrics.get("avg_novelty", 0)
                rankings[algo]["runs"] += 1

        for algo in rankings:
            runs = rankings[algo]["runs"]
            rankings[algo]["avg_novelty"] = rankings[algo]["total_novelty"] / runs if runs else 0

        sorted_rankings = sorted(rankings.items(), key=lambda x: x[1]["avg_novelty"], reverse=True)
        return {"rankings": [{"algorithm": k, **v} for k, v in sorted_rankings]}
]]>
