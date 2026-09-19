import re
from typing import List, Dict, Any, Optional
from app.services.embedding import embedding_service
from app.core.config import settings


class RedundancyDetector:
    """
    Identifies semantic duplicates and thread redundancies using:
    - Subject normalization (stripping Re:, Fwd:, [Ticket-123], etc.)
    - Sender domain matching
    - Embedding cosine similarity
    """

    PREFIX_PATTERN = r'^(?:re|fwd|fw|aw|sv)\s*:\s*|^\[.*?\]\s*'

    @classmethod
    def normalize_subject(cls, subject: str) -> str:
        if not subject:
            return ""
        norm = subject.strip()
        while True:
            new_norm = re.sub(cls.PREFIX_PATTERN, '', norm, flags=re.IGNORECASE).strip()
            if new_norm == norm:
                break
            norm = new_norm
        return norm.lower()

    @classmethod
    def check_duplicate(
        cls,
        candidate_subject: str,
        candidate_sender: str,
        candidate_embedding: List[float],
        existing_emails: List[Dict[str, Any]],
        threshold: float = settings.DUPLICATE_SIMILARITY_THRESHOLD
    ) -> Dict[str, Any]:
        """
        Compare candidate against a list of existing emails.
        Returns duplicate status, best match email_id, similarity score, and reasoning.
        """
        norm_subj = cls.normalize_subject(candidate_subject)
        cand_domain = candidate_sender.split("@")[-1].lower() if "@" in candidate_sender else ""

        best_match_id: Optional[str] = None
        max_similarity = 0.0
        reason = "Unique email"

        for item in existing_emails:
            other_id = item.get("id")
            other_subj = cls.normalize_subject(item.get("subject", ""))
            other_sender = item.get("sender", "")
            other_domain = other_sender.split("@")[-1].lower() if "@" in other_sender else ""
            other_vec = item.get("embedding", [])

            sim = 0.0
            if candidate_embedding and other_vec:
                sim = embedding_service.cosine_similarity(candidate_embedding, other_vec)

            # Check exact or near-identical subject match with same domain
            same_subject = (norm_subj == other_subj and len(norm_subj) > 5)
            same_sender_domain = (cand_domain == other_domain and len(cand_domain) > 2)

            if same_subject and same_sender_domain and sim >= 0.75:
                if sim > max_similarity:
                    max_similarity = sim
                    best_match_id = other_id
                    reason = f"Identical normalized subject '{norm_subj}' from same sender domain with semantic similarity {sim:.2f}"
            elif sim >= threshold:
                if sim > max_similarity:
                    max_similarity = sim
                    best_match_id = other_id
                    reason = f"High semantic text similarity ({sim:.2f} >= threshold {threshold})"

        is_duplicate = (max_similarity >= threshold) or (max_similarity >= 0.75 and norm_subj and best_match_id is not None)

        return {
            "is_duplicate": is_duplicate,
            "canonical_email_id": best_match_id if is_duplicate else None,
            "similarity_score": round(max_similarity, 3),
            "reason": reason if is_duplicate else "No duplicate detected"
        }


redundancy_detector = RedundancyDetector()
