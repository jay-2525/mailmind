from typing import List, Dict, Any, Set
from app.services.embedding import embedding_service
from app.core.config import settings


class JobMatcher:
    """
    Computes an exact, mathematical Job Match Score (0-100) comparing
    extracted job requirements against the candidate's parsed resume.
    """

    EDUCATION_RANKS = {
        "phd": 5, "doctorate": 5,
        "master": 4, "masters": 4, "m.tech": 4, "ms": 4, "mba": 4,
        "bachelor": 3, "bachelors": 3, "b.tech": 3, "bs": 3, "be": 3,
        "associate": 2, "diploma": 2,
        "high school": 1
    }

    def __init__(
        self,
        weight_req: float = settings.WEIGHT_REQUIRED_SKILLS,
        weight_pref: float = settings.WEIGHT_PREFERRED_SKILLS,
        weight_sem: float = settings.WEIGHT_SEMANTIC_SIMILARITY,
        weight_exp: float = settings.WEIGHT_EXPERIENCE,
        weight_edu: float = settings.WEIGHT_EDUCATION
    ):
        self.w_req = weight_req
        self.w_pref = weight_pref
        self.w_sem = weight_sem
        self.w_exp = weight_exp
        self.w_edu = weight_edu

    def match_job(
        self,
        job_required_skills: List[str],
        job_preferred_skills: List[str],
        candidate_skills: List[str],
        job_experience_years: float,
        candidate_experience_years: float,
        job_education: str,
        candidate_education: str,
        job_embedding: List[float],
        resume_embedding: List[float]
    ) -> Dict[str, Any]:
        cand_skill_set: Set[str] = {s.strip().lower() for s in candidate_skills if s}

        # 1. Required skills match
        req_norm = [s.strip().lower() for s in job_required_skills if s]
        matched_req = [s for s in req_norm if s in cand_skill_set]
        missing_req = [s for s in req_norm if s not in cand_skill_set]
        req_pct = (len(matched_req) / len(req_norm)) * 100.0 if req_norm else 100.0

        # 2. Preferred skills match
        pref_norm = [s.strip().lower() for s in job_preferred_skills if s]
        matched_pref = [s for s in pref_norm if s in cand_skill_set]
        missing_pref = [s for s in pref_norm if s not in cand_skill_set]
        pref_pct = (len(matched_pref) / len(pref_norm)) * 100.0 if pref_norm else 100.0

        # All matched and missing
        all_matched = sorted(list(set(matched_req + matched_pref)))
        all_missing = sorted(list(set(missing_req + missing_pref)))

        # 3. Experience alignment
        if job_experience_years <= 0.0:
            exp_pct = 100.0
        else:
            exp_ratio = candidate_experience_years / job_experience_years
            exp_pct = min(100.0, exp_ratio * 100.0)

        # 4. Education alignment
        job_edu_rank = self._get_edu_rank(job_education)
        cand_edu_rank = self._get_edu_rank(candidate_education)
        if job_edu_rank == 0:
            edu_pct = 100.0
        elif cand_edu_rank >= job_edu_rank:
            edu_pct = 100.0
        else:
            edu_pct = max(50.0, (cand_edu_rank / job_edu_rank) * 100.0)

        # 5. Semantic similarity
        sem_sim = 0.8  # default baseline
        if job_embedding and resume_embedding:
            sem_sim = embedding_service.cosine_similarity(job_embedding, resume_embedding)
        sem_pct = round(sem_sim * 100.0, 1)

        # Weighted calculation
        total_score = (
            (req_pct * self.w_req) +
            (pref_pct * self.w_pref) +
            (sem_pct * self.w_sem) +
            (exp_pct * self.w_exp) +
            (edu_pct * self.w_edu)
        )
        total_score = max(0.0, min(100.0, round(total_score, 1)))

        return {
            "match_score": total_score,
            "breakdown": {
                "required_skill_match_pct": round(req_pct, 1),
                "preferred_skill_match_pct": round(pref_pct, 1),
                "semantic_similarity_pct": round(sem_pct, 1),
                "experience_match_pct": round(exp_pct, 1),
                "education_match_pct": round(edu_pct, 1),
            },
            "matched_skills": all_matched,
            "missing_skills": all_missing,
        }

    def _get_edu_rank(self, edu_str: str) -> int:
        if not edu_str:
            return 0
        edu_lower = edu_str.lower()
        for key, rank in self.EDUCATION_RANKS.items():
            if key in edu_lower:
                return rank
        return 2  # default college level


job_matcher = JobMatcher()
