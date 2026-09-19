from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class ApprovalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    recommendation_id: str
    action_type: str
    target_resource: str
    risk_level: str
    reason: str
    evidence: Dict[str, Any] = {}
    consequences: Optional[str] = None
    status: str  # PENDING, APPROVED, REJECTED, EDITED
    user_comments: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None


class ApprovalActionRequest(BaseModel):
    action: str  # "APPROVE", "REJECT", "EDIT"
    user_comments: Optional[str] = None
    edited_parameters: Optional[Dict[str, Any]] = None


class ApprovalActionResponse(BaseModel):
    approval_id: str
    status: str
    execution_result: Optional[Dict[str, Any]] = None
    message: str
