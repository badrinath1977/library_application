import pytest

from enterprise_logging.config.loader import load_config
from enterprise_logging.core.exceptions import LoggingConfigurationError
from enterprise_logging.core.types import LogLevel


def test_loads_defaults() -> None:
    config = load_config()

    assert config.enabled is True
    assert config.level == LogLevel.INFO
    assert config.outputs[0].type == "console"


def test_env_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOGGING_LEVEL", "DEBUG")
    monkeypatch.setenv("LOGGING_APPLICATION", "orders")
    monkeypatch.setenv("LOGGING_ASYNC_ENABLED", "false")

    config = load_config({"level": "INFO"})

    assert config.level == LogLevel.DEBUG
    assert config.metadata.application == "orders"
    assert config.async_.enabled is False


def test_runtime_overrides_win_over_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOGGING_LEVEL", "ERROR")

    config = load_config(overrides={"level": "TRACE"})

    assert config.level == LogLevel.TRACE


def test_invalid_config_rejected() -> None:
    with pytest.raises(LoggingConfigurationError):
        load_config({"outputs": [{"type": "file"}]})


def test_json_config_file(tmp_path) -> None:
    path = tmp_path / "logging.json"
    path.write_text('{"level":"WARN","outputs":[{"type":"console"}]}', encoding="utf-8")

    config = load_config(path)

    assert config.level == LogLevel.WARN
