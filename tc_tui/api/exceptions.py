"""API exception classes."""


class ThreatConnectAPIError(Exception):
    """Base exception for API errors."""

    def __init__(self, message: str, status_code: int = None, response_body: str = None):
        self.message = message
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(self.message)


class AuthenticationError(ThreatConnectAPIError):
    """Raised when authentication fails."""
    pass


class RateLimitError(ThreatConnectAPIError):
    """Raised when rate limit is exceeded."""
    pass


class NotFoundError(ThreatConnectAPIError):
    """Raised when resource is not found."""
    pass


class ValidationError(ThreatConnectAPIError):
    """Raised when request validation fails."""
    pass


class NetworkError(ThreatConnectAPIError):
    """Raised when network operation fails."""
    pass
