from __future__ import annotations

from pathlib import Path


def test_seed_hostname_db_from_os_populates_blank_database(monkeypatch, tmp_path: Path) -> None:
    from routershell.lib.common.constants import ROUTER_SHELL_DB_FILE_ENV, STATUS_OK
    from routershell.lib.common.singleton import Singleton
    from routershell.lib.db.interface_db import InterfaceDatabase
    from routershell.lib.db.sqlite_db.router_shell_db import RouterShellDB
    from routershell.lib.db.system_db import SystemDatabase
    from routershell.lib.system.system_call import SystemCall

    monkeypatch.setenv(ROUTER_SHELL_DB_FILE_ENV, str(tmp_path / "routershell.db"))
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


def test_startup_seeds_hostname_without_reconfiguring_existing_hostname(monkeypatch) -> None:
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


def test_running_config_hostname_falls_back_to_os_hostname(monkeypatch) -> None:
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
