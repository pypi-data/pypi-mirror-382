"""
QDF SDK Exception classes
"""


class QDFError(Exception):
    """Base exception for QDF SDK"""
    pass


class APIError(QDFError):
    """API request failed"""
    def __init__(self, message: str, status_code: int = None, response_text: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class NetworkError(QDFError):
    """Network-related error (timeout, connection error, etc.)"""
    pass


class ValidationError(QDFError):
    """Data validation error"""
    pass


class NotFoundError(APIError):
    """Resource not found (404)"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class RateLimitError(APIError):
    """Rate limit exceeded"""
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after