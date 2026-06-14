### Summary
Fixed GitHub Actions test failures caused by DB-backed imports falling back to `/var/lib/routershell` before tests selected a temporary SQLite database. The affected tests now set `ROUTERSHELL_DB_FILE` before importing modules that construct `RouterShellDB`, and the FAQ documents the failure mode.

### Modified Files
- tests/packaging/test_hostname_startup.py
- tests/packaging/test_interface_auto_discovery.py
- doc/faq.md
- todo.md

### Commands Executed And Results
- `gh auth status` -> pass, authenticated as `mgarcia01752` with repo/workflow scope.
- `gh run view 27508761793 --repo mgarcia01752/RouterShell --job 81304837393 --log` -> pass, showed 5 pytest failures with `PermissionError: [Errno 13] Permission denied: '/var/lib/routershell'`.
- `env -u ROUTERSHELL_DB_FILE /opt/routershell/venv/bin/python -m pytest tests/packaging/test_hostname_startup.py tests/packaging/test_interface_auto_discovery.py -q` -> pass, 8 passed.
- `env -u ROUTERSHELL_DB_FILE /opt/routershell/venv/bin/python -m pytest -q` -> pass, 60 passed.
- `/opt/routershell/venv/bin/python -m ruff check .` -> pass, all checks passed.
- `bash -n tools/vm/*.sh install/install.sh install/uninstall.sh tools/maintenance/clean.sh` -> pass.

### Tests
- `pytest` -> pass, 60 passed with `ROUTERSHELL_DB_FILE` unset in the outer environment.
- `ruff` -> pass, all checks passed.
- `bash -n` -> pass for VM, install, uninstall, and maintenance scripts.

### Notes / Warnings
- The failing GitHub job checked out the exact release commit correctly; this was a hermetic test setup issue, not a checkout issue.
- Tests importing DB-backed modules must set a temp `ROUTERSHELL_DB_FILE` before import because several DB wrapper classes instantiate `DB()` at class scope.

### Remaining TODOs / Follow-Ups
- Re-run the GitHub Actions matrix to confirm the CI runner no longer attempts to create `/var/lib/routershell` during tests.

# FILE: tests/packaging/test_hostname_startup.py
from __future__ import annotations

from pathlib import Path

TEST_DB_FILE_ENV = "ROUTERSHELL_DB_FILE"


def test_seed_hostname_db_from_os_populates_blank_database(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv(TEST_DB_FILE_ENV, str(tmp_path / "routershell.db"))

    from routershell.lib.common.constants import ROUTER_SHELL_DB_FILE_ENV, STATUS_OK
    from routershell.lib.common.singleton import Singleton
    from routershell.lib.db.interface_db import InterfaceDatabase
    from routershell.lib.db.sqlite_db.router_shell_db import RouterShellDB
    from routershell.lib.db.system_db import SystemDatabase
    from routershell.lib.system.system_call import SystemCall

    assert ROUTER_SHELL_DB_FILE_ENV == TEST_DB_FILE_ENV
    Singleton._instances.pop(RouterShellDB, None)
    RouterShellDB.connection = None
    RouterShellDB.connection_created = False
    SystemDatabase.rsdb = RouterShellDB()
    InterfaceDatabase.rsdb = SystemDatabase.rsdb

    system_call = SystemCall()
    monkeypatch.setattr(system_call, "get_hostname_os", lambda: "dev01")

    assert system_call.sys_db.get_hostname_db() is None
    assert system_call.seed_hostname_db_from_os() == STATUS_OK
    assert system_call.sys_db.get_hostname_db() == "dev01"


def test_startup_seeds_hostname_without_reconfiguring_existing_hostname(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv(TEST_DB_FILE_ENV, str(tmp_path / "routershell.db"))

    from routershell.lib.common.constants import STATUS_OK
    from routershell.lib.system.system_start_up import SystemStartUp

    seed_calls = []

    class FakeSystemCall:
        def seed_hostname_db_from_os(self) -> bool:
            seed_calls.append(True)
            return STATUS_OK

    monkeypatch.setattr(SystemStartUp, "fetch_db_interface_names", lambda self: ["enp1s0"])
    monkeypatch.setattr(SystemStartUp, "set_os_rename_interface", lambda self: STATUS_OK)
    monkeypatch.setattr(
        "routershell.lib.system.system_start_up.SystemCall",
        lambda: FakeSystemCall(),
    )
    monkeypatch.setattr(
        "routershell.lib.system.system_start_up.CopyStartRun",
        lambda: type("FakeCopyStartRun", (), {"read_start_config": lambda self: STATUS_OK})(),
    )

    SystemStartUp()

    assert seed_calls == [True]


def test_running_config_hostname_falls_back_to_os_hostname(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv(TEST_DB_FILE_ENV, str(tmp_path / "routershell.db"))

    from routershell.lib.cli.show.router_configuration import RouterConfiguration

    class FakeSystemDatabase:
        def get_hostname_db(self) -> None:
            return None

    class FakeSystemCall:
        def get_hostname_os(self) -> str:
            return "dev01"

    monkeypatch.setattr(
        "routershell.lib.cli.show.router_configuration.SystemDatabase",
        lambda: FakeSystemDatabase(),
    )
    monkeypatch.setattr(
        "routershell.lib.cli.show.router_configuration.SystemCall",
        lambda: FakeSystemCall(),
    )

    assert RouterConfiguration()._get_hostname() == ["hostname dev01"]

# FILE: tests/packaging/test_interface_auto_discovery.py
from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

TEST_DB_FILE_ENV = "ROUTERSHELL_DB_FILE"


def test_cli_entrypoint_enables_system_startup(monkeypatch) -> None:
    startup_values = []

    class FakeRouterCLI:
        def __init__(self, system_start_up: bool = False) -> None:
            startup_values.append(system_start_up)

        def run(self) -> None:
            return None

    fake_module = types.ModuleType("routershell.lib.cli.router_main_cli")
    fake_module.RouterCLI = FakeRouterCLI
    monkeypatch.setitem(sys.modules, "routershell.lib.cli.router_main_cli", fake_module)

    from routershell import cli

    assert cli.main([]) == 0
    assert startup_values == [True]


def test_cli_entrypoint_loads_config_file(monkeypatch, tmp_path: Path) -> None:
    startup_values = []
    config_files = []
    config_file = tmp_path / "lab-router.cfg"
    config_file.write_text("enable\nshow running-config\n")

    class FakeRouterCLI:
        def __init__(self, system_start_up: bool = False) -> None:
            startup_values.append(system_start_up)

        def run(self, config_file: Path | None = None) -> None:
            config_files.append(config_file)

    fake_module = types.ModuleType("routershell.lib.cli.router_main_cli")
    fake_module.RouterCLI = FakeRouterCLI
    monkeypatch.setitem(sys.modules, "routershell.lib.cli.router_main_cli", fake_module)

    from routershell import cli

    assert cli.main(["--config-file", str(config_file)]) == 0
    assert startup_values == [True]
    assert config_files == [config_file]


def test_cli_entrypoint_rejects_missing_config_file(monkeypatch, tmp_path: Path) -> None:
    startup_values = []
    missing_config_file = tmp_path / "missing.cfg"

    class FakeRouterCLI:
        def __init__(self, system_start_up: bool = False) -> None:
            startup_values.append(system_start_up)

    fake_module = types.ModuleType("routershell.lib.cli.router_main_cli")
    fake_module.RouterCLI = FakeRouterCLI
    monkeypatch.setitem(sys.modules, "routershell.lib.cli.router_main_cli", fake_module)

    from routershell import cli

    with pytest.raises(SystemExit) as error:
        cli.main(["--config-file", str(missing_config_file)])

    assert error.value.code == 2
    assert startup_values == []


def test_os_interface_discovery_uses_unprivileged_ip(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv(TEST_DB_FILE_ENV, str(tmp_path / "routershell.db"))

    from routershell.lib.network_manager.common.run_commands import RunResult
    from routershell.lib.network_manager.network_operations.interface import Interface

    commands = []
    iface = Interface()

    def fake_run(command: list[str], suppress_error: bool = False, shell: bool = False, sudo: bool = True) -> RunResult:
        commands.append((command, sudo))
        return RunResult(
            stdout=(
                "["
                '{"ifname": "lo", "link_type": "loopback"},'
                '{"ifname": "enp1s0", "link_type": "ether"},'
                '{"ifname": "wlp6s0", "link_type": "ether"}'
                "]"
            ),
            stderr="",
            exit_code=0,
            command=command,
        )

    monkeypatch.setattr(iface, "run", fake_run)
    monkeypatch.setattr(
        "routershell.lib.network_manager.network_operations.interface.os.path.isdir",
        lambda path: path.endswith("/wlp6s0/wireless"),
    )

    assert iface.get_os_network_interfaces() == ["enp1s0", "wlp6s0"]
    assert commands == [(["ip", "-json", "link", "show"], False)]


def test_blank_database_is_populated_from_os_interfaces(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv(TEST_DB_FILE_ENV, str(tmp_path / "routershell.db"))

    from routershell.lib.common.constants import ROUTER_SHELL_DB_FILE_ENV, STATUS_OK
    from routershell.lib.common.singleton import Singleton
    from routershell.lib.db.interface_db import InterfaceDatabase
    from routershell.lib.db.sqlite_db.router_shell_db import RouterShellDB
    from routershell.lib.network_manager.common.interface import InterfaceType
    from routershell.lib.network_manager.common.phy import State
    from routershell.lib.network_manager.network_operations.interface import Interface

    assert ROUTER_SHELL_DB_FILE_ENV == TEST_DB_FILE_ENV
    Singleton._instances.pop(RouterShellDB, None)
    RouterShellDB.connection = None
    RouterShellDB.connection_created = False
    InterfaceDatabase.rsdb = RouterShellDB()

    iface = Interface()
    monkeypatch.setattr(iface, "get_os_network_interfaces", lambda: ["enp1s0"])
    monkeypatch.setattr(iface, "get_os_interface_type_extened", lambda interface_name: InterfaceType.ETHERNET)

    shutdown_updates = []

    def fake_update_shutdown(interface_name: str, state: State) -> bool:
        shutdown_updates.append((interface_name, state))
        return STATUS_OK

    monkeypatch.setattr(iface, "update_shutdown", fake_update_shutdown)

    assert iface.fetch_db_interface_names() == []
    assert iface.update_interface_db_from_os() == STATUS_OK
    assert iface.fetch_db_interface_names() == ["enp1s0"]
    assert shutdown_updates == [("enp1s0", State.UP)]

    assert iface.update_interface_db_from_os() == STATUS_OK
    assert iface.fetch_db_interface_names() == ["enp1s0"]

# FILE: doc/faq.md
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright (c) 2026 Maurice Garcia -->

# RouterShell FAQ

## Python 3.10 CI fails with missing tomllib

If the Python 3.10 GitHub Actions job fails during `python -m pytest -q` with
this error:

```text
ModuleNotFoundError: No module named 'tomllib'
```

make sure RouterShell includes the Python 3.10 TOML backport dependency and
uses the compatibility import fallback:

```python
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
```

The `tomllib` module is built into Python 3.11 and newer. Python 3.10 needs
`tomli`, which is installed through the conditional `pyproject.toml`
dependency.

## Release CI checks out an ambiguous version ref

If every GitHub Actions matrix job fails at `python -m pytest -q` after a
release push, check whether a branch and tag share the same version name, such
as `v0.1.6`. Ambiguous release refs can make checkout behavior harder to
reason about.

RouterShell CI checks out the exact triggering commit SHA:

```yaml
ref: ${{ github.sha }}
```

Keep the workflow on Node 24-compatible action versions, such as
`actions/checkout@v5` and `actions/setup-python@v6`, so runner deprecation
warnings do not hide the real test failure.

## CI tests fail with permission denied for /var/lib/routershell

If GitHub Actions fails in `python -m pytest -q` with this error:

```text
PermissionError: [Errno 13] Permission denied: '/var/lib/routershell'
```

a test imported a RouterShell module that constructs a database object before
the test selected a temporary `ROUTERSHELL_DB_FILE`. Tests that import
DB-backed modules must set `ROUTERSHELL_DB_FILE` to a `tmp_path` database before
the import, because CI runners cannot create `/var/lib/routershell`.

## Install fails with setuptools InvalidConfigError

If `sudo ./install/install.sh --development` fails while getting editable
build requirements and reports this error:

```text
setuptools.errors.InvalidConfigError: License classifiers have been superseded by license expressions
```

Update RouterShell to a version whose `pyproject.toml` uses the SPDX
`license = "Apache-2.0"` expression without deprecated license classifiers,
then rerun the installer:

```bash
sudo ./install/install.sh --development
```

This error is raised by newer setuptools releases during package metadata
validation.

## VSCode reports unresolved RouterShell imports

If VSCode or Pylance reports unresolved imports for `routershell` or
`tools.release.qa_checker`, reload the VSCode window after opening the
RouterShell workspace. The workspace settings select the installed development
interpreter at `/opt/routershell/venv/bin/python` and add the project `src`
layout plus release tooling paths to Python analysis.

If command-line Pyright is also needed, reinstall development extras:

```bash
/opt/routershell/venv/bin/python -m pip install -e ".[dev]"
```

If VSCode reports a Pylint `E0401:import-error` for a RouterShell module such
as `routershell.lib.cli.base.clear_mode`, make sure the workspace is using the
RouterShell interpreter and reload VSCode. The workspace settings configure the
Pylint extension to run from `/opt/routershell/venv/bin/python` with the
project `src` layout on the import path.

If the Pylint extension reports that Pylint is missing, refresh development
dependencies in the installer-created virtual environment:

```bash
sudo /opt/routershell/venv/bin/python -m pip install -e ".[dev]"
```

## RouterShell fails with unable to open database file

If `routershell` exits during startup with this error:

```text
RouterShellDB - ERROR - Error: unable to open database file
AttributeError: 'NoneType' object has no attribute 'cursor'
```

the launcher is missing a writable `ROUTERSHELL_DB_FILE` setting or is using an
older install. Reinstall RouterShell so the launcher-loaded env file gets any
missing required keys and the installed package receives the current DB path
code:

```bash
sudo ./install/install.sh --development
```

For local/development installs, the default database path is
`.routershell/routershell.db` under the project root. For production installs,
the default path is `/var/lib/routershell/routershell.db`.

## Interface database is empty after install

`routershell` should seed the interface database during startup when the
database has no interface records. Start the CLI normally:

```bash
routershell
```

Then verify the discovered interfaces:

```text
show interface database
```

If the database is still empty, confirm that the launcher-loaded environment
file defines a writable `ROUTERSHELL_DB_FILE` path and reinstall with the
current installer.

## Running configuration shows hostname None

If `show running-config` displays this line:

```text
hostname None
```

the runtime database is missing a RouterShell hostname value. Current
RouterShell startup seeds the hostname database value from the operating system
when it is blank, and running configuration output falls back to the OS
hostname instead of rendering `None`.

Start RouterShell normally, then check the running configuration again:

```bash
routershell
```

```text
show running-config
```

# FILE: todo.md
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright (c) 2026 Maurice Garcia -->

# RouterShell TODO

- Keep Python-version compatibility troubleshooting notes current when CI
  compatibility errors are fixed.
- Keep release-ref troubleshooting notes current when CI checkout behavior
  changes.
- Keep CI database-path troubleshooting notes current when hermetic test setup
  changes.
- Keep install troubleshooting notes current when installer errors are fixed.
- Keep IDE import troubleshooting notes current when workspace settings change.
- Keep runtime database troubleshooting notes current when DB path handling changes.
- Keep runtime display troubleshooting notes current when CLI output renders missing DB values.

