"""Central logging configuration for RouterShell."""

from __future__ import annotations

import logging
import logging.config
import os
from pathlib import Path

from routershell.lib.common.types import FilePath, LoggerName, LogLevelName, PredicateResult, StatusResult

DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FILE = Path("/tmp/log/routershell.log")
DEFAULT_LOG_MAX_BYTES = 5 * 1024 * 1024
DEFAULT_LOG_BACKUP_COUNT = 5

LOG_LEVEL_ENV = "ROUTERSHELL_LOG_LEVEL"
LOG_FILE_ENV = "ROUTERSHELL_LOG_FILE"
LOG_CONSOLE_ENV = "ROUTERSHELL_LOG_CONSOLE"
LOG_FILE_ENABLED_ENV = "ROUTERSHELL_LOG_FILE_ENABLED"

_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}
_LEVELS = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "WARN": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "NOTSET": logging.NOTSET,
}


class RouterShellLogging:
    """Configure and retrieve RouterShell loggers."""

    @staticmethod
    def configure(
        level: LogLevelName = DEFAULT_LOG_LEVEL,
        log_file: FilePath = DEFAULT_LOG_FILE,
        console: bool = True,
        file_logging: bool = True,
    ) -> None:
        """Configure root logging for RouterShell runtime processes.

        Environment variables override the passed values:
        `ROUTERSHELL_LOG_LEVEL`, `ROUTERSHELL_LOG_FILE`,
        `ROUTERSHELL_LOG_CONSOLE`, and `ROUTERSHELL_LOG_FILE_ENABLED`.
        File logging uses a rotating handler and is skipped when the target
        directory cannot be created or written.
        """
        resolved_level = RouterShellLogging._resolve_level(os.getenv(LOG_LEVEL_ENV, level))
        resolved_file = Path(os.getenv(LOG_FILE_ENV, str(log_file)))
        resolved_console = RouterShellLogging._resolve_bool(os.getenv(LOG_CONSOLE_ENV), console)
        resolved_file_logging = RouterShellLogging._resolve_bool(os.getenv(LOG_FILE_ENABLED_ENV), file_logging)

        handlers: dict[str, dict[str, object]] = {}
        root_handlers: list[str] = []

        if resolved_console:
            handlers["console"] = {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": resolved_level,
            }
            root_handlers.append("console")

        if resolved_file_logging and RouterShellLogging._can_write_log_file(resolved_file):
            handlers["file"] = {
                "backupCount": DEFAULT_LOG_BACKUP_COUNT,
                "class": "logging.handlers.RotatingFileHandler",
                "encoding": "utf-8",
                "filename": str(resolved_file),
                "formatter": "default",
                "level": resolved_level,
                "maxBytes": DEFAULT_LOG_MAX_BYTES,
            }
            root_handlers.append("file")

        if not root_handlers:
            handlers["null"] = {
                "class": "logging.NullHandler",
                "level": resolved_level,
            }
            root_handlers.append("null")

        logging.config.dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "default": {
                        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    },
                },
                "handlers": handlers,
                "root": {
                    "handlers": root_handlers,
                    "level": resolved_level,
                },
            }
        )

    @staticmethod
    def get_logger(name: LoggerName) -> logging.Logger:
        """Return a named logger using RouterShell's logging configuration."""
        return logging.getLogger(name)

    @staticmethod
    def _resolve_level(level: LogLevelName) -> int:
        return _LEVELS.get(level.strip().upper(), _LEVELS[DEFAULT_LOG_LEVEL])

    @staticmethod
    def _resolve_bool(value: str | None, default: bool) -> StatusResult:
        if value is None:
            return default

        normalized = value.strip().lower()
        if normalized in _TRUE_VALUES:
            return True
        if normalized in _FALSE_VALUES:
            return False
        return default

    @staticmethod
    def _can_write_log_file(log_file: Path) -> PredicateResult:
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            with log_file.open("a", encoding="utf-8"):
                return True
        except OSError:
            return False


def configure_logging(
    level: LogLevelName = DEFAULT_LOG_LEVEL,
    log_file: FilePath = DEFAULT_LOG_FILE,
    console: bool = True,
    file_logging: bool = True,
) -> None:
    """Configure RouterShell logging with standard runtime defaults."""
    RouterShellLogging.configure(
        level=level,
        log_file=log_file,
        console=console,
        file_logging=file_logging,
    )


def get_logger(name: LoggerName) -> logging.Logger:
    """Return a RouterShell logger by name."""
    return RouterShellLogging.get_logger(name)
