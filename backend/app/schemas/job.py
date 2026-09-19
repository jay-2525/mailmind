from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class JobSkillRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    skill_name: str
    skill_type: str
    category: str


class JobMatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    job_id: str
    resume_id: str
    match_score: float
    required_skill_match_pct: float
    preferred_skill_match_pct: float
    semantic_similarity_pct: float
    experience_match_pct: float
    education_match_pct: float
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    prepared_application: Dict[str, Any] = {}
    calculated_at: datetime


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email_id: str
    company: str
    role: str
    location: str
    work_type: str
    salary_range: Optional[str] = None
    experience_years: float
    education: Optional[str] = None
    application_url: Optional[str] = None
    deadline: Optional[datetime] = None
    recruiter_email: Optional[str] = None
    trust_score: float
    trust_level: str
    trust_reasons: List[str] = []
    raw_description: str
    created_at: datetime
    skills: List[JobSkillRead] = []
    matches: List[JobMatchRead] = []


class ResumeSkillRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    skill_name: str
    category: str
    proficiency_level: str


class ResumeProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    full_name: str
    summary: Optional[str] = None
    raw_text: str
    experience_years: float
    education_level: Optional[str] = None
    updated_at: datetime
    skills: List[ResumeSkillRead] = []


class ResumeSkillCreate(BaseModel):
    skill_name: str
    category: str = "Technical"
    proficiency_level: str = "Proficient"


class PrepareApplicationRequest(BaseModel):
    custom_notes: Optional[str] = None


class PrepareApplicationResponse(BaseModel):
    job_id: str
    role: str
    company: str
    cover_letter: str
    recruiter_pitch: str
    interview_qa: List[Dict[str, str]]
    application_url: Optional[str]
