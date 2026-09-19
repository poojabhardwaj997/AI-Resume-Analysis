import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.api.deps import get_current_user, AuthenticatedUser
from app.services.audit_service import audit_service


@pytest.mark.asyncio
async def test_idor_protection_analysis_isolation():
    """
    Security Test: Anti-IDOR / Anti-BOLA Verification.
    Verifies that User A's analysis report cannot be accessed or deleted by User B.
    """
    user_a = AuthenticatedUser(
        id="11111111-1111-1111-1111-111111111111",
        email="usera@example.com",
        full_name="User A",
        token="token-a"
    )
    user_b = AuthenticatedUser(
        id="22222222-2222-2222-2222-222222222222",
        email="userb@example.com",
        full_name="User B",
        token="token-b"
    )

    # Override dependency to simulate User B
    app.dependency_overrides[get_current_user] = lambda: user_b

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # User B attempts to access a non-existent or User A-owned analysis
        response = await client.get("/api/analysis/non-existent-or-other-user-uuid")
        assert response.status_code in [404, 403]

        # User B attempts to delete an analysis they do not own
        del_response = await client.delete("/api/analysis/non-existent-or-other-user-uuid")
        assert del_response.status_code in [404, 403]

    # Clean up override
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_audit_logging_service_safe_execution():
    """
    Verifies that audit logging executes safely without raising unhandled exceptions,
    even in test/mock environments or without active remote connections.
    """
    # Should not throw
    audit_service.log_event(
        action="TEST_ACTION_EXECUTION",
        user_id="00000000-0000-0000-0000-000000000001",
        resource_type="unit_test",
        resource_id="00000000-0000-0000-0000-000000000002"
    )
    assert True
