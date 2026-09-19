from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.nlp.entity_extractor import entity_extractor
from app.services.nlp.temporal_parser import temporal_parser
from app.services.embedding import embedding_service
from app.services.llm_provider import llm_provider
from app.scoring.waste_scorer import storage_waste_scorer
from app.scoring.redundancy_detector import redundancy_detector
from app.scoring.trust_scorer import job_trust_scorer
from app.scoring.job_matcher import job_matcher
from app.services.commitment_fsm import commitment_fsm
from app.safety.policy_guard import safety_policy_guard
from app.agents.langgraph_workflow import email_intelligence_graph
from app.rag.hybrid_rag import hybrid_rag_service

router = APIRouter()


class AcademicDemoRequest(BaseModel):
    step_name: str
    input_data: Dict[str, Any]


@router.post("/pipeline-step")
def run_academic_pipeline_step(
    req: AcademicDemoRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Interactive Algorithm Inspector for Academic Viva and B.Tech Project Review.
    Executes an individual pipeline algorithm and returns step-by-step math and outputs.
    """
    step = req.step_name.lower()
    data = req.input_data

    if step == "ner":
        text = data.get("text", "Please submit the report to Prof. David Roberts at university.edu by Friday 5 PM.")
        entities = entity_extractor.extract_entities(text)
        return {
            "algorithm": "Named Entity Recognition (NER)",
            "input": text,
            "intermediate": f"Scanned for ORG, PERSON, DEADLINE, MONEY, URL using regex-augmented lexical parsing.",
            "output": entities
        }

    elif step == "temporal":
        text = data.get("text", "Submit the project by this Friday at 5:00 PM.")
        parsed_dt = temporal_parser.parse_deadline(text)
        return {
            "algorithm": "Temporal and Deadline Extraction",
            "input": text,
            "intermediate": "Parsed day token and time offset relative to current reference time.",
            "output": {
                "parsed_iso": parsed_dt.isoformat() if parsed_dt else None,
                "weekday": parsed_dt.strftime("%A") if parsed_dt else None,
                "time": parsed_dt.strftime("%I:%M %p") if parsed_dt else None
            }
        }

    elif step == "waste_score":
        size_bytes = data.get("size_bytes", 15728640)  # 15 MB
        is_promo = data.get("is_promotional", True)
        redundancy_score = data.get("redundancy_score", 0.90)
        has_tasks = data.get("has_tasks", False)
        has_commitments = data.get("has_commitments", False)

        eval_result = storage_waste_scorer.compute_waste_score(
            size_bytes=size_bytes,
            is_promotional=is_promo,
            redundancy_score=redundancy_score,
            received_at=datetime.now(timezone.utc),
            has_tasks=has_tasks,
            has_commitments=has_commitments,
            category="Promotion"
        )
        return {
            "algorithm": "Storage Waste Scoring Formula",
            "formula": "Waste Score = min(100, sum(w_i * s_i) - sum(v_j * p_j))",
            "input": {
                "size_mb": size_bytes / (1024*1024),
                "is_promotional": is_promo,
                "redundancy_score": redundancy_score,
                "has_tasks": has_tasks
            },
            "output": eval_result
        }

    elif step == "duplicate_detection":
        subject_a = data.get("subject_a", "Mega Cloud Hosting Clearance - 80% OFF")
        subject_b = data.get("subject_b", "Fwd: Mega Cloud Hosting Clearance - 80% OFF")
        text_a = data.get("text_a", "Unbeatable flash sale for cloud instances!")
        text_b = data.get("text_b", "Unbeatable flash sale for cloud instances!")

        vec_a = embedding_service.embed_text(f"{subject_a}\n{text_a}")
        vec_b = embedding_service.embed_text(f"{subject_b}\n{text_b}")
        sim = embedding_service.cosine_similarity(vec_a, vec_b)

        norm_a = redundancy_detector.normalize_subject(subject_a)
        norm_b = redundancy_detector.normalize_subject(subject_b)

        return {
            "algorithm": "Semantic Duplicate & Redundancy Detection",
            "formula": "cosine_similarity = dot(A, B) / (norm(A) * norm(B))",
            "normalized_subjects": {"a": norm_a, "b": norm_b, "match": norm_a == norm_b},
            "cosine_similarity": round(sim, 4),
            "is_duplicate": sim >= 0.88 or (norm_a == norm_b and sim >= 0.75),
            "threshold": 0.88
        }

    elif step == "job_matching":
        req_skills = data.get("required_skills", ["Java", "Python", "SQL", "Git"])
        cand_skills = data.get("candidate_skills", ["Java", "Python", "SQL", "Git", "React"])
        cand_exp = data.get("candidate_exp", 1.5)
        job_exp = data.get("job_exp", 1.0)
        cand_edu = data.get("candidate_edu", "Bachelor of Technology in CS")
        job_edu = data.get("job_edu", "Bachelor of Technology in CS")

        res = job_matcher.match_job(
            job_required_skills=req_skills,
            job_preferred_skills=["Docker", "Cloud"],
            candidate_skills=cand_skills,
            job_experience_years=job_exp,
            candidate_experience_years=cand_exp,
            job_education=job_edu,
            candidate_education=cand_edu,
            job_embedding=[0.5] * 384,
            resume_embedding=[0.5] * 384
        )
        return {
            "algorithm": "Job Match Scoring Engine",
            "formula": "0.35 * S_req + 0.15 * S_pref + 0.20 * S_sem + 0.15 * S_exp + 0.15 * S_edu",
            "output": res
        }

    elif step == "trust_analysis":
        sender = data.get("sender", "careers.consultant@gmail.com")
        company = data.get("company", "Global Tech Corp")
        desc = data.get("body", "Immediate hire! Cashier check will be mailed. Deposit and wire transfer via Western Union.")

        trust_res = job_trust_scorer.evaluate_job_trust(sender, company, desc)
        return {
            "algorithm": "Job & Recruiter Trust Risk Analysis",
            "input": {"sender": sender, "company": company},
            "output": trust_res
        }

    elif step == "commitment_fsm":
        current_state = data.get("current_state", "PROMISED")
        new_state = data.get("new_state", "COMPLETED")
        can_move = commitment_fsm.can_transition(current_state, new_state)

        return {
            "algorithm": "Commitment Finite State Machine (FSM)",
            "states": ["OPEN", "PROMISED", "COMPLETED", "OVERDUE", "CANCELLED"],
            "transition": f"{current_state} -> {new_state}",
            "is_valid_transition": can_move,
            "allowed_from_current": commitment_fsm.VALID_TRANSITIONS.get(current_state.upper(), [])
        }

    elif step == "rag":
        query = data.get("query", "distributed systems assignment deadline")
        rag_res = hybrid_rag_service.retrieve_context(db=db, query=query, user_id=user.id, top_k=3)
        return {
            "algorithm": "Hybrid RAG (Dense Vector + Sparse Keyword RRF)",
            "query": query,
            "retrieved_count": len(rag_res),
            "results": rag_res
        }

    elif step == "safety_policy":
        action = data.get("action", "DELETE")
        injection = data.get("prompt_injection", True)
        pol = safety_policy_guard.evaluate_action_policy(
            recommended_action=action,
            confidence=0.90,
            security_risk_level="HIGH" if injection else "LOW",
            prompt_injection_flag=injection
        )
        return {
            "algorithm": "Safety & Policy Guard (Untrusted Input Quarantine)",
            "input": {"action": action, "prompt_injection_detected": injection},
            "output": pol
        }

    elif step == "langgraph":
        sample_state = {
            "subject": data.get("subject", "Immediate meeting request"),
            "body": data.get("body", "Please connect tomorrow at 3 PM to review the final code."),
            "sender": data.get("sender", "team@techcorp.io"),
            "size_bytes": 12000,
            "has_attachments": False
        }
        res = email_intelligence_graph.invoke(sample_state)
        return {
            "algorithm": "LangGraph Orchestrated Agent State Machine",
            "nodes_traversed": [
                "START", "understand_email", "retrieve_context",
                "storage_analysis", "task_commitment", "job_analysis",
                "decision_agent", "safety_policy", "END"
            ],
            "state_output": {
                "recommendation": res.get("recommendation"),
                "policy_result": res.get("policy_result"),
                "approval_status": res.get("approval_status"),
                "waste_score": res.get("storage_analysis", {}).get("waste_score"),
                "tasks_count": len(res.get("tasks", [])),
                "commitments_count": len(res.get("commitments", []))
            }
        }

    return {"error": f"Unknown step '{step_name}'."}
