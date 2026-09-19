from typing import List, Optional
from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.schemas.common import APIResponse
from app.services.skill_gap import detect_skill_gaps, SkillGapResult

router = APIRouter(prefix="/api/skill-gap", tags=["Skill Gap Analysis"])


class SkillGapAnalysisRequest(BaseModel):
    candidate_skills: List[str] = Field(..., description="List of raw or normalized candidate skills")
    required_job_skills: List[str] = Field(..., description="List of required job skills")
    preferred_job_skills: Optional[List[str]] = Field(default_factory=list, description="List of optional preferred skills")
    resume_raw_text: Optional[str] = Field(default="", description="Optional raw resume text for textual evidence quoting")


@router.post("/analyze", response_model=APIResponse[SkillGapResult], status_code=status.HTTP_200_OK)
async def analyze_skill_gaps(payload: SkillGapAnalysisRequest):
    """
    Direct endpoint to perform skill gap analysis between candidate skills and job requirements:
    - Normalizes terms (e.g. JS -> JavaScript)
    - Detects Matched Skills (with resume quotes)
    - Detects Missing Required Skills
    - Detects Transferable / Adjacent Skills
    - Detects Preferred Skill Gaps
    """
    result = detect_skill_gaps(
        candidate_skills=payload.candidate_skills,
        required_job_skills=payload.required_job_skills,
        preferred_job_skills=payload.preferred_job_skills or [],
        resume_raw_text=payload.resume_raw_text or ""
    )

    return APIResponse(
        success=True,
        message="Skill gap analysis evaluated successfully",
        data=result
    )
