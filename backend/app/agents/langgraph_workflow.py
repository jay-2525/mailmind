from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, TypedDict
from langgraph.graph import StateGraph, START, END

from app.services.llm_provider import llm_provider
from app.services.embedding import embedding_service
from app.services.nlp.entity_extractor import entity_extractor
from app.scoring.waste_scorer import storage_waste_scorer
from app.scoring.redundancy_detector import redundancy_detector
from app.scoring.trust_scorer import job_trust_scorer
from app.scoring.job_matcher import job_matcher
from app.safety.policy_guard import safety_policy_guard


class AgentState(TypedDict, total=False):
    user_id: str
    email_id: str
    subject: str
    body: str
    sender: str
    received_at: str
    size_bytes: int
    has_attachments: bool

    # Pipeline stages
    email_analysis: Dict[str, Any]
    entities: List[Dict[str, Any]]
    retrieved_context: List[Dict[str, Any]]
    storage_analysis: Dict[str, Any]
    tasks: List[Dict[str, Any]]
    commitments: List[Dict[str, Any]]
    job_analysis: Optional[Dict[str, Any]]
    recommendation: Dict[str, Any]
    policy_result: Dict[str, Any]
    approval_status: str
    action_result: Optional[Dict[str, Any]]


def understand_email_node(state: AgentState) -> Dict[str, Any]:
    """Node 1: Extract intent, category, entities, tasks, and initial signals."""
    subject = state.get("subject", "")
    body = state.get("body", "")
    sender = state.get("sender", "")

    analysis = llm_provider.analyze_email(subject, body, sender)
    entities = entity_extractor.extract_entities(f"{subject}\n{body}")

    return {
        "email_analysis": analysis,
        "entities": entities,
        "tasks": analysis.get("extracted_tasks", []),
        "commitments": analysis.get("commitments", [])
    }


def retrieve_context_node(state: AgentState) -> Dict[str, Any]:
    """Node 2: Retrieve historical email context (simulated in state or passed from caller)."""
    # Context retrieval signals are passed or initialized
    return {
        "retrieved_context": state.get("retrieved_context", [])
    }


def storage_analysis_node(state: AgentState) -> Dict[str, Any]:
    """Node 3: Compute Storage Waste Score and redundancy signals."""
    size_bytes = state.get("size_bytes", 0)
    analysis = state.get("email_analysis", {})
    category = analysis.get("category", "Other")
    is_promotional = analysis.get("is_promotional", False)
    has_tasks = len(state.get("tasks", [])) > 0
    has_commitments = len(state.get("commitments", [])) > 0

    # Parse date
    rec_str = state.get("received_at", datetime.now(timezone.utc).isoformat())
    try:
        received_at = datetime.fromisoformat(rec_str)
    except Exception:
        received_at = datetime.now(timezone.utc)

    # Redundancy score (from caller or default 0.0)
    redundancy_info = state.get("storage_analysis", {})
    redundancy_score = redundancy_info.get("redundancy_score", 0.0)

    waste_result = storage_waste_scorer.compute_waste_score(
        size_bytes=size_bytes,
        is_promotional=is_promotional,
        redundancy_score=redundancy_score,
        received_at=received_at,
        has_tasks=has_tasks,
        has_commitments=has_commitments,
        category=category,
        future_value_indicators=category in ["Finance", "Security", "Education"]
    )

    return {"storage_analysis": waste_result}


def task_commitment_node(state: AgentState) -> Dict[str, Any]:
    """Node 4: Validate and track tasks and commitment state."""
    tasks = state.get("tasks", [])
    commitments = state.get("commitments", [])
    return {"tasks": tasks, "commitments": commitments}


def job_analysis_node(state: AgentState) -> Dict[str, Any]:
    """Node 5: Analyze job opportunities and recruiter trust."""
    analysis = state.get("email_analysis", {})
    if not analysis.get("is_job_related", False):
        return {"job_analysis": None}

    subject = state.get("subject", "")
    body = state.get("body", "")
    sender = state.get("sender", "")

    # Evaluate recruiter trust
    trust_eval = job_trust_scorer.evaluate_job_trust(
        sender_email=sender,
        company_name="Identified Employer",
        job_description=f"{subject}\n{body}"
    )

    job_data = {
        "is_job": True,
        "trust_score": trust_eval["trust_score"],
        "trust_level": trust_eval["trust_level"],
        "trust_reasons": trust_eval["reasons"]
    }
    return {"job_analysis": job_data}


def decision_agent_node(state: AgentState) -> Dict[str, Any]:
    """Node 6: Synthesize multi-signal intelligence into recommended action."""
    analysis = state.get("email_analysis", {})
    storage = state.get("storage_analysis", {})
    job = state.get("job_analysis")
    tasks = state.get("tasks", [])
    commitments = state.get("commitments", [])
    category = analysis.get("category", "Other")

    waste_score = storage.get("waste_score", 0.0)
    urgency = analysis.get("urgency", 0.5)

    reasons: List[str] = []
    action = "KEEP"
    confidence = 0.85

    if job is not None:
        if job["trust_level"] == "HIGH_RISK_SIGNALS":
            action = "REVIEW_REQUIRED"
            confidence = 0.90
            reasons.append("Job email contains high-risk recruiter signals. Caution advised.")
        else:
            action = "PREPARE_APPLICATION"
            confidence = 0.88
            reasons.append("Legitimate job opportunity detected; candidate matching recommended.")
    elif len(tasks) > 0 or len(commitments) > 0:
        action = "REMIND"
        confidence = 0.92
        reasons.append(f"Contains {len(tasks)} actionable task(s) and {len(commitments)} commitment(s).")
    elif waste_score >= 80:
        action = "DELETE"
        confidence = 0.91
        reasons.append(f"High storage waste score ({waste_score}/100) and no unresolved tasks.")
    elif waste_score >= 50 or category in ["Promotion", "Newsletter"]:
        action = "ARCHIVE"
        confidence = 0.89
        reasons.append(f"Promotional or aging content ({waste_score}/100 waste score). Safe to archive.")
    else:
        action = "KEEP"
        confidence = 0.85
        reasons.append("Important communication with low storage footprint.")

    recommendation = {
        "action": action,
        "confidence": confidence,
        "reasons": reasons,
        "waste_score": waste_score
    }
    return {"recommendation": recommendation}


def safety_policy_node(state: AgentState) -> Dict[str, Any]:
    """Node 7: Apply untrusted input policy and determine approval gating."""
    recommendation = state.get("recommendation", {})
    action = recommendation.get("action", "KEEP")
    confidence = recommendation.get("confidence", 0.85)
    analysis = state.get("email_analysis", {})
    sec_risk = analysis.get("security_risk_level", "LOW")
    raw = analysis.get("raw_analysis", {})
    injection_flag = raw.get("injection_flag", False)

    policy_eval = safety_policy_guard.evaluate_action_policy(
        recommended_action=action,
        confidence=confidence,
        security_risk_level=sec_risk,
        prompt_injection_flag=injection_flag
    )

    approval_status = "PENDING" if policy_eval["approval_required"] else "APPROVED"

    return {
        "policy_result": policy_eval,
        "approval_status": approval_status
    }


def build_email_intelligence_graph():
    """Build and compile the LangGraph workflow."""
    workflow = StateGraph(AgentState)

    workflow.add_node("understand_email", understand_email_node)
    workflow.add_node("retrieve_context", retrieve_context_node)
    workflow.add_node("storage_analysis", storage_analysis_node)
    workflow.add_node("task_commitment", task_commitment_node)
    workflow.add_node("job_analysis", job_analysis_node)
    workflow.add_node("decision_agent", decision_agent_node)
    workflow.add_node("safety_policy", safety_policy_node)

    workflow.add_edge(START, "understand_email")
    workflow.add_edge("understand_email", "retrieve_context")
    workflow.add_edge("retrieve_context", "storage_analysis")
    workflow.add_edge("storage_analysis", "task_commitment")
    workflow.add_edge("task_commitment", "job_analysis")
    workflow.add_edge("job_analysis", "decision_agent")
    workflow.add_edge("decision_agent", "safety_policy")
    workflow.add_edge("safety_policy", END)

    return workflow.compile()


email_intelligence_graph = build_email_intelligence_graph()
