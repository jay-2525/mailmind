from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.email import Email, EmailThread, EmailAnalysis, ExtractedEntity
from app.schemas.email import EmailRead, EmailThreadRead
from app.agents.langgraph_workflow import email_intelligence_graph
from app.models.action import AuditLog

router = APIRouter()


@router.get("", response_model=List[EmailRead])
def list_emails(
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = db.query(Email).filter(Email.user_id == user.id)
    if category:
        q = q.join(EmailAnalysis).filter(EmailAnalysis.category.ilike(f"%{category}%"))
    if search:
        q = q.filter((Email.subject.ilike(f"%{search}%")) | (Email.sender.ilike(f"%{search}%")))

    emails = q.order_by(Email.received_at.desc()).offset(offset).limit(limit).all()
    return emails


@router.get("/threads", response_model=List[EmailThreadRead])
def list_email_threads(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    threads = db.query(EmailThread).filter(EmailThread.user_id == user.id).order_by(EmailThread.last_message_at.desc()).all()
    return threads


@router.get("/{email_id}", response_model=EmailRead)
def get_email_details(
    email_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    email = db.query(Email).filter(Email.id == email_id, Email.user_id == user.id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email


@router.post("/sync")
def trigger_email_sync(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Syncs email mailbox and runs LangGraph analysis workflow on all pending messages.
    """
    unprocessed = db.query(Email).filter(Email.user_id == user.id, Email.processing_status == "UNPROCESSED").all()
    analyzed_count = 0

    for email in unprocessed:
        # Run LangGraph pipeline
        state = {
            "user_id": user.id,
            "email_id": email.id,
            "subject": email.subject,
            "body": email.body_text,
            "sender": email.sender,
            "received_at": email.received_at.isoformat(),
            "size_bytes": email.size_bytes,
            "has_attachments": email.has_attachments
        }
        graph_output = email_intelligence_graph.invoke(state)
        email.processing_status = "PROCESSED"
        analyzed_count += 1

    db.add(AuditLog(
        user_id=user.id,
        event_type="EMAIL_SYNC_COMPLETED",
        target_resource="mailbox",
        action_taken=f"Mailbox sync completed ({analyzed_count} emails processed)",
        performed_by="AGENT"
    ))
    db.commit()

    return {
        "status": "SUCCESS",
        "processed_count": analyzed_count,
        "message": f"Successfully synchronized and analyzed {analyzed_count} emails."
    }
