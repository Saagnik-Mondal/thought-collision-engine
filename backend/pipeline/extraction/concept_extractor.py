<![CDATA["""
Concept Extractor — Extract key concepts using Embedding-based Keyword Extraction.
"""
import numpy as np
from loguru import logger

class ConceptExtractor:
    STOP_CONCEPTS = {
        "the", "and", "for", "this", "that", "with", "from", "have", "been",
        "also", "such", "which", "where", "when", "some", "more", "other",
        "than", "into", "only", "each", "most", "very", "just", "over",
        "these", "those", "can", "will", "would", "could", "should",
    }

    def __init__(self, embedding_model=None):
        self._nlp = None
        self._encoder = embedding_model

    def _load_models(self):
        if self._nlp is None:
            try:
                import spacy
                self._nlp = spacy.load("en_core_web_sm")
            except Exception as e:
                logger.warning(f"Failed to load spaCy: {e}")

        if self._encoder is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._encoder = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception as e:
                logger.warning(f"Failed to load SentenceTransformer: {e}")

    def extract(self, text: str, top_n: int = 30) -> list[dict]:
        """Extract key concepts by comparing candidate chunk embeddings to the document embedding."""
        self._load_models()
        if not self._nlp or not self._encoder:
            return self._fallback_extract(text, top_n)

        # 1. Extract Candidate Noun Chunks
        doc = self._nlp(text[:100000])
        candidates = set()
        for chunk in doc.noun_chunks:
            concept = chunk.text.strip().lower()
            if len(concept) > 3 and concept not in self.STOP_CONCEPTS and not concept.isnumeric():
                candidates.add(chunk.text.strip())

        if not candidates:
            return []

        candidates = list(candidates)

        try:
            # 2. Embed Document and Candidates
            doc_embedding = self._encoder.encode([text[:10000]])[0]
            candidate_embeddings = self._encoder.encode(candidates)

            # 3. Compute Cosine Similarity
            from numpy.linalg import norm
            doc_norm = norm(doc_embedding)
            if doc_norm == 0:
                doc_norm = 1e-9

            similarities = []
            for i, cand_emb in enumerate(candidate_embeddings):
                cand_norm = norm(cand_emb)
                if cand_norm == 0:
                    cand_norm = 1e-9
                sim = np.dot(doc_embedding, cand_emb) / (doc_norm * cand_norm)
                similarities.append((candidates[i], float(sim), cand_emb.tolist()))

            # 4. Sort and return Top N
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            concepts = []
            for name, score, vector in similarities[:top_n]:
                concepts.append({
                    "name": name,
                    "type": "concept",
                    "confidence": round(score, 3), # Score acts as confidence/relevance
                    "embedding": vector
                })
            
            logger.info(f"Extracted {len(concepts)} concepts via Embedding similarity.")
            return concepts

        except Exception as e:
            logger.error(f"Error during semantic concept extraction: {e}")
            return self._fallback_extract(text, top_n)

    def _fallback_extract(self, text: str, top_n: int) -> list[dict]:
        """Fallback extraction using basic word frequencies if models fail."""
        from collections import Counter
        words = text.lower().split()
        word_freq = Counter(w for w in words if len(w) > 4 and w.isalpha() and w not in self.STOP_CONCEPTS)
        return [{"name": w, "type": "concept", "confidence": 0.5, "embedding": None} for w, _ in word_freq.most_common(top_n)]
]]>
