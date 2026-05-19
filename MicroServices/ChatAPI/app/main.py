from __future__ import annotations

from contextlib import asynccontextmanager

import httpx
from enterprise_logging import initialize_logger, shutdown
from fastapi import FastAPI

from app.core.cache_manager import TTLCache
from app.core.settings import Settings, get_settings
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.correlation_middleware import CorrelationMiddleware
from app.middleware.exception_middleware import ExceptionMiddleware
from app.routes.chat_routes import router as chat_router
from app.routes.health_routes import router as health_router
from app.services.api_execution_service import ApiExecutionService
from app.services.audit_trace_service import AuditTraceService
from app.services.chat_orchestrator_service import ChatOrchestratorService
from app.services.config_client_service import ConfigClientService
from app.services.conversation_memory_service import ConversationMemoryService
from app.services.intent_service import IntentService
from app.services.llm_response_service import LlmResponseService


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
        app.state.cache = TTLCache(settings.default_cache_ttl_seconds)
        app.state.config_registry_client = httpx.AsyncClient(
            base_url=settings.config_registry_base_url,
            timeout=settings.config_registry_timeout_seconds,
        )
        app.state.downstream_client = httpx.AsyncClient(timeout=settings.http_timeout_seconds)
        app.state.config_client_service = ConfigClientService(app.state.config_registry_client, app.state.cache, settings)
        app.state.memory_service = ConversationMemoryService(settings)
        app.state.audit_trace_service = AuditTraceService(settings)
        app.state.chat_orchestrator = ChatOrchestratorService(
            config_client=app.state.config_client_service,
            memory_service=app.state.memory_service,
            intent_service=IntentService(),
            api_execution_service=ApiExecutionService(app.state.downstream_client),
            llm_response_service=LlmResponseService(),
            audit_trace_service=app.state.audit_trace_service,
        )
        yield
        await app.state.config_registry_client.aclose()
        await app.state.downstream_client.aclose()
        shutdown()

    app = FastAPI(
        title="ChatAPI",
        version=settings.app_version,
        description="Generic agentic orchestration API driven by ConfigRegistryAPI configuration.",
        lifespan=lifespan,
    )
    app.add_middleware(ExceptionMiddleware)
    app.add_middleware(AuthMiddleware, settings=settings)
    app.add_middleware(CorrelationMiddleware)
    app.include_router(health_router)
    app.include_router(chat_router)
    return app


app = create_app()

