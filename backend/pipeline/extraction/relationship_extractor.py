<![CDATA["""
Relationship Extractor — Infer relationships between concepts.
"""
from itertools import combinations
from loguru import logger

class RelationshipExtractor:
    def extract(self, concepts: list[dict], text: str, window_size: int = 200) -> list[dict]:
        """Extract relationships based on co-occurrence within text windows."""
        relationships = []
        text_lower = text.lower()

        concept_names = [c["name"].lower() for c in concepts]
        concept_positions = {}
        for name in concept_names:
            positions = []
            start = 0
            while True:
                idx = text_lower.find(name, start)
                if idx == -1:
                    break
                positions.append(idx)
                start = idx + 1
            if positions:
                concept_positions[name] = positions

        # Find co-occurring concepts within window
        seen = set()
        names_list = list(concept_positions.keys())
        for i, name_a in enumerate(names_list):
            for j, name_b in enumerate(names_list):
                if i >= j:
                    continue
                key = tuple(sorted([name_a, name_b]))
                if key in seen:
                    continue
                # Check if they co-occur within window
                for pos_a in concept_positions[name_a]:
                    for pos_b in concept_positions[name_b]:
                        if abs(pos_a - pos_b) < window_size:
                            seen.add(key)
                            weight = 1.0 / (1.0 + abs(pos_a - pos_b) / window_size)
                            relationships.append({
                                "source": name_a, "target": name_b,
                                "type": "co_occurrence", "weight": round(weight, 3),
                            })
                            break
                    if key in seen:
                        break

        logger.info("Extracted {} relationships", len(relationships))
        return relationships
]]>
