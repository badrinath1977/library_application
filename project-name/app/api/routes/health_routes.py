from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.sqldbconnection import check_sql_database_connection
from app.utils.response_builder import build_error_response, build_success_response

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
async def health_check():
    settings = get_settings()
    return build_success_response(
        data={
            "status": "ok",
            "service": settings.service_name,
            "version": settings.api_version,
        },
        message="Service is healthy",
    )


@router.get("/db")
async def database_health_check():
    result = check_sql_database_connection()
    if result["connected"]:
        return build_success_response(data=result, message="Database connection is healthy")

    return JSONResponse(
        status_code=503,
        content=build_error_response(
            message="Database connection is unhealthy",
            error_code="DATABASE_HEALTH_CHECK_FAILED",
            details=result,
        ),
    )
