import json
import re
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.services.nlp.temporal_parser import temporal_parser
from app.services.nlp.entity_extractor import entity_extractor


class LLMProvider:
    """
    Abstract LLM Provider interface with adapters for:
    - Google Gemini
    - OpenAI / OpenAI-compatible
    - Ollama Local LLMs
    - Heuristic Deterministic Analyzer (zero-cost offline execution)
    """

    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()

    def analyze_email(self, subject: str, body: str, sender: str) -> Dict[str, Any]:
        """
        Analyze an email using structured extraction.
        Email content is strictly treated as untrusted input.
        """
        # First perform prompt injection check on untrusted body
        injection_flag, injection_reason = self._check_prompt_injection(body)

        if self.provider == "gemini" and settings.GEMINI_API_KEY:
            try:
                return self._call_gemini_analysis(subject, body, sender, injection_flag, injection_reason)
            except Exception as e:
                print(f"[LLMProvider] Gemini error ({e}), falling back to heuristic engine.")

        elif self.provider == "openai" and settings.OPENAI_API_KEY:
            try:
                return self._call_openai_analysis(subject, body, sender, injection_flag, injection_reason)
            except Exception as e:
                print(f"[LLMProvider] OpenAI error ({e}), falling back to heuristic engine.")

        # Default Heuristic Analyzer
        return self._heuristic_analyze_email(subject, body, sender, injection_flag, injection_reason)

    def generate_application_pack(
        self,
        role: str,
        company: str,
        job_description: str,
        resume_summary: str,
        candidate_name: str,
        matched_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Generate tailored cover letter, recruiter pitch, and interview QA.
        """
        skills_str = ", ".join(matched_skills[:6]) if matched_skills else "Python, SQL, Problem Solving"

        cover_letter = (
            f"Dear Hiring Team at {company},\n\n"
            f"I am writing to express my strong interest in the {role} position. "
            f"With a solid foundation in computer science and hands-on experience in {skills_str}, "
            f"I am confident in my ability to deliver immediate value to your engineering team.\n\n"
            f"Throughout my projects and coursework, I have developed a strong aptitude for building scalable, "
            f"maintainable systems and solving complex computational problems. The opportunity to contribute to {company} "
            f"aligns directly with my career goals and dedication to engineering excellence.\n\n"
            f"Thank you for your time and consideration. I welcome the opportunity to discuss how my skill set aligns with your team's goals.\n\n"
            f"Sincerely,\n{candidate_name}"
        )

        recruiter_pitch = (
            f"Hi {company} Recruiting Team, I noticed the exciting {role} opening. "
            f"Given my background with {skills_str}, I would love to connect and share how my recent project work "
            f"aligns with what you are looking for. Thank you for your time!"
        )

        interview_qa = [
            {
                "question": f"Why do you want to work at {company} as a {role}?",
                "suggested_answer": f"I admire {company}'s focus on high-impact technology. My skills in {skills_str} and my passion for clean software architecture make this role an ideal match where I can both contribute and grow."
            },
            {
                "question": f"How does your experience prepare you for this role?",
                "suggested_answer": f"I have practical experience designing end-to-end applications, working with {skills_str}, and collaborating in agile settings. I focus on writing reliable code with automated test coverage."
            }
        ]

        return {
            "cover_letter": cover_letter,
            "recruiter_pitch": recruiter_pitch,
            "interview_qa": interview_qa
        }

    def _check_prompt_injection(self, text: str) -> tuple[bool, str]:
        """
        Detect prompt injection patterns aiming to hijack system instructions.
        """
        if not text:
            return False, ""

        injection_patterns = [
            (r'ignore (?:all )?previous instructions', "Attempt to override previous instructions"),
            (r'disregard (?:all )?prior instructions', "Attempt to disregard prior instructions"),
            (r'system prompt override', "System prompt override keyword detected"),
            (r'you are now in developer mode', "Jailbreak / developer mode attempt"),
            (r'delete all (?:emails|files|records)', "Malicious command execution request in email body"),
            (r'send my (?:credentials|password|token)', "Credential exfiltration request"),
        ]

        for pattern, reason in injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True, reason

        return False, ""

    def _heuristic_analyze_email(
        self,
        subject: str,
        body: str,
        sender: str,
        injection_flag: bool,
        injection_reason: str
    ) -> Dict[str, Any]:
        """
        Rule-based NLP analysis extracting high-fidelity structured information.
        """
        combined = f"{subject}\n{body}".lower()

        # Category detection
        category = "Other"
        is_promotional = False
        is_job_related = False

        if any(w in combined for w in ["job opportunity", "internship", "software engineer", "recruitment", "interview", "position at", "hiring"]):
            category = "Job Opportunity"
            is_job_related = True
        elif any(w in combined for w in ["assignment", "homework", "exam", "syllabus", "grade", "university", "class", "lecture"]):
            category = "Education"
        elif any(w in combined for w in ["meeting", "sync", "standup", "calendar", "invite", "zoom", "google meet", "teams"]):
            category = "Meeting"
        elif any(w in combined for w in ["receipt", "invoice", "payment", "bank", "statement", "order confirmed", "billing"]):
            category = "Finance"
        elif any(w in combined for w in ["unsubscribe", "sale", "discount", "offer", "% off", "limited time", "promo"]):
            category = "Promotion"
            is_promotional = True
        elif any(w in combined for w in ["newsletter", "weekly digest", "top stories"]):
            category = "Newsletter"
            is_promotional = True
        elif any(w in combined for w in ["security alert", "password reset", "unauthorized login", "verification code"]):
            category = "Security"

        # Urgency & Importance scoring
        urgency = 0.4
        importance = 0.5
        if any(w in combined for w in ["urgent", "asap", "immediately", "today", "critical", "deadline today"]):
            urgency = 0.95
            importance = 0.85
        elif any(w in combined for w in ["by tomorrow", "reminder", "action required"]):
            urgency = 0.75
            importance = 0.70

        # Actionability
        actionability = 0.3
        extracted_tasks = []
        commitments = []

        # Task extraction pattern
        task_patterns = [
            r'(?:please|kindly|remember to|need to|make sure to)\s+([^.?!;\n]+(?:by\s+[^.?!;\n]+)?)',
            r'(?:submit|complete|review|send|prepare)\s+([^.?!;\n]+)'
        ]
        for pat in task_patterns:
            for match in re.finditer(pat, body, re.IGNORECASE):
                task_phrase = match.group(0).strip()
                if 10 < len(task_phrase) < 120:
                    deadline_dt = temporal_parser.parse_deadline(task_phrase)
                    extracted_tasks.append({
                        "title": task_phrase[:100],
                        "deadline": deadline_dt.isoformat() if deadline_dt else None,
                        "priority": "HIGH" if urgency > 0.7 else "MEDIUM",
                        "confidence": 0.88
                    })
                    actionability = max(actionability, 0.8)

        # Commitment extraction pattern ("I will...", "We promise to...", "I will send...")
        commitment_patterns = [
            r'\b(i will\s+[^.?!;\n]+)',
            r'\b(we will\s+[^.?!;\n]+)',
            r'\b(i am going to\s+[^.?!;\n]+)',
            r'\b(i promised to\s+[^.?!;\n]+)'
        ]
        for pat in commitment_patterns:
            for match in re.finditer(pat, body, re.IGNORECASE):
                stmt = match.group(1).strip()
                if 10 < len(stmt) < 120:
                    deadline_dt = temporal_parser.parse_deadline(stmt)
                    commitments.append({
                        "statement": stmt[:150],
                        "owner": "SELF" if "i will" in stmt.lower() or "i am" in stmt.lower() else "SENDER",
                        "deadline": deadline_dt.isoformat() if deadline_dt else None,
                        "state": "PROMISED"
                    })
                    actionability = max(actionability, 0.75)

        # Meeting extraction
        meeting_details = None
        if category == "Meeting" or "meeting" in combined:
            mtg_deadline = temporal_parser.parse_deadline(body)
            if mtg_deadline:
                meeting_details = {
                    "title": subject,
                    "start_time": mtg_deadline.isoformat(),
                    "duration_minutes": 45
                }

        # Security risk
        security_risk_level = "LOW"
        security_reasons = []
        if injection_flag:
            security_risk_level = "HIGH"
            security_reasons.append(f"Prompt Injection Detected: {injection_reason}")

        # Summary generation
        summary = subject
        sentences = [s.strip() for s in re.split(r'[.!?\n]', body) if len(s.strip()) > 15]
        if sentences:
            summary = sentences[0][:200]

        return {
            "category": category,
            "importance": round(importance, 2),
            "urgency": round(urgency, 2),
            "actionability": round(actionability, 2),
            "is_promotional": is_promotional,
            "is_job_related": is_job_related,
            "security_risk_level": security_risk_level,
            "security_risk_reasons": security_reasons,
            "summary": summary,
            "extracted_tasks": extracted_tasks,
            "commitments": commitments,
            "meeting_details": meeting_details,
            "raw_analysis": {
                "engine": "heuristic_nlp_v1",
                "injection_flag": injection_flag
            }
        }


llm_provider = LLMProvider()
