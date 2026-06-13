"""Shared RouterShell type definitions."""

from __future__ import annotations

from pathlib import Path
from typing import NewType, TypeAlias

CommandArgs: TypeAlias = list[str]
EnvironmentMap: TypeAlias = dict[str, str]
FilePath: TypeAlias = str | Path
JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]
LogLevelName: TypeAlias = str

EpochSeconds = NewType("EpochSeconds", int)
InterfaceName = NewType("InterfaceName", str)
MacAddressText = NewType("MacAddressText", str)
InetAddressText = NewType("InetAddressText", str)
