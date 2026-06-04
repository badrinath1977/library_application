from typing import Any
import re


def mask_pii(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: mask_pii(item) for key, item in value.items()}

    if isinstance(value, list):
        return [mask_pii(item) for item in value]

    if not isinstance(value, str):
        return value

    value = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "***@***", value)
    value = re.sub(r"\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b", "***-**-****", value)
    value = re.sub(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", "***-***-****", value)
    value = re.sub(r"\b\d{13,19}\b", "****", value)
    return value
