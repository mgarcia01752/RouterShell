from __future__ import annotations

import sys
import types
from pathlib import Path


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

    assert cli.main() == 0
    assert startup_values == [True]


def test_os_interface_discovery_uses_unprivileged_ip(monkeypatch) -> None:
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
    from routershell.lib.common.constants import ROUTER_SHELL_DB_FILE_ENV, STATUS_OK
    from routershell.lib.common.singleton import Singleton
    from routershell.lib.db.interface_db import InterfaceDatabase
    from routershell.lib.db.sqlite_db.router_shell_db import RouterShellDB
    from routershell.lib.network_manager.common.interface import InterfaceType
    from routershell.lib.network_manager.common.phy import State
    from routershell.lib.network_manager.network_operations.interface import Interface

    monkeypatch.setenv(ROUTER_SHELL_DB_FILE_ENV, str(tmp_path / "routershell.db"))
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
