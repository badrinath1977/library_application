from typing import Any


def build_success_response(data: Any = None, message: str = "Success") -> dict[str, Any]:
    return {
        "success": True,
        "message": message,
        "data": data,
        "error": None,
    }


def build_error_response(
    *,
    message: str,
    error_code: str,
    details: Any = None,
    correlation_id: str | None = None,
) -> dict[str, Any]:
    return {
        "success": False,
        "message": message,
        "data": None,
        "error": {
            "code": error_code,
            "message": message,
            "details": details,
            "correlation_id": correlation_id,
        },
    }
