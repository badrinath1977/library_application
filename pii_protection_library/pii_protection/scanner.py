from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from jsonpath_ng import parse
from jsonpath_ng.exceptions import JsonPathParserError

from pii_protection.exceptions import PiiConfigError


@dataclass(frozen=True)
class JsonPathMatch:
    path: Any
    value: Any


class JsonPathScanner:
    def find(self, payload: Any, json_path: str) -> list[JsonPathMatch]:
        try:
            expression = parse(json_path)
        except JsonPathParserError as exc:
            raise PiiConfigError(f"Invalid JSONPath: {json_path}") from exc
        return [JsonPathMatch(match.full_path, match.value) for match in expression.find(payload)]

    def update(self, payload: Any, match: JsonPathMatch, value: Any) -> None:
        match.path.update(payload, value)

    def drop(self, payload: Any, match: JsonPathMatch) -> None:
        match.path.filter(lambda _: True, payload)
