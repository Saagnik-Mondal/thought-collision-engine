<![CDATA["""Tests for the novelty scoring system."""
from algorithms.novelty.scorer import NoveltyScorer

def test_novelty_scorer(sample_collision):
    scorer = NoveltyScorer()
    score = scorer.score(sample_collision)
    assert 0 <= score <= 100
    assert score > 30  # Cross-domain collisions should score well

def test_novelty_breakdown(sample_collision):
    scorer = NoveltyScorer()
    breakdown = scorer.score_breakdown(sample_collision)
    assert "semantic_distance" in breakdown
    assert "rarity" in breakdown
    assert "graph_separation" in breakdown
    assert "citation_uniqueness" in breakdown
    assert "concept_diversity" in breakdown

def test_same_domain_lower_score():
    scorer = NoveltyScorer()
    same_domain = {"domain_a": "biology", "domain_b": "biology",
        "semantic_distance": 0.3, "graph_distance": 0.2, "bridge_score": 0.3}
    cross_domain = {"domain_a": "biology", "domain_b": "computer_science",
        "semantic_distance": 0.7, "graph_distance": 0.8, "bridge_score": 0.7}
    assert scorer.score(cross_domain) > scorer.score(same_domain)
]]>
