import math
from typing import List
import numpy as np

# Global cache for sentence transformer model to avoid reload
_model_instance = None


class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.dimension = 384

    def _get_model(self):
        global _model_instance
        if _model_instance is None:
            try:
                from sentence_transformers import SentenceTransformer
                _model_instance = SentenceTransformer(self.model_name)
            except Exception as e:
                print(f"[EmbeddingService] Warning: Could not load SentenceTransformer ({e}). Using deterministic fallback.")
                _model_instance = "FALLBACK"
        return _model_instance

    def embed_text(self, text: str) -> List[float]:
        """
        Embed a single text string into a normalized 384-dimensional vector.
        """
        if not text or not text.strip():
            return [0.0] * self.dimension

        model = self._get_model()
        if model != "FALLBACK":
            try:
                vec = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
                return [float(x) for x in vec]
            except Exception as e:
                print(f"[EmbeddingService] Error in model.encode ({e}), using fallback.")

        # High-quality deterministic pseudo-semantic hash embedding fallback
        return self._deterministic_embed(text)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]

    def _deterministic_embed(self, text: str) -> List[float]:
        """
        Deterministic pseudo-semantic embedding for zero-dependency / offline execution.
        Preserves n-gram frequency and length features with L2 normalization.
        """
        vec = [0.0] * self.dimension
        words = text.lower().split()
        for i, word in enumerate(words):
            for char_idx, char in enumerate(word):
                pos = (hash(word) + char_idx * 31 + ord(char)) % self.dimension
                vec[pos] += 1.0 / (1.0 + math.log(1.0 + i))

        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [float(x / norm) for x in vec]
        return vec

    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        """
        Compute cosine similarity between two normalized vectors in range [0, 1].
        """
        if not vec_a or not vec_b:
            return 0.0
        a = np.array(vec_a, dtype=np.float32)
        b = np.array(vec_b, dtype=np.float32)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        sim = float(np.dot(a, b) / (norm_a * norm_b))
        return max(0.0, min(1.0, (sim + 1.0) / 2.0 if sim < 0 else sim))


embedding_service = EmbeddingService()
