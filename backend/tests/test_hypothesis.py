<![CDATA["""Tests for the hypothesis generation system."""
from algorithms.hypothesis.generator import HypothesisGenerator

def test_hypothesis_generation():
    gen = HypothesisGenerator()
    hypotheses = gen.generate(
        domain_a="biology", domain_b="computer_science",
        reasoning="Both use distributed decision-making", novelty_score=85, confidence_score=70, count=3,
    )
    assert len(hypotheses) == 3
    for h in hypotheses:
        assert h.title
        assert h.description
        assert h.hypothesis_type in ("research", "startup", "insight", "combination")
        assert len(h.reasoning_chain) > 0
        assert len(h.potential_applications) > 0

def test_hypothesis_types():
    gen = HypothesisGenerator()
    hypotheses = gen.generate(domain_a="physics", domain_b="economics",
        reasoning="test", novelty_score=50, confidence_score=50, count=4)
    types = {h.hypothesis_type for h in hypotheses}
    assert len(types) >= 3  # Should generate diverse types
]]>
