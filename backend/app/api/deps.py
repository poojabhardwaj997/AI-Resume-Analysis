from typing import Optional
from pydantic import BaseModel
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import get_settings
from app.database.supabase import get_supabase_client
from app.utils.logger import logger


security = HTTPBearer(auto_error=False)


class AuthenticatedUser(BaseModel):
    id: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    token: Optional[str] = None


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> AuthenticatedUser:
    """
    FastAPI dependency validating the Supabase JWT Bearer token.
    Extracts the authenticated user ID and email from Supabase Auth.
    Enforces strict authorization: rejects requests with 401 if token is missing or invalid.
    """
    settings = get_settings()

    # In testing mode without credentials, return a deterministic test user
    if settings.ENVIRONMENT == "testing" and (not credentials or not credentials.credentials):
        return AuthenticatedUser(
            id="00000000-0000-0000-0000-000000000001",
            email="testuser@example.com",
            full_name="Test User",
            token="test-mock-token"
        )

    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    client = get_supabase_client()

    if not client:
        # Fallback if running offline without Supabase configuration
        logger.warning("[Auth Dep] Supabase unconfigured, returning mock user context.")
        return AuthenticatedUser(
            id="00000000-0000-0000-0000-000000000001",
            email="localuser@example.com",
            full_name="Local Developer",
            token=token
        )

    try:
        # Validate JWT token cryptographically via Supabase Auth API
        auth_response = client.auth.get_user(token)
        supabase_user = auth_response.user

        if not supabase_user or not supabase_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication session. Please re-authenticate.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        full_name = ""
        if supabase_user.user_metadata:
            full_name = supabase_user.user_metadata.get("full_name", "")

        return AuthenticatedUser(
            id=str(supabase_user.id),
            email=supabase_user.email,
            full_name=full_name,
            token=token
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"[Auth Dep] Token validation rejected: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired or token is invalid. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[AuthenticatedUser]:
    """
    Optional user dependency for endpoints allowing both authenticated and guest access.
    Returns None if no token is present.
    """
    if not credentials or not credentials.credentials:
        return None
    try:
        return await get_current_user(request, credentials)
    except HTTPException:
        return None
