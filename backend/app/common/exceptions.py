"""
STTS Custom Exception Hierarchy
────────────────────────────────
Centralized exceptions for clean error propagation across layers.
"""


class STTSException(Exception):
    """Base exception for all STTS errors."""

    def __init__(self, message: str = "An unexpected error occurred", status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(STTSException):
    """Raised when a requested resource is not found."""

    def __init__(self, resource: str = "Resource", identifier: str = ""):
        detail = f"{resource} not found"
        if identifier:
            detail = f"{resource} with id '{identifier}' not found"
        super().__init__(message=detail, status_code=404)


class DuplicateException(STTSException):
    """Raised when attempting to create a duplicate resource."""

    def __init__(self, resource: str = "Resource", field: str = ""):
        detail = f"{resource} already exists"
        if field:
            detail = f"{resource} with this {field} already exists"
        super().__init__(message=detail, status_code=409)


class AuthenticationException(STTSException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message=message, status_code=401)


class AuthorizationException(STTSException):
    """Raised when user lacks permissions."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message=message, status_code=403)


class ValidationException(STTSException):
    """Raised when input validation fails at the service layer."""

    def __init__(self, message: str = "Validation error"):
        super().__init__(message=message, status_code=422)


class LLMServiceException(STTSException):
    """Raised when the LLM service is unavailable or returns an error."""

    def __init__(self, message: str = "AI service temporarily unavailable"):
        super().__init__(message=message, status_code=503)
