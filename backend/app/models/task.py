import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email_id = Column(String(36), ForeignKey("emails.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)
    priority = Column(String(20), default="MEDIUM")  # LOW, MEDIUM, HIGH, URGENT
    status = Column(String(20), default="OPEN", index=True)  # OPEN, PROMISED, COMPLETED, OVERDUE, CANCELLED
    confidence = Column(Float, default=0.9)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    email = relationship("Email", back_populates="tasks")
    user = relationship("User", back_populates="tasks")


class Commitment(Base):
    __tablename__ = "commitments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email_id = Column(String(36), ForeignKey("emails.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    statement = Column(String(1000), nullable=False)
    owner = Column(String(50), default="SELF")  # SELF, SENDER, THIRD_PARTY
    deadline = Column(DateTime(timezone=True), nullable=True)
    state = Column(String(20), default="PROMISED", index=True)  # OPEN, PROMISED, COMPLETED, OVERDUE, CANCELLED
    evidence_email_id = Column(String(36), nullable=True)
    last_state_change_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    email = relationship("Email", back_populates="commitments")
    user = relationship("User", back_populates="commitments")
