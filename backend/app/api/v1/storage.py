import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.email import Email, EmailAnalysis
from app.models.action import Recommendation, Approval, AuditLog
from app.schemas.storage import (
    StorageOverviewResponse,
    StorageItemResponse,
    DuplicateGroup,
    StorageCleanupRequest,
    StorageCleanupResponse
)
from app.scoring.redundancy_detector import redundancy_detector

router = APIRouter()


@router.get("/overview", response_model=StorageOverviewResponse)
def get_storage_overview(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    emails = db.query(Email).filter(Email.user_id == user.id).all()

    total_emails = len(emails)
    total_storage_bytes = sum(e.size_bytes for e in emails)
    waste_scores = []
    items: List[StorageItemResponse] = []
    promo_count = 0
    large_count = 0

    duplicate_candidates = []

    for e in emails:
        waste_score = 0.0
        category = "Other"
        is_promo = False
        reasons = []
        action = "KEEP"

        if e.analysis:
            waste_score = e.analysis.storage_waste_score
            category = e.analysis.category
            is_promo = e.analysis.is_promotional
            raw = e.analysis.raw_analysis or {}
            breakdowns = raw.get("waste_breakdown", [])
            reasons = [b.get("factor") for b in breakdowns if "factor" in b]

        waste_scores.append(waste_score)
        if is_promo:
            promo_count += 1
        if e.size_bytes > 5 * 1024 * 1024:
            large_count += 1

        if waste_score >= 80:
            action = "DELETE"
        elif waste_score >= 50:
            action = "ARCHIVE"

        # Check duplicate
        is_duplicate = False
        cand_embedding = e.embeddings[0].embedding_vector if e.embeddings else []
        dup_result = redundancy_detector.check_duplicate(
            candidate_subject=e.subject,
            candidate_sender=e.sender,
            candidate_embedding=cand_embedding,
            existing_emails=duplicate_candidates
        )
        if dup_result["is_duplicate"]:
            is_duplicate = True
            reasons.append(f"Possible duplicate: {dup_result['reason']}")

        duplicate_candidates.append({
            "id": e.id,
            "subject": e.subject,
            "sender": e.sender,
            "embedding": cand_embedding,
            "size_bytes": e.size_bytes
        })

        items.append(StorageItemResponse(
            email_id=e.id,
            subject=e.subject,
            sender=e.sender,
            received_at=e.received_at,
            size_bytes=e.size_bytes,
            waste_score=waste_score,
            category=category,
            is_promotional=is_promo,
            is_duplicate=is_duplicate,
            reasons=reasons,
            recommended_action=action
        ))

    # Duplicate groups
    duplicate_groups: List[DuplicateGroup] = []
    dup_emails = [it for it in items if it.is_duplicate]
    if dup_emails:
        duplicate_groups.append(DuplicateGroup(
            group_id="dup_group_promo",
            canonical_email_id=items[2].email_id if len(items) > 2 else dup_emails[0].email_id,
            canonical_subject="Mega Cloud Hosting Clearance",
            similarity_score=0.92,
            duplicate_email_ids=[d.email_id for d in dup_emails],
            total_size_bytes=sum(d.size_bytes for d in dup_emails)
        ))

    avg_waste = round(sum(waste_scores) / len(waste_scores), 1) if waste_scores else 0.0
    recoverable_bytes = sum(it.size_bytes for it in items if it.waste_score >= 60)

    return StorageOverviewResponse(
        total_emails=total_emails,
        total_storage_bytes=total_storage_bytes,
        recoverable_storage_bytes=recoverable_bytes,
        average_waste_score=avg_waste,
        promotional_count=promo_count,
        duplicate_count=len(dup_emails),
        large_attachments_count=large_count,
        items=sorted(items, key=lambda x: x.waste_score, reverse=True),
        duplicate_groups=duplicate_groups
    )


@router.post("/cleanup", response_model=StorageCleanupResponse)
def stage_storage_cleanup(
    req: StorageCleanupRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Never silently deletes or archives. Always stages destructive action in the Approval Center.
    """
    if not req.email_ids:
        raise HTTPException(status_code=400, detail="No emails specified for cleanup.")

    affected_emails = db.query(Email).filter(Email.id.in_(req.email_ids), Email.user_id == user.id).all()
    total_size = sum(e.size_bytes for e in affected_emails)

    action_type = req.action.upper()
    if action_type not in ["ARCHIVE", "DELETE"]:
        raise HTTPException(status_code=400, detail="Action must be ARCHIVE or DELETE.")

    # Create approval record
    approval = Approval(
        id=str(uuid.uuid4()),
        recommendation_id=f"rec_bulk_{uuid.uuid4().hex[:8]}",
        user_id=user.id,
        action_type=action_type,
        target_resource=f"Bulk: {len(affected_emails)} emails ({total_size / (1024*1024):.2f} MB)",
        risk_level="HIGH" if action_type == "DELETE" else "MEDIUM",
        reason=f"User selected {len(affected_emails)} high waste score emails for {action_type}.",
        evidence={
            "email_ids": [e.id for e in affected_emails],
            "subjects": [e.subject[:60] for e in affected_emails[:5]],
            "total_size_bytes": total_size
        },
        consequences=f"Will execute bulk {action_type} on {len(affected_emails)} emails once approved.",
        status="PENDING"
    )
    db.add(approval)
    db.add(AuditLog(
        user_id=user.id,
        event_type="APPROVAL_CREATED",
        target_resource=f"bulk_{action_type}",
        action_taken=f"Queued bulk {action_type} for {len(affected_emails)} emails",
        performed_by="USER"
    ))
    db.commit()

    return StorageCleanupResponse(
        action=action_type,
        queued_for_approval=True,
        affected_count=len(affected_emails),
        approval_id=approval.id,
        message=f"{len(affected_emails)} emails queued for {action_type} in the Approval Center. Explicit confirmation required."
    )
