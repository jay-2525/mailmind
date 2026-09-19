import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email_id = Column(String(36), ForeignKey("emails.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(String(50), nullable=False)  # KEEP, ARCHIVE, DELETE, REMIND, SCHEDULE, FOLLOW_UP, JOB_REVIEW, PREPARE_APPLICATION, NO_ACTION
    confidence = Column(Float, default=0.85)  # 0.0 to 1.0
    reasons = Column(JSON, default=list)  # list of bullet explanations
    supporting_signals = Column(JSON, default=dict)
    risk_level = Column(String(20), default="LOW")  # LOW, MEDIUM, HIGH
    status = Column(String(30), default="PENDING", index=True)  # PENDING, APPROVED, REJECTED, EXECUTED
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    email = relationship("Email", back_populates="recommendations")
    user = relationship("User", back_populates="recommendations")
    approval = relationship("Approval", back_populates="recommendation", uselist=False, cascade="all, delete-orphan")


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    recommendation_id = Column(String(36), ForeignKey("recommendations.id", ondelete="CASCADE"), unique=True, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    action_type = Column(String(50), nullable=False)
    target_resource = Column(String(500), nullable=False)
    risk_level = Column(String(20), default="HIGH")  # MEDIUM, HIGH
    reason = Column(Text, nullable=False)
    evidence = Column(JSON, default=dict)
    consequences = Column(Text, nullable=True)
    status = Column(String(30), default="PENDING", index=True)  # PENDING, APPROVED, REJECTED, EDITED
    user_comments = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    recommendation = relationship("Recommendation", back_populates="approval")
    user = relationship("User", back_populates="approvals")


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    email_id = Column(String(36), ForeignKey("emails.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    location = Column(String(255), nullable=True)
    attendees = Column(JSON, default=list)
    google_event_id = Column(String(255), nullable=True)
    status = Column(String(30), default="TENTATIVE")  # TENTATIVE, CONFIRMED, CANCELLED
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="calendar_events")
    email = relationship("Email", back_populates="calendar_events")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)  # EMAIL_ANALYZED, TASK_CREATED, POLICY_BLOCKED, USER_APPROVED, etc.
    target_resource = Column(String(500), nullable=False)
    action_taken = Column(String(255), nullable=False)
    reason = Column(Text, nullable=True)
    performed_by = Column(String(50), default="AGENT")  # AGENT, USER, SYSTEM
    metadata_json = Column(JSON, default=dict)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("User", back_populates="audit_logs")


class PolicyEvent(Base):
    __tablename__ = "policy_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    email_id = Column(String(36), nullable=True, index=True)
    rule_name = Column(String(100), nullable=False)
    risk_tier = Column(String(20), default="MEDIUM")  # LOW, MEDIUM, HIGH
    verdict = Column(String(20), default="ALLOW")  # ALLOW, WARN, BLOCK
    details = Column(JSON, default=dict)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
