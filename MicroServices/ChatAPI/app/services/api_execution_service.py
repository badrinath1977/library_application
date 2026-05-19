from __future__ import annotations

import time
from string import Template
from typing import Any

import httpx

from app.models.config_models import ApiConfig
from app.models.response_models import ApiExecution


class DownstreamApiError(Exception):
    def __init__(self, api_execution: ApiExecution, message: str) -> None:
        super().__init__(message)
        self.api_execution = api_execution


class ApiExecutionService:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def execute(self, api: ApiConfig, parameters: dict[str, Any]) -> tuple[ApiExecution, Any]:
        method = api.method.upper()
        url = self._build_url(api, parameters)
        query = self._render_mapping(api.query_parameters, parameters)
        body = self._render_mapping(api.request_body_template or {}, parameters)
        headers = self._render_mapping(api.headers, parameters)
        request_payload = body if method not in {"GET", "DELETE"} else query
        started = time.perf_counter()
        status_code: int | None = None
        try:
            response = await self._client.request(
                method,
                url,
                params=query if method in {"GET", "DELETE"} else None,
                json=body if method not in {"GET", "DELETE"} else None,
                headers=headers,
                timeout=api.timeout,
            )
            status_code = response.status_code
            execution = self._execution(api, request_payload, status_code, started)
            if response.status_code >= 400:
                raise DownstreamApiError(execution, "Downstream API returned an error response.")
            return execution, self._response_payload(response)
        except httpx.HTTPError as exc:
            execution = self._execution(api, request_payload, status_code, started)
            raise DownstreamApiError(execution, str(exc)) from exc

    @staticmethod
    def _build_url(api: ApiConfig, parameters: dict[str, Any]) -> str:
        endpoint = Template(api.endpoint).safe_substitute(parameters)
        base = api.base_url.rstrip("/")
        return f"{base}/{endpoint.lstrip('/')}"

    @staticmethod
    def _render_mapping(template: Any, parameters: dict[str, Any]) -> Any:
        if isinstance(template, dict):
            return {key: ApiExecutionService._render_mapping(value, parameters) for key, value in template.items()}
        if isinstance(template, list):
            return [ApiExecutionService._render_mapping(value, parameters) for value in template]
        if isinstance(template, str):
            return Template(template).safe_substitute(parameters)
        return template

    @staticmethod
    def _response_payload(response: httpx.Response) -> Any:
        try:
            return response.json()
        except ValueError:
            return response.text

    @staticmethod
    def _execution(
        api: ApiConfig,
        request_payload: dict[str, Any] | None,
        status_code: int | None,
        started: float,
    ) -> ApiExecution:
        return ApiExecution(
            apiName=api.api_name,
            endpoint=api.endpoint,
            method=api.method.upper(),
            requestPayload=request_payload or {},
            statusCode=status_code,
            executionTimeMs=int((time.perf_counter() - started) * 1000),
        )

