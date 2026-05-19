from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar, Token
from typing import Any
from uuid import uuid4

_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)
_request_id: ContextVar[str | None] = ContextVar("request_id", default=None)
_context: ContextVar[dict[str, Any] | None] = ContextVar("logging_context", default=None)


def get_correlation_id() -> str | None:
    return _correlation_id.get()


def set_correlation_id(correlation_id: str | None) -> Token[str | None]:
    return _correlation_id.set(correlation_id)


def ensure_correlation_id() -> str:
    current = _correlation_id.get()
    if current:
        return current
    generated = str(uuid4())
    _correlation_id.set(generated)
    return generated


def get_request_id() -> str | None:
    return _request_id.get()


def set_request_id(request_id: str | None) -> Token[str | None]:
    return _request_id.set(request_id)


def get_context() -> dict[str, Any]:
    return dict(_context.get() or {})


def bind_context(**values: Any) -> Token[dict[str, Any] | None]:
    current = dict(_context.get() or {})
    current.update(values)
    return _context.set(current)


def reset_correlation_id(token: Token[str | None]) -> None:
    _correlation_id.reset(token)


def reset_request_id(token: Token[str | None]) -> None:
    _request_id.reset(token)


def reset_context(token: Token[dict[str, Any] | None]) -> None:
    _context.reset(token)


@contextmanager
def with_correlation_id(correlation_id: str) -> Iterator[None]:
    token = set_correlation_id(correlation_id)
    try:
        yield
    finally:
        reset_correlation_id(token)


@contextmanager
def request_context(
    *,
    correlation_id: str | None = None,
    request_id: str | None = None,
    **values: Any,
) -> Iterator[str]:
    correlation_token = set_correlation_id(correlation_id or str(uuid4()))
    request_token = set_request_id(request_id)
    context_token = bind_context(**values)
    try:
        yield _correlation_id.get() or ""
    finally:
        reset_context(context_token)
        reset_request_id(request_token)
        reset_correlation_id(correlation_token)
