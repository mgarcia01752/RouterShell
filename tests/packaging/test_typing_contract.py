"""RouterShell typing contract tests."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

from routershell.lib.common import types as rs_types
from routershell.lib.common.constants import ROUTERSHELL_DEFAULT_LOG_FILE, proc_ipv4_conf_path


def test_package_declares_pep561_typing_support() -> None:
    """RouterShell should ship a py.typed marker for type-aware consumers."""
    assert files("routershell").joinpath("py.typed").is_file()


def test_common_type_aliases_are_importable() -> None:
    """Shared RouterShell type aliases should be available from one module."""
    command: rs_types.CommandArgs = ["ip", "addr", "show"]
    log_path: rs_types.FilePath = ROUTERSHELL_DEFAULT_LOG_FILE
    payload: rs_types.JsonObject = {
        "command": command,
        "log_path": str(log_path),
        "ok": True,
    }

    assert command == ["ip", "addr", "show"]
    assert str(log_path) == "/tmp/log/routershell.log"
    assert payload["ok"] is True


def test_common_path_constants_are_importable() -> None:
    """Shared Linux path constants should be available from one module."""
    arp_path = proc_ipv4_conf_path(rs_types.InterfaceName("all"), "proxy_arp")

    assert arp_path == Path("/proc/sys/net/ipv4/conf/all/proxy_arp")
