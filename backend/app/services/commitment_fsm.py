from datetime import datetime, timezone
from typing import Optional, Dict, Any, List


class CommitmentFSM:
    """
    Finite State Machine for managing email commitments.
    Valid states: OPEN, PROMISED, COMPLETED, OVERDUE, CANCELLED
    """

    VALID_TRANSITIONS = {
        "OPEN": ["PROMISED", "COMPLETED", "OVERDUE", "CANCELLED"],
        "PROMISED": ["COMPLETED", "OVERDUE", "CANCELLED"],
        "OVERDUE": ["COMPLETED", "CANCELLED"],
        "COMPLETED": [],  # Terminal unless manually reopened
        "CANCELLED": ["OPEN", "PROMISED"]
    }

    @classmethod
    def can_transition(cls, current_state: str, new_state: str) -> bool:
        allowed = cls.VALID_TRANSITIONS.get(current_state.upper(), [])
        return new_state.upper() in allowed

    @classmethod
    def evaluate_state(
        cls,
        current_state: str,
        deadline: Optional[datetime],
        has_fulfillment_evidence: bool,
        is_user_dismissed: bool = False
    ) -> str:
        """
        Evaluate and return updated commitment state based on temporal and evidence signals.
        """
        if is_user_dismissed:
            return "CANCELLED"

        if has_fulfillment_evidence:
            return "COMPLETED"

        if deadline is not None:
            now = datetime.now(timezone.utc)
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)
            if now > deadline and current_state.upper() in ["OPEN", "PROMISED"]:
                return "OVERDUE"

        return current_state.upper()

    @classmethod
    def detect_fulfillment(cls, commitment_statement: str, reply_text: str) -> bool:
        """
        Check if a reply email provides evidence of fulfilling the commitment statement.
        E.g., "attached the report", "sending the document", "here is the file you requested".
        """
        if not reply_text:
            return False

        reply_lower = reply_text.lower()
        fulfillment_keywords = [
            "attached", "attaching", "here is the", "here are the",
            "as promised", "completed the", "have submitted", "have sent",
            "please find attached", "shared the document"
        ]

        # Extract core nouns/verbs from statement
        statement_words = [w.lower() for w in commitment_statement.split() if len(w) > 3]
        keyword_present = any(kw in reply_lower for kw in fulfillment_keywords)
        topic_present = any(word in reply_lower for word in statement_words)

        return keyword_present and (topic_present or len(statement_words) == 0)


commitment_fsm = CommitmentFSM()
