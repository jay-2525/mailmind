from app.scoring.job_matcher import JobMatcher


def test_job_matcher_high_alignment():
    matcher = JobMatcher()
    result = matcher.match_job(
        job_required_skills=["Java", "Python", "SQL", "Git"],
        job_preferred_skills=["Docker", "Kubernetes"],
        candidate_skills=["Java", "Python", "SQL", "Git", "React", "Docker"],
        job_experience_years=1.0,
        candidate_experience_years=1.5,
        job_education="Bachelor of Technology in CS",
        candidate_education="Bachelor of Technology in CS",
        job_embedding=[0.5] * 384,
        resume_embedding=[0.5] * 384
    )

    assert result["match_score"] >= 85.0
    assert result["breakdown"]["required_skill_match_pct"] == 100.0
    assert result["breakdown"]["preferred_skill_match_pct"] == 50.0  # has Docker, missing Kubernetes
    assert "docker" in result["matched_skills"]
    assert "kubernetes" in result["missing_skills"]


def test_job_matcher_low_alignment():
    matcher = JobMatcher()
    result = matcher.match_job(
        job_required_skills=["Rust", "C++", "Assembly"],
        job_preferred_skills=["Embedded", "RTOS"],
        candidate_skills=["Python", "HTML", "CSS"],
        job_experience_years=5.0,
        candidate_experience_years=0.5,
        job_education="PhD in Computer Engineering",
        candidate_education="High School",
        job_embedding=[0.1] * 384,
        resume_embedding=[0.9] * 384
    )

    assert result["match_score"] < 40.0
    assert result["breakdown"]["required_skill_match_pct"] == 0.0
    assert len(result["missing_skills"]) >= 3
