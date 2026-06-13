"""Tests for RouterShell logging configuration."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from routershell.logging_config import (
    LOG_CONSOLE_ENV,
    LOG_FILE_ENABLED_ENV,
    LOG_FILE_ENV,
    LOG_LEVEL_ENV,
    configure_logging,
    get_logger,
)


def test_configure_logging_uses_rotating_file_handler(tmp_path, monkeypatch) -> None:
    """Default file logging should use a bounded rotating file handler."""
    log_file = tmp_path / "routershell.log"
    monkeypatch.setenv(LOG_FILE_ENV, str(log_file))
    monkeypatch.setenv(LOG_CONSOLE_ENV, "false")

    configure_logging()

    handlers = logging.getLogger().handlers
    assert len(handlers) == 1
    assert isinstance(handlers[0], RotatingFileHandler)

    logger = get_logger("routershell.test")
    logger.info("hello from test")

    assert log_file.exists()
    assert "hello from test" in log_file.read_text(encoding="utf-8")


def test_configure_logging_honors_env_level(tmp_path, monkeypatch) -> None:
    """The log level environment variable should control the root logger."""
    monkeypatch.setenv(LOG_FILE_ENV, str(tmp_path / "routershell.log"))
    monkeypatch.setenv(LOG_LEVEL_ENV, "DEBUG")
    monkeypatch.setenv(LOG_CONSOLE_ENV, "false")

    configure_logging()

    assert logging.getLogger().level == logging.DEBUG


def test_configure_logging_ignores_invalid_env_level(tmp_path, monkeypatch) -> None:
    """Invalid log levels should fall back to the default INFO level."""
    monkeypatch.setenv(LOG_FILE_ENV, str(tmp_path / "routershell.log"))
    monkeypatch.setenv(LOG_LEVEL_ENV, "LOUD")
    monkeypatch.setenv(LOG_CONSOLE_ENV, "false")

    configure_logging()

    assert logging.getLogger().level == logging.INFO


def test_configure_logging_is_idempotent(tmp_path, monkeypatch) -> None:
    """Repeated configuration should replace handlers instead of duplicating them."""
    monkeypatch.setenv(LOG_FILE_ENV, str(tmp_path / "routershell.log"))
    monkeypatch.setenv(LOG_CONSOLE_ENV, "false")

    configure_logging()
    configure_logging()

    assert len(logging.getLogger().handlers) == 1


def test_configure_logging_can_disable_file_logging(monkeypatch) -> None:
    """RouterShell should support console-only logging."""
    monkeypatch.setenv(LOG_FILE_ENABLED_ENV, "false")
    monkeypatch.setenv(LOG_CONSOLE_ENV, "true")

    configure_logging()

    handlers = logging.getLogger().handlers
    assert len(handlers) == 1
    assert isinstance(handlers[0], logging.StreamHandler)
    assert not isinstance(handlers[0], RotatingFileHandler)
