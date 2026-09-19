from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    OWASP Recommended Security Headers Middleware.
    Injects defensive headers on all outgoing HTTP responses:
    - X-Content-Type-Options: Prevents MIME-type sniffing
    - X-Frame-Options: Prevents clickjacking attacks (iframe framing)
    - X-XSS-Protection: Activates legacy XSS filter
    - Referrer-Policy: Prevents referrer information leakage
    - Permissions-Policy: Restricts sensitive browser features
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        
        # Defense-in-depth headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # Obfuscate / remove tech stack signature headers if present
        if "server" in response.headers:
            del response.headers["server"]
            
        return response
