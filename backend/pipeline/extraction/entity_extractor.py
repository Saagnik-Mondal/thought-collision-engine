<![CDATA["""
Entity Extractor — NLP-based entity extraction using spaCy.
"""
from typing import Optional
from loguru import logger

class EntityExtractor:
    def __init__(self, model_name: str = "en_core_web_sm"):
        self._nlp = None
        self._model_name = model_name

    def _load_model(self):
        if self._nlp is None:
            try:
                import spacy
                self._nlp = spacy.load(self._model_name)
                logger.info("spaCy model '{}' loaded", self._model_name)
            except Exception as e:
                logger.warning("Failed to load spaCy model: {}", e)

    def extract(self, text: str) -> list[dict]:
        """Extract named entities from text."""
        self._load_model()
        if not self._nlp:
            return []
        doc = self._nlp(text[:100000])  # Limit text length
        entities = []
        seen = set()
        for ent in doc.ents:
            key = (ent.text.lower(), ent.label_)
            if key not in seen and len(ent.text) > 2:
                seen.add(key)
                entities.append({
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                })
        logger.info("Extracted {} unique entities", len(entities))
        return entities
]]>
