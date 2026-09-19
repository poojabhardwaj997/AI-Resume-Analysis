import pytest
from app.services.recommendation import RecommendationEngine, RecommendationItem
from app.services.skill_gap import SkillMatchItem


def test_tech_skill_recommendation():
    """Verify Docker missing skill produces complete actionable roadmap"""
    engine = RecommendationEngine()
    gaps = [
        SkillMatchItem(skill="Docker", status="missing", explanation="Docker is missing")
    ]
    recs = engine.generate_recommendations_for_gaps(
        missing_skills=gaps,
        job_title="Backend Developer",
        company_name="TechCorp"
    )

    assert len(recs) == 1
    rec = recs[0]
    assert isinstance(rec, RecommendationItem)
    assert rec.skill == "Docker"
    assert "container" in rec.why_it_matters.lower()
    assert "dockerfile" in rec.learning_objective.lower()
    assert len(rec.practical_exercise) > 10
    assert len(rec.suggested_project) > 10


def test_business_and_hr_recommendations():
    """Verify Power BI and Recruitment produce domain-specific roadmaps"""
    engine = RecommendationEngine()
    gaps = [
        SkillMatchItem(skill="Power BI", status="missing"),
        SkillMatchItem(skill="Recruitment & Talent Acquisition", status="missing")
    ]
    recs = engine.generate_recommendations_for_gaps(
        missing_skills=gaps,
        job_title="Business & HR Analyst"
    )

    assert len(recs) == 2
    pbi = next(r for r in recs if r.skill == "Power BI")
    assert "dax" in pbi.learning_objective.lower() or "power query" in pbi.learning_objective.lower()
    assert "dashboard" in pbi.suggested_project.lower()

    hr = next(r for r in recs if "Recruitment" in r.skill)
    assert "sourcing" in hr.learning_objective.lower()


def test_dynamic_fallback_for_custom_skill():
    """Verify uncataloged skills generate valid structural recommendations without failing"""
    engine = RecommendationEngine()
    gaps = [
        SkillMatchItem(skill="Solidity", status="missing")
    ]
    recs = engine.generate_recommendations_for_gaps(
        missing_skills=gaps,
        job_title="Blockchain Engineer",
        company_name="CryptoTech"
    )

    assert len(recs) == 1
    rec = recs[0]
    assert rec.skill == "Solidity"
    assert "Blockchain Engineer" in rec.why_it_matters
    assert "CryptoTech" in rec.why_it_matters
    assert len(rec.suggested_project) > 0
