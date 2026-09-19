from fastapi import APIRouter, Depends
from app.config import Settings, get_settings
from app.schemas.common import APIResponse
from app.database.supabase import SupabaseService

router = APIRouter(prefix="/api/health", tags=["Health & Status"])


@router.get("", response_model=APIResponse[dict])
async def health_check(settings: Settings = Depends(get_settings)):
    """
    Health check and diagnostics endpoint.
    Verifies that the FastAPI application is alive and inspects service readiness.
    """
    db_service = SupabaseService()
    db_status = db_service.check_connection()

    health_data = {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "services": {
            "database": db_status["status"],
            "database_detail": db_status["detail"],
            "llm_service": "configured" if settings.is_openai_configured else "pending_credentials",
            "pdf_parser": "ready (PyMuPDF)",
            "docx_parser": "ready (python-docx)"
        },
        "scoring_weights": {
            "required_skills": settings.WEIGHT_REQUIRED_SKILLS,
            "preferred_skills": settings.WEIGHT_PREFERRED_SKILLS,
            "experience": settings.WEIGHT_EXPERIENCE,
            "education": settings.WEIGHT_EDUCATION
        }
    }
    return APIResponse(
        success=True,
        message="FastAPI service is running normally",
        data=health_data
    )
