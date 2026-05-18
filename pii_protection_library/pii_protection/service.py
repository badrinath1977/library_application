from __future__ import annotations

import copy
import json
import re
import time
from typing import Any

from pii_protection.audit import AuditLogger, NoOpAuditLogger
from pii_protection.config_loader import PiiConfigLoader
from pii_protection.crypto.key_provider import EnvKeyProvider, KeyProvider
from pii_protection.exceptions import (
    PiiRestoreDeniedError,
    PiiValidationError,
)
from pii_protection.models import (
    PiiConfig,
    PiiItem,
    PiiMapping,
    PiiProtectedResult,
    PiiRequestContext,
    PiiRestoredItem,
    PiiRestoreResult,
)
from pii_protection.processors import PiiActionProcessorFactory
from pii_protection.scanner import JsonPathScanner
from pii_protection.store.base import PiiMappingStore
from pii_protection.store.memory import InMemoryPiiMappingStore
from pii_protection.validators import RegexValidator

TOKEN_PATTERN = re.compile(r"\{\{PII_[A-Z_]+_\d{3,}\}\}")


class PiiProtectionService:
    def __init__(
        self,
        *,
        mapping_store: PiiMappingStore | None = None,
        audit_logger: AuditLogger | None = None,
        key_provider: KeyProvider | None = None,
    ) -> None:
        self.mapping_store = mapping_store or InMemoryPiiMappingStore()
        self.audit_logger = audit_logger or NoOpAuditLogger()
        self.config_loader = PiiConfigLoader()
        self.scanner = JsonPathScanner()
        self.regex_validator = RegexValidator()
        self._key_provider = key_provider

    def protect(
        self,
        payload: str | dict[str, Any] | list[Any],
        config: str | dict[str, Any] | PiiConfig,
        context: PiiRequestContext | dict[str, Any] | None = None,
    ) -> PiiProtectedResult:
        pii_config = self.config_loader.load(config)
        request_context = self._context(context, pii_config)
        normalized, output_as_json_string = self._normalize_payload(payload)
        processor_factory = self._processor_factory(pii_config)
        pii_items: list[PiiItem] = []

        for rule in pii_config.rules:
            matches = self.scanner.find(normalized, rule.json_path)
            if rule.required and not matches:
                raise PiiValidationError(f"Required PII path not found: {rule.json_path}")
            for match in matches:
                if match.value is None:
                    continue
                original_value = str(match.value)
                if not self.regex_validator.validate(original_value, rule.regex):
                    raise PiiValidationError(f"Value for rule {rule.name} failed regex validation")
                processor = processor_factory.get_processor(rule.action.type)
                result = processor.protect(original_value, rule, request_context)
                if result.dropped:
                    self.scanner.drop(normalized, match)
                    protected_token = f"<{rule.type.value}_DROPPED>"
                else:
                    protected_token = str(result.protected_value)
                    self.scanner.update(normalized, match, protected_token)
                if result.reversible and result.protected_value:
                    expires_at = (
                        time.time() + result.ttl_seconds
                        if result.ttl_seconds and result.ttl_seconds > 0
                        else None
                    )
                    self.mapping_store.save(
                        request_context.correlation_id,
                        result.protected_value,
                        PiiMapping(
                            originalValue=original_value,
                            protectedValue=result.protected_value,
                            type=rule.type,
                            jsonPath=rule.json_path,
                            action=rule.action.type,
                            restoreAllowed=result.restore_allowed,
                            expiresAt=expires_at,
                        ),
                    )
                pii_items.append(
                    PiiItem(
                        token=protected_token,
                        type=rule.type,
                        jsonPath=rule.json_path,
                        action=rule.action.type,
                    )
                )

        self.audit_logger.audit(
            "pii.protect",
            request_context,
            {"application": pii_config.application, "items": len(pii_items)},
        )
        return PiiProtectedResult(
            protectedPayload=self._format_payload(normalized, output_as_json_string),
            correlationId=request_context.correlation_id,
            piiItems=pii_items,
        )

    def restore(
        self,
        payload: str | dict[str, Any] | list[Any],
        correlation_id: str,
        config: str | dict[str, Any] | PiiConfig,
        context: PiiRequestContext | dict[str, Any] | None = None,
    ) -> PiiRestoreResult:
        pii_config = self.config_loader.load(config)
        request_context = self._context(context, pii_config, correlation_id=correlation_id)
        self._authorize_restore(pii_config, request_context)
        mappings = self.mapping_store.find_all(correlation_id)
        normalized, output_as_json_string = self._normalize_restore_payload(payload)
        restored_items: list[PiiRestoredItem] = []

        if isinstance(normalized, str):
            restored_payload = normalized
            tokens = set(TOKEN_PATTERN.findall(restored_payload))
            tokens.update(
                mapping.protected_value
                for mapping in mappings
                if mapping.protected_value in restored_payload
            )
            for token in sorted(tokens, key=len, reverse=True):
                mapping = self.mapping_store.find(correlation_id, token)
                if mapping is None or not mapping.restore_allowed:
                    continue
                restored_payload = restored_payload.replace(token, mapping.original_value)
                restored_items.append(
                    PiiRestoredItem(token=token, type=mapping.type, restored=True)
                )
            final_payload: Any = restored_payload
        else:
            final_payload = copy.deepcopy(normalized)
            for mapping in mappings:
                replaced = self._replace_in_json(
                    final_payload,
                    mapping.protected_value,
                    mapping.original_value,
                )
                if replaced:
                    restored_items.append(
                        PiiRestoredItem(
                            token=mapping.protected_value,
                            type=mapping.type,
                            restored=True,
                        )
                    )
            final_payload = self._format_payload(final_payload, output_as_json_string)

        self.audit_logger.audit(
            "pii.restore",
            request_context,
            {"application": pii_config.application, "items": len(restored_items)},
        )
        return PiiRestoreResult(
            restoredPayload=final_payload,
            correlationId=correlation_id,
            restoredItems=restored_items,
        )

    def _processor_factory(self, pii_config: PiiConfig) -> PiiActionProcessorFactory:
        key_provider = self._key_provider or EnvKeyProvider(pii_config.key_config)
        return PiiActionProcessorFactory(key_provider)

    @staticmethod
    def _context(
        context: PiiRequestContext | dict[str, Any] | None,
        config: PiiConfig,
        *,
        correlation_id: str | None = None,
    ) -> PiiRequestContext:
        if isinstance(context, PiiRequestContext):
            data = context.model_dump(by_alias=True)
        else:
            data = dict(context or {})
        data.setdefault("application", config.application)
        if correlation_id is not None:
            data["correlationId"] = correlation_id
        return PiiRequestContext.model_validate(data)

    @staticmethod
    def _normalize_payload(payload: str | dict[str, Any] | list[Any]) -> tuple[Any, bool]:
        if isinstance(payload, str):
            return json.loads(payload), True
        return copy.deepcopy(payload), False

    @staticmethod
    def _normalize_restore_payload(payload: str | dict[str, Any] | list[Any]) -> tuple[Any, bool]:
        if not isinstance(payload, str):
            return copy.deepcopy(payload), False
        try:
            return json.loads(payload), True
        except json.JSONDecodeError:
            return payload, False

    @staticmethod
    def _format_payload(payload: Any, output_as_json_string: bool) -> Any:
        if output_as_json_string:
            return json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        return payload

    @staticmethod
    def _authorize_restore(config: PiiConfig, context: PiiRequestContext) -> None:
        policy = config.restore_policy
        if not policy.enabled:
            raise PiiRestoreDeniedError("Restore is disabled by policy")
        if policy.allowed_roles and not (policy.allowed_roles & context.roles):
            raise PiiRestoreDeniedError("Restore denied: user does not have an allowed role")
        if policy.require_reason and not context.reason:
            raise PiiRestoreDeniedError("Restore denied: reason is required")

    def _replace_in_json(self, value: Any, token: str, original: str) -> bool:
        replaced = False
        if isinstance(value, dict):
            for key, child in list(value.items()):
                if child == token:
                    value[key] = original
                    replaced = True
                elif isinstance(child, str) and token in child:
                    value[key] = child.replace(token, original)
                    replaced = True
                else:
                    replaced = self._replace_in_json(child, token, original) or replaced
        elif isinstance(value, list):
            for index, child in enumerate(value):
                if child == token:
                    value[index] = original
                    replaced = True
                elif isinstance(child, str) and token in child:
                    value[index] = child.replace(token, original)
                    replaced = True
                else:
                    replaced = self._replace_in_json(child, token, original) or replaced
        return replaced


_default_service = PiiProtectionService()


def protect(
    payload: str | dict[str, Any] | list[Any],
    config: str | dict[str, Any] | PiiConfig,
    context: PiiRequestContext | dict[str, Any] | None = None,
) -> PiiProtectedResult:
    return _default_service.protect(payload, config, context)


def restore(
    payload: str | dict[str, Any] | list[Any],
    correlation_id: str,
    config: str | dict[str, Any] | PiiConfig,
    context: PiiRequestContext | dict[str, Any] | None = None,
) -> PiiRestoreResult:
    return _default_service.restore(payload, correlation_id, config, context)
