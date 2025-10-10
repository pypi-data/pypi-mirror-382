"""
Custom exceptions for Ringmaster SDK
"""

class RingmasterError(Exception):
    """Base exception for all Ringmaster SDK errors"""
    pass


class AuthenticationError(RingmasterError):
    """Raised when authentication fails"""
    pass


class RateLimitError(RingmasterError):
    """Raised when rate limit is exceeded"""
    def __init__(self, message: str, retry_after: float = None):
        super().__init__(message)
        self.retry_after = retry_after


class SessionNotFoundError(RingmasterError):
    """Raised when session is not found"""
    pass


class SessionNotCompletedError(RingmasterError):
    """Raised when trying to get results for incomplete session"""
    pass


class ValidationError(RingmasterError):
    """Raised when request validation fails"""
    pass


class NetworkError(RingmasterError):
    """Raised on network-related failures"""
    pass


class TimeoutError(RingmasterError):
    """Raised when operation times out"""
    pass


class WebSocketError(RingmasterError):
    """Raised on WebSocket-related errors"""
    pass


class RetryExhaustedError(RingmasterError):
    """Raised when all retry attempts are exhausted"""
    pass