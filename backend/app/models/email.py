import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class EmailThread(Base):
    __tablename__ = "email_threads"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    thread_id_external = Column(String(255), index=True, nullable=False)
    subject = Column(String(500), nullable=True)
    snippet = Column(Text, nullable=True)
    message_count = Column(Integer, default=1)
    last_message_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="email_threads")
    emails = relationship("Email", back_populates="thread", cascade="all, delete-orphan", order_by="Email.received_at")


class Email(Base):
    __tablename__ = "emails"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    thread_id = Column(String(36), ForeignKey("email_threads.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    message_id_external = Column(String(255), unique=True, index=True, nullable=False)
    sender = Column(String(255), index=True, nullable=False)
    sender_name = Column(String(255), nullable=True)
    recipients = Column(JSON, default=list)  # list of email addresses
    subject = Column(String(500), nullable=False, default="(No Subject)")
    body_text = Column(Text, nullable=False, default="")
    body_html = Column(Text, nullable=True)
    received_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    labels = Column(JSON, default=list)
    size_bytes = Column(Integer, default=0)
    has_attachments = Column(Boolean, default=False)
    attachment_metadata = Column(JSON, default=list)  # list of {filename, size_bytes, content_type}
    processing_status = Column(String(50), default="UNPROCESSED", index=True)  # UNPROCESSED, PROCESSING, PROCESSED, FAILED

    thread = relationship("EmailThread", back_populates="emails")
    user = relationship("User", back_populates="emails")
    analysis = relationship("EmailAnalysis", back_populates="email", uselist=False, cascade="all, delete-orphan")
    embeddings = relationship("EmailEmbedding", back_populates="email", cascade="all, delete-orphan")
    entities = relationship("ExtractedEntity", back_populates="email", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="email", cascade="all, delete-orphan")
    commitments = relationship("Commitment", back_populates="email", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="email", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="email", cascade="all, delete-orphan")
    calendar_events = relationship("CalendarEvent", back_populates="email", cascade="all, delete-orphan")


class EmailAnalysis(Base):
    __tablename__ = "email_analysis"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email_id = Column(String(36), ForeignKey("emails.id", ondelete="CASCADE"), unique=True, nullable=False)
    category = Column(String(100), default="Other", index=True)
    importance = Column(Float, default=0.5)  # 0.0 to 1.0
    urgency = Column(Float, default=0.5)  # 0.0 to 1.0
    actionability = Column(Float, default=0.5)  # 0.0 to 1.0
    storage_waste_score = Column(Float, default=0.0)  # 0 to 100
    is_promotional = Column(Boolean, default=False)
    is_job_related = Column(Boolean, default=False)
    security_risk_level = Column(String(20), default="LOW")  # LOW, MEDIUM, HIGH
    security_risk_reasons = Column(JSON, default=list)
    summary = Column(Text, nullable=True)
    raw_analysis = Column(JSON, default=dict)
    analyzed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    email = relationship("Email", back_populates="analysis")


class EmailEmbedding(Base):
    __tablename__ = "email_embeddings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email_id = Column(String(36), ForeignKey("emails.id", ondelete="CASCADE"), nullable=False, index=True)
    embedding_vector = Column(JSON, nullable=False)  # stored as JSON list of floats for universal DB portability
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    email = relationship("Email", back_populates="embeddings")


class ExtractedEntity(Base):
    __tablename__ = "extracted_entities"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email_id = Column(String(36), ForeignKey("emails.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)  # PERSON, ORG, DATE, TIME, DEADLINE, LOCATION, URL, MONEY
    entity_value = Column(String(500), nullable=False)
    confidence = Column(Float, default=1.0)
    metadata_json = Column(JSON, default=dict)

    email = relationship("Email", back_populates="entities")
