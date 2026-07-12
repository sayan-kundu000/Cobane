import contextvars
from datetime import datetime, timezone
from typing import Any
from fastapi.responses import JSONResponse
from app.utils.datetime_helpers import get_utc_now

# Async-safe request id tracking context
request_id_context = contextvars.ContextVar("request_id", default="system")


def get_standard_envelope(success: bool, payload: Any, error_code: str = None, message: str = None) -> dict:
    """Wraps JSON response parameters into a unified system envelope."""
    now = get_utc_now().isoformat()
    req_id = request_id_context.get()

    if success:
        return {"success": True, "data": payload, "timestamp": now, "request_id": req_id}
    else:
        return {
            "success": False,
            "error": error_code or "INTERNAL_SERVER_ERROR",
            "message": message or "An unexpected event occurred",
            "details": payload,
            "timestamp": now,
            "request_id": req_id,
        }


class StandardJSONResponse(JSONResponse):
    """Custom standard HTTP response builder to enforce envelopes."""

    def __init__(
        self, content: Any, status_code: int = 200, headers: dict = None, media_type: str = None, **kwargs
    ) -> None:
        envelope = get_standard_envelope(success=True, payload=content)
        super().__init__(content=envelope, status_code=status_code, headers=headers, media_type=media_type, **kwargs)
