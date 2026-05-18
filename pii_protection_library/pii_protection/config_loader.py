from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from pii_protection.exceptions import PiiConfigError
from pii_protection.models import PiiConfig


class PiiConfigLoader:
    def load(self, config: str | Path | dict[str, Any] | PiiConfig) -> PiiConfig:
        if isinstance(config, PiiConfig):
            return config
        if isinstance(config, dict):
            return self._validate(config)
        if isinstance(config, Path):
            return self._load_path(config)
        text = str(config)
        path = Path(text)
        if path.exists():
            return self._load_path(path)
        try:
            return self._validate(json.loads(text))
        except json.JSONDecodeError as exc:
            raise PiiConfigError(
                "Config must be a PiiConfig, dict, JSON string, or file path"
            ) from exc

    def _load_path(self, path: Path) -> PiiConfig:
        try:
            return self._validate(json.loads(path.read_text(encoding="utf-8")))
        except OSError as exc:
            raise PiiConfigError(f"Unable to read PII config: {path}") from exc
        except json.JSONDecodeError as exc:
            raise PiiConfigError(f"PII config is not valid JSON: {path}") from exc

    @staticmethod
    def _validate(raw: dict[str, Any]) -> PiiConfig:
        try:
            return PiiConfig.model_validate(raw)
        except ValidationError as exc:
            raise PiiConfigError(str(exc)) from exc
