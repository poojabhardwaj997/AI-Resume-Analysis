from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import get_settings
from app.utils.logger import logger
from app.schemas.common import ErrorResponse
from app.api.routes import health, resume, job, skill_gap, analysis

from app.middleware import SecurityHeadersMiddleware, RateLimitMiddleware, global_rate_limiter

settings = get_settings()

# Sync rate limit toggle with configuration
global_rate_limiter.enabled = settings.RATE_LIMIT_ENABLED

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## AI-Powered Resume Analysis API with Skill Gap Detection using LLMs
    
    This API orchestrates resume ingestion (PDF/DOCX), LLM entity extraction,
    job description requirement parsing, taxonomy skill normalization,
    transparent compatibility scoring, and actionable learning recommendations.
    
    ### Tech Stack:
    - **FastAPI & Python 3.11+**
    - **PyMuPDF & python-docx**
    - **OpenAI API (JSON Output Mode)**
    - **Supabase PostgreSQL & Storage**
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# -------------------------------------------------------------------
# Security & Rate Limiting Middleware
# -------------------------------------------------------------------
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)

# -------------------------------------------------------------------
# CORS (Cross-Origin Resource Sharing) Configuration
# -------------------------------------------------------------------
configured_frontend = settings.FRONTEND_URL.rstrip("/") if settings.FRONTEND_URL else ""

allowed_origins = [
    "https://ai-resume-analysis-frontend-orcin.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:80",
    "http://localhost",
]

if configured_frontend and configured_frontend not in allowed_origins:
    allowed_origins.append(configured_frontend)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"^https:\/\/.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# -------------------------------------------------------------------
# Exception Handlers
# -------------------------------------------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Formats all standard HTTPExceptions into consistent ErrorResponse envelope"""
    logger.warning(f"HTTP {exc.status_code} on {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            message=str(exc.detail),
            error_code=f"HTTP_{exc.status_code}",
            details=getattr(exc, "headers", None)
        ).model_dump()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Formats Pydantic request validation errors cleanly for frontend consumption"""
    errors = exc.errors()
    logger.warning(f"Validation error on {request.url.path}: {errors}")
    first_msg = errors[0]["msg"] if errors else "Invalid request data"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            success=False,
            message=f"Validation failed: {first_msg}",
            error_code="VALIDATION_ERROR",
            details=errors
        ).model_dump()
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catches unhandled server errors and prevents internal stack trace leaks"""
    logger.error(f"Unhandled Exception on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            success=False,
            message="An internal server error occurred. Please contact the administrator.",
            error_code="INTERNAL_SERVER_ERROR"
        ).model_dump()
    )


# -------------------------------------------------------------------
# Route Mounting
# -------------------------------------------------------------------
app.include_router(health.router)
app.include_router(resume.router)
app.include_router(job.router)
app.include_router(skill_gap.router)
app.include_router(analysis.router)


@app.get("/", tags=["Root"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs_url": "/docs"
    }
