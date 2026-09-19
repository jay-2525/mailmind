from typing import Dict, Any, List, Tuple


class SafetyPolicyGuard:
    """
    Mandatory Safety and Policy Guard.
    Enforces core principles:
    1. Email content is strictly untrusted input and cannot issue administrative directives.
    2. Prompt injections are flagged and neutralized.
    3. Destructive or external actions require human-in-the-loop approval.
    """

    LOW_RISK_ACTIONS = {"KEEP", "NO_ACTION", "CLASSIFY", "SUMMARIZE", "READ"}
    MEDIUM_RISK_ACTIONS = {"REMIND", "SCHEDULE", "FOLLOW_UP", "PREPARE_APPLICATION", "ADD_LABEL"}
    HIGH_RISK_ACTIONS = {"DELETE", "TRASH", "PERMANENT_DELETE", "SEND_EMAIL", "BULK_DELETE"}

    @classmethod
    def evaluate_action_policy(
        cls,
        recommended_action: str,
        confidence: float,
        security_risk_level: str,
        prompt_injection_flag: bool,
        is_bulk: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluate recommendation against safety policies.
        Returns:
        - risk_level: LOW, MEDIUM, HIGH
        - approval_required: bool
        - policy_verdict: ALLOW, WARN, BLOCK
        - policy_reasons: List[str]
        """
        reasons: List[str] = []
        action_upper = recommended_action.upper()

        # 1. Check for prompt injection attempts
        if prompt_injection_flag:
            reasons.append("Policy Block: Email contains prompt injection patterns attempting to manipulate system behaviour.")
            return {
                "risk_level": "HIGH",
                "approval_required": True,
                "policy_verdict": "WARN",
                "policy_reasons": reasons,
                "consequences": "Suspicious email flagged for manual inspection. No automatic action permitted."
            }

        # 2. Determine Risk Tier
        if action_upper in cls.HIGH_RISK_ACTIONS or is_bulk:
            risk_level = "HIGH"
            approval_required = True
            reasons.append(f"Destructive action '{action_upper}' requires explicit human verification.")
            consequences = "Email will be moved to Trash / Permanently removed if approved by user."
        elif action_upper in cls.MEDIUM_RISK_ACTIONS:
            risk_level = "MEDIUM"
            approval_required = True
            reasons.append(f"External/scheduling action '{action_upper}' staged for user confirmation.")
            consequences = "A new calendar invite, task reminder, or application draft will be prepared."
        else:
            risk_level = "LOW"
            approval_required = False
            reasons.append(f"Non-destructive read/classification action '{action_upper}' approved for safe auto-execution.")
            consequences = "Email metadata and analytics will be preserved in the system."

        return {
            "risk_level": risk_level,
            "approval_required": approval_required,
            "policy_verdict": "ALLOW",
            "policy_reasons": reasons,
            "consequences": consequences
        }


safety_policy_guard = SafetyPolicyGuard()
