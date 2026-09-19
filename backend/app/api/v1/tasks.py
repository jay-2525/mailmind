import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.task import Task, Commitment
from app.schemas.task import (
    TaskRead, TaskCreate, TaskUpdate,
    CommitmentRead, CommitmentUpdate
)
from app.services.commitment_fsm import commitment_fsm
from app.models.action import AuditLog

router = APIRouter()


@router.get("", response_model=List[TaskRead])
def list_tasks(
    status: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = db.query(Task).filter(Task.user_id == user.id)
    if status:
        q = q.filter(Task.status == status.upper())
    return q.order_by(Task.deadline.asc().nullslast()).all()


@router.post("", response_model=TaskRead)
def create_task(
    req: TaskCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = Task(
        id=str(uuid.uuid4()),
        email_id=req.email_id,
        user_id=user.id,
        title=req.title,
        description=req.description,
        deadline=req.deadline,
        priority=req.priority.upper(),
        status="OPEN",
        confidence=1.0
    )
    db.add(task)
    db.add(AuditLog(
        user_id=user.id,
        event_type="TASK_CREATED",
        target_resource=f"task:{task.id}",
        action_taken=f"Created task: {task.title}",
        performed_by="USER"
    ))
    db.commit()
    db.refresh(task)
    return task


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: str,
    req: TaskUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if req.title is not None:
        task.title = req.title
    if req.description is not None:
        task.description = req.description
    if req.deadline is not None:
        task.deadline = req.deadline
    if req.priority is not None:
        task.priority = req.priority.upper()
    if req.status is not None:
        task.status = req.status.upper()

    db.commit()
    db.refresh(task)
    return task


@router.get("/commitments", response_model=List[CommitmentRead])
def list_commitments(
    state: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    commitments = db.query(Commitment).filter(Commitment.user_id == user.id).all()

    # Dynamically evaluate states (e.g. check for overdue)
    now = datetime.now(timezone.utc)
    for c in commitments:
        if c.state in ["OPEN", "PROMISED"] and c.deadline:
            dl = c.deadline if c.deadline.tzinfo else c.deadline.replace(tzinfo=timezone.utc)
            if now > dl:
                c.state = "OVERDUE"
                c.last_state_change_at = now
    db.commit()

    if state:
        return [c for c in commitments if c.state == state.upper()]
    return commitments


@router.patch("/commitments/{commitment_id}", response_model=CommitmentRead)
def update_commitment_state(
    commitment_id: str,
    req: CommitmentUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    c = db.query(Commitment).filter(Commitment.id == commitment_id, Commitment.user_id == user.id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Commitment not found")

    new_state = req.state.upper()
    if not commitment_fsm.can_transition(c.state, new_state):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid FSM transition: Cannot transition from '{c.state}' to '{new_state}'."
        )

    old_state = c.state
    c.state = new_state
    c.last_state_change_at = datetime.now(timezone.utc)
    if req.deadline is not None:
        c.deadline = req.deadline

    db.add(AuditLog(
        user_id=user.id,
        event_type="COMMITMENT_STATE_CHANGED",
        target_resource=f"commitment:{c.id}",
        action_taken=f"Transitioned commitment from {old_state} to {new_state}",
        performed_by="USER"
    ))
    db.commit()
    db.refresh(c)
    return c
