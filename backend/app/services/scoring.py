import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.config import get_settings
from app.services.skill_gap import SkillGapResult
from app.schemas.resume import CandidateProfile, EducationItem, ExperienceItem


class ScoreBreakdown(BaseModel):
    """Detailed sub-scores for analytical transparency"""
    required_skills_match: float = Field(..., description="Score for mandatory job skills (0 - 100)")
    preferred_skills_match: float = Field(..., description="Score for bonus/preferred skills (0 - 100)")
    experience_match: float = Field(..., description="Score for experience fit (0 - 100)")
    education_match: float = Field(..., description="Score for academic/degree fit (0 - 100)")


class CompatibilityScoreResult(BaseModel):
    """Overall AI-assisted compatibility scoring report"""
    compatibility_score: float = Field(..., description="AI-Assisted Job Compatibility Score (0.00 to 100.00)")
    indicator_label: str = Field(default="AI-Assisted Job Compatibility Score")
    score_breakdown: ScoreBreakdown
    applied_weights: Dict[str, float]
    fairness_disclaimer: str = (
        "Notice: This score is an analytical indicator based on skill taxonomy matching and semantic criteria. "
        "It does NOT represent a guaranteed hiring decision, employment probability, or automatic screening rejection."
    )


def extract_years_from_text(text: str) -> float:
    """Extracts first numerical years representation from string e.g. '2+ years' -> 2.0"""
    if not text:
        return 0.0
    match = re.search(r'(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)', text, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return 0.0
    return 0.0


def calculate_experience_score(candidate_exp: List[ExperienceItem], jd_experience_reqs: List[str]) -> float:
    """
    Computes experience score comparing candidate's experience history with JD criteria.
    - If JD has no explicit experience criteria: 100.0 (open to all levels)
    - If candidate meets or exceeds required years: 100.0
    - If candidate has partial years: proportional ratio
    - If candidate has listed experience without exact duration: default baseline 75.0
    """
    if not jd_experience_reqs:
        return 100.0

    jd_required_years = 0.0
    for req in jd_experience_reqs:
        yrs = extract_years_from_text(req)
        if yrs > jd_required_years:
            jd_required_years = yrs

    # If JD is entry-level or 0 years required
    if jd_required_years == 0.0:
        return 100.0

    # Calculate candidate years
    total_candidate_years = 0.0
    for exp in candidate_exp:
        if exp.duration:
            yrs = extract_years_from_text(exp.duration)
            total_candidate_years += yrs if yrs > 0 else 1.0
        else:
            total_candidate_years += 1.0  # 1 year assumption per listed role

    if total_candidate_years >= jd_required_years:
        return 100.0
    elif total_candidate_years > 0:
        ratio = (total_candidate_years / jd_required_years) * 100.0
        return round(min(100.0, max(30.0, ratio)), 2)
    else:
        # Candidate has no explicit work experience (fresher / student)
        return 40.0


def calculate_education_score(candidate_edu: List[EducationItem], jd_education_reqs: List[str]) -> float:
    """
    Computes degree alignment score.
    - If candidate has a relevant degree (BSc, BTech, BBA, BCom, Master, etc.): 100.0
    - If candidate has general education: 80.0
    - If no education provided: 50.0
    """
    if not jd_education_reqs:
        return 100.0 if candidate_edu else 80.0

    if not candidate_edu:
        return 50.0

    degree_hierarchy = ["phd", "master", "mba", "msc", "mtech", "bachelor", "btech", "bsc", "bba", "bcom", "diploma"]
    candidate_degrees = " ".join([(e.degree or "").lower() for e in candidate_edu])

    # Check if candidate has degree mentioned
    has_degree = any(d in candidate_degrees for d in degree_hierarchy)
    if has_degree:
        return 100.0
    return 75.0


def calculate_compatibility_score(
    gap_result: SkillGapResult,
    candidate_profile: CandidateProfile,
    jd_experience_reqs: Optional[List[str]] = None,
    jd_education_reqs: Optional[List[str]] = None,
    custom_weights: Optional[Dict[str, float]] = None
) -> CompatibilityScoreResult:
    """
    Calculates transparent AI-assisted job compatibility score.
    Uses configurable weights:
    Score = (W_req * S_req) + (W_pref * S_pref) + (W_exp * S_exp) + (W_edu * S_edu)
    """
    settings = get_settings()

    # Load configurable weights
    w_req = custom_weights.get("required_skills", settings.WEIGHT_REQUIRED_SKILLS) if custom_weights else settings.WEIGHT_REQUIRED_SKILLS
    w_pref = custom_weights.get("preferred_skills", settings.WEIGHT_PREFERRED_SKILLS) if custom_weights else settings.WEIGHT_PREFERRED_SKILLS
    w_exp = custom_weights.get("experience", settings.WEIGHT_EXPERIENCE) if custom_weights else settings.WEIGHT_EXPERIENCE
    w_edu = custom_weights.get("education", settings.WEIGHT_EDUCATION) if custom_weights else settings.WEIGHT_EDUCATION

    # 1. Required Skills Match Score (Transferable skills count as 50% partial credit)
    req_match_score = gap_result.match_ratio * 100.0

    # 2. Preferred Skills Match Score
    total_pref = len(gap_result.preferred_skill_gaps) + len([m for m in gap_result.matched_skills if m.status == "matched" and m.skill not in [m.skill for m in gap_result.matched_skills if m.status == "matched"][:gap_result.total_matched]])
    matched_pref = len([m for m in gap_result.matched_skills if m.status == "matched" and "preferred" in (m.explanation or "").lower()])
    
    # If preferred skills are specified in the JD
    all_preferred_count = len(gap_result.preferred_skill_gaps) + matched_pref
    if all_preferred_count > 0:
        pref_match_score = round((matched_pref / all_preferred_count) * 100.0, 2)
    else:
        # If job does not list any preferred skills, full credit awarded
        pref_match_score = 100.0

    # 3. Experience Match Score
    exp_score = calculate_experience_score(
        candidate_exp=candidate_profile.experience,
        jd_experience_reqs=jd_experience_reqs or []
    )

    # 4. Education Match Score
    edu_score = calculate_education_score(
        candidate_edu=candidate_profile.education,
        jd_education_reqs=jd_education_reqs or []
    )

    # Calculate Weighted Overall Score
    raw_score = (w_req * req_match_score) + (w_pref * pref_match_score) + (w_exp * exp_score) + (w_edu * edu_score)
    final_score = round(min(100.0, max(0.0, raw_score)), 2)

    breakdown = ScoreBreakdown(
        required_skills_match=round(req_match_score, 2),
        preferred_skills_match=round(pref_match_score, 2),
        experience_match=round(exp_score, 2),
        education_match=round(edu_score, 2)
    )

    applied_weights = {
        "required_skills": w_req,
        "preferred_skills": w_pref,
        "experience": w_exp,
        "education": w_edu
    }

    return CompatibilityScoreResult(
        compatibility_score=final_score,
        score_breakdown=breakdown,
        applied_weights=applied_weights
    )
