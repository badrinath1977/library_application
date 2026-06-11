from typing import Any, Mapping


class AppException(Exception):
    def __init__(
        self,
        message: str,
        *,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Any = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
        self.headers = dict(headers) if headers else None
        super().__init__(message)


class AuthenticationError(AppException):
    def __init__(self, message: str = "Authentication failed", details: Any = None) -> None:
        super().__init__(
            message,
            status_code=401,
            error_code="AUTHENTICATION_FAILED",
            details=details,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ValidationAppError(AppException):
    def __init__(self, message: str = "Validation failed", details: Any = None) -> None:
        super().__init__(
            message,
            status_code=422,
            error_code="VALIDATION_FAILED",
            details=details,
        )
