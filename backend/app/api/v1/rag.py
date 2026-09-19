from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.rag import RAGQueryRequest, RAGQueryResponse, RAGResultItem
from app.rag.hybrid_rag import hybrid_rag_service

router = APIRouter()


@router.post("/search", response_model=RAGQueryResponse)
def search_historical_context(
    req: RAGQueryRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    results = hybrid_rag_service.retrieve_context(
        db=db,
        query=req.query,
        user_id=user.id,
        category_filter=req.category_filter,
        sender_filter=req.sender_filter,
        top_k=req.top_k
    )

    items = [
        RAGResultItem(
            email_id=r["email_id"],
            subject=r["subject"],
            sender=r["sender"],
            received_at=r["received_at"],
            snippet=r["snippet"],
            similarity_score=r["similarity_score"],
            retrieval_method=r["retrieval_method"],
            reason_for_retrieval=r["reason_for_retrieval"]
        )
        for r in results
    ]

    summary = (
        f"Retrieved {len(items)} historical emails matching query '{req.query}'. "
        f"Hybrid retrieval combined vector semantic similarity and metadata keywords."
        if items else "No historical emails matched the search criteria."
    )

    return RAGQueryResponse(
        query=req.query,
        total_retrieved=len(items),
        results=items,
        context_summary=summary
    )
