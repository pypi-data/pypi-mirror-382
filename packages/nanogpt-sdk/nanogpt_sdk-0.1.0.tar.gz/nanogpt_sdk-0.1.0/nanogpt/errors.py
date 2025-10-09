from typing import Optional

class APIError(Exception):
    """Generic API error for NanoGPT.

    Attributes:
        message: Human-readable message.
        status: HTTP status code.
        code: Optional API-specific error code.
    """
    def __init__(self, message: str, status_code: int, code: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.code = code

class RateLimitError(APIError):
    """Raised when HTTP 429 is returned."""
    pass

class AuthError(APIError):
    """Raised on HTTP 401 Unauthorized."""
    pass

class NotFoundError(APIError):
    """Raised on HTTP 404 Not Found."""
    pass