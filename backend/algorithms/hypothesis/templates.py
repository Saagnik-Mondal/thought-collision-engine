<![CDATA["""
Hypothesis Templates — Structured templates for generating different hypothesis types.
"""

TEMPLATES = {
    "research": {
        "title": "Research Hypothesis: {domain_a} × {domain_b}",
        "format": (
            "Based on the collision between concepts from {domain_a} and {domain_b}, "
            "we hypothesize that principles from {domain_a} — specifically regarding {reasoning_hint} — "
            "could be applied to solve open problems in {domain_b}. "
            "This cross-pollination could yield novel approaches to {application}."
        ),
        "applications": [
            "novel algorithmic design", "improved system architecture",
            "enhanced modeling approaches", "new theoretical frameworks",
        ],
    },
    "startup": {
        "title": "Startup Concept: {domain_a} meets {domain_b}",
        "format": (
            "A startup that applies {domain_a} principles to the {domain_b} industry. "
            "By leveraging {reasoning_hint}, this venture could create a new category of "
            "products/services that addresses unmet needs in {domain_b} through {application}."
        ),
        "applications": [
            "SaaS platform", "developer tools", "analytics service",
            "automation framework", "marketplace", "API service",
        ],
    },
    "insight": {
        "title": "Cross-Domain Insight: {domain_a} ↔ {domain_b}",
        "format": (
            "An unexpected parallel exists between {domain_a} and {domain_b}: "
            "{reasoning_hint}. This structural similarity suggests that advances in one field "
            "could directly inform breakthroughs in the other, particularly in {application}."
        ),
        "applications": [
            "pattern recognition", "system optimization", "adaptive mechanisms",
            "fault tolerance", "resource allocation", "emergent behavior",
        ],
    },
    "combination": {
        "title": "Novel Combination: {domain_a} + {domain_b}",
        "format": (
            "Combining the core mechanisms of {domain_a} with the constraints of {domain_b} "
            "produces a novel approach: {reasoning_hint}. This fusion could lead to {application} "
            "that neither field could achieve independently."
        ),
        "applications": [
            "hybrid algorithms", "bio-inspired computing", "cross-disciplinary frameworks",
            "new measurement techniques", "integrated systems",
        ],
    },
}
]]>
