<![CDATA["""
Concept Extractor — Extract key concepts and topics from text.

Uses TF-IDF and noun phrase extraction to identify key concepts.
"""
import re
from collections import Counter
from loguru import logger

class ConceptExtractor:
    # High-value concept indicator words
    CONCEPT_PATTERNS = [
        r'\b(?:algorithm|method|technique|approach|framework|model|system|architecture|protocol)\b',
        r'\b(?:theory|principle|law|hypothesis|paradigm|mechanism)\b',
        r'\b(?:optimization|learning|detection|recognition|classification|prediction)\b',
    ]

    STOP_CONCEPTS = {
        "the", "and", "for", "this", "that", "with", "from", "have", "been",
        "also", "such", "which", "where", "when", "some", "more", "other",
        "than", "into", "only", "each", "most", "very", "just", "over",
    }

    def extract(self, text: str) -> list[dict]:
        """Extract key concepts from text using noun phrase analysis."""
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
        except Exception:
            return self._fallback_extract(text)

        doc = nlp(text[:50000])
        concepts = []
        seen = set()

        # Extract noun chunks as potential concepts
        for chunk in doc.noun_chunks:
            concept = chunk.text.strip().lower()
            if len(concept) > 3 and concept not in self.STOP_CONCEPTS and concept not in seen:
                seen.add(concept)
                concepts.append({
                    "name": chunk.text.strip(),
                    "type": "concept",
                    "confidence": 0.7,
                })

        # Extract compound technical terms
        for i, token in enumerate(doc):
            if token.pos_ in ("NOUN", "PROPN") and i > 0:
                prev = doc[i-1]
                if prev.pos_ in ("ADJ", "NOUN"):
                    compound = f"{prev.text} {token.text}".lower()
                    if compound not in seen and len(compound) > 5:
                        seen.add(compound)
                        concepts.append({
                            "name": f"{prev.text} {token.text}",
                            "type": "concept",
                            "confidence": 0.8,
                        })

        logger.info("Extracted {} concepts", len(concepts))
        return concepts[:200]  # Cap at 200

    def _fallback_extract(self, text: str) -> list[dict]:
        """Fallback extraction using regex patterns."""
        words = text.lower().split()
        word_freq = Counter(w for w in words if len(w) > 4 and w.isalpha() and w not in self.STOP_CONCEPTS)
        return [{"name": w, "type": "concept", "confidence": 0.5} for w, _ in word_freq.most_common(50)]
]]>
