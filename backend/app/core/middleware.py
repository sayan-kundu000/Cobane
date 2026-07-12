import time
import uuid
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.responses import request_id_context
from app.core.logging import app_logger, api_logger


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """Middleware that injects a unique X-Request-ID trace indicator to both incoming contexts and outgoing headers."""

    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Set the ContextVar trace identifier
        token = request_id_context.set(req_id)
        request.state.request_id = req_id

        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = req_id
            return response
        finally:
            request_id_context.reset(token)


class RequestTimeMiddleware(BaseHTTPMiddleware):
    """Middleware that tracks request durations and logs route completions."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        api_logger.info(
            f"Method: {request.method} | Path: {request.url.path} | "
            f"Status: {response.status_code} | Duration: {duration:.4f}s"
        )
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware applying standard protective headers to responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response


def register_middlewares(app: FastAPI) -> None:
    """Configures application with base infrastructure middlewares."""
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestTimeMiddleware)
    app.add_middleware(CorrelationIDMiddleware)
