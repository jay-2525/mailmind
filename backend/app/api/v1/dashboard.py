from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.email import Email, EmailAnalysis
from app.models.task import Task, Commitment
from app.models.job import Job, JobMatch
from app.models.action import Approval, Recommendation

router = APIRouter()


@router.get("/summary")
def get_dashboard_summary(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    emails = db.query(Email).filter(Email.user_id == user.id).all()
    tasks = db.query(Task).filter(Task.user_id == user.id).all()
    commitments = db.query(Commitment).filter(Commitment.user_id == user.id).all()
    jobs = db.query(Job).filter(Job.user_id == user.id).all()
    approvals = db.query(Approval).filter(Approval.user_id == user.id, Approval.status == "PENDING").all()

    now = datetime.now(timezone.utc)

    # 1. KPIs
    unread_important = 0
    action_required = 0
    total_waste_score = 0.0
    recoverable_bytes = 0
    category_counts: Dict[str, int] = {}

    recent_urgent_emails = []

    for e in emails:
        cat = "Other"
        waste = 0.0
        imp = 0.5
        urg = 0.5
        act = 0.5

        if e.analysis:
            cat = e.analysis.category
            waste = e.analysis.storage_waste_score
            imp = e.analysis.importance
            urg = e.analysis.urgency
            act = e.analysis.actionability

        category_counts[cat] = category_counts.get(cat, 0) + 1
        total_waste_score += waste
        if waste >= 60:
            recoverable_bytes += e.size_bytes

        if imp >= 0.75:
            unread_important += 1
        if act >= 0.70:
            action_required += 1

        if urg >= 0.75:
            recent_urgent_emails.append({
                "id": e.id,
                "subject": e.subject,
                "sender": e.sender,
                "category": cat,
                "urgency": urg,
                "importance": imp,
                "received_at": e.received_at
            })

    # 2. Task metrics
    overdue_tasks = 0
    upcoming_deadlines = 0
    task_status_counts = {"OPEN": 0, "PROMISED": 0, "COMPLETED": 0, "OVERDUE": 0}

    for t in tasks:
        task_status_counts[t.status] = task_status_counts.get(t.status, 0) + 1
        if t.deadline:
            dl = t.deadline if t.deadline.tzinfo else t.deadline.replace(tzinfo=timezone.utc)
            if now > dl and t.status in ["OPEN", "PROMISED"]:
                overdue_tasks += 1
            elif dl <= now + timedelta(days=3):
                upcoming_deadlines += 1

    for c in commitments:
        if c.state == "OVERDUE":
            overdue_tasks += 1
        task_status_counts[c.state] = task_status_counts.get(c.state, 0) + 1

    # 3. Job metrics
    high_match_jobs = 0
    job_matches_list = []
    for j in jobs:
        score = 0.0
        if j.matches:
            score = j.matches[0].match_score
        if score >= 70:
            high_match_jobs += 1
        job_matches_list.append({
            "id": j.id,
            "role": j.role,
            "company": j.company,
            "match_score": score,
            "trust_score": j.trust_score,
            "trust_level": j.trust_level
        })

    avg_waste_pct = round(total_waste_score / len(emails), 1) if emails else 0.0

    return {
        "kpis": {
            "unread_important": unread_important,
            "action_required": action_required,
            "overdue_tasks": overdue_tasks,
            "upcoming_deadlines": upcoming_deadlines,
            "average_waste_score": avg_waste_pct,
            "recoverable_mb": round(recoverable_bytes / (1024 * 1024), 1),
            "job_opportunities": len(jobs),
            "high_match_jobs": high_match_jobs,
            "pending_approvals": len(approvals)
        },
        "charts": {
            "categories": [{"category": k, "count": v} for k, v in category_counts.items()],
            "task_statuses": [{"status": k, "count": v} for k, v in task_status_counts.items()],
            "storage_waste": [
                {"name": "Low Waste (0-40)", "count": sum(1 for e in emails if e.analysis and e.analysis.storage_waste_score <= 40)},
                {"name": "Moderate (41-70)", "count": sum(1 for e in emails if e.analysis and 40 < e.analysis.storage_waste_score <= 70)},
                {"name": "High Waste (71-100)", "count": sum(1 for e in emails if e.analysis and e.analysis.storage_waste_score > 70)},
            ]
        },
        "recent_urgent": recent_urgent_emails[:5],
        "top_jobs": sorted(job_matches_list, key=lambda x: x["match_score"], reverse=True)[:4]
    }
