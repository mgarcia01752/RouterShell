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
PredicateResult = NewType("PredicateResult", bool)
StatusResult = NewType("StatusResult", bool)

BridgeName: TypeAlias = str
ClientIdText: TypeAlias = str
ClientName: TypeAlias = str
CommandName: TypeAlias = str
DbTableName: TypeAlias = str
DbFilePath: TypeAlias = str | Path
DhcpPoolName: TypeAlias = str
DomainNameText: TypeAlias = str
EnvironmentVariableName: TypeAlias = str
EpochSeconds: TypeAlias = int
HostnameText: TypeAlias = str
InetAddressText: TypeAlias = str
InetCidrText: TypeAlias = str
InterfaceTypeName: TypeAlias = str
InterfaceName: TypeAlias = str
IpSetName: TypeAlias = str
LoggerName: TypeAlias = str
MacAddressText: TypeAlias = str
NatPoolName: TypeAlias = str
ServiceName: TypeAlias = str
SsidText: TypeAlias = str
VlanName: TypeAlias = str
WifiPassphraseText: TypeAlias = str
WifiPolicyName: TypeAlias = str
