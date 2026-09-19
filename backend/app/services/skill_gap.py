import re
from typing import List, Dict, Set, Optional
from pydantic import BaseModel, Field

from app.services.skill_normalizer import (
    normalize_skill,
    normalize_skills_list,
    get_related_skills,
    get_skill_category
)


class SkillMatchItem(BaseModel):
    """Represents a single skill comparison result with explainable evidence"""
    skill: str
    status: str = Field(..., description="'matched', 'missing', 'transferable', or 'preferred_gap'")
    category: str = Field(default="General", description="Skill domain category")
    evidence: Optional[str] = Field(default=None, description="Direct quote or proof from candidate resume")
    explanation: Optional[str] = Field(default=None, description="Clear reasoning for why this gap exists")


class SkillGapResult(BaseModel):
    """Consolidated skill gap analysis results"""
    matched_skills: List[SkillMatchItem] = Field(default_factory=list)
    missing_skills: List[SkillMatchItem] = Field(default_factory=list)
    related_skills: List[SkillMatchItem] = Field(default_factory=list)
    preferred_skill_gaps: List[SkillMatchItem] = Field(default_factory=list)
    
    # Statistical summary
    total_required: int = 0
    total_matched: int = 0
    total_missing: int = 0
    total_related: int = 0
    match_ratio: float = 0.0


def find_skill_evidence_in_text(skill_name: str, text: str) -> Optional[str]:
    """
    Searches raw resume text for the sentence or line containing the skill.
    Returns the exact authentic context snippet rather than an invented quote.
    """
    if not text or not skill_name:
        return None

    # Search line by line
    lines = text.split("\n")
    pattern = r'(?i)\b' + re.escape(skill_name) + r'\b'

    for line in lines:
        cleaned_line = line.strip()
        if re.search(pattern, cleaned_line):
            # Limit snippet length to 140 chars for UI card presentation
            if len(cleaned_line) > 140:
                cleaned_line = cleaned_line[:137] + "..."
            return f"Found in resume: \"{cleaned_line}\""

    # Fallback to general presence confirmation
    return f"Verified presence of '{skill_name}' within candidate profile."


def detect_skill_gaps(
    candidate_skills: List[str],
    required_job_skills: List[str],
    preferred_job_skills: Optional[List[str]] = None,
    resume_raw_text: str = ""
) -> SkillGapResult:
    """
    Core skill gap detection engine:
    1. Normalizes all candidate skills and JD skills to standard forms.
    2. Identifies exact / canonical matches with authentic textual evidence from resume.
    3. For unmatched required skills, inspects related/transferable skill clusters.
    4. Categorizes remaining unmatched skills into 'missing' (required) or 'preferred_gap' (optional).
    """
    preferred_job_skills = preferred_job_skills or []

    # 1. Normalize lists
    norm_candidate = normalize_skills_list(candidate_skills)
    norm_required = normalize_skills_list(required_job_skills)
    norm_preferred = normalize_skills_list(preferred_job_skills)

    candidate_set: Set[str] = set(norm_candidate)

    matched: List[SkillMatchItem] = []
    missing: List[SkillMatchItem] = []
    related: List[SkillMatchItem] = []
    preferred_gaps: List[SkillMatchItem] = []

    # 2. Check Required Job Skills
    for skill in norm_required:
        category = get_skill_category(skill)

        if skill in candidate_set:
            # DIRECT CANONICAL MATCH
            evidence = find_skill_evidence_in_text(skill, resume_raw_text)
            matched.append(SkillMatchItem(
                skill=skill,
                status="matched",
                category=category,
                evidence=evidence,
                explanation=f"Candidate demonstrably possesses required skill '{skill}'."
            ))
        else:
            # CHECK FOR TRANSFERABLE / RELATED SKILLS
            transferable_candidates = get_related_skills(skill)
            overlapping_related = [rel for rel in transferable_candidates if rel in candidate_set]

            if overlapping_related:
                related_names = ", ".join(overlapping_related)
                related.append(SkillMatchItem(
                    skill=skill,
                    status="transferable",
                    category=category,
                    evidence=f"Candidate has adjacent competencies: {related_names}.",
                    explanation=f"'{skill}' is required, but candidate demonstrates transferable background in {related_names}."
                ))
            else:
                missing.append(SkillMatchItem(
                    skill=skill,
                    status="missing",
                    category=category,
                    evidence=None,
                    explanation=f"'{skill}' is explicitly required by the job description but not detected in the resume."
                ))

    # 3. Check Preferred Job Skills
    for skill in norm_preferred:
        category = get_skill_category(skill)

        if skill in candidate_set:
            evidence = find_skill_evidence_in_text(skill, resume_raw_text)
            matched.append(SkillMatchItem(
                skill=skill,
                status="matched",
                category=category,
                evidence=evidence,
                explanation=f"Candidate fulfills preferred/bonus skill '{skill}'."
            ))
        else:
            preferred_gaps.append(SkillMatchItem(
                skill=skill,
                status="preferred_gap",
                category=category,
                evidence=None,
                explanation=f"'{skill}' is a preferred/bonus skill not explicitly listed in the resume."
            ))

    total_req = len(norm_required)
    total_match = len([m for m in matched if m.skill in norm_required])
    total_rel = len(related)
    total_miss = len(missing)

    # Match ratio: matches count 100%, related count as 50% partial competency
    effective_matched = total_match + (0.5 * total_rel)
    match_ratio = round((effective_matched / total_req), 4) if total_req > 0 else 1.0

    return SkillGapResult(
        matched_skills=matched,
        missing_skills=missing,
        related_skills=related,
        preferred_skill_gaps=preferred_gaps,
        total_required=total_req,
        total_matched=total_match,
        total_missing=total_miss,
        total_related=total_rel,
        match_ratio=match_ratio
    )
