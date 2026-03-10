from __future__ import annotations


class WOOFiError(Exception):
    """Base exception for WOOFi SDK."""


class WOOFiHTTPError(WOOFiError):
    """Upstream returned non-2xx status."""

    def __init__(self, status_code: int, response_body: str):
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(f"HTTP {status_code}: {response_body}")


class WOOFiTimeoutError(WOOFiError):
    """Request timed out."""


class WOOFiPayloadError(WOOFiError):
    """Upstream response JSON parse failed."""


class WOOFiValidationError(WOOFiError):
    """Pydantic model validation failed."""
