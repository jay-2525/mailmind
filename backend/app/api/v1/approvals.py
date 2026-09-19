from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User, OAuthAccount
from app.models.action import Approval, AuditLog, CalendarEvent
from app.models.email import Email
from app.schemas.approval import ApprovalRead, ApprovalActionRequest, ApprovalActionResponse
from app.integrations.gmail_service import gmail_service
from app.integrations.calendar_service import calendar_service

router = APIRouter()


@router.get("", response_model=List[ApprovalRead])
def list_pending_approvals(
    status: Optional[str] = "PENDING",
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = db.query(Approval).filter(Approval.user_id == user.id)
    if status:
        q = q.filter(Approval.status == status.upper())
    return q.order_by(Approval.created_at.desc()).all()


@router.post("/{approval_id}/action", response_model=ApprovalActionResponse)
def execute_approval_action(
    approval_id: str,
    req: ApprovalActionRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    approval = db.query(Approval).filter(Approval.id == approval_id, Approval.user_id == user.id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")

    action_choice = req.action.upper()
    now = datetime.now(timezone.utc)

    # Fetch user's Google oauth access token if present
    oauth_acc = db.query(OAuthAccount).filter(OAuthAccount.user_id == user.id).first()
    access_token = oauth_acc.access_token if oauth_acc else "demo_token"

    execution_result = {}

    if action_choice == "REJECT":
        approval.status = "REJECTED"
        approval.reviewed_at = now
        approval.user_comments = req.user_comments or "Rejected by user in Approval Center."

        db.add(AuditLog(
            user_id=user.id,
            event_type="USER_REJECTED",
            target_resource=approval.target_resource,
            action_taken=f"Rejected {approval.action_type}",
            reason=approval.user_comments,
            performed_by="USER"
        ))
        db.commit()
        return ApprovalActionResponse(
            approval_id=approval.id,
            status="REJECTED",
            message=f"Action '{approval.action_type}' was successfully rejected."
        )

    elif action_choice in ["APPROVE", "EDIT"]:
        approval.status = "APPROVED" if action_choice == "APPROVE" else "EDITED"
        approval.reviewed_at = now
        approval.user_comments = req.user_comments

        # Execute target action
        action_type = approval.action_type.upper()

        if action_type in ["ARCHIVE", "DELETE"]:
            # Check if bulk or single
            evidence = approval.evidence or {}
            email_ids = evidence.get("email_ids", [])

            if not email_ids and approval.recommendation and approval.recommendation.email_id:
                email_ids = [approval.recommendation.email_id]

            affected = 0
            for eid in email_ids:
                em = db.query(Email).filter(Email.id == eid).first()
                if em:
                    if action_type == "ARCHIVE":
                        res = gmail_service.archive_email(em.message_id_external, access_token)
                        if "INBOX" in em.labels:
                            em.labels = [lbl for lbl in em.labels if lbl != "INBOX"]
                    else:  # DELETE / TRASH
                        res = gmail_service.trash_email(em.message_id_external, access_token)
                        em.labels = list(set(em.labels + ["TRASH"]))
                    affected += 1

            execution_result = {"action": action_type, "affected_emails": affected, "status": "SUCCESS"}

        elif action_type == "SCHEDULE":
            # Push calendar event
            cal_evt = db.query(CalendarEvent).filter(CalendarEvent.user_id == user.id, CalendarEvent.status == "TENTATIVE").first()
            if cal_evt:
                res = calendar_service.create_event(
                    title=cal_evt.title,
                    start_time=cal_evt.start_time,
                    end_time=cal_evt.end_time,
                    location=cal_evt.location,
                    access_token=access_token
                )
                cal_evt.status = "CONFIRMED"
                cal_evt.google_event_id = res.get("event_id")
                execution_result = res

        db.add(AuditLog(
            user_id=user.id,
            event_type="USER_APPROVED",
            target_resource=approval.target_resource,
            action_taken=f"Approved and executed {approval.action_type}",
            reason=approval.reason,
            performed_by="USER",
            metadata_json=execution_result
        ))
        db.commit()

        return ApprovalActionResponse(
            approval_id=approval.id,
            status=approval.status,
            execution_result=execution_result,
            message=f"Action '{approval.action_type}' was approved and executed successfully."
        )

    else:
        raise HTTPException(status_code=400, detail="Invalid action choice. Must be APPROVE, REJECT, or EDIT.")
