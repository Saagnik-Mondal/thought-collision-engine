<![CDATA["""
Relationship Extractor — Infer relationships between concepts using SVO Dependency Parsing.
"""
from loguru import logger

class RelationshipExtractor:
    def __init__(self):
        self._nlp = None

    def _load_model(self):
        if self._nlp is None:
            try:
                import spacy
                self._nlp = spacy.load("en_core_web_sm")
            except Exception as e:
                logger.warning(f"Failed to load spaCy model: {e}")

    def extract(self, concepts: list[dict], text: str) -> list[dict]:
        """Extract explicit semantic relationships (SVO) between identified concepts."""
        self._load_model()
        if not self._nlp:
            return self._fallback_extract(concepts, text)

        relationships = []
        doc = self._nlp(text[:100000])

        # Create a fast lookup for concept names
        concept_names = {c["name"].lower(): c["name"] for c in concepts}
        if not concept_names:
            return []

        seen_edges = set()

        for sent in doc.sents:
            subjects = []
            objects = []
            verb = None

            for token in sent:
                if token.dep_ in ("nsubj", "nsubjpass"):
                    # Does this subject map to a concept?
                    subj_text = token.text.lower()
                    if subj_text in concept_names:
                        subjects.append(concept_names[subj_text])
                elif token.dep_ in ("dobj", "pobj"):
                    # Does this object map to a concept?
                    obj_text = token.text.lower()
                    if obj_text in concept_names:
                        objects.append(concept_names[obj_text])
                elif token.pos_ == "VERB":
                    verb = token.lemma_

            if subjects and objects and verb:
                for subj in subjects:
                    for obj in objects:
                        if subj == obj:
                            continue
                        edge_key = (subj, obj)
                        if edge_key not in seen_edges:
                            seen_edges.add(edge_key)
                            relationships.append({
                                "source": subj,
                                "target": obj,
                                "type": f"SVO_{verb.upper()}",
                                "weight": 0.9, # High weight for explicit syntactic relationship
                                "label": verb
                            })

        logger.info(f"Extracted {len(relationships)} explicit SVO relationships.")
        
        # Merge with fallback co-occurrence to ensure graph connectedness
        co_occur = self._fallback_extract(concepts, text)
        for r in co_occur:
            edge_key = (r["source"], r["target"])
            if edge_key not in seen_edges:
                relationships.append(r)
                seen_edges.add(edge_key)

        return relationships

    def _fallback_extract(self, concepts: list[dict], text: str, window_size: int = 100) -> list[dict]:
        """Fallback to weighted co-occurrence if SVO parsing misses connections."""
        relationships = []
        text_lower = text.lower()
        concept_names = [c["name"].lower() for c in concepts]
        
        # Simplified proximity detection for performance
        words = text_lower.split()
        concept_positions = {}
        for idx, word in enumerate(words):
            if word in concept_names:
                if word not in concept_positions:
                    concept_positions[word] = []
                concept_positions[word].append(idx)

        seen = set()
        names_list = list(concept_positions.keys())
        
        for i, name_a in enumerate(names_list):
            for j, name_b in enumerate(names_list):
                if i >= j:
                    continue
                key = tuple(sorted([name_a, name_b]))
                if key in seen:
                    continue
                
                for pos_a in concept_positions[name_a]:
                    for pos_b in concept_positions[name_b]:
                        if abs(pos_a - pos_b) < window_size:
                            seen.add(key)
                            weight = 0.5 / (1.0 + abs(pos_a - pos_b) / 10.0) # Lower max weight than SVO
                            relationships.append({
                                "source": name_a, "target": name_b,
                                "type": "co_occurrence", 
                                "weight": round(weight, 3),
                                "label": "co_occurs_with"
                            })
                            break
                    if key in seen:
                        break

        return relationships
]]>
