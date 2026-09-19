import pytest
from app.services.skill_gap import detect_skill_gaps
from app.services.scoring import (
    calculate_compatibility_score,
    calculate_experience_score,
    calculate_education_score,
    CompatibilityScoreResult
)
from app.schemas.resume import CandidateProfile, EducationItem, ExperienceItem


def test_perfect_candidate_score():
    """Verify that a candidate fulfilling all required and preferred skills, education, and experience achieves 100%"""
    profile = CandidateProfile(
        candidate_name="Alice Wonder",
        skills=["Python", "FastAPI", "React", "Docker"],
        education=[EducationItem(degree="BSc in Computer Science", institution="University", year="2022")],
        experience=[ExperienceItem(title="Developer", company="Corp", duration="3 years")]
    )
    gap_result = detect_skill_gaps(
        candidate_skills=profile.skills,
        required_job_skills=["Python", "FastAPI", "React"],
        preferred_job_skills=["Docker"]
    )

    result = calculate_compatibility_score(
        gap_result=gap_result,
        candidate_profile=profile,
        jd_experience_reqs=["2+ years in software engineering"],
        jd_education_reqs=["Bachelor's degree in CS or IT"]
    )

    assert isinstance(result, CompatibilityScoreResult)
    assert result.compatibility_score == 100.0
    assert result.score_breakdown.required_skills_match == 100.0
    assert result.score_breakdown.education_match == 100.0
    assert result.indicator_label == "AI-Assisted Job Compatibility Score"
    assert "analytical indicator" in result.fairness_disclaimer.lower()


def test_zero_match_candidate_score():
    """Verify scoring behavior when candidate has zero required skills"""
    profile = CandidateProfile(
        skills=["Photoshop", "Illustrator"],
        education=[],
        experience=[]
    )
    gap_result = detect_skill_gaps(
        candidate_skills=profile.skills,
        required_job_skills=["Python", "FastAPI", "SQL", "Docker"]
    )

    result = calculate_compatibility_score(
        gap_result=gap_result,
        candidate_profile=profile,
        jd_experience_reqs=["3+ years"],
        jd_education_reqs=["BTech Computer Science"]
    )

    # 60% * 0 + 15% * 100(no pref) + 15% * 40(fresher) + 10% * 50(no edu)
    # = 0 + 15 + 6 + 5 = 26.0
    assert result.score_breakdown.required_skills_match == 0.0
    assert result.compatibility_score < 40.0


def test_transferable_skill_partial_credit():
    """Verify that a candidate with transferable skills receives partial credit (50%)"""
    profile = CandidateProfile(
        skills=["Python", "Flask", "SQL"],  # Flask is related to FastAPI
        education=[EducationItem(degree="BSc IT")],
        experience=[ExperienceItem(duration="2 years")]
    )
    gap_result = detect_skill_gaps(
        candidate_skills=profile.skills,
        required_job_skills=["Python", "FastAPI"]  # 1 matched, 1 transferable
    )
    # Effective match = 1 + (0.5 * 1) = 1.5 / 2 = 0.75 (75%)
    assert gap_result.match_ratio == 0.75

    result = calculate_compatibility_score(
        gap_result=gap_result,
        candidate_profile=profile
    )
    assert result.score_breakdown.required_skills_match == 75.0


def test_custom_configurable_weights():
    """Verify application supports changing weights without hardcoded values"""
    profile = CandidateProfile(
        skills=["Python"],
        education=[],
        experience=[]
    )
    gap_result = detect_skill_gaps(
        candidate_skills=profile.skills,
        required_job_skills=["Python"]
    )
    # Custom weights: 90% skills, 10% education
    custom = {
        "required_skills": 0.90,
        "preferred_skills": 0.0,
        "experience": 0.0,
        "education": 0.10
    }
    result = calculate_compatibility_score(
        gap_result=gap_result,
        candidate_profile=profile,
        jd_education_reqs=["Bachelor degree in Engineering"],
        custom_weights=custom
    )
    # 0.9 * 100 + 0.1 * 50 = 90 + 5 = 95.0
    assert result.compatibility_score == 95.0
    assert result.applied_weights["required_skills"] == 0.90
