import pytest
from app.database.supabase import SupabaseService, get_supabase_client

def test_supabase_service_unconfigured_fallback():
    """Verify that SupabaseService behaves gracefully and safely when credentials are not yet supplied"""
    service = SupabaseService()
    check = service.check_connection()
    assert "status" in check
    # In test/default environment without actual keys, status is either unconfigured or error
    assert check["status"] in ["unconfigured", "connected", "error"]

def test_insert_fallback_id_generation():
    """Verify that insert methods return valid UUID strings even in mock mode"""
    service = SupabaseService(client=None)
    resume_id = service.insert_resume(
        file_name="test_resume.pdf",
        file_type="application/pdf",
        file_size=1024,
        raw_text="Test resume text with Python and FastAPI",
        parsed_profile={"skills": ["Python"]}
    )
    assert resume_id is not None
    assert len(resume_id) == 36  # Valid UUID length
