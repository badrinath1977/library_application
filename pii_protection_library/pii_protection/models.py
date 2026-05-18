from __future__ import annotations

from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class PiiType(StrEnum):
    NAME = "NAME"
    FIRST_NAME = "FIRST_NAME"
    LAST_NAME = "LAST_NAME"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    SSN = "SSN"
    PAN = "PAN"
    AADHAAR = "AADHAAR"
    PASSPORT = "PASSPORT"
    DRIVER_LICENSE = "DRIVER_LICENSE"
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"
    BANK_ACCOUNT = "BANK_ACCOUNT"
    IBAN = "IBAN"
    IP_ADDRESS = "IP_ADDRESS"
    MAC_ADDRESS = "MAC_ADDRESS"
    DOB = "DOB"
    ADDRESS = "ADDRESS"
    ZIP_CODE = "ZIP_CODE"
    USERNAME = "USERNAME"
    PASSWORD = "PASSWORD"
    API_KEY = "API_KEY"
    ACCESS_TOKEN = "ACCESS_TOKEN"
    REFRESH_TOKEN = "REFRESH_TOKEN"
    FREE_TEXT = "FREE_TEXT"
    CUSTOM = "CUSTOM"


class PiiActionType(StrEnum):
    MASK = "MASK"
    PARTIAL_MASK = "PARTIAL_MASK"
    REDACT = "REDACT"
    DROP = "DROP"
    HASH = "HASH"
    TOKENIZE = "TOKENIZE"
    ENCRYPT = "ENCRYPT"
    FORMAT_PRESERVING_TOKENIZE = "FORMAT_PRESERVING_TOKENIZE"


class PiiAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: PiiActionType
    restore: bool = False
    params: dict[str, Any] = Field(default_factory=dict)


class RestorePolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    allowed_roles: set[str] = Field(default_factory=set, alias="allowedRoles")
    require_reason: bool = Field(default=False, alias="requireReason")
    audit: bool = True


class KeyConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key_provider: str = Field(default="ENV", alias="keyProvider")
    key1_ref: str | None = Field(default=None, alias="key1Ref")
    key2_ref: str | None = Field(default=None, alias="key2Ref")


class PiiRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    json_path: str = Field(alias="jsonPath")
    type: PiiType
    regex: str | None = None
    required: bool = False
    action: PiiAction

    @field_validator("name", "json_path")
    @classmethod
    def non_blank(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("value must not be blank")
        return value


class PiiConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    application: str
    version: str
    default_action: PiiAction = Field(
        default_factory=lambda: PiiAction(type=PiiActionType.TOKENIZE, restore=True),
        alias="defaultAction",
    )
    restore_policy: RestorePolicy = Field(default_factory=RestorePolicy, alias="restorePolicy")
    key_config: KeyConfig = Field(default_factory=KeyConfig, alias="keyConfig")
    rules: list[PiiRule] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_rule_names(self) -> PiiConfig:
        names = [rule.name for rule in self.rules]
        if len(names) != len(set(names)):
            raise ValueError("PII rule names must be unique")
        return self


class PiiRequestContext(BaseModel):
    application: str | None = None
    correlation_id: str = Field(default_factory=lambda: str(uuid4()), alias="correlationId")
    user_id: str | None = Field(default=None, alias="userId")
    roles: set[str] = Field(default_factory=set)
    reason: str | None = None
    request_id: str | None = Field(default=None, alias="requestId")
    tenant_id: str | None = Field(default=None, alias="tenantId")

    model_config = ConfigDict(populate_by_name=True)


class PiiItem(BaseModel):
    token: str
    type: PiiType
    json_path: str = Field(alias="jsonPath")
    action: PiiActionType

    model_config = ConfigDict(populate_by_name=True)


class PiiRestoredItem(BaseModel):
    token: str
    type: PiiType
    restored: bool


class PiiProtectedResult(BaseModel):
    protected_payload: Any = Field(alias="protectedPayload")
    correlation_id: str = Field(alias="correlationId")
    pii_items: list[PiiItem] = Field(default_factory=list, alias="piiItems")

    model_config = ConfigDict(populate_by_name=True)


class PiiRestoreResult(BaseModel):
    restored_payload: Any = Field(alias="restoredPayload")
    correlation_id: str = Field(alias="correlationId")
    restored_items: list[PiiRestoredItem] = Field(default_factory=list, alias="restoredItems")

    model_config = ConfigDict(populate_by_name=True)


class PiiMapping(BaseModel):
    original_value: str = Field(alias="originalValue")
    protected_value: str = Field(alias="protectedValue")
    type: PiiType
    json_path: str = Field(alias="jsonPath")
    action: PiiActionType
    restore_allowed: bool = Field(alias="restoreAllowed")
    expires_at: float | None = Field(default=None, alias="expiresAt")

    model_config = ConfigDict(populate_by_name=True)
