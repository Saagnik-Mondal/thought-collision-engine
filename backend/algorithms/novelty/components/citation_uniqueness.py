<![CDATA["""Citation uniqueness component."""
class CitationUniquenessComponent:
    name = "citation_uniqueness"
    weight = 0.15

    def score(self, collision: dict) -> float:
        # Higher if concepts come from different, non-overlapping citation networks
        bridge = collision.get("bridge_score", 0.5)
        return bridge * 100
]]>
