from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    event_type: str
    target_resource: str
    action_taken: str
    reason: Optional[str] = None
    performed_by: str
    metadata_json: Dict[str, Any] = {}
    timestamp: datetime
