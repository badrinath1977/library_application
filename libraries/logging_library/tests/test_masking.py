# ruff: noqa: S105

from libraries.logging_library.enterprise_logging.config.schema import MaskingConfig
from libraries.logging_library.enterprise_logging.masking.masker import SensitiveDataMasker
from libraries.logging_library.enterprise_logging.serializers.safe import SafeSerializer


def test_recursive_masking_is_immutable_and_handles_arrays() -> None:
    source = {
        "user": "alice",
        "password": "clear",
        "nested": {"accessToken": "abc", "items": [{"apiKey": "xyz"}]},
    }
    masker = SensitiveDataMasker(MaskingConfig())

    masked = masker.mask(source)

    assert source["password"] == "clear"
    assert masked["password"] == "***MASKED***"
    assert masked["nested"]["accessToken"] == "***MASKED***"
    assert masked["nested"]["items"][0]["apiKey"] == "***MASKED***"


def test_circular_references_are_safe() -> None:
    payload: dict[str, object] = {}
    payload["self"] = payload

    serialized = SafeSerializer().serialize(payload)
    masked = SensitiveDataMasker(MaskingConfig()).mask(payload)

    assert serialized["self"] == "[CircularReference]"
    assert masked["self"] == "[CircularReference]"


def test_authorization_header_pattern_masks_token() -> None:
    masker = SensitiveDataMasker(MaskingConfig())

    masked = masker.mask({"header": "Bearer abc.def.ghi"})

    assert masked["header"] == "Bearer ***MASKED***"
