from fastapi import APIRouter, UploadFile, File, HTTPException, status, Request, Depends
from app.utils.file_validation import read_and_validate_upload
from app.services.resume_parser import parse_resume_document
from app.services.text_cleaner import estimate_word_count
from app.database.supabase import SupabaseService
from app.api.deps import get_current_user, AuthenticatedUser
from app.services.audit_service import audit_service
from app.schemas.common import APIResponse
from app.schemas.resume import ResumeUploadResponse
from app.utils.logger import logger

router = APIRouter(prefix="/api/resumes", tags=["Resumes"])


@router.post("/upload", response_model=APIResponse[ResumeUploadResponse], status_code=status.HTTP_201_CREATED)
async def upload_resume(
    request: Request,
    file: UploadFile = File(...),
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Validates, extracts text from, and securely uploads a candidate resume (.pdf or .docx).
    - Checks file extensions and binary magic signatures.
    - Caps file size at 10 MB.
    - Extracts clean digital text using PyMuPDF (PDF) or python-docx (DOCX).
    - Saves document to Supabase Storage and records metadata with user ownership.
    """
    safe_filename, file_type, file_bytes = await read_and_validate_upload(file)
    file_size = len(file_bytes)

    # Extract & sanitize text
    extracted_text = parse_resume_document(file_bytes=file_bytes, filename=safe_filename)
    word_count = estimate_word_count(extracted_text)

    db_service = SupabaseService(user_token=user.token)

    # Upload to Supabase Storage if configured
    storage_path = db_service.upload_file_to_storage(
        file_bytes=file_bytes,
        original_filename=safe_filename,
        content_type=file_type,
        user_id=user.id
    )

    # Insert metadata record in PostgreSQL resumes table with extracted raw_text and user_id
    resume_id = db_service.insert_resume(
        file_name=safe_filename,
        file_type=file_type,
        file_size=file_size,
        raw_text=extracted_text,
        parsed_profile={},
        storage_path=storage_path,
        user_id=user.id
    )

    audit_service.log_event(
        action="RESUME_UPLOADED",
        user_id=user.id,
        resource_type="resume",
        resource_id=resume_id,
        request=request
    )

    logger.info(f"Resume uploaded and parsed successfully: ID={resume_id}, Words={word_count}, User={user.id}")

    response_data = ResumeUploadResponse(
        resume_id=resume_id,
        file_name=safe_filename,
        file_size=file_size,
        file_type=file_type,
        storage_path=storage_path,
        raw_text_preview=extracted_text[:300] + ("..." if len(extracted_text) > 300 else ""),
        word_count=word_count,
        status="parsed",
        message="Resume uploaded, validated, and parsed successfully."
    )

    return APIResponse(
        success=True,
        message="Resume uploaded and text extracted successfully",
        data=response_data
    )


@router.get("/{resume_id}", response_model=APIResponse[dict])
async def get_resume(
    resume_id: str,
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Retrieves metadata for a previously uploaded resume strictly checking user ownership.
    """
    db_service = SupabaseService(user_token=user.token)
    resume = db_service.get_resume(resume_id, user_id=user.id)

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume '{resume_id}' not found or you do not have permission to view it."
        )

    audit_service.log_event(
        action="RESUME_VIEWED",
        user_id=user.id,
        resource_type="resume",
        resource_id=resume_id,
        request=request
    )

    return APIResponse(
        success=True,
        message="Resume found",
        data=resume
    )
