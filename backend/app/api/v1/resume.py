import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.job import ResumeProfile, ResumeSkill
from app.schemas.job import ResumeProfileRead, ResumeSkillRead, ResumeSkillCreate
from app.services.embedding import embedding_service
from app.models.action import AuditLog

router = APIRouter()


@router.get("", response_model=ResumeProfileRead)
def get_user_resume(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume = db.query(ResumeProfile).filter(ResumeProfile.user_id == user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="No resume profile found. Please upload one.")
    return resume


@router.post("/upload", response_model=ResumeProfileRead)
async def upload_resume(
    file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    content = ""
    if file:
        raw_bytes = await file.read()
        content = raw_bytes.decode("utf-8", errors="ignore")
    elif resume_text:
        content = resume_text
    else:
        raise HTTPException(status_code=400, detail="Provide either a file or resume text.")

    if not content.strip():
        raise HTTPException(status_code=400, detail="Uploaded resume content is empty.")

    # Generate embedding
    vec = embedding_service.embed_text(content)

    resume = db.query(ResumeProfile).filter(ResumeProfile.user_id == user.id).first()
    if not resume:
        resume = ResumeProfile(
            id=str(uuid.uuid4()),
            user_id=user.id,
            full_name=user.full_name or "Candidate",
            summary=content[:250],
            raw_text=content,
            experience_years=2.0,
            education_level="Bachelor of Technology",
            embedding_json=vec
        )
        db.add(resume)
    else:
        resume.raw_text = content
        resume.summary = content[:250]
        resume.embedding_json = vec

    db.commit()
    db.refresh(resume)

    # Basic skill extraction from text
    known_skills = ["Python", "Java", "C++", "JavaScript", "TypeScript", "React", "Node.js",
                    "SQL", "PostgreSQL", "Docker", "Kubernetes", "AWS", "Git", "REST APIs", "FastAPI"]
    existing_skills = {s.skill_name.lower() for s in resume.skills}
    content_lower = content.lower()

    for skill in known_skills:
        if skill.lower() in content_lower and skill.lower() not in existing_skills:
            db.add(ResumeSkill(
                id=str(uuid.uuid4()),
                resume_id=resume.id,
                skill_name=skill,
                category="Technical",
                proficiency_level="Proficient"
            ))

    db.add(AuditLog(
        user_id=user.id,
        event_type="RESUME_UPLOADED",
        target_resource=f"resume:{resume.id}",
        action_taken="Parsed resume and updated vector profile",
        performed_by="USER"
    ))
    db.commit()
    db.refresh(resume)
    return resume


@router.post("/skills", response_model=ResumeSkillRead)
def add_resume_skill(
    req: ResumeSkillCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume = db.query(ResumeProfile).filter(ResumeProfile.user_id == user.id).first()
    if not resume:
        raise HTTPException(status_code=400, detail="Create resume profile first.")

    skill = ResumeSkill(
        id=str(uuid.uuid4()),
        resume_id=resume.id,
        skill_name=req.skill_name,
        category=req.category,
        proficiency_level=req.proficiency_level
    )
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


@router.delete("/skills/{skill_id}")
def delete_resume_skill(
    skill_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    skill = db.query(ResumeSkill).filter(ResumeSkill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    db.delete(skill)
    db.commit()
    return {"status": "SUCCESS", "message": "Skill deleted."}
