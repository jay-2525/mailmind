from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    email_id: str
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: str = "MEDIUM"


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email_id: str
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: str
    status: str
    confidence: float
    created_at: datetime


class CommitmentUpdate(BaseModel):
    state: str
    deadline: Optional[datetime] = None


class CommitmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email_id: str
    statement: str
    owner: str
    deadline: Optional[datetime] = None
    state: str
    evidence_email_id: Optional[str] = None
    last_state_change_at: datetime
    created_at: datetime
