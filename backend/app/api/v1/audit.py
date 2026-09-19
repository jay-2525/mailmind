from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.action import AuditLog
from app.schemas.audit import AuditLogRead

router = APIRouter()


@router.get("/logs", response_model=List[AuditLogRead])
def get_audit_logs(
    limit: int = Query(100, ge=1, le=500),
    event_type: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = db.query(AuditLog).filter(AuditLog.user_id == user.id)
    if event_type:
        q = q.filter(AuditLog.event_type.ilike(f"%{event_type}%"))
    return q.order_by(AuditLog.timestamp.desc()).limit(limit).all()
