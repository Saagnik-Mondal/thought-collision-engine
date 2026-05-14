<![CDATA["""Semantic distance component."""
class SemanticDistanceComponent:
    name = "semantic_distance"
    weight = 0.25

    def score(self, collision: dict) -> float:
        return collision.get("semantic_distance", 0.5) * 100
]]>
