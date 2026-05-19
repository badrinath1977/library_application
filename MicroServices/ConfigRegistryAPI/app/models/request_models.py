from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AppConfigInsertRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    application_name: str = Field(alias="ApplicationName", min_length=1, max_length=200)
    environment_name: str = Field(alias="EnvironmentName", min_length=1, max_length=100)
    config_key: str = Field(alias="ConfigKey", min_length=1, max_length=300)
    config_value: str = Field(alias="ConfigValue", min_length=0)
    config_type: str | None = Field(default=None, alias="ConfigType", max_length=100)
    is_sensitive: bool = Field(default=False, alias="IsSensitive")
    is_active: bool = Field(default=True, alias="IsActive")
    description: str | None = Field(default=None, alias="Description", max_length=1000)
    created_by: str | None = Field(default=None, alias="CreatedBy", max_length=200)


class AppConfigUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    config_value: str = Field(alias="ConfigValue", min_length=0)
    config_type: str | None = Field(default=None, alias="ConfigType", max_length=100)
    is_sensitive: bool = Field(default=False, alias="IsSensitive")
    is_active: bool = Field(default=True, alias="IsActive")
    description: str | None = Field(default=None, alias="Description", max_length=1000)
    updated_by: str | None = Field(default=None, alias="UpdatedBy", max_length=200)


class AppConfigUpsertRequest(AppConfigInsertRequest):
    updated_by: str | None = Field(default=None, alias="UpdatedBy", max_length=200)


class AppConfigSetActiveRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    is_active: bool = Field(alias="IsActive")
    updated_by: str | None = Field(default=None, alias="UpdatedBy", max_length=200)

