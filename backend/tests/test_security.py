import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.middleware.rate_limiter import InMemoryRateLimiter, RateLimitMiddleware, global_rate_limiter
from app.utils.pii_sanitizer import (
    mask_email,
    mask_phone,
    sanitize_profile_for_logs,
    redact_sensitive_text
)


client = TestClient(app)


def test_security_headers_present():
    """Verify OWASP recommended security headers are attached to API responses"""
    response = client.get("/api/health")
    assert response.status_code == 200
    headers = response.headers
    
    assert headers.get("x-content-type-options") == "nosniff"
    assert headers.get("x-frame-options") == "DENY"
    assert headers.get("x-xss-protection") == "1; mode=block"
    assert headers.get("referrer-policy") == "strict-origin-when-cross-origin"
    assert "server" not in headers


def test_rate_limiter_unit_logic():
    """Verify rate limiter allows up to limit and blocks above limit"""
    limiter = InMemoryRateLimiter(default_limit=3, window_seconds=60)
    client_ip = "192.168.1.100"
    path = "/api/test"

    # Calls 1, 2, 3 should be permitted
    limited, count, _ = limiter.is_rate_limited(client_ip, path)
    assert limited is False
    assert count == 1

    limited, count, _ = limiter.is_rate_limited(client_ip, path)
    assert limited is False
    assert count == 2

    limited, count, _ = limiter.is_rate_limited(client_ip, path)
    assert limited is False
    assert count == 3

    # Call 4 should trigger 429 limit
    limited, count, retry_after = limiter.is_rate_limited(client_ip, path)
    assert limited is True
    assert count == 3
    assert retry_after > 0


def test_rate_limiter_http_middleware_integration():
    """Test rate limiter HTTP 429 response on a configured endpoint"""
    global_rate_limiter.reset()
    
    # Temporarily set very low limit for testing
    original_limit = global_rate_limiter.default_limit
    global_rate_limiter.default_limit = 2
    
    try:
        # Call 1: Success
        r1 = client.get("/")
        assert r1.status_code == 200
        
        # Call 2: Success
        r2 = client.get("/")
        assert r2.status_code == 200
        
        # Call 3: Exceeds limit -> HTTP 429
        r3 = client.get("/")
        assert r3.status_code == 429
        assert "Too many requests" in r3.json()["message"]
        assert "Retry-After" in r3.headers
    finally:
        global_rate_limiter.default_limit = original_limit
        global_rate_limiter.reset()


def test_pii_masking_email():
    """Verify email addresses are properly masked"""
    assert mask_email("john.doe@example.com") == "j***e@example.com"
    assert mask_email("a@b.com") == "a***@b.com"
    assert mask_email("") == ""


def test_pii_masking_phone():
    """Verify phone numbers are properly masked leaving only last 4 digits"""
    masked = mask_phone("+1-555-432-8765")
    assert masked.endswith("8765")
    assert "***" in masked


def test_pii_sanitize_profile_for_logs():
    """Verify candidate profile dictionary has PII masked safely"""
    raw_profile = {
        "candidate_name": "Vikram Patel",
        "email": "vikram.patel@gmail.com",
        "phone": "+91 9876543210",
        "skills": ["Python", "FastAPI"]
    }
    safe = sanitize_profile_for_logs(raw_profile)
    assert safe["email"] == "v***l@gmail.com"
    assert safe["phone"].endswith("3210")
    assert safe["skills"] == ["Python", "FastAPI"]
    # Ensure original was not mutated in place
    assert raw_profile["email"] == "vikram.patel@gmail.com"


def test_pii_redact_sensitive_text():
    """Verify raw strings with embedded emails/phones are redacted"""
    text = "Candidate email is candidate@test.com and phone is 555-234-5678."
    redacted = redact_sensitive_text(text)
    assert "candidate@test.com" not in redacted
    assert "[REDACTED_EMAIL]" in redacted
    assert "555-234-5678" not in redacted
    assert "[REDACTED_PHONE]" in redacted
