import os
import re
from typing import Tuple
from fastapi import UploadFile, HTTPException, status

# 10 Megabytes maximum file size limit
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

# Allowed file extensions and MIME types
ALLOWED_EXTENSIONS = {".pdf", ".docx"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "application/octet-stream"  # sometimes sent by browsers on Windows
}

# Magic bytes headers for true binary verification
PDF_MAGIC_BYTES = b"%PDF"
DOCX_MAGIC_BYTES = b"PK\x03\x04"


def sanitize_filename(filename: str) -> str:
    """
    Strips directory traversal sequences (../, ..\\) and dangerous characters.
    Replaces spaces with underscores.
    """
    clean_name = os.path.basename(filename)
    clean_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', clean_name)
    return clean_name or "uploaded_resume.pdf"


def validate_resume_file(filename: str, content_type: str, file_bytes: bytes) -> Tuple[bool, str]:
    """
    Comprehensive file validation pipeline:
    1. Empty file check
    2. File size cap (10 MB)
    3. File extension check (.pdf, .docx)
    4. Binary magic header check
    """
    # 1. Empty check
    if not file_bytes or len(file_bytes) == 0:
        return False, "The uploaded file is empty (0 bytes). Please upload a valid document."

    # 2. Size limit
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        size_mb = len(file_bytes) / (1024 * 1024)
        return False, f"File size ({size_mb:.2f} MB) exceeds the maximum allowed limit of 10 MB."

    # 3. Extension check
    _, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file extension '{ext}'. Only PDF (.pdf) and Word (.docx) documents are permitted."

    # 4. Binary magic signature check
    if ext == ".pdf":
        if not file_bytes.startswith(PDF_MAGIC_BYTES):
            return False, "File has a .pdf extension but is not a valid PDF document (missing %PDF signature)."
    elif ext == ".docx":
        if not file_bytes.startswith(DOCX_MAGIC_BYTES):
            return False, "File has a .docx extension but is not a valid OpenXML Word document (missing PK zip signature)."

    return True, "File is valid."


async def read_and_validate_upload(file: UploadFile) -> Tuple[str, str, bytes]:
    """
    FastAPI helper to read UploadFile contents, validate them, and return
    (safe_filename, file_type, file_bytes).
    Raises HTTPException(400) if validation fails.
    """
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file was attached to the upload request."
        )

    safe_filename = sanitize_filename(file.filename)
    file_bytes = await file.read()

    is_valid, error_msg = validate_resume_file(
        filename=safe_filename,
        content_type=file.content_type or "",
        file_bytes=file_bytes
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    _, ext = os.path.splitext(safe_filename.lower())
    inferred_content_type = "application/pdf" if ext == ".pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    return safe_filename, inferred_content_type, file_bytes
