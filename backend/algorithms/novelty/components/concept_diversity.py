<![CDATA["""Concept diversity component."""
class ConceptDiversityComponent:
    name = "concept_diversity"
    weight = 0.20

    def score(self, collision: dict) -> float:
        # Different domains = higher diversity
        domain_a = collision.get("domain_a", "")
        domain_b = collision.get("domain_b", "")
        if domain_a and domain_b and domain_a != domain_b:
            return 85.0
        elif domain_a != domain_b:
            return 60.0
        return 30.0
]]>
