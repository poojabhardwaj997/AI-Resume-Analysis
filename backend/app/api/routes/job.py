from fastapi import APIRouter, HTTPException, status, Request, Depends
from app.schemas.common import APIResponse
from app.schemas.job import JobAnalysisRequest, JobAnalysisResponse, JobRequirements
from app.services.llm_service import LLMService
from app.database.supabase import SupabaseService
from app.api.deps import get_current_user, AuthenticatedUser
from app.services.audit_service import audit_service
from app.utils.logger import logger

router = APIRouter(prefix="/api/job", tags=["Job Descriptions"])


@router.post("/analyze", response_model=APIResponse[JobAnalysisResponse], status_code=status.HTTP_200_OK)
async def analyze_job(
    request: Request,
    payload: JobAnalysisRequest,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Parses unstructured Job Description text into structured requirements:
    - Required / Mandatory Skills
    - Preferred / Nice-to-have Skills
    - Experience Criteria
    - Minimum Education Criteria
    - Persists record in Supabase job_descriptions and job_skills with user ownership
    """
    llm_service = LLMService()
    parsed_reqs: JobRequirements = llm_service.analyze_job_description(
        jd_text=payload.job_description_text,
        job_title=payload.job_title,
        company_name=payload.company_name
    )

    db_service = SupabaseService(user_token=user.token)

    # Save to Supabase job_descriptions table with user ownership
    job_id = db_service.insert_job_description(
        job_title=parsed_reqs.job_title or payload.job_title or "General Role",
        company_name=parsed_reqs.company_name or payload.company_name or "Hiring Organization",
        raw_text=payload.job_description_text,
        parsed_requirements=parsed_reqs.model_dump(),
        user_id=user.id
    )

    # Save individual required & preferred skills to job_skills table
    job_skills_data = []
    for skill in parsed_reqs.required_skills:
        job_skills_data.append({
            "skill_name": skill,
            "normalized_name": skill,
            "requirement_type": "required",
            "importance_weight": 1.0
        })
    for skill in parsed_reqs.preferred_skills:
        job_skills_data.append({
            "skill_name": skill,
            "normalized_name": skill,
            "requirement_type": "preferred",
            "importance_weight": 0.5
        })
    db_service.insert_job_skills(job_id, job_skills_data)

    audit_service.log_event(
        action="JOB_ANALYZED",
        user_id=user.id,
        resource_type="job_description",
        resource_id=job_id,
        request=request
    )

    logger.info(f"Job Description analyzed: ID={job_id}, RequiredSkills={len(parsed_reqs.required_skills)}, PreferredSkills={len(parsed_reqs.preferred_skills)}, User={user.id}")

    response_data = JobAnalysisResponse(
        job_id=job_id,
        job_title=parsed_reqs.job_title,
        company_name=parsed_reqs.company_name,
        parsed_requirements=parsed_reqs,
        message="Job description analyzed successfully."
    )

    return APIResponse(
        success=True,
        message="Job description analyzed and requirements structured successfully",
        data=response_data
    )


@router.get("/{job_id}", response_model=APIResponse[dict])
async def get_job(
    job_id: str,
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Retrieves a previously stored job description record ensuring user ownership"""
    db_service = SupabaseService(user_token=user.token)
    job = db_service.get_job(job_id, user_id=user.id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description '{job_id}' not found or you do not have permission to view it."
        )

    audit_service.log_event(
        action="JOB_VIEWED",
        user_id=user.id,
        resource_type="job_description",
        resource_id=job_id,
        request=request
    )

    return APIResponse(
        success=True,
        message="Job description found",
        data=job
    )
