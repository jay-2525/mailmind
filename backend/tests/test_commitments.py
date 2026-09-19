from datetime import datetime, timedelta, timezone
from app.services.commitment_fsm import CommitmentFSM


def test_commitment_fsm_valid_transitions():
    assert CommitmentFSM.can_transition("OPEN", "PROMISED") is True
    assert CommitmentFSM.can_transition("OPEN", "COMPLETED") is True
    assert CommitmentFSM.can_transition("PROMISED", "OVERDUE") is True
    assert CommitmentFSM.can_transition("COMPLETED", "OPEN") is False  # Terminal


def test_commitment_state_overdue_evaluation():
    past_deadline = datetime.now(timezone.utc) - timedelta(days=2)
    state = CommitmentFSM.evaluate_state(
        current_state="PROMISED",
        deadline=past_deadline,
        has_fulfillment_evidence=False
    )
    assert state == "OVERDUE"


def test_commitment_fulfillment_detection():
    statement = "I will send the project report tomorrow"
    reply_text = "Hi Alex, please find attached the project report as requested."
    is_fulfilled = CommitmentFSM.detect_fulfillment(statement, reply_text)
    assert is_fulfilled is True
