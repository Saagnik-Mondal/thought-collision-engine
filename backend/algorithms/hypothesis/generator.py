<![CDATA["""
Hypothesis Generator — Generate human-readable hypotheses from collisions.
"""
import uuid
import random
from core.models import Hypothesis
from algorithms.hypothesis.templates import TEMPLATES

class HypothesisGenerator:
    def generate(self, domain_a: str, domain_b: str, reasoning: str,
                 novelty_score: float, confidence_score: float, count: int = 3) -> list[Hypothesis]:
        """Generate hypotheses from a collision."""
        hypotheses = []
        types = list(TEMPLATES.keys())
        random.shuffle(types)

        for i in range(min(count, len(types))):
            h_type = types[i]
            template = TEMPLATES[h_type]
            application = random.choice(template["applications"])
            reasoning_hint = reasoning[:200] if reasoning else "shared structural patterns"

            title = template["title"].format(domain_a=domain_a or "Domain A", domain_b=domain_b or "Domain B")
            description = template["format"].format(
                domain_a=domain_a or "Domain A", domain_b=domain_b or "Domain B",
                reasoning_hint=reasoning_hint, application=application,
            )

            reasoning_chain = [
                f"Identified collision between {domain_a} and {domain_b}",
                f"Analyzed structural similarities: {reasoning_hint[:100]}",
                f"Generated {h_type} hypothesis with application to {application}",
                f"Novelty assessment: {novelty_score:.0f}/100",
            ]

            hypotheses.append(Hypothesis(
                id=str(uuid.uuid4()), title=title, hypothesis_type=h_type,
                description=description, reasoning_chain=reasoning_chain,
                potential_applications=[application] + random.sample(template["applications"], min(2, len(template["applications"])-1)),
                novelty_score=novelty_score * (0.9 + random.random() * 0.2),
                confidence_score=confidence_score * (0.85 + random.random() * 0.3),
            ))

        return hypotheses
]]>
