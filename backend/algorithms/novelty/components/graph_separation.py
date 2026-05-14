<![CDATA["""Graph separation component."""
class GraphSeparationComponent:
    name = "graph_separation"
    weight = 0.25

    def score(self, collision: dict) -> float:
        return collision.get("graph_distance", 0.5) * 100
]]>
