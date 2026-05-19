from __future__ import annotations

from contextlib import asynccontextmanager

from enterprise_logging import initialize_logger, shutdown
from fastapi import FastAPI

from app.core.database import Database
from app.core.exception_handler import register_exception_handlers
from app.core.settings import Settings, get_settings
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.correlation_middleware import CorrelationMiddleware
from app.repositories.absence_repository import AbsenceRepository
from app.routes.absence_routes import router as absence_router
from app.routes.health_routes import router as health_router
from app.services.absence_service import AbsenceService


def _logging_config(settings: Settings) -> dict:
    outputs = [{"type": "console", "enabled": True, "format": settings.log_format}]
    if settings.log_file_path:
        outputs.append({"type": "file", "enabled": True, "format": "json", "path": settings.log_file_path})
    return {
        "level": settings.log_level,
        "format": settings.log_format,
        "outputs": outputs,
        "metadata": {
            "application": settings.app_name,
            "environment": settings.environment,
            "service": settings.service_name,
            "version": settings.app_version,
        },
        "masking": {"enabled": True},
        "async": {"enabled": True},
    }


def create_app() -> FastAPI:
    settings = get_settings()
    initialize_logger(_logging_config(settings))

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.settings = settings
        app.state.database = Database(settings)
        app.state.absence_repository = AbsenceRepository(app.state.database)
        app.state.absence_service = AbsenceService(app.state.absence_repository, settings)
        yield
        shutdown()

    app = FastAPI(
        title="AbsenceAPI",
        version=settings.app_version,
        description="Stored-procedure-only employee absence search API consumed by ChatAPI.",
        lifespan=lifespan,
    )
    app.add_middleware(AuthMiddleware, settings=settings)
    app.add_middleware(CorrelationMiddleware)
    register_exception_handlers(app)
    app.include_router(health_router)
    app.include_router(absence_router)
    return app


app = create_app()

