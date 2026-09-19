import io
import os
import fitz  # PyMuPDF
from docx import Document  # python-docx
from fastapi import HTTPException, status
from app.services.text_cleaner import clean_extracted_text
from app.utils.logger import logger

MIN_EXTRACTED_CHARACTERS = 40


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extracts text from PDF binary streams using PyMuPDF (fitz).
    Handles multi-column layouts, header blocks, and text blocks.
    Raises HTTPException if the PDF is corrupted, password-protected, or scanned.
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as e:
        logger.error(f"Failed to open PDF stream: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The PDF file is corrupted, encrypted, or cannot be opened."
        )

    if doc.is_encrypted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The PDF file is password-protected. Please upload an unprotected document."
        )

    full_text_chunks = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_text = page.get_text("text")
        if page_text:
            full_text_chunks.append(page_text)

    raw_text = "\n\n".join(full_text_chunks).strip()

    # Check for scanned image-only PDF
    if len(raw_text) < MIN_EXTRACTED_CHARACTERS:
        logger.warning("Extracted PDF text is under minimum character threshold - likely a scanned document.")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Scanned / image-only PDF detected. The document does not contain selectable text. "
                "Please export your resume directly as a digital PDF from Word, Google Docs, or Canva."
            )
        )

    return raw_text


def extract_text_from_docx(docx_bytes: bytes) -> str:
    """
    Extracts text from Word documents (.docx) using python-docx.
    Extracts both standard paragraphs and table contents (often used for skills and education).
    """
    try:
        doc_stream = io.BytesIO(docx_bytes)
        doc = Document(doc_stream)
    except Exception as e:
        logger.error(f"Failed to parse DOCX stream: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The Word (.docx) document is corrupted or invalid."
        )

    chunks = []

    # 1. Extract paragraphs
    for p in doc.paragraphs:
        text = p.text.strip()
        if text:
            chunks.append(text)

    # 2. Extract text inside tables (resumes often use 2-column tables for skills/education)
    for table in doc.tables:
        for row in table.rows:
            row_texts = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_texts:
                chunks.append(" | ".join(row_texts))

    raw_text = "\n\n".join(chunks).strip()

    if len(raw_text) < MIN_EXTRACTED_CHARACTERS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The Word document contains insufficient readable text. Please ensure it is not empty."
        )

    return raw_text


def parse_resume_document(file_bytes: bytes, filename: str) -> str:
    """
    Unified entry point for resume text extraction and cleaning.
    Detects file format from extension, extracts raw text, and sanitizes noise.
    """
    _, ext = os.path.splitext(filename.lower())

    if ext == ".pdf":
        raw_text = extract_text_from_pdf(pdf_bytes=file_bytes)
    elif ext == ".docx":
        raw_text = extract_text_from_docx(docx_bytes=file_bytes)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}' for text extraction."
        )

    cleaned_text = clean_extracted_text(raw_text)
    logger.info(f"Parsed {filename}: extracted {len(cleaned_text)} characters ({len(cleaned_text.split())} words).")
    return cleaned_text
