import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.job import Job, JobMatch, JobSkill, ResumeProfile, ResumeSkill
from app.schemas.job import (
    JobRead, JobMatchRead,
    PrepareApplicationRequest, PrepareApplicationResponse
)
from app.scoring.job_matcher import job_matcher
from app.services.llm_provider import llm_provider
from app.models.action import AuditLog

router = APIRouter()


@router.get("", response_model=List[JobRead])
def list_jobs(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    jobs = db.query(Job).filter(Job.user_id == user.id).order_by(Job.created_at.desc()).all()
    return jobs


@router.get("/{job_id}", response_model=JobRead)
def get_job_detail(
    job_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/{job_id}/match", response_model=JobMatchRead)
def recalculate_job_match(
    job_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    resume = db.query(ResumeProfile).filter(ResumeProfile.user_id == user.id).first()
    if not resume:
        raise HTTPException(status_code=400, detail="Please upload or create a resume profile first.")

    req_skills = [s.skill_name for s in job.skills if s.skill_type == "REQUIRED"]
    pref_skills = [s.skill_name for s in job.skills if s.skill_type == "PREFERRED"]
    cand_skills = [s.skill_name for s in resume.skills]

    # Get email embedding if available
    job_emb = job.email.embeddings[0].embedding_vector if (job.email and job.email.embeddings) else []
    resume_emb = resume.embedding_json or []

    match_result = job_matcher.match_job(
        job_required_skills=req_skills,
        job_preferred_skills=pref_skills,
        candidate_skills=cand_skills,
        job_experience_years=job.experience_years,
        candidate_experience_years=resume.experience_years,
        job_education=job.education or "",
        candidate_education=resume.education_level or "",
        job_embedding=job_emb,
        resume_embedding=resume_emb
    )

    # Save or update JobMatch
    job_match = db.query(JobMatch).filter(JobMatch.job_id == job.id, JobMatch.resume_id == resume.id).first()
    if not job_match:
        job_match = JobMatch(
            id=str(uuid.uuid4()),
            job_id=job.id,
            resume_id=resume.id
        )
        db.add(job_match)

    job_match.match_score = match_result["match_score"]
    job_match.required_skill_match_pct = match_result["breakdown"]["required_skill_match_pct"]
    job_match.preferred_skill_match_pct = match_result["breakdown"]["preferred_skill_match_pct"]
    job_match.semantic_similarity_pct = match_result["breakdown"]["semantic_similarity_pct"]
    job_match.experience_match_pct = match_result["breakdown"]["experience_match_pct"]
    job_match.education_match_pct = match_result["breakdown"]["education_match_pct"]
    job_match.matched_skills = match_result["matched_skills"]
    job_match.missing_skills = match_result["missing_skills"]

    db.add(AuditLog(
        user_id=user.id,
        event_type="JOB_MATCH_RECALCULATED",
        target_resource=f"job:{job.id}",
        action_taken=f"Job match recalculated: {job_match.match_score}%",
        performed_by="AGENT"
    ))
    db.commit()
    db.refresh(job_match)
    return job_match


@router.post("/{job_id}/prepare-application", response_model=PrepareApplicationResponse)
def prepare_job_application(
    job_id: str,
    req: PrepareApplicationRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    resume = db.query(ResumeProfile).filter(ResumeProfile.user_id == user.id).first()
    matched_skills = []
    if job.matches:
        matched_skills = job.matches[0].matched_skills or []

    app_pack = llm_provider.generate_application_pack(
        role=job.role,
        company=job.company,
        job_description=job.raw_description,
        resume_summary=resume.summary if resume else "",
        candidate_name=user.full_name or "Alex Morgan",
        matched_skills=matched_skills
    )

    # Save to JobMatch
    if job.matches:
        job.matches[0].prepared_application = app_pack
        db.commit()

    db.add(AuditLog(
        user_id=user.id,
        event_type="APPLICATION_PREPARED",
        target_resource=f"job:{job.id}",
        action_taken=f"Prepared application pack for {job.role} at {job.company}",
        performed_by="AGENT"
    ))
    db.commit()

    return PrepareApplicationResponse(
        job_id=job.id,
        role=job.role,
        company=job.company,
        cover_letter=app_pack["cover_letter"],
        recruiter_pitch=app_pack["recruiter_pitch"],
        interview_qa=app_pack["interview_qa"],
        application_url=job.application_url
    )
