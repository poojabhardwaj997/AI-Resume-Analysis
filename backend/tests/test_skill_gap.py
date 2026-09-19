import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.skill_gap import detect_skill_gaps, find_skill_evidence_in_text


def test_user_prompt_exact_example():
    """
    Test exact example from user prompt requirements:
    Candidate: Python, SQL, HTML, CSS
    Job: Python, SQL, Git, Machine Learning
    Result:
    Matched: Python, SQL
    Missing: Git, Machine Learning
    Related: None
    """
    candidate = ["Python", "SQL", "HTML", "CSS"]
    required = ["Python", "SQL", "Git", "Machine Learning"]

    result = detect_skill_gaps(
        candidate_skills=candidate,
        required_job_skills=required
    )

    matched_names = [m.skill for m in result.matched_skills]
    missing_names = [m.skill for m in result.missing_skills]
    related_names = [m.skill for m in result.related_skills]

    assert "Python" in matched_names
    assert "SQL" in matched_names
    assert "Git" in missing_names
    assert "Machine Learning" in missing_names
    assert len(related_names) == 0
    assert result.total_matched == 2
    assert result.total_missing == 2


def test_transferable_skill_detection():
    """Verify that when candidate has Flask or Django, required FastAPI is detected as transferable"""
    candidate = ["Python", "Django", "Flask", "SQL"]
    required = ["Python", "FastAPI", "SQL"]

    result = detect_skill_gaps(
        candidate_skills=candidate,
        required_job_skills=required
    )

    matched_names = [m.skill for m in result.matched_skills]
    transferable_names = [m.skill for m in result.related_skills]

    assert "Python" in matched_names
    assert "SQL" in matched_names
    assert "FastAPI" in transferable_names


def test_authentic_textual_evidence():
    """Verify that evidence finder quotes the exact line from candidate resume text"""
    resume_text = (
        "Jane Doe\n"
        "Proficient in Python programming and building asynchronous microservices with FastAPI.\n"
        "Extensive experience with PostgreSQL and Docker containers."
    )
    evidence_python = find_skill_evidence_in_text("Python", resume_text)
    assert "Python" in evidence_python
    assert "Found in resume" in evidence_python

    evidence_nonexistent = find_skill_evidence_in_text("Kubernetes", resume_text)
    assert "Kubernetes" in evidence_nonexistent


def test_preferred_skill_gaps():
    """Verify preferred skills are categorized as preferred_gap and don't count as missing required skills"""
    candidate = ["Python", "React"]
    required = ["Python", "React"]
    preferred = ["Docker", "Kubernetes"]

    result = detect_skill_gaps(
        candidate_skills=candidate,
        required_job_skills=required,
        preferred_job_skills=preferred
    )

    assert result.total_missing == 0
    assert len(result.preferred_skill_gaps) == 2
    pref_gap_names = [p.skill for p in result.preferred_skill_gaps]
    assert "Docker" in pref_gap_names
    assert "Kubernetes" in pref_gap_names


@pytest.mark.asyncio
async def test_skill_gap_api_endpoint():
    """Verify POST /api/skill-gap/analyze returns 200 OK with full gap result"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "candidate_skills": ["JS", "Python", "HTML"],
            "required_job_skills": ["JavaScript", "Python", "Docker"],
            "preferred_job_skills": ["AWS"],
            "resume_raw_text": "Experienced in Python and JavaScript frontend engineering."
        }
        response = await client.post("/api/skill-gap/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        res = data["data"]
        matched_skills = [m["skill"] for m in res["matched_skills"]]
        missing_skills = [m["skill"] for m in res["missing_skills"]]
        
        # JS normalized to JavaScript and matched!
        assert "JavaScript" in matched_skills
        assert "Python" in matched_skills
        assert "Docker" in missing_skills
