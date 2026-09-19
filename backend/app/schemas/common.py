from typing import Generic, TypeVar, Optional, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standardized API Response wrapper"""
    success: bool = Field(default=True, description="Indicates whether the request succeeded")
    message: str = Field(default="Operation completed successfully", description="Human-readable message")
    data: Optional[T] = Field(default=None, description="Response payload")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp"
    )


class ErrorResponse(BaseModel):
    """Standardized error envelope"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Any] = None
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
