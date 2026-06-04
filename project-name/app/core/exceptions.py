from typing import Any


class AppException(Exception):
    def __init__(
        self,
        message: str,
        *,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Any = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
        super().__init__(message)


class AuthenticationError(AppException):
    def __init__(self, message: str = "Authentication failed", details: Any = None) -> None:
        super().__init__(
            message,
            status_code=401,
            error_code="AUTHENTICATION_FAILED",
            details=details,
        )


class ValidationAppError(AppException):
    def __init__(self, message: str = "Validation failed", details: Any = None) -> None:
        super().__init__(
            message,
            status_code=422,
            error_code="VALIDATION_FAILED",
            details=details,
        )
