from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from typing import Any, Optional
from app.core.responses import get_standard_envelope
from app.core.logging import app_logger


class CobaneException(HTTPException):
    """Base exception class for all custom Cobane application errors."""

    def __init__(
        self, status_code: int, detail: str, error_code: str = "APPLICATION_ERROR", details: Optional[Any] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.details = details


class DatabaseException(CobaneException):
    def __init__(self, detail: str = "Database transaction failed", details: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="DATABASE_ERROR",
            details=details,
        )


class AuthException(CobaneException):
    def __init__(self, detail: str = "Invalid credentials or token expired", details: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, error_code="UNAUTHORIZED", details=details
        )


class ForbiddenException(CobaneException):
    def __init__(self, detail: str = "Action forbidden for current user role", details: Optional[Any] = None):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail, error_code="FORBIDDEN", details=details)


class ValidationException(CobaneException):
    def __init__(self, detail: str = "Input validation constraints breached", details: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class NotFoundException(CobaneException):
    def __init__(self, detail: str = "Requested resource not located", details: Optional[Any] = None):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail, error_code="NOT_FOUND", details=details)


def register_exception_handlers(app: FastAPI) -> None:
    """Registers standard handlers to format exceptions in standardized JSON envelopes."""

    @app.exception_handler(CobaneException)
    async def cobane_exception_handler(request: Request, exc: CobaneException):
        app_logger.warning(f"Application exception raised: {exc.detail} [Code: {exc.error_code}]")
        envelope = get_standard_envelope(
            success=False, payload=exc.details, error_code=exc.error_code, message=exc.detail
        )
        return JSONResponse(status_code=exc.status_code, content=envelope)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        app_logger.warning(f"Validation error: {exc.errors()}")
        envelope = get_standard_envelope(
            success=False,
            payload=exc.errors(),
            error_code="VALIDATION_ERROR",
            message="Request parameter validation failed.",
        )
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=envelope)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        app_logger.warning(f"HTTP exception: {exc.detail}")
        envelope = get_standard_envelope(success=False, payload=None, error_code="HTTP_ERROR", message=exc.detail)
        return JSONResponse(status_code=exc.status_code, content=envelope)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        app_logger.error("Unhandled server exception encountered", exc_info=exc)
        envelope = get_standard_envelope(
            success=False,
            payload=None,
            error_code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred on the server.",
        )
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=envelope)
