import time
from collections import defaultdict
from typing import Dict, List, Optional
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class InMemoryRateLimiter:
    """
    Sliding window in-memory rate limiter per IP address.
    Tracks timestamps of requests within a sliding time window.
    """

    def __init__(self, default_limit: int = 100, window_seconds: int = 60):
        self.default_limit = default_limit
        self.window_seconds = window_seconds
        # client_ip -> list of epoch timestamps
        self._history: Dict[str, List[float]] = defaultdict(list)
        # Specific route overrides: path prefix -> limit per window
        self._route_limits: Dict[str, int] = {
            "/api/analysis/create": 20,
            "/api/resumes/upload": 25,
            "/api/job/analyze": 25,
        }
        self.enabled = True

    def _get_limit_for_path(self, path: str) -> int:
        for prefix, limit in self._route_limits.items():
            if path.startswith(prefix):
                return limit
        return self.default_limit

    def is_rate_limited(self, client_ip: str, path: str) -> tuple[bool, int, int]:
        """
        Checks if the client exceeds the limit for the specified path.
        Returns: (is_limited, current_count, retry_after_seconds)
        """
        if not self.enabled:
            return False, 0, 0

        now = time.time()
        window_start = now - self.window_seconds
        limit = self._get_limit_for_path(path)

        key = f"{client_ip}:{path}" if path in self._route_limits else client_ip
        timestamps = self._history[key]

        # Evict timestamps older than the sliding window
        valid_timestamps = [ts for ts in timestamps if ts > window_start]
        self._history[key] = valid_timestamps

        if len(valid_timestamps) >= limit:
            oldest_timestamp = valid_timestamps[0]
            retry_after = max(1, int(self.window_seconds - (now - oldest_timestamp)))
            return True, len(valid_timestamps), retry_after

        # Record this request
        valid_timestamps.append(now)
        return False, len(valid_timestamps), 0

    def reset(self):
        """Clears rate limit state (useful in test teardown)"""
        self._history.clear()


# Singleton instance
global_rate_limiter = InMemoryRateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI / Starlette Middleware enforcing rate limits per client IP.
    """

    def __init__(self, app, limiter: Optional[InMemoryRateLimiter] = None):
        super().__init__(app)
        self.limiter = limiter or global_rate_limiter

        # Paths that should not be rate-limited (e.g. health checks, API docs)
        self.exempt_prefixes = [
            "/api/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico"
        ]

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Pre-flight OPTIONS requests are not rate limited
        if request.method == "OPTIONS":
            return await call_next(request)

        path = request.url.path
        # Check exemption
        for prefix in self.exempt_prefixes:
            if path.startswith(prefix):
                return await call_next(request)

        # Extract client IP safely (support proxies / headers)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "127.0.0.1"

        is_limited, count, retry_after = self.limiter.is_rate_limited(client_ip, path)

        if is_limited:
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "message": f"Too many requests. Rate limit exceeded. Please wait {retry_after} seconds before retrying.",
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "details": {
                        "retry_after_seconds": retry_after,
                        "client_ip": client_ip
                    }
                },
                headers={"Retry-After": str(retry_after)}
            )

        response = await call_next(request)
        return response
