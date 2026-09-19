import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email_id = Column(String(36), ForeignKey("emails.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    company = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    location = Column(String(255), default="Remote")
    work_type = Column(String(50), default="REMOTE")  # REMOTE, HYBRID, ONSITE
    salary_range = Column(String(100), nullable=True)
    experience_years = Column(Float, default=0.0)
    education = Column(String(255), nullable=True)
    application_url = Column(String(1000), nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)
    recruiter_email = Column(String(255), nullable=True)
    trust_score = Column(Float, default=80.0)  # 0 to 100
    trust_level = Column(String(50), default="LOW_RISK_SIGNALS")  # LOW_RISK_SIGNALS, REVIEW_REQUIRED, HIGH_RISK_SIGNALS
    trust_reasons = Column(JSON, default=list)
    raw_description = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    email = relationship("Email", back_populates="jobs")
    user = relationship("User", back_populates="jobs")
    skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")
    matches = relationship("JobMatch", back_populates="job", cascade="all, delete-orphan")


class JobSkill(Base):
    __tablename__ = "job_skills"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String(100), nullable=False, index=True)
    skill_type = Column(String(20), default="REQUIRED")  # REQUIRED, PREFERRED
    category = Column(String(50), default="Technical")

    job = relationship("Job", back_populates="skills")


class ResumeProfile(Base):
    __tablename__ = "resume_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    summary = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=False)
    experience_years = Column(Float, default=0.0)
    education_level = Column(String(255), nullable=True)
    embedding_json = Column(JSON, nullable=True)  # Vector embedding of resume text
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="resume_profile")
    skills = relationship("ResumeSkill", back_populates="resume", cascade="all, delete-orphan")
    matches = relationship("JobMatch", back_populates="resume", cascade="all, delete-orphan")


class ResumeSkill(Base):
    __tablename__ = "resume_skills"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    resume_id = Column(String(36), ForeignKey("resume_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String(100), nullable=False, index=True)
    category = Column(String(50), default="Technical")
    proficiency_level = Column(String(50), default="Proficient")  # Beginner, Intermediate, Proficient, Expert

    resume = relationship("ResumeProfile", back_populates="skills")


class JobMatch(Base):
    __tablename__ = "job_matches"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = Column(String(36), ForeignKey("resume_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    match_score = Column(Float, default=0.0)  # 0 to 100
    required_skill_match_pct = Column(Float, default=0.0)
    preferred_skill_match_pct = Column(Float, default=0.0)
    semantic_similarity_pct = Column(Float, default=0.0)
    experience_match_pct = Column(Float, default=0.0)
    education_match_pct = Column(Float, default=0.0)
    matched_skills = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    prepared_application = Column(JSON, default=dict)  # cover_letter, recruiter_pitch, answers
    calculated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    job = relationship("Job", back_populates="matches")
    resume = relationship("ResumeProfile", back_populates="matches")
