<![CDATA["""
Entity Extractor — NLP-based Named Entity Recognition using spaCy.
"""
from typing import Optional
from loguru import logger

class EntityExtractor:
    # High-value entity types for cross-domain discovery
    TARGET_LABELS = {"ORG", "GPE", "PRODUCT", "EVENT", "WORK_OF_ART", "LAW", "NORP"}

    def __init__(self, model_name: str = "en_core_web_sm"):
        self._nlp = None
        self._model_name = model_name

    def _load_model(self):
        if self._nlp is None:
            try:
                import spacy
                self._nlp = spacy.load(self._model_name)
                logger.info(f"spaCy model '{self._model_name}' loaded")
            except Exception as e:
                logger.warning(f"Failed to load spaCy model: {e}")

    def extract(self, text: str) -> list[dict]:
        """Extract high-value named entities from text."""
        self._load_model()
        if not self._nlp:
            return []

        # SpaCy limits doc size by default; chunk if necessary, but we cap to 100k here
        doc = self._nlp(text[:100000])  
        
        entities_dict = {}
        for ent in doc.ents:
            if ent.label_ in self.TARGET_LABELS and len(ent.text) > 2:
                key = ent.text.lower()
                if key not in entities_dict:
                    entities_dict[key] = {
                        "name": ent.text,
                        "type": "entity",
                        "label": ent.label_,
                        "confidence": 0.85, # Base confidence for direct NER hits
                        "mentions": 1,
                    }
                else:
                    entities_dict[key]["mentions"] += 1
                    # Increase confidence slightly with more mentions
                    entities_dict[key]["confidence"] = min(0.99, entities_dict[key]["confidence"] + 0.02)

        entities = list(entities_dict.values())
        logger.info(f"Extracted {len(entities)} high-value unique entities.")
        return entities
]]>
