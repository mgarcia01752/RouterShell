"""Runtime database path tests."""

from __future__ import annotations

from pathlib import Path

from routershell.lib.common.constants import ROUTER_SHELL_DB_FILE_ENV, ROUTER_SHELL_PROJECT_ROOT_ENV
from routershell.lib.db.sqlite_db.router_shell_db import RouterShellDB


def test_database_path_prefers_explicit_env(monkeypatch, tmp_path: Path) -> None:
    db_file = tmp_path / "state" / "routershell.db"

    monkeypatch.setenv(ROUTER_SHELL_DB_FILE_ENV, str(db_file))
    monkeypatch.setenv(ROUTER_SHELL_PROJECT_ROOT_ENV, str(tmp_path / "project"))

    assert RouterShellDB.default_db_file_path() == str(db_file)


def test_database_path_uses_project_root_runtime_dir(monkeypatch, tmp_path: Path) -> None:
    project_root = tmp_path / "project"

    monkeypatch.delenv(ROUTER_SHELL_DB_FILE_ENV, raising=False)
    monkeypatch.setenv(ROUTER_SHELL_PROJECT_ROOT_ENV, str(project_root))

    assert RouterShellDB.default_db_file_path() == project_root / ".routershell" / "routershell.db"
