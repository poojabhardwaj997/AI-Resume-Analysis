import pytest
import io
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.utils.file_validation import (
    validate_resume_file,
    sanitize_filename,
    PDF_MAGIC_BYTES,
    DOCX_MAGIC_BYTES,
    MAX_FILE_SIZE_BYTES
)


def test_sanitize_filename():
    """Verify path traversal prevention and character sanitization"""
    assert sanitize_filename("../../secret_resume.pdf") == "secret_resume.pdf"
    assert sanitize_filename("..\\..\\windows\\system32.pdf") == "system32.pdf"
    assert sanitize_filename("John Doe Resume (2026).pdf") == "John_Doe_Resume__2026_.pdf"


def test_valid_pdf_validation():
    """Verify valid PDF binary content passes validation"""
    valid_pdf_bytes = b"%PDF-1.5 \n1 0 obj << /Type /Catalog >> endobj"
    is_valid, msg = validate_resume_file("john_doe.pdf", "application/pdf", valid_pdf_bytes)
    assert is_valid is True
    assert msg == "File is valid."


def test_valid_docx_validation():
    """Verify valid DOCX binary content passes validation"""
    valid_docx_bytes = b"PK\x03\x04\x14\x00\x06\x00word/document.xml"
    is_valid, msg = validate_resume_file("candidate.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", valid_docx_bytes)
    assert is_valid is True
    assert msg == "File is valid."


def test_empty_file_rejected():
    """Verify 0-byte file is rejected"""
    is_valid, msg = validate_resume_file("empty.pdf", "application/pdf", b"")
    assert is_valid is False
    assert "empty" in msg.lower()


def test_oversized_file_rejected():
    """Verify files larger than 10MB are rejected"""
    oversized = b"%PDF" + (b"A" * (MAX_FILE_SIZE_BYTES + 1024))
    is_valid, msg = validate_resume_file("huge.pdf", "application/pdf", oversized)
    assert is_valid is False
    assert "exceeds" in msg.lower()


def test_disguised_file_rejected():
    """Verify files with fake PDF extension but wrong magic header are rejected"""
    fake_pdf = b"MZ\x90\x00This is an executable binary"
    is_valid, msg = validate_resume_file("virus.pdf", "application/pdf", fake_pdf)
    assert is_valid is False
    assert "not a valid pdf" in msg.lower()


def test_unsupported_extension_rejected():
    """Verify files with invalid extensions (e.g. .exe, .png) are rejected"""
    is_valid, msg = validate_resume_file("image.png", "image/png", b"\x89PNG\r\n\x1a\n")
    assert is_valid is False
    assert "unsupported file extension" in msg.lower()


@pytest.mark.asyncio
async def test_upload_resume_endpoint_success():
    """Verify POST /api/resumes/upload processes a valid PDF and returns 201"""
    import fitz
    doc = fitz.open()
    p = doc.new_page()
    p.insert_text((50, 72), "Jane Doe\nFull Stack Developer\nSkills: Python, FastAPI, React, PostgreSQL")
    real_pdf_bytes = doc.tobytes()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {
            "file": ("jane_doe_resume.pdf", io.BytesIO(real_pdf_bytes), "application/pdf")
        }
        response = await client.post("/api/resumes/upload", files=files)
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "resume_id" in data["data"]
        assert data["data"]["file_name"] == "jane_doe_resume.pdf"
        assert data["data"]["file_type"] == "application/pdf"


@pytest.mark.asyncio
async def test_upload_resume_endpoint_invalid_file():
    """Verify POST /api/resumes/upload rejects invalid extension with 400 Bad Request"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {
            "file": ("script.py", io.BytesIO(b"print('hello')"), "text/plain")
        }
        response = await client.post("/api/resumes/upload", files=files)
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "unsupported file extension" in data["message"].lower()
