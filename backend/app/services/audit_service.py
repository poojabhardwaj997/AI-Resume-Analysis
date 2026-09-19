import uuid
from typing import Optional
from starlette.requests import Request
from app.database.supabase import get_supabase_client
from app.utils.logger import logger


def get_client_ip(request: Optional[Request]) -> Optional[str]:
    """Extracts client IP address safely considering proxies"""
    if not request:
        return None
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else None


def get_user_agent(request: Optional[Request]) -> Optional[str]:
    """Extracts browser user-agent from request"""
    if not request:
        return None
    return request.headers.get("User-Agent")


class AuditService:
    """
    Forensic security audit logging service.
    Inserts immutable audit log entries into public.audit_logs.
    Never logs passwords, tokens, API keys, or raw confidential resume text.
    """

    def __init__(self):
        self.client = get_supabase_client()

    def log_event(
        self,
        action: str,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        request: Optional[Request] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        ip = ip_address or get_client_ip(request)
        ua = user_agent or get_user_agent(request)

        # Truncate user-agent to reasonable length
        if ua and len(ua) > 255:
            ua = ua[:255]

        logger.info(f"[AUDIT] action={action} user_id={user_id or 'ANONYMOUS'} resource={resource_type}:{resource_id or 'N/A'} ip={ip or 'UNKNOWN'}")

        if not self.client:
            return

        try:
            log_row = {
                "user_id": user_id,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "ip_address": ip,
                "user_agent": ua
            }
            self.client.table("audit_logs").insert(log_row).execute()
        except Exception as e:
            # Audit failures must not crash the primary transaction, but should be alerted
            logger.error(f"[AUDIT FAILURE] Could not persist audit log to Supabase: {str(e)}")


# Singleton instance
audit_service = AuditService()
