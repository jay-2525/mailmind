import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.email import EmailThread, Email, EmailEmbedding, EmailAnalysis, ExtractedEntity
from app.models.task import Task, Commitment
from app.models.job import Job, JobSkill, ResumeProfile, ResumeSkill, JobMatch
from app.models.action import Recommendation, Approval, CalendarEvent, AuditLog
from app.services.embedding import embedding_service
from app.scoring.waste_scorer import storage_waste_scorer
from app.scoring.job_matcher import job_matcher
from app.scoring.trust_scorer import job_trust_scorer
from app.core.config import settings


def seed_demo_data(db: Session) -> User:
    """
    Populates the database with realistic, high-fidelity demo emails and candidate profiles.
    Completely resets demo state if already populated.
    """
    # 1. Check or create demo user
    user = db.query(User).filter(User.email == settings.DEMO_USER_EMAIL).first()
    if user:
        # Delete previous demo data to ensure a clean idempotent state
        db.delete(user)
        db.commit()

    user = User(
        id=str(uuid.uuid4()),
        email=settings.DEMO_USER_EMAIL,
        full_name=settings.DEMO_USER_NAME,
        is_demo=True,
        preferences={"theme": "dark", "auto_analyze": True}
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    now = datetime.now(timezone.utc)

    # 2. Seed Candidate Resume Profile
    resume_text = (
        "Alex Morgan - Senior B.Tech Computer Science and Engineering Student.\n"
        "Proficient in Python, Java, SQL, Git, REST APIs, FastAPI, Docker, and React.\n"
        "Experience building scalable distributed web applications, machine learning pipelines, "
        "and cloud microservices. Education: Bachelor of Technology in CSE, GPA 8.9/10."
    )
    resume_embedding = embedding_service.embed_text(resume_text)

    resume = ResumeProfile(
        id=str(uuid.uuid4()),
        user_id=user.id,
        full_name="Alex Morgan",
        summary="Final year B.Tech Computer Science student specializing in AI systems, backend microservices, and modern web architectures.",
        raw_text=resume_text,
        experience_years=1.5,
        education_level="Bachelor of Technology in Computer Science",
        embedding_json=resume_embedding
    )
    db.add(resume)
    db.commit()

    candidate_skills = [
        ("Python", "Technical", "Expert"),
        ("Java", "Technical", "Proficient"),
        ("SQL", "Technical", "Proficient"),
        ("Git", "Technical", "Proficient"),
        ("REST APIs", "Technical", "Expert"),
        ("FastAPI", "Technical", "Proficient"),
        ("Docker", "Technical", "Intermediate"),
        ("React", "Technical", "Proficient"),
    ]
    for skill_name, cat, prof in candidate_skills:
        db.add(ResumeSkill(
            id=str(uuid.uuid4()),
            resume_id=resume.id,
            skill_name=skill_name,
            category=cat,
            proficiency_level=prof
        ))
    db.commit()

    # 3. Seed Dataset Definitions
    demo_emails_def = [
        {
            "key": "assignment",
            "thread_external": "thread_uni_001",
            "subject": "CS401: Distributed Systems - Final Project Submission Deadline",
            "sender": "prof.roberts@university.edu",
            "sender_name": "Prof. David Roberts",
            "recipients": [user.email],
            "body": (
                "Dear Class,\n\n"
                "This is a gentle reminder that the final project submission for CS401: Distributed Systems "
                "is due this Friday at 5:00 PM. Please make sure to submit your complete Git repository link, "
                "architecture documentation, and test reports via the student portal.\n\n"
                "Late submissions will incur a 10% penalty per day. I will hold office hours tomorrow from 2 PM to 4 PM.\n\n"
                "Best regards,\nProf. David Roberts"
            ),
            "received_at": now - timedelta(hours=4),
            "size_bytes": 18450,
            "has_attachments": False,
            "category": "Education",
            "importance": 0.90,
            "urgency": 0.85,
            "actionability": 0.90,
            "is_promotional": False,
            "is_job_related": False,
            "tasks": [
                {"title": "Submit CS401 Distributed Systems final project and Git link", "deadline": now + timedelta(days=2), "priority": "HIGH"}
            ],
            "commitments": [],
            "action": "REMIND",
            "risk_level": "MEDIUM"
        },
        {
            "key": "meeting",
            "thread_external": "thread_sprint_002",
            "subject": "Invitation: Capstone Project Architecture Review & Sprint Sync",
            "sender": "priya.sharma@techcorp.io",
            "sender_name": "Priya Sharma",
            "recipients": [user.email, "dev-team@techcorp.io"],
            "body": (
                "Hi Alex,\n\n"
                "Let us connect tomorrow from 3:00 PM to 4:00 PM for our Capstone Project Architecture Review. "
                "We will evaluate the LangGraph agent state machine, RAG vector retrieval latency, and approval workflow.\n\n"
                "Meeting link: https://meet.google.com/xyz-inboxguard-demo\n\n"
                "See you all tomorrow!\nRegards,\nPriya"
            ),
            "received_at": now - timedelta(hours=10),
            "size_bytes": 12300,
            "has_attachments": False,
            "category": "Meeting",
            "importance": 0.80,
            "urgency": 0.70,
            "actionability": 0.85,
            "is_promotional": False,
            "is_job_related": False,
            "tasks": [],
            "commitments": [],
            "calendar_event": {
                "title": "Capstone Project Architecture Review & Sprint Sync",
                "start_time": now + timedelta(days=1, hours=2),
                "end_time": now + timedelta(days=1, hours=3),
                "location": "Google Meet (https://meet.google.com/xyz-inboxguard-demo)"
            },
            "action": "SCHEDULE",
            "risk_level": "MEDIUM"
        },
        {
            "key": "promo1",
            "thread_external": "thread_promo_003",
            "subject": "Mega Cloud Hosting Clearance - 80% OFF Dedicated Servers!",
            "sender": "deals@cloudhoster-specials.com",
            "sender_name": "Cloud Hoster Specials",
            "recipients": [user.email],
            "body": (
                "Unbeatable flash sale! Get up to 80% off on premium dedicated servers, VPS instances, "
                "and domain names this weekend only! Use code MEGA80 at checkout. Click here to claim your discount. "
                "To unsubscribe from marketing updates, click here."
            ),
            "received_at": now - timedelta(days=45),
            "size_bytes": 354000,
            "has_attachments": False,
            "category": "Promotion",
            "importance": 0.15,
            "urgency": 0.10,
            "actionability": 0.05,
            "is_promotional": True,
            "is_job_related": False,
            "tasks": [],
            "commitments": [],
            "action": "ARCHIVE",
            "risk_level": "LOW"
        },
        {
            "key": "promo_dup",
            "thread_external": "thread_promo_004",
            "subject": "Fwd: Mega Cloud Hosting Clearance - 80% OFF Dedicated Servers!",
            "sender": "deals@cloudhoster-specials.com",
            "sender_name": "Cloud Hoster Specials",
            "recipients": [user.email],
            "body": (
                "Unbeatable flash sale! Get up to 80% off on premium dedicated servers, VPS instances, "
                "and domain names this weekend only! Use code MEGA80 at checkout. Click here to claim your discount. "
                "To unsubscribe from marketing updates, click here."
            ),
            "received_at": now - timedelta(days=40),
            "size_bytes": 356000,
            "has_attachments": False,
            "category": "Promotion",
            "importance": 0.10,
            "urgency": 0.10,
            "actionability": 0.0,
            "is_promotional": True,
            "is_job_related": False,
            "tasks": [],
            "commitments": [],
            "action": "DELETE",
            "risk_level": "HIGH"
        },
        {
            "key": "large_file",
            "thread_external": "thread_asset_005",
            "subject": "Outdated Raw 4K Video B-Roll Assets for Marketing Campaign",
            "sender": "media@marketingagency.org",
            "sender_name": "Creative Media Team",
            "recipients": [user.email],
            "body": (
                "Attached are the raw uncompressed video takes (24 MB) from last quarter's promotional shoot. "
                "These are no longer needed as the final edits have been published."
            ),
            "received_at": now - timedelta(days=95),
            "size_bytes": 25165824,  # 24 MB
            "has_attachments": True,
            "attachment_metadata": [{"filename": "broll_take1_raw.mp4", "size_bytes": 25165824, "content_type": "video/mp4"}],
            "category": "Other",
            "importance": 0.10,
            "urgency": 0.10,
            "actionability": 0.0,
            "is_promotional": False,
            "is_job_related": False,
            "tasks": [],
            "commitments": [],
            "action": "DELETE",
            "risk_level": "HIGH"
        },
        {
            "key": "newsletter",
            "thread_external": "thread_news_006",
            "subject": "The AI Engineering Dispatch: Issue #89",
            "sender": "newsletter@aiengineering.dev",
            "sender_name": "AI Engineering Weekly",
            "recipients": [user.email],
            "body": (
                "In this week's issue: Advancements in Small Language Models, Hybrid RAG pipelines with Reciprocal Rank Fusion, "
                "and agentic orchestration patterns with LangGraph. Read the full issue online."
            ),
            "received_at": now - timedelta(days=14),
            "size_bytes": 85000,
            "has_attachments": False,
            "category": "Newsletter",
            "importance": 0.35,
            "urgency": 0.15,
            "actionability": 0.10,
            "is_promotional": True,
            "is_job_related": False,
            "tasks": [],
            "commitments": [],
            "action": "ARCHIVE",
            "risk_level": "LOW"
        },
        {
            "key": "job_google",
            "thread_external": "thread_job_007",
            "subject": "Google Careers: Software Engineer Intern (Backend Systems) - Opportunity",
            "sender": "university-recruiting@google.com",
            "sender_name": "Google University Recruiting",
            "recipients": [user.email],
            "body": (
                "Dear Alex,\n\n"
                "We reviewed your profile and wanted to invite you to apply for our Software Engineer Intern position "
                "in Cloud & Distributed Systems. We are looking for candidates pursuing a Bachelor's degree in Computer Science.\n\n"
                "Key requirements:\n"
                "- Strong problem-solving skills in Java, Python, or C++\n"
                "- Experience with SQL and relational databases\n"
                "- Understanding of REST APIs and Git version control\n"
                "- Familiarity with Docker or Kubernetes is preferred\n\n"
                "Location: Mountain View, CA / Hybrid. Application deadline: October 31, 2026.\n"
                "Please submit your application at: https://careers.google.com/jobs/results/sw-intern-2026\n\n"
                "Best regards,\nGoogle University Programs Team"
            ),
            "received_at": now - timedelta(hours=8),
            "size_bytes": 22400,
            "has_attachments": False,
            "category": "Job Opportunity",
            "importance": 0.95,
            "urgency": 0.80,
            "actionability": 0.95,
            "is_promotional": False,
            "is_job_related": True,
            "job_details": {
                "company": "Google",
                "role": "Software Engineer Intern (Backend Systems)",
                "location": "Mountain View, CA / Hybrid",
                "work_type": "HYBRID",
                "salary_range": "$55 - $65 / hr",
                "experience_years": 1.0,
                "education": "Bachelor of Technology in Computer Science",
                "application_url": "https://careers.google.com/jobs/results/sw-intern-2026",
                "deadline": now + timedelta(days=30),
                "recruiter_email": "university-recruiting@google.com",
                "required_skills": ["Python", "Java", "SQL", "Git", "REST APIs"],
                "preferred_skills": ["Docker", "Kubernetes", "Cloud"]
            },
            "tasks": [],
            "commitments": [],
            "action": "PREPARE_APPLICATION",
            "risk_level": "MEDIUM"
        },
        {
            "key": "job_phishing",
            "thread_external": "thread_scam_008",
            "subject": "URGENT IMMEDIATE HIRE: Data Entry Clerk ($45/hr) - No Interview Needed",
            "sender": "hiring.manager.careers@gmail.com",
            "sender_name": "Executive Hiring Consultant",
            "recipients": [user.email],
            "body": (
                "Congratulations! You have been selected for immediate remote employment as a Data Entry Specialist at Global Logistics Inc. "
                "Salary is $45 per hour. No prior interview needed! We will mail you a cashier check of $2,500 to purchase home office equipment. "
                "You must deposit the check and wire transfer the remaining balance via Bitcoin or Western Union within 24 hours. "
                "Contact our manager on Telegram immediately to receive your offer letter."
            ),
            "received_at": now - timedelta(hours=18),
            "size_bytes": 14500,
            "has_attachments": False,
            "category": "Job Opportunity",
            "importance": 0.30,
            "urgency": 0.90,
            "actionability": 0.20,
            "is_promotional": False,
            "is_job_related": True,
            "job_details": {
                "company": "Global Logistics Inc",
                "role": "Data Entry Specialist",
                "location": "Remote",
                "work_type": "REMOTE",
                "salary_range": "$45 / hr",
                "experience_years": 0.0,
                "education": "High School",
                "application_url": "",
                "deadline": now + timedelta(days=1),
                "recruiter_email": "hiring.manager.careers@gmail.com",
                "required_skills": ["Data Entry", "Fast Typing"],
                "preferred_skills": []
            },
            "tasks": [],
            "commitments": [],
            "action": "REVIEW_REQUIRED",
            "risk_level": "HIGH"
        },
        {
            "key": "followup",
            "thread_external": "thread_research_009",
            "subject": "Following up on our AI Research Paper draft",
            "sender": "dr.chen@institute.org",
            "sender_name": "Dr. Alan Chen",
            "recipients": [user.email],
            "body": (
                "Hi Alex,\n\n"
                "Following up on our discussion regarding the benchmark results for the Agentic RAG paper. "
                "Have you finished running the evaluation scripts on the pgvector test split? "
                "Let me know so we can finalize Section 4.\n\n"
                "Thanks,\nAlan"
            ),
            "received_at": now - timedelta(days=1, hours=3),
            "size_bytes": 16200,
            "has_attachments": False,
            "category": "Education",
            "importance": 0.85,
            "urgency": 0.75,
            "actionability": 0.80,
            "is_promotional": False,
            "is_job_related": False,
            "tasks": [
                {"title": "Run evaluation scripts on pgvector test split for Section 4", "deadline": now + timedelta(days=3), "priority": "HIGH"}
            ],
            "commitments": [],
            "action": "FOLLOW_UP",
            "risk_level": "MEDIUM"
        },
        {
            "key": "commitment_self",
            "thread_external": "thread_commit_010",
            "subject": "Re: Project Milestone 3 Deliverables",
            "sender": user.email,
            "sender_name": "Alex Morgan",
            "recipients": ["prof.roberts@university.edu"],
            "body": (
                "Dear Prof. Roberts,\n\n"
                "Thank you for the constructive feedback on our project design. "
                "I will complete the backend API documentation and upload the OpenAPI specification by tomorrow at 6:00 PM.\n\n"
                "Best regards,\nAlex"
            ),
            "received_at": now - timedelta(hours=6),
            "size_bytes": 11800,
            "has_attachments": False,
            "category": "Education",
            "importance": 0.80,
            "urgency": 0.70,
            "actionability": 0.85,
            "is_promotional": False,
            "is_job_related": False,
            "tasks": [],
            "commitments": [
                {
                    "statement": "Complete backend API documentation and upload OpenAPI specification",
                    "owner": "SELF",
                    "deadline": now + timedelta(days=1),
                    "state": "PROMISED"
                }
            ],
            "action": "REMIND",
            "risk_level": "MEDIUM"
        }
    ]

    created_emails = []

    # Iterate and build models
    for item in demo_emails_def:
        # Create thread
        thread = EmailThread(
            id=str(uuid.uuid4()),
            user_id=user.id,
            thread_id_external=item["thread_external"],
            subject=item["subject"],
            snippet=item["body"][:150],
            message_count=1,
            last_message_at=item["received_at"]
        )
        db.add(thread)
        db.commit()

        email = Email(
            id=str(uuid.uuid4()),
            thread_id=thread.id,
            user_id=user.id,
            message_id_external=f"msg_{item['key']}_{uuid.uuid4().hex[:8]}",
            sender=item["sender"],
            sender_name=item["sender_name"],
            recipients=item["recipients"],
            subject=item["subject"],
            body_text=item["body"],
            received_at=item["received_at"],
            labels=["INBOX", item["category"]],
            size_bytes=item["size_bytes"],
            has_attachments=item["has_attachments"],
            attachment_metadata=item.get("attachment_metadata", []),
            processing_status="PROCESSED"
        )
        db.add(email)
        db.commit()
        created_emails.append(email)

        # Generate and store embedding
        vec = embedding_service.embed_text(f"{item['subject']}\n{item['body']}")
        db.add(EmailEmbedding(
            id=str(uuid.uuid4()),
            email_id=email.id,
            embedding_vector=vec,
            chunk_text=item["body"][:500]
        ))

        # Compute Waste Score
        has_tasks = len(item.get("tasks", [])) > 0
        has_commitments = len(item.get("commitments", [])) > 0
        redundancy_val = 0.92 if item["key"] == "promo_dup" else 0.0

        waste_eval = storage_waste_scorer.compute_waste_score(
            size_bytes=item["size_bytes"],
            is_promotional=item["is_promotional"],
            redundancy_score=redundancy_val,
            received_at=item["received_at"],
            has_tasks=has_tasks,
            has_commitments=has_commitments,
            category=item["category"]
        )

        analysis = EmailAnalysis(
            id=str(uuid.uuid4()),
            email_id=email.id,
            category=item["category"],
            importance=item["importance"],
            urgency=item["urgency"],
            actionability=item["actionability"],
            storage_waste_score=waste_eval["waste_score"],
            is_promotional=item["is_promotional"],
            is_job_related=item["is_job_related"],
            security_risk_level="HIGH" if item["key"] == "job_phishing" else "LOW",
            security_risk_reasons=["High risk recruitment scam indicators"] if item["key"] == "job_phishing" else [],
            summary=item["subject"],
            raw_analysis={"waste_breakdown": waste_eval["breakdown"]}
        )
        db.add(analysis)

        # Add tasks
        for t in item.get("tasks", []):
            db.add(Task(
                id=str(uuid.uuid4()),
                email_id=email.id,
                user_id=user.id,
                title=t["title"],
                deadline=t["deadline"],
                priority=t["priority"],
                status="OPEN",
                confidence=0.92
            ))

        # Add commitments
        for c in item.get("commitments", []):
            db.add(Commitment(
                id=str(uuid.uuid4()),
                email_id=email.id,
                user_id=user.id,
                statement=c["statement"],
                owner=c["owner"],
                deadline=c["deadline"],
                state=c["state"],
                last_state_change_at=now
            ))

        # Add calendar event if applicable
        if "calendar_event" in item:
            ce = item["calendar_event"]
            db.add(CalendarEvent(
                id=str(uuid.uuid4()),
                user_id=user.id,
                email_id=email.id,
                title=ce["title"],
                description=f"Extracted from email: {item['subject']}",
                start_time=ce["start_time"],
                end_time=ce["end_time"],
                location=ce["location"],
                status="TENTATIVE"
            ))

        # Add job if applicable
        if item.get("job_details"):
            jd = item["job_details"]
            trust_eval = job_trust_scorer.evaluate_job_trust(
                sender_email=jd["recruiter_email"],
                company_name=jd["company"],
                job_description=item["body"],
                application_url=jd["application_url"]
            )

            job = Job(
                id=str(uuid.uuid4()),
                email_id=email.id,
                user_id=user.id,
                company=jd["company"],
                role=jd["role"],
                location=jd["location"],
                work_type=jd["work_type"],
                salary_range=jd["salary_range"],
                experience_years=jd["experience_years"],
                education=jd["education"],
                application_url=jd["application_url"],
                deadline=jd["deadline"],
                recruiter_email=jd["recruiter_email"],
                trust_score=trust_eval["trust_score"],
                trust_level=trust_eval["trust_level"],
                trust_reasons=trust_eval["reasons"],
                raw_description=item["body"]
            )
            db.add(job)
            db.commit()

            # Add required skills
            for req_skill in jd["required_skills"]:
                db.add(JobSkill(
                    id=str(uuid.uuid4()),
                    job_id=job.id,
                    skill_name=req_skill,
                    skill_type="REQUIRED"
                ))
            for pref_skill in jd["preferred_skills"]:
                db.add(JobSkill(
                    id=str(uuid.uuid4()),
                    job_id=job.id,
                    skill_name=pref_skill,
                    skill_type="PREFERRED"
                ))
            db.commit()

            # Calculate match with candidate resume
            cand_skill_names = [s[0] for s in candidate_skills]
            match_eval = job_matcher.match_job(
                job_required_skills=jd["required_skills"],
                job_preferred_skills=jd["preferred_skills"],
                candidate_skills=cand_skill_names,
                job_experience_years=jd["experience_years"],
                candidate_experience_years=resume.experience_years,
                job_education=jd["education"],
                candidate_education=resume.education_level or "",
                job_embedding=vec,
                resume_embedding=resume_embedding
            )

            job_match = JobMatch(
                id=str(uuid.uuid4()),
                job_id=job.id,
                resume_id=resume.id,
                match_score=match_eval["match_score"],
                required_skill_match_pct=match_eval["breakdown"]["required_skill_match_pct"],
                preferred_skill_match_pct=match_eval["breakdown"]["preferred_skill_match_pct"],
                semantic_similarity_pct=match_eval["breakdown"]["semantic_similarity_pct"],
                experience_match_pct=match_eval["breakdown"]["experience_match_pct"],
                education_match_pct=match_eval["breakdown"]["education_match_pct"],
                matched_skills=match_eval["matched_skills"],
                missing_skills=match_eval["missing_skills"],
                prepared_application={
                    "cover_letter": f"Dear Hiring Team at {jd['company']},\n\nI am thrilled to apply for the {jd['role']} role...",
                    "recruiter_pitch": f"Hi {jd['company']} Recruiting, excited about the {jd['role']} opportunity!"
                }
            )
            db.add(job_match)

        # Add recommendation
        rec = Recommendation(
            id=str(uuid.uuid4()),
            email_id=email.id,
            user_id=user.id,
            action=item["action"],
            confidence=0.88,
            reasons=[f"Classified as {item['category']} with urgency {item['urgency']}"],
            supporting_signals={"waste_score": waste_eval["waste_score"]},
            risk_level=item["risk_level"],
            status="PENDING" if item["risk_level"] in ["MEDIUM", "HIGH"] else "APPROVED"
        )
        db.add(rec)
        db.commit()

        # If high risk (delete) or medium risk (schedule, application), add to Approval Center
        if item["risk_level"] in ["MEDIUM", "HIGH"]:
            approval = Approval(
                id=str(uuid.uuid4()),
                recommendation_id=rec.id,
                user_id=user.id,
                action_type=item["action"],
                target_resource=f"Email: {item['subject']}",
                risk_level=item["risk_level"],
                reason=f"Recommendation: {item['action']}. Risk level: {item['risk_level']}.",
                evidence={"subject": item["subject"], "sender": item["sender"], "size_bytes": item["size_bytes"]},
                consequences="Destructive or calendar modification requiring human-in-the-loop authorization.",
                status="PENDING"
            )
            db.add(approval)

        # Audit log
        db.add(AuditLog(
            id=str(uuid.uuid4()),
            user_id=user.id,
            event_type="EMAIL_ANALYZED",
            target_resource=f"email:{email.id}",
            action_taken=f"Analyzed {item['subject'][:40]}",
            reason="Initial ingestion and LangGraph analysis pipeline completed",
            performed_by="AGENT",
            metadata_json={"action": item["action"], "risk_level": item["risk_level"]}
        ))

    db.commit()
    print(f"[SeedData] Successfully seeded {len(demo_emails_def)} demo emails for {user.email}")
    return user
