<![CDATA["""
Leaderboard — Track best performing algorithms.
"""
class Leaderboard:
    def __init__(self):
        self._entries = []

    def update(self, algorithm: str, metrics: dict):
        """Update leaderboard with new experiment results."""
        self._entries.append({"algorithm": algorithm, **metrics})

    def get_top(self, n: int = 10) -> list[dict]:
        """Get top N algorithms by average novelty."""
        sorted_entries = sorted(self._entries, key=lambda x: x.get("avg_novelty", 0), reverse=True)
        return sorted_entries[:n]

leaderboard = Leaderboard()
]]>
