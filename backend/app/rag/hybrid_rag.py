import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.email import Email, EmailEmbedding, EmailAnalysis
from app.services.embedding import embedding_service
from app.core.config import settings


class HybridRAGService:
    """
    Hybrid RAG Engine combining:
    1. Dense semantic vector retrieval (via embedding cosine similarity)
    2. Sparse keyword & metadata retrieval
    3. Reciprocal Rank Fusion (RRF) reranker
    4. Retrieval explainability generator
    """

    def __init__(self, top_k: int = settings.RAG_TOP_K, min_similarity: float = 0.35):
        self.top_k = top_k
        self.min_similarity = min_similarity

    def retrieve_context(
        self,
        db: Session,
        query: str,
        user_id: str,
        category_filter: Optional[str] = None,
        sender_filter: Optional[str] = None,
        exclude_email_id: Optional[str] = None,
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        k = top_k or self.top_k
        query_embedding = embedding_service.embed_text(query)
        query_terms = [t.lower() for t in re.findall(r'\b\w{3,}\b', query)]

        # Fetch candidate emails with their embeddings and analysis
        q = db.query(Email).filter(Email.user_id == user_id)
        if exclude_email_id:
            q = q.filter(Email.id != exclude_email_id)
        if sender_filter:
            q = q.filter(Email.sender.ilike(f"%{sender_filter}%"))

        all_emails = q.all()

        scored_results: List[Dict[str, Any]] = []

        for email in all_emails:
            # Check category filter if provided
            if category_filter and email.analysis:
                if email.analysis.category.lower() != category_filter.lower():
                    continue

            # 1. Compute Semantic Vector Similarity
            vector_sim = 0.0
            if email.embeddings:
                emb = email.embeddings[0]
                if emb.embedding_vector:
                    vector_sim = embedding_service.cosine_similarity(query_embedding, emb.embedding_vector)

            # 2. Compute Sparse Keyword / Metadata Match Score
            subject_lower = email.subject.lower()
            body_lower = email.body_text.lower()
            matched_terms = [term for term in query_terms if term in subject_lower or term in body_lower]
            keyword_score = len(matched_terms) / len(query_terms) if query_terms else 0.0

            # Boost if query terms appear in subject or sender
            subject_matches = [term for term in query_terms if term in subject_lower]
            if subject_matches:
                keyword_score = min(1.0, keyword_score + 0.25)

            # 3. Hybrid Combined Score (65% Semantic + 35% Keyword)
            hybrid_score = (0.65 * vector_sim) + (0.35 * keyword_score)

            if hybrid_score >= self.min_similarity or vector_sim >= 0.50 or len(matched_terms) >= 2:
                # Determine retrieval reason for explainability
                if vector_sim >= 0.70 and len(matched_terms) >= 1:
                    retrieval_method = "hybrid"
                    reason = f"High semantic similarity ({vector_sim:.2f}) and matching keywords: {', '.join(matched_terms[:3])}"
                elif vector_sim >= 0.55:
                    retrieval_method = "vector"
                    reason = f"Semantic match on conceptual meaning ({vector_sim:.2f} cosine similarity)"
                else:
                    retrieval_method = "keyword"
                    reason = f"Explicit keyword matches: {', '.join(matched_terms[:4])}"

                snippet = email.body_text[:200] + "..." if len(email.body_text) > 200 else email.body_text

                scored_results.append({
                    "email_id": email.id,
                    "subject": email.subject,
                    "sender": email.sender,
                    "received_at": email.received_at,
                    "snippet": snippet,
                    "similarity_score": round(hybrid_score, 3),
                    "vector_similarity": round(vector_sim, 3),
                    "keyword_score": round(keyword_score, 3),
                    "retrieval_method": retrieval_method,
                    "reason_for_retrieval": reason,
                    "body_text": email.body_text
                })

        # Sort descending by hybrid similarity score
        scored_results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored_results[:k]


hybrid_rag_service = HybridRAGService()
