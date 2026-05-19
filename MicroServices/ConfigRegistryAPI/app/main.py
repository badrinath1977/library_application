from __future__ import annotations

from contextlib import asynccontextmanager

from enterprise_logging import initialize_logger, shutdown
from fastapi import FastAPI

from app.config.database import Database
from app.core.exception_handler import register_exception_handlers
from app.core.keyvault import initialize_keyvault_manager
from app.core.settings import Settings, get_settings
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.correlation_middleware import CorrelationMiddleware
from app.models.response_models import HealthResponse
from app.repositories.appconfig_repository import AppConfigRepository
from app.routes.appconfig_routes import router as appconfig_router
from app.services.appconfig_service import AppConfigService


def _logging_config(settings: Settings) -> dict:
    outputs = [{"type": "console", "enabled": True, "format": settings.log_format}]
    if settings.log_file_path:
        outputs.append(
            {
                "type": "file",
                "enabled": True,
                "format": "json",
                "path": settings.log_file_path,
                "rolling_policy": {
                    "max_bytes": 10485760,
                    "backup_count": 5,
                    "compression": False,
                },
            }
        )
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
        "async": {"enabled": True, "queue_size": 10000, "batch_size": 100},
    }


def create_app() -> FastAPI:
    settings = get_settings()
    initialize_logger(_logging_config(settings))

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.settings = settings
        app.state.database = Database(settings)
        app.state.appconfig_repository = AppConfigRepository(app.state.database)
        app.state.appconfig_service = AppConfigService(app.state.appconfig_repository, settings)
        app.state.keyvault_manager = initialize_keyvault_manager(settings)
        yield
        shutdown()

    app = FastAPI(
        title="ConfigRegistryAPI",
        version=settings.app_version,
        description=(
            "Stored-procedure-only registry service for GenAI.AppConfig. "
            "Protected routes require JWT bearer authentication."
        ),
        lifespan=lifespan,
    )

    app.add_middleware(AuthMiddleware, settings=settings)
    app.add_middleware(CorrelationMiddleware)
    register_exception_handlers(app, settings)
    app.include_router(appconfig_router)

    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    async def health() -> HealthResponse:
        return HealthResponse(
            status="healthy",
            service=settings.service_name,
            version=settings.app_version,
            environment=settings.environment,
        )

    @app.get("/live", response_model=HealthResponse, tags=["Health"])
    async def live() -> HealthResponse:
        return HealthResponse(
            status="live",
            service=settings.service_name,
            version=settings.app_version,
            environment=settings.environment,
        )

    @app.get("/ready", response_model=HealthResponse, tags=["Health"])
    async def ready() -> HealthResponse:
        return HealthResponse(
            status="ready",
            service=settings.service_name,
            version=settings.app_version,
            environment=settings.environment,
        )

    return app


app = create_app()
