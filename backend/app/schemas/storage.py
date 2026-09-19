from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class StorageItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email_id: str
    subject: str
    sender: str
    received_at: datetime
    size_bytes: int
    waste_score: float
    category: str
    is_promotional: bool
    is_duplicate: bool
    reasons: List[str]
    recommended_action: str


class DuplicateGroup(BaseModel):
    group_id: str
    canonical_email_id: str
    canonical_subject: str
    similarity_score: float
    duplicate_email_ids: List[str]
    total_size_bytes: int


class StorageOverviewResponse(BaseModel):
    total_emails: int
    total_storage_bytes: int
    recoverable_storage_bytes: int
    average_waste_score: float
    promotional_count: int
    duplicate_count: int
    large_attachments_count: int
    items: List[StorageItemResponse]
    duplicate_groups: List[DuplicateGroup]


class StorageCleanupRequest(BaseModel):
    email_ids: List[str]
    action: str  # "ARCHIVE" or "DELETE"
    requires_approval: bool = True


class StorageCleanupResponse(BaseModel):
    action: str
    queued_for_approval: bool
    affected_count: int
    approval_id: Optional[str] = None
    message: str
