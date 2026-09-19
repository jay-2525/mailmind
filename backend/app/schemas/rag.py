from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class RAGResultItem(BaseModel):
    email_id: str
    subject: str
    sender: str
    received_at: datetime
    snippet: str
    similarity_score: float
    retrieval_method: str  # "vector", "keyword", "hybrid"
    reason_for_retrieval: str


class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = 5
    category_filter: Optional[str] = None
    sender_filter: Optional[str] = None


class RAGQueryResponse(BaseModel):
    query: str
    total_retrieved: int
    results: List[RAGResultItem]
    context_summary: str
