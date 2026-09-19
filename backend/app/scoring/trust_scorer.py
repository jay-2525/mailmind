import re
from typing import Dict, Any, List


class JobTrustScorer:
    """
    Evaluates recruitment email legitimacy and calculates a Trust Score (0-100).
    Categorizes trust level into:
    - LOW_RISK_SIGNALS (High trust, authentic domains, standard recruitment flow)
    - REVIEW_REQUIRED (Ambiguous domains, free webmail, missing details)
    - HIGH_RISK_SIGNALS (Upfront fee requests, suspicious checks, phishing keywords)
    """

    FREE_DOMAINS = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", "mail.com", "proton.me"]

    HIGH_RISK_PATTERNS = [
        (r'\b(?:wire transfer|crypto|bitcoin|gift card|western union|moneygram)\b', "Requests payment via untraceable transfer method", 35),
        (r'\b(?:pay for equipment|equipment check|cashier check|reimbursement check)\b', "Advance-fee or fake equipment check scam pattern", 40),
        (r'\b(?:send bank details|ssn|social security number|passport copy upfront)\b', "Asks for sensitive personal/financial credentials before interview", 35),
        (r'\b(?:urgent hire|immediate start without interview|no interview needed)\b', "Suspicious immediate hiring claim without evaluation", 25),
        (r'\b(?:registration fee|application fee|training fee|processing fee)\b', "Demands upfront payment for job application or training", 40),
        (r'\b(?:telegram|whatsapp)\s+(?:only|interview|chat)\b', "Directs critical interview exclusively to unverified messaging platform", 20),
    ]

    def evaluate_job_trust(
        self,
        sender_email: str,
        company_name: str,
        job_description: str,
        application_url: str = ""
    ) -> Dict[str, Any]:
        reasons: List[str] = []
        risk_points = 0  # 0 means safe, 100 means extreme danger

        sender_lower = sender_email.lower()
        sender_domain = sender_lower.split("@")[-1] if "@" in sender_lower else ""
        desc_lower = job_description.lower()

        # 1. High risk pattern scans
        for pattern, msg, penalty in self.HIGH_RISK_PATTERNS:
            if re.search(pattern, desc_lower, re.IGNORECASE):
                reasons.append(f"High-Risk Signal: {msg}")
                risk_points += penalty

        # 2. Domain consistency check
        if sender_domain in self.FREE_DOMAINS:
            reasons.append(f"Recruiter contacted from free webmail provider (@{sender_domain}) rather than official corporate domain")
            risk_points += 20
        elif company_name:
            # Clean company name
            clean_company = re.sub(r'[^a-zA-Z0-9]', '', company_name.lower())
            if clean_company and clean_company not in sender_domain:
                reasons.append(f"Sender domain (@{sender_domain}) does not clearly match specified company '{company_name}'")
                risk_points += 15
            else:
                reasons.append(f"Sender domain (@{sender_domain}) aligns with claimed company '{company_name}'")

        # 3. Application URL destination check
        if application_url:
            app_url_lower = application_url.lower()
            if any(shortener in app_url_lower for shortener in ["bit.ly", "tinyurl.com", "rb.gy", "t.co", "goo.gl"]):
                reasons.append("Application URL uses a shortened link that masks final destination")
                risk_points += 15
            elif "http://" in app_url_lower:
                reasons.append("Application URL is unencrypted (HTTP instead of HTTPS)")
                risk_points += 10
        else:
            reasons.append("No official application or portal link provided in communication")
            risk_points += 5

        # Calculate trust score (100 - risk_points)
        trust_score = max(0.0, min(100.0, round(100.0 - risk_points, 1)))

        if trust_score >= 80:
            trust_level = "LOW_RISK_SIGNALS"
            reasons.insert(0, "No critical anomalies detected; standard recruitment signals present")
        elif trust_score >= 50:
            trust_level = "REVIEW_REQUIRED"
            reasons.insert(0, "Exercise caution: some unverified recruiter details or domain mismatch observed")
        else:
            trust_level = "HIGH_RISK_SIGNALS"
            reasons.insert(0, "Warning: Significant scam or phishing indicators identified in message content")

        return {
            "trust_score": trust_score,
            "trust_level": trust_level,
            "reasons": reasons,
            "risk_points": risk_points
        }


job_trust_scorer = JobTrustScorer()
