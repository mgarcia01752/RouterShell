### Summary
RouterShell semantic string arguments were refactored to use shared aliases from src/routershell/lib/common/types.py instead of bare str for public network/configuration values. CODING_AGENT.md now makes the semantic-argument rule explicit for public methods and meaningful private methods.

### Modified Files
- CODING_AGENT.md
- src/routershell/lib/cli/base/copy_start_run.py
- src/routershell/lib/cli/base/global_cmd_op.py
- src/routershell/lib/cli/base/global_operation.py
- src/routershell/lib/cli/common/router_prompt.py
- src/routershell/lib/cli/config-bak/bridge_config.py
- src/routershell/lib/cli/config-bak/configure_prompt.py
- src/routershell/lib/cli/config-bak/dhcp_server_config.py
- src/routershell/lib/cli/config-bak/if_config.py
- src/routershell/lib/cli/config-bak/vlan_config.py
- src/routershell/lib/cli/config/bridge/bridge_config.py
- src/routershell/lib/cli/config/bridge/bridge_config_cmd.py
- src/routershell/lib/cli/config/config_cmds.py
- src/routershell/lib/cli/config/configure_prompt.py
- src/routershell/lib/cli/config/dhcp/pool/dhcp_pool_config.py
- src/routershell/lib/cli/config/dhcp/pool/dhcp_pool_config_cmd.py
- src/routershell/lib/cli/config/ethernet/if_control-orig.py
- src/routershell/lib/cli/config/interface/if_control-orig.py
- src/routershell/lib/cli/show/dump_db_show.py
- src/routershell/lib/common/common.py
- src/routershell/lib/common/types.py
- src/routershell/lib/db/bridge_db.py
- src/routershell/lib/db/dhcp_client_db.py
- src/routershell/lib/db/dhcp_server_db.py
- src/routershell/lib/db/dhcpd_db-bak.py
- src/routershell/lib/db/interface_db.py
- src/routershell/lib/db/nat_db.py
- src/routershell/lib/db/router_config_db.py
- src/routershell/lib/db/sqlite_db/router_shell_db.py
- src/routershell/lib/db/system_db.py
- src/routershell/lib/db/vlan_db.py
- src/routershell/lib/db/wifi_db.py
- src/routershell/lib/network_manager/common/inet.py
- src/routershell/lib/network_manager/common/interface.py
- src/routershell/lib/network_manager/common/mac.py
- src/routershell/lib/network_manager/common/phy.py
- src/routershell/lib/network_manager/network_interfaces/bridge/bridge_factory.py
- src/routershell/lib/network_manager/network_interfaces/bridge/bridge_group_interface_abc.py
- src/routershell/lib/network_manager/network_interfaces/bridge/bridge_interface.py
- src/routershell/lib/network_manager/network_interfaces/create_loopback_net_interface.py
- src/routershell/lib/network_manager/network_interfaces/ethernet/ethernet_interface.py
- src/routershell/lib/network_manager/network_interfaces/loopback_interface.py
- src/routershell/lib/network_manager/network_interfaces/network_interface.py
- src/routershell/lib/network_manager/network_interfaces/network_interface_factory.py
- src/routershell/lib/network_manager/network_interfaces/vlan/vlan_mangement.py
- src/routershell/lib/network_manager/network_interfaces/vlan/vlan_switchport_interface_abc.py
- src/routershell/lib/network_manager/network_interfaces/wireless_wifi_interface.py
- src/routershell/lib/network_manager/network_operations/arp.py
- src/routershell/lib/network_manager/network_operations/bridge.py
- src/routershell/lib/network_manager/network_operations/dhcp/client/dhcp_client.py
- src/routershell/lib/network_manager/network_operations/dhcp/client/dhcp_clinet_interface_abc.py
- src/routershell/lib/network_manager/network_operations/dhcp/client/supported_dhcp_clients.py
- src/routershell/lib/network_manager/network_operations/dhcp/server/dhcp_server.py
- src/routershell/lib/network_manager/network_operations/hostapd_mgr.py
- src/routershell/lib/network_manager/network_operations/interface.py
- src/routershell/lib/network_manager/network_operations/nat.py
- src/routershell/lib/network_manager/network_operations/network_mgr.py
- src/routershell/lib/network_manager/network_operations/vlan.py
- src/routershell/lib/network_manager/network_operations/wireless_wifi.py
- src/routershell/lib/network_manager/network_operations/wireless_wifi_iw.py
- src/routershell/lib/network_services/dhcp/dnsmasq/dnsmasq.py
- src/routershell/lib/network_services/dhcp/dnsmasq/dnsmasq_config_gen.py
- src/routershell/lib/network_services/telnet/telnet_server.py
- src/routershell/lib/system/system.py
- src/routershell/lib/system/system_call.py
- src/routershell/lib/system/system_service_control/system_service_control.py
- src/routershell/logging_config.py

### Commands Executed And Results
- `/opt/routershell/venv/bin/ruff check .` -> pass; All checks passed
- `/opt/routershell/venv/bin/python -m pytest` -> pass; 11 passed
- `python3 -m py_compile $(find src/routershell -type f -name '*.py')` -> pass; all source files compiled
- `rg -n "\b\w*(?:name|Name|address|Address|interface|Interface|hostname|ssid|pool|subnet|cidr|file|service|table)\w*\s*:\s*str\b" src/routershell || true` -> pass; no semantic bare-str argument hits
- `rg -n "\b(inet_address|ip_address|mac_address|hw_address|hardware_address|interface_name|ifName|hostname|bridge_name|bridge_group|vlan_name|nat_pool_name|dhcp_pool_name|wifi_policy_name|ssid|domain|client_id): str\b" src/routershell || true` -> pass; no targeted semantic bare-str hits

### Tests
- `pytest` -> pass; 11 passed
- `ruff` -> pass; full project check passed
- `py_compile` -> pass; all RouterShell source files compiled

### Notes / Warnings
- Semantic aliases are type aliases for raw text values that are still validated by existing runtime code.
- Bare str remains acceptable for free-form text and local glue values per CODING_AGENT.md.

### Remaining TODOs / Follow-Ups
- Consider replacing selected aliases with validated value objects after call sites construct validated values consistently.

# FILE: CODING_AGENT.md
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright (c) 2026 Maurice Garcia -->

# AGENTS.md

This file provides guidance for coding agents working in this repository.
Keep it short, accurate, and updated when workflows change.

## Agent Permissions

<environment_context>
    <sandbox_mode>danger-full-access</sandbox_mode>
    <network_access>enabled</network_access>
    <!-- Access is governed by this file and explicit user approval -->
</environment_context>

## Project Basics

- Language: Python (3.10+)
- User shorthand: when Maurice says `RS`, treat it as `RouterShell`.
- This repo is NOT greenfield; extend existing code and patterns.
- Build/test entry points are defined in `pyproject.toml`, `Makefile`, or `scripts/`.
- Read `README.md` first for setup and usage.
- Type checking is strict; avoid `Any` and generic container types.
- Ruff compliance is required (do not auto-format unless explicitly requested).

## External Consumers (Compatibility Contract)

- BareMetalRouterOS may consume RouterShell through Yocto recipes and image builds.
- Preserve public CLI, package, and install behavior unless the user explicitly approves breaking changes.
- If a change affects downstream image integration, call out the cross-repo impact before making it.

## Repo Conventions

- RouterShell implementation code lives under `src/routershell/`.
- Runtime install tooling lives under `install/`.
- Development, release, VM, and operational helpers live under categorized `tools/` directories.
- Keep Linux host mutation workflows guarded, documented, and VM-tested where practical.

## Documentation

- Docs must follow the existing repo docs layout and conventions.
- Update docs alongside code changes (choose the correct location by inspecting the existing docs tree; do not invent parallel structures).
- Do not modify `mkdocs.yml` or navigation unless explicitly required by the task.
- Markdown must render correctly in both MkDocs and GitHub.
- No emojis in documentation.
- Use generic placeholders:
  - MAC: `aa:bb:cc:dd:ee:ff`
  - IP: `192.168.0.100`
- Emojis are allowed only in `install.sh`; they are prohibited everywhere else.
- When adding new terms or acronyms, update `docs/definition/index.md` and keep entries in alphabetical order.
- After completing a task, create a single “agent review” file that concatenates the full contents of all files changed in that task (path and naming should follow existing repo practice).
- Always regenerate the agent review bundle after any subsequent edits so it reflects every changed file.
- When an error is fixed, add or update a FAQ entry with the error and resolution, and add a TODO entry noting the FAQ update requirement.

### Reuse Index

- Agents MUST consult the existing reuse / symbol index under `tools/agent-review/` (if present) before introducing new:
  - types, validators, ID formats, storage conventions, persistence adapters, or config namespaces
- Any deviation requires an explicit gap justification and user approval.

## DB Backend Migration (Locked Decisions)

Agents working on the DB backend refactor MUST follow the locked decisions recorded in the design docs (see `docs/design/db/`):

- PyPNM owns persistence, schema initialization, and DB APIs.
- Install-time backend selection via `install.sh` flags + interactive default to SQLite.
- Postgres secrets via env var overrides (no plaintext requirement in tracked JSON).
- Idempotent schema apply using shipped DDL assets + seeding `UNKNOWN` sysDescr + default artifact store(s).
- SQLite for single-writer; Postgres recommended for multi-worker / multi-process (especially downstream orchestration use).
- Paths stored in DB are portable (app-root relative), resolved at runtime.
- CI validates SQLite (required) and Postgres (service container, recommended as required).
- JSON ledger persistence is deprecated and removed from runtime paths (optional offline migrator only).

## Configuration

- `system.json` is the single source of truth.
- New configuration namespaces must be implemented as Pydantic BaseModels.
- BaseModels must use one-line `Field(..., description="...")`.
- Avoid generic `str` for semantic identifiers or paths in public models and APIs; use existing RouterShell value objects or add a focused helper type under `src/routershell/lib/`.
- When working with MAC or inet strings, validate using `MacAddress()` or `Inet()` instead of assuming `str(...)` formatting is valid.
- Request override defaults: missing or null means use `system.json` defaults; blank strings are invalid.

## Timestamp Conventions

- All stored timestamps are epoch seconds.
- Convert to ISO-8601 only at display or external response boundaries.

## Coding Guidelines (Strict)

- No generic container imports (`Dict`, `List`, `Tuple`, `Union`).
  Use built-in types and `|`.
- RouterShell is a PEP 561 typed package; keep `src/routershell/py.typed`
  packaged and covered by tests.
- Shared RouterShell type aliases live in
  `src/routershell/lib/common/types.py`.
- Do not create competing type alias modules without explicit approval.
- Ruff follows the PyPNM direction: `F`, `E`, `W`, `I`, `B`, `UP`, `ANN`,
  `SIM`, and `PERF` are selected in `pyproject.toml`.
- Temporary Ruff ignores are allowed only for the existing legacy annotation
  and whitespace backlog; do not add new ignores without approval.
- Modern type syntax is mandatory in touched code: use `list`, `dict`,
  `tuple`, and `X | Y` rather than `List`, `Dict`, `Tuple`, or `Union`.
- Docstrings and comments must use the same modern type spellings so examples
  do not preserve legacy typing forms.
- Public method arguments must not use bare `str` for semantic RouterShell
  values such as interface names, inet addresses, MAC addresses, hostnames,
  bridge names, VLAN names, NAT pool names, DHCP pool names, Wi-Fi policy
  names, SSIDs, or paths. Use the shared aliases in
  `src/routershell/lib/common/types.py`.
- Private method arguments should use those shared semantic aliases when the
  value carries the same domain meaning. Bare `str` is acceptable only for
  genuinely free-form text, command output, log text, or local glue values.
- Avoid `Any` unless unavoidable; isolate and justify its usage.
- Every function argument must be annotated.
- Avoid `None` returns; prefer empty values unless `None` is semantically required.
- Avoid magic numbers; use named constants.
- Prefer `BaseModel` over raw dicts for public/stateful structures (state, configuration, persistence records).
- dicts are allowed only for short-lived internal glue logic.
- Prefer classes with static methods over standalone functions.
- Public methods MUST have detailed docstrings.
- Private methods may have minimal docstrings.
- Avoid method-level debug logs.
- Do not add Ruff ignores (`# noqa`, `# ruff: noqa`). If an ignore is needed, ask for permission first.
- Logging pattern in classes:

  ```python
  self.logger = logging.getLogger(f"{self.__class__.__name__}")
  ```

- Prefer `match/case` over long if/else chains.
- No code should contain 3+ nested loops. 2 nested loops are discouraged unless necessary.
- No one-line if statements (E701).
- Preserve all existing whitespace and alignment.
- Never auto-format or re-align code.
- Do not enforce snake_case; keep existing naming conventions as-is.

## FastAPI Guidelines (PyPNM)

- Router files must be lean:
  - `router.py` contains routing glue only (APIRouter configuration, endpoint registration, HTTP status translation).
  - No business logic in `router.py`. Business logic must live in `service.py` for that route group (same folder) or a shared service module if reused.
- All request/response bodies must be Pydantic BaseModels.
- Prefer POST for payload submission and endpoint contracts (PyPNM default).
  - Allow GET only where already present or clearly appropriate (health, readiness, version, status).
- Reuse shared models under the existing `src/pypnm/api/common/` structure (inspect current tree before adding anything new).
- Do not block request paths with `time.sleep()`.

## Tests (Mandatory)

- Every phase deliverable MUST include pytest coverage for new or changed behavior.
- Do not claim a phase item is complete unless pytest has been added and executed (or a concrete blocker is documented).
- Tests must remain hermetic: no live CMTS/cable modem dependencies.

## Burndown Governance

- Agents MUST consult the current burndown and DB design docs before implementing work.
- Agents MUST NOT update burndown checkmarks unless explicitly instructed by the user.
- Code written does not imply progress accepted.

## Workflow Rules

- When the user says “train”, read code silently until told otherwise.
- Do not assume missing context; ask.
- Keep changes minimal and scoped.
- Do not refactor unrelated code.
- Avoid destructive commands unless explicitly requested.
- Do not print file contents into chat unless the user explicitly requests it; ask first if unsure.
- Always end tasks with an agent review bundle containing the full contents of all files touched in the task.
- Agent review bundles must start with the standard summary template block below (before any `# FILE:` sections).
- When the user says `CAT_FILES`, create a single bundle file containing the full contents of every file touched in the task, each preceded by `# FILE: <path>`, and provide the `cat` command for the bundle.
- Keep a brief summary of user prompts after any request for a commit message and track changes since the most recent commit message request.
- When asked for a commit message, respond with the format below, keep it succinct, and include all changes since the last commit message request.
- Before changing version behavior or release tooling, review `tools/git/`, `tools/release/`, and `tools/support/bump_version.py` to avoid version-control drift.
- `tools/git/git-save.sh` is the normal save-commit path and accepts `--commit-msg "<commit-msg>"`.
- `tools/release/release.py` is the supported flow for committed release version updates, tags, and pushes.

## Commit Message Format

- If the chat request starts with `commit-msg`, use the message as the value for `./tools/git/git-save.sh --commit-msg "<commit-msg>"`.
- Always include the `./tools/git/git-save.sh --commit-msg` prefix when responding to commit-message requests.
- First line: one-line summary, maximum 50 characters.
- First line must start with one of: `Feature:`, `Bugfix:`, `Docs:`, `Refactor:`, `Test:`, `Tooling:`, `Release:`.
- Detailed description lines are maximum 72 characters per line.
- Every line after the first must start with `-`.
- When the user asks for a commit message, provide plain text for direct paste into the terminal or UI text box.
- Do not wrap commit message suggestions in quotes, backticks, or code fences unless the user explicitly asks for that format.
- Prefer detailed commit messages that describe the current change set clearly.
- Do not default to a one-line commit message when the change set is broad; provide a title plus concise bullet points.
- Avoid redundant wording and avoid repeating the exact prior commit message suggestion unless the diff is unchanged and the user explicitly asks to reuse it.
- If the user asks for "in a text box", return plain text only.
- If the user asks for "in a markdown text box", return the commit message inside a fenced code block with `text`.

### Agent Review Bundle Summary Template (Standard)

Use this Summary block at the very top of every `*.review.md` bundle (before any `# FILE:` sections).

### Summary
<1–3 sentences describing what changed and why. Keep it factual and phase-scoped.>

### Modified Files
- <absolute or repo-relative path 1>
- <path 2>
- <path N>

### Commands Executed And Results
- `<command 1>` → <result (pass/fail + key output)>
- `<command 2>` → <result>
- `<command N>` → <result>

### Tests
- `pytest` → <pass/fail + notes>
- `ruff` → <pass/fail + notes>
- <other> → <pass/fail + notes>

### Notes / Warnings
- <any relevant warnings, deprecations, expected exclusions, or operational notes>
- <or: None>

### Remaining TODOs / Follow-Ups
- <todo 1>
- <todo 2>
- <or: None>

## Repo Hygiene

- License is Apache-2.0; keep SPDX headers aligned with `LICENSE` and `NOTICE`.
- For any modified or newly created file, update the SPDX header year to 2026.
- If a file already has a SPDX year and the year has changed, update it as a range (example: 2025 -> 2025-2026).
- Keep implementation code inside `src/routershell/`; do not add loose root-level Python modules unless they are established project entry points or standard configuration files.
- Treat RouterShell as non-legacy code for packaging decisions; avoid compatibility shims that keep obsolete root-level modules alive unless Maurice explicitly approves them.
- Keep `tools/` organized by category.
- Do not add files directly under `tools/` root.

## Agent Self-Checks

Before responding:

- Re-read this file and `README.md`.
- Confirm pytest coverage exists or is explicitly blocked.
- Confirm pytest and ruff output have no deprecation warnings (treat as failures).
- Confirm changes align to the current phase and do not leak scope.
- Confirm formatting and alignment are preserved.

## Training

When the user requests "train", read the following sources:

- `AGENTS.md`
- `src/routershell/lib/` (RouterShell implementation modules)
- `tools/agent-review/` (all files, if present)

# FILE: src/routershell/lib/cli/base/copy_start_run.py
import logging

from routershell.lib.cli.common.router_prompt import PromptFeeder, RouterPrompt
from routershell.lib.cli.config.config import Configure
from routershell.lib.common.common import Common
from routershell.lib.common.constants import STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import FilePath


class CopyStartRunError(Exception):
    """
    Custom exception class for CopyStartRun errors.

    This exception is raised when there are issues with reading or processing the configuration files.
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class CopyStartRun(RouterPrompt):
    """
    A class that extends RouterPrompt to include functionality for copying and running startup configurations.

    This class initializes with the top-level commands registered for configuration and provides methods to read
    the startup configuration file.

    Attributes:
        None
    """

    def __init__(self):
        """
        Initializes the CopyStartRun class.

        Calls the superclass initializer and registers top-level commands from the Configure class.
        """
        super().__init__()
        RouterPrompt.__init__(self)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().COPY_START_RUN)
        
        self.register_top_lvl_cmds(Configure())

    def read_start_config(self, startup_config_fname: FilePath | None = None) -> bool:
        """
        Reads the startup configuration file and initializes the prompt feeder.

        This method attempts to read a startup configuration file from a specified path.
        If no file name is provided, it defaults to 'startup-config.cfg' located in the 'config'
        directory under the project's root directory. The method then processes the configuration
        file using PromptFeeder and initializes the system with the loaded configuration.

        Args:
            startup_config_fname (str, optional): The startup configuration file name.
                If None, the default 'startup-config.cfg' is used.

        Returns:
            bool: STATUS_OK on successful reading and initialization of the configuration file.
        """
        
        if not startup_config_fname:
            start_config_fname = 'startup-config.cfg'
        else:
            start_config_fname = startup_config_fname

        rs_path = Common.get_env('ROUTERSHELL_PROJECT_ROOT')
        prompt_file = f'{rs_path}/config/{start_config_fname}'

        pf = PromptFeeder(PromptFeeder.process_file(prompt_file))
        self.log.debug(f'{pf.__str__()}')
        self.start(pf)

        return STATUS_OK

# FILE: src/routershell/lib/cli/base/global_cmd_op.py
import logging
import os
import subprocess

from routershell.lib.cli.common.command_class_interface import CmdPrompt
from routershell.lib.cli.common.exec_priv_mode import ExecMode
from routershell.lib.common.common import STATUS_OK, Common
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import InterfaceName
from routershell.lib.network_manager.network_operations.interface import Interface
from routershell.lib.network_manager.network_operations.network_mgr import NetworkManager


class Global(CmdPrompt, NetworkManager):
    """
    Class representing global commands.
    """

    def __init__(self) -> None:
        """
        Initializes Global instance.
        """
        super().__init__(global_commands=True, exec_mode=ExecMode.USER_MODE)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().GLOBAL_MODE)
        
    def help(self) -> None:
        """
        Display help for available commands.
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            method_name_stripped = method_name.lstrip('_')
            print(f"{method.__doc__}")

    @CmdPrompt.register_sub_commands()         
    def global_end(self, args=None):
        """end\t\t\tend configuration"""
        raise SystemExit

    @CmdPrompt.register_sub_commands()  
    def global_exit(self, args=None):
        """exit\t\t\texit from current mode"""
        raise SystemExit
    
    @CmdPrompt.register_sub_commands()             
    def global_cls(self, args=None):
        """cls\t\t\tClear Screen"""
        print("\033[2J\033[H")       

    @CmdPrompt.register_sub_commands()     
    def global_clock(self, args=None):
        """clock\t\t\tShow clock"""
        
        print(Common.getclock("%H:%M:%S.%f PST %a %b %d %Y"))
        return False

    @CmdPrompt.register_sub_commands() 
    def global_reload(self, args=None) -> bool:
        confirmation = input("Are you sure you want to reboot? (yes/no): ")
        if confirmation.lower() == 'yes':
            reboot_command = Common.get_reboot_command()
            print(f"Using reboot command: {reboot_command}")
            os.system(reboot_command)
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands() 
    def global_version(self, args=None):
        """version\t\t\tGet version"""
        print("v1.0")
        return STATUS_OK

    @CmdPrompt.register_sub_commands()
    def global_ping(self, args=None):
        """ping\t\t\tping <IPv4 address>"""
        self.log.debug(f'ping: {args}')
        
        if isinstance(args, list):
            args = args[0]
        
        try:
            # Split the input args=None into individual arguments
            args = args.split()

            if len(args) < 1:
                print("Usage: ping <destination>")
                return False

            # Construct the ping command
            ping_command = ['ping', '-c', '4', args[0]]

            # Start the ping process in the background
            self.ping_process = subprocess.Popen(ping_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Read and print the output of the ping process
            while True:
                output_line = self.ping_process.stdout.readline()
                if not output_line:
                    break
                print(output_line.strip())

            # Wait for the ping process to complete
            self.ping_process.wait()

            return False  # Command executed successfully

        except Exception as e:
            print(f"Error: {e}")
            return False  # Command execution failed

    @CmdPrompt.register_sub_commands()
    def global_ping6(self, args=None):
        """ping6\t\t\tping6"""
        return False

    @CmdPrompt.register_sub_commands()        
    def global_traceroute(self, args=None):
        """traceroute\t\ttraceroute"""
        try:
            # Split the input args=None into individual arguments
            args = args.split()

            if len(args) < 1:
                print("Usage: traceroute <destination>")
                return False  # Command execution failed

            # Construct the traceroute command with the '-n' option to disable DNS resolution
            traceroute_command = ['traceroute', '-n'] + args

            # Execute the traceroute command and capture the output
            traceroute_output = subprocess.run(traceroute_command, capture_output=True, text=True)

            if traceroute_output.returncode == 0:
                # Print the traceroute results
                print(traceroute_output.stdout)
                return True  # Command executed successfully
            else:
                print(f"Error executing 'traceroute' command: {traceroute_output.stderr}")
                return False  # Command execution failed

        except Exception as e:
            print(f"Error: {e}")
            return False  # Command execution failed
        
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=Interface().get_os_network_interfaces())       
    def global_flush(self, interface_name: InterfaceName) -> bool:
        """
        Command to flush the configuration of a network interface.

        This command allows the user to flush the configuration of a network interface,
        effectively removing all assigned IP addresses and resetting the interface.

        Args:
            interface_name (str): The name of the network interface to flush.

        Usage:
            flush <interface_name>

        Example:
            flush eth0
        """
        self.log.debug(f'global_flush() -> interface: {interface_name}')

        # TODO
        #if self.get_exec_mode() != ExecMode.PRIV_MODE:
        #    print(f"Unable to flush, must be in Privilege Mode")
        #    return
                
        return self.flush_interface(interface_name[0])
    
    @CmdPrompt.register_sub_commands()
    def global_shell(self, args=None):
        """
        Open an interactive bash shell session through the SystemCall class.

        This method creates an instance of the SystemCall class and calls its `shell` method 
        to open an interactive bash shell session. It catches any exceptions that occur 
        during the execution and prints an error message.
        """
        print('shell not implemented yet')
        pass
        
        
        

# FILE: src/routershell/lib/cli/base/global_operation.py
import argparse
import os
import subprocess

import parser
from bs4 import Comment

from routershell.lib.cli.common.exec_priv_mode import ExecMode
from routershell.lib.common.common import Common
from routershell.lib.common.types import InterfaceName
from routershell.lib.network_manager.network_operations.network_mgr import NetworkManager


class GlobalPrivCommand(NetworkManager):

    def __init__(self):
        super().__init__()
        
    def do_reboot(self, args=None):
        '''
        Reboot the system.
        
        Args:
            line (str): Additional arguments (not used).
        
        Returns:
            bool: False if reboot is canceled, otherwise returns False.
        '''
        
        if self.get_exec_mode() != ExecMode.PRIV_MODE:
            print("Unable to reboot, must be in Privilege Mode")
            return
        
        try:
            args = parser.parse_args(args.split())
        except SystemExit:
            return
        
        if args.force:
            # Add logic for a forced reboot here
            print("Forced Rebooting...")
        else:
            confirmation = input("Are you sure you want to reboot? (yes/no): ")
            if confirmation.lower() == 'yes':
                reboot_command = Common.get_reboot_command()
                print(f"Using reboot command: {reboot_command}")
                os.system(reboot_command)  # Execute the selected reboot command
            else:
                print("Reboot canceled.")
        
    def do_flush(self, interface_name: InterfaceName):
        """
        Command to flush the configuration of a network interface.

        This command allows the user to flush the configuration of a network interface,
        effectively removing all assigned IP addresses and resetting the interface.

        Args:
            interface_name (str): The name of the network interface to flush.

        Usage:
            flush <interface_name>

        Example:
            flush eth0
        """
        if self.get_exec_mode() != ExecMode.PRIV_MODE:
            print("Unable to flush, must be in Privilege Mode")
            return
                
        self.flush_interface(interface_name)

    def do_adduser(self, args=None):
        '''
        Add a user (implementation pending).
        
        Args:
            args=None (str): Additional arguments (not used).
        
        Returns:
            bool: False (implementation pending).
        '''
        if self.get_exec_mode() != ExecMode.PRIV_MODE:
            print("Unable to add user, must be in Privilege Mode")
            return
                
        return False
    
    def do_deluser(self, args=None):
        '''
        Delete a user (implementation pending).
        
        Args:
            args=None (str): Additional arguments (not used).
        
        Returns:
            bool: False (implementation pending).
        '''
        if self.get_exec_mode() != ExecMode.PRIV_MODE:
            print("Unable to delete user, must be in Privilege Mode")
            return
        return False
    
    def set_prompt_prefix(self, prefix: str):
        ''' 
                    Add a prefix to the command prompt, typically the hostname.

                    Args:
                        prefix (str): The prefix to be added to the prompt.

                    Returns:
                        str: The updated command prompt string.
        '''
        
        self.prompt_prefix = prefix

class GlobalUserCommand:

    def __init__(self, args=None):
        pass

    def do_end(self, args=None):
        '''
        Drop from top to lower level
        '''
        raise SystemExit
                
    def do_cls(self, args=None):
        """
        Clear the screen (console).
        
        Args:
            arg (str, optional): Additional arguments (not used).
        
        Returns:
            None
        """
        parser = argparse.ArgumentParser(description="Clear the screen",
                                         epilog="")
        
        try:
            args = parser.parse_args(args.split())
        except SystemExit:
            # In this case, just return without taking any action.
            return
        
        if os.name == 'posix':  # Unix/Linux/Mac
            os.system('clear')

    def do_clock(self, args=None):
        '''
        Display the current system time.
        
        Args:
            line (str): Additional arguments (not used).
        
        Returns:
            bool: Always returns False.
        '''
        
        print(Comment.getclock("%H:%M:%S.%f PST %a %b %d %Y"))
        return False
    
    def do_reload(self, args=None):
        '''
        Reload the system (alias for 'do_reboot').
        
        Args:
            args=None (str): Additional arguments (not used).
        
        Returns:
            bool: False if reboot is canceled, otherwise returns False.
        '''
        self.do_reboot(args=None)
        return False

    def do_version(self, args=None):
        '''
        Show version of RouterCLI.
        
        Args:
            args=None (str): Additional arguments (not used).
        
        Returns:
            bool: False.
        '''
        if len(args=None.split()) < 1:
            print("Takes no arguments")
            return False
        print("v1.0")
        return False
    
    def do_ping(self, args=None):
        '''
        Ping a destination.
        
        Args:
            args=None (str): The destination to ping.
        
        Returns:
            bool: True if the ping is successful, otherwise False.
        '''
        try:
            # Split the input args=None into individual arguments
            args = args.split()

            if len(args) < 1:
                print("Usage: ping <destination>")
                return False

            # Construct the ping command
            ping_command = ['ping', '-c', '4', args[0]]

            # Start the ping process in the background
            self.ping_process = subprocess.Popen(ping_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Read and print the output of the ping process
            while True:
                output_line = self.ping_process.stdout.readline()
                if not output_line:
                    break
                print(output_line.strip())

            # Wait for the ping process to complete
            self.ping_process.wait()

            return False  # Command executed successfully

        except Exception as e:
            print(f"Error: {e}")
            return False  # Command execution failed
    
    def do_ping6(self, args=None):
        '''
        Ping a destination using IPv6.
        
        Args:
            args=None (str): The destination to ping.
        
        Returns:
            bool: False (implementation pending).
        '''
        return False
        
    def do_traceroute(self, args=None):
        '''
        Perform a traceroute to a destination.
        
        Args:
            args=None (str): The destination to trace.
        
        Returns:
            bool: True if the traceroute is successful, otherwise False.
        '''
        try:
            # Split the input args=None into individual arguments
            args = args.split()

            if len(args) < 1:
                print("Usage: traceroute <destination>")
                return False  # Command execution failed

            # Construct the traceroute command with the '-n' option to disable DNS resolution
            traceroute_command = ['traceroute', '-n'] + args

            # Execute the traceroute command and capture the output
            traceroute_output = subprocess.run(traceroute_command, capture_output=True, text=True)

            if traceroute_output.returncode == 0:
                # Print the traceroute results
                print(traceroute_output.stdout)
                return True  # Command executed successfully
            else:
                print(f"Error executing 'traceroute' command: {traceroute_output.stderr}")
                return False  # Command execution failed

        except Exception as e:
            print(f"Error: {e}")
            return False  # Command execution failed



# FILE: src/routershell/lib/cli/common/router_prompt.py
import logging
from time import sleep

from common.common import Common
from prompt_toolkit import PromptSession
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.history import InMemoryHistory

from routershell.lib.cli.common.command_class_interface import CmdPrompt
from routershell.lib.cli.common.exec_priv_mode import ExecMode
from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.string_formats import StringFormats
from routershell.lib.common.types import CommandName, FilePath
from routershell.lib.system.system_call import SystemCall


class PromptFeeder:
    """
    A class to manage and simulate feeding prompts.

    This class is designed to handle a list of prompt commands or inputs,
    allowing them to be processed sequentially.

    Attributes:
        prompt_feed (list[list[str]]): The initial list of prompts/commands.
        start_length (int): The length of the initial prompt feed.

    Methods:
        pop() -> bool:
            Removes the top entry from the prompt feed.
        top() -> list[str]:
            Returns the top entry from the prompt feed without removing it.
        length() -> int:
            Returns the current length of the prompt feed.
        get_start_length() -> int:
            Returns the initial length of the prompt feed.
        next() -> list[str]:
            Returns and removes the top entry from the prompt feed.
    """
    @staticmethod
    def process_file(file_path: FilePath) -> list[list[str]]:
        """
        Processes a file and creates a nested list where each line is a list,
        and each word in the line is a string.

        Args:
            file_path (str): The path to the input file.

        Returns:
            list[list[str]]: The processed nested list.
        """
        nested_list = []

        try:
            with open(file_path) as file:
                for line in file:
                    line_list = [word for word in line.strip().split()]
                    nested_list.append(line_list)
                            
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")

        return nested_list
    
    def __init__(self, prompt_feed: list[list[str]] = []):
        """
        Initializes the PromptFeed with a list of prompts/commands.

        Args:
            prompt_feed (list[list[str]]): The initial list of prompts/commands.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().PROMPT_FEEDER)
                
        self.prompt_feed = prompt_feed[:]
        self.start_length = len(self.prompt_feed)

    def pop(self) -> bool:
        """
        Removes the top entry from the prompt feed.

        Returns:
            bool: STATUS_OK if the operation is successful.
        """
        if self.prompt_feed:
            self.prompt_feed.pop(0)
        return STATUS_OK

    def top(self) -> list[str]:
        """
        Returns the top entry from the prompt feed without removing it.

        Returns:
            list[str]: The top entry or an empty list if the prompt feed is empty.
        """
        if self.prompt_feed:
            return self.prompt_feed[0]
        return []

    def length(self) -> int:
        """
        Returns the current length of the prompt feed.

        Returns:
            int: The current length of the prompt feed.
        """
        return len(self.prompt_feed)

    def get_start_length(self) -> int:
        """
        Returns the initial length of the prompt feed.

        Returns:
            int: The initial length of the prompt feed.
        """
        return self.start_length

    def next(self) -> list[str]:
        """
        Returns and removes the top entry from the prompt feed.

        Returns:
            list[str]: The top entry from the prompt feed, or an empty list if the prompt feed is empty.
        """
        if self.prompt_feed:
            return self.prompt_feed.pop(0)
        return []

    def __str__(self) -> str:
        """
        Returns a string representation of the PromptFeed object.

        Returns:
            str: A string representation of the PromptFeed object.
        """
        return f"PromptFeed(start_length={self.start_length}, current_length={len(self.prompt_feed)}, top_entry={self.top()})"

class RouterPromptError(Exception):
    """
    Custom exception class for RouterPrompt errors.

    This exception is raised when there are issues RouterPrompt.
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class RouterPrompt:
    """
    Class for managing router prompt session.
    """
    USER_MODE_PROMPT = '>'
    PRIV_MODE_PROMPT = '#'
  
    PROMPT_PARTS_CMD = 0
    PROMPT_PARTS_IF = 1
    PROMPT_MAX_LENGTH = 2

    DEF_PREFIX_START = ""
    DEF_START_HOSTNAME = "RouterShell"
    DEF_CONFIG_MODE_PROMPT = 'config'
    DEF_NO_CONFIG_MODE_PROMPT = None
    PREFIX_SEP = ':'
    
    PROMPT_REMARK_SYMBOL = [';', '!']
    
    #Create an shared empty object
    _prompt_feeder_obj = PromptFeeder([])
    
    #Keep track of user execute mode
    _current_execute_mode = ExecMode.USER_MODE
    
    def __init__(self, exec_mode: ExecMode = ExecMode.USER_MODE, 
                 sub_cmd_name: CommandName | None = None) -> None:
        """
        Initializes RouterPromptSession instance.
        """
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().ROUTER_PROMPT)
         
        self._register_top_lvl_cmds = {}
        self._command_dict_completer = {'enable':{}}
        
        self.execute_mode = exec_mode
        self.SUB_CMD_START = sub_cmd_name
        
        self.completer = NestedCompleter.from_nested_dict({'FAKE':{}})
        self.history = InMemoryHistory()
        self.session = PromptSession(completer=self.completer, history=self.history)

        self.hostname = Common.getHostName()
            
        '''Start Prompt Router>'''
        self._prompt_dict = {
            'Hostname' : self.DEF_START_HOSTNAME,
            'ConfigMode' : self.DEF_CONFIG_MODE_PROMPT,
            'ExecModePrompt' : self.USER_MODE_PROMPT
        }

        if (Common.getHostName() is None):
            self.hostname = self.DEF_START_HOSTNAME

        self.update_prompt()

    def prompt_feeder_length(self) -> int:
        """
        Get the length of the prompt feeder.

        Returns:
            int: The length of the prompt feeder.
        """
        return RouterPrompt._prompt_feeder_obj.length()
    
    def get_prompt_feeder(self) -> PromptFeeder | None:
        """
        Get the current prompt feeder.

        Returns:
            PromptFeeder | None: The current prompt feeder if available, otherwise None.
        """
        return RouterPrompt._prompt_feeder_obj
    
    def load_prompt_feeder(self, pf: PromptFeeder) -> bool:
        """
        Load a new prompt feeder.

        Args:
            pf (PromptFeeder):  The new prompt feeder to load. 

        Returns:
            bool: STATUS_OK if the prompt feeder is successfully loaded, STATUS_NOK otherwise.
        """
        if not isinstance(pf, PromptFeeder):
            return False
        
        RouterPrompt._prompt_feeder_obj = pf
        if RouterPrompt._prompt_feeder_obj.length() < 0:
            return STATUS_NOK
        
        return STATUS_OK
        
    def intro(self) -> str:
        return ""
         
    def rs_prompt(self, 
                  split: bool=True, 
                  ws_trim_lead: bool=True,
                  ws_reduce: bool=True) -> list[str] | str:
        """
        Displays router prompt and returns user input.

        Args:
            split (bool, optional): Whether to split the output. Defaults to False.

        Returns:
            str or list: User input from the prompt. If split is True, returns a list of words.
        """
        self.update_prompt()
        
        _ = self.session.prompt(f'{self.get_prompt()}',
                                completer=self.completer, 
                                complete_in_thread=False)
        
        # Check if the input contains any remark symbols, if so, skip line
        if any(_.startswith(symbol) for symbol in RouterPrompt.PROMPT_REMARK_SYMBOL):
            return []
        
        if ws_trim_lead:
            _.lstrip()
            
        if ws_reduce:
            _ = StringFormats.reduce_ws(_)
        
        if _.split(' ')[0] == 'enable':
            self.execute_mode = ExecMode.PRIV_MODE
            self.update_prompt()
            return ''
        
        if not split:
            return _
                    
        return _.split(' ')

    def register_top_lvl_cmds(self, class_name: CmdPrompt) -> bool:
        """
        Register top-level commands for the router prompt session.

        Args:
            class_name (Type): Class containing top-level commands.
            class_nested_cmds (bool, optional): Whether the commands are nested or not. Defaults to False.
        
        Returns:
            bool: Status indicating whether the registration was successful.
        """
        self.log.debug(f'register_top_lvl_cmds() -> {class_name}')
        
        cmd_list = class_name.get_command_list()
        due_to_global = True
        
        for cmd in cmd_list:

            if not class_name.isGlobal():
                cmd = class_name.getClassStartCmd() + '_' + cmd
                due_to_global = False
            
            self.log.debug(f'Top-Level-Cmd: {cmd}\tClass: {class_name}')
                        
            self._register_top_lvl_cmds[cmd] = class_name
            
            cmd_dict = class_name.get_command_dict(skip_top_key=due_to_global)
            
            self._command_dict_completer.update(cmd_dict)
        
        # This populates the tab completions    
        self.completer = NestedCompleter.from_nested_dict(self._command_dict_completer)

        return STATUS_OK

    def update_prompt(self) -> str:
        '''
        Update the router command prompt based on the current configuration mode and optional interface name.

        Returns:
            str: The formatted command prompt string.
        '''
        self.log.debug(f"update_prompt() -> Execute-Mode: {self.execute_mode}")
        
        self.update_prompt_hostname()        
        self.prompt_parts = [self._prompt_dict['Hostname']]
                
        if self.execute_mode is ExecMode.USER_MODE:
            self.log.debug("User-Mode")
            self.current_prompt = f"{self._prompt_dict['Hostname']}{self._prompt_dict['ExecModePrompt']}"
            self.log.debug(f"User-Mode - Prompt -> {self.current_prompt}")
     
        elif self.execute_mode is ExecMode.PRIV_MODE:
            self.log.debug("Priv-Mode")
            self._prompt_dict['ExecModePrompt'] = self.PRIV_MODE_PROMPT
            self.prompt_parts = [self._prompt_dict['Hostname']]
            self.current_prompt = f"{self._prompt_dict['Hostname']}{self._prompt_dict['ExecModePrompt']}"
            self.log.debug(f"Priv-Mode - Prompt -> {self.current_prompt}")
     
        elif self.execute_mode is ExecMode.CONFIG_MODE:
            self.log.debug("Config-Mode")
            self._prompt_dict['ExecModePrompt'] = self.PRIV_MODE_PROMPT
            self.current_prompt = f"{self._prompt_dict['Hostname']}({self._prompt_dict['ConfigMode']}){self._prompt_dict['ExecModePrompt']}"
                                 
            if self.SUB_CMD_START:
                self.log.debug(f"Config Mode - SubCommand -> ({self.SUB_CMD_START})")
                self.current_prompt = f"{self._prompt_dict['Hostname']}({self._prompt_dict['ConfigMode']}-{self.SUB_CMD_START}){self._prompt_dict['ExecModePrompt']}"  
            
            self.log.debug(f"Config Mode -> Prompt -> {self.current_prompt}")
        
        else:
            self.log.error(f"No execute_mode defined ({self.execute_mode})")  
        
        return self.current_prompt 
    
    def get_prompt(self):
        '''
        Get the current router command prompt.

        Returns:
            str: The current command prompt string.
        '''
        return self.current_prompt
    
    def set_exec_mode(self, execute_mode: ExecMode):
        '''
        Set the execution mode for the CLI session.

        Args:
            execute_mode (ExecMode): The execution mode to set (e.g., EXEC_MODE_NORMAL, EXEC_MODE_DEBUG).

        Returns:
            None
        '''
        self.execute_mode = execute_mode
        self.update_prompt()

    def get_exec_mode(self) -> ExecMode:
        return self.execute_mode
        
    def update_prompt_hostname(self) -> bool:
        """
        Update the prompt hostname attribute based on the hostname retrieved from the 'SystemConfig'.

        Returns:
            bool: STATUS_OK if the update is successful, STATUS_NOK otherwise.
        """
        self._prompt_dict['Hostname'] = SystemCall().get_hostname_os()
            
        return STATUS_OK

    def get_prompt_hostname(self) -> str:
        """
        Get the prompt hostname attribute.

        Returns:
            str: The prompt hostname.
        """
        return self._prompt_dict['Hostname']

    def get_top_level_cmd_object(self, cmd: list[str]) -> CmdPrompt | None:
        """
        Retrieve the top-level command object.

        Args:
            cmd (list[str]): list of command parts to search for.

        Returns:
            CmdPrompt | None: The command object if found, else None.
        """
        self.log.debug(f'get_top_level_cmd_object() -> cmds: {cmd}')
        
        #self.log.debug(f"TOP-LVL-CMD-SEARCH: ({cmd})\n" + "\n".join([f"{key} ----> {value}" \
        #    for key, value in self._register_top_lvl_cmds.items()]))

        # Check for Global defined classes
        if cmd[0] in self._register_top_lvl_cmds:
            self.log.debug(f'get_top_level_cmd_object() -> Command Found (Global): {cmd[0]}')
            return self._register_top_lvl_cmds[cmd[0]]
        
        # Check for non-global classes
        combined_cmd = '_'.join(cmd[:2])
        self.log.debug(f'get_top_level_cmd_object() -> combined_cmd: {combined_cmd}')
        if combined_cmd in self._register_top_lvl_cmds:
            self.log.debug(f'get_top_level_cmd_object() -> Command Found (Non-Global): {combined_cmd}')
            return self._register_top_lvl_cmds[combined_cmd]
        
        self.log.debug(f'get_top_level_cmd_object() -> cmd: {cmd} - No Match!!!')
        
        return None

    def clear_completer(self):
        """
        Clear the current completer, removing all suggestions.
        """
        self.session.completer = None

    def _process_prompt_feeder_line(self, line: list[str]) -> list[str]:
        """
        Processes a single line from the prompt feeder.

        This method checks if the line contains any remark symbols and skips it if so.
        Additionally, it updates the execution mode if the line contains the 'enable' command.

        Args:
            line (list[str]): The line to be processed, represented as a list of strings.

        Returns:
            list[str]: The processed line, or an empty list if the line is a remark or contains the 'enable' command.
        """
        # Check if the line is empty
        if not line:
            return []
        
        # Check if the input contains any remark symbols, if so, skip line
        if any(line[0].startswith(symbol) for symbol in RouterPrompt.PROMPT_REMARK_SYMBOL):
            return []
        
        # Check if the line starts with the 'enable' command
        if line[0] == 'enable':
            self.execute_mode = ExecMode.PRIV_MODE
            self.update_prompt()
            return []

        return line

    def _read_prompt_file(self, pf: PromptFeeder , sleep_ms: float=200) -> bool:
       
        self.log.debug(f'_read_prompt_file() PromptFeed: {pf.__str__()} - sleep_ms: {sleep_ms}')
       
        while pf.length():
            
            line = pf.next()
            self.log.debug(f'Line: {line}')
            line = self._process_prompt_feeder_line(line)
            
            if sleep_ms > 0:
                sleep(sleep_ms/1000)
            
            if self._process_command(line):
                break
                    
        return STATUS_OK

    def start(self, pf : PromptFeeder = None) -> bool:
        """
        Start the process with an optional prompt feeder.

        Args:
            pf PromptFeeder`: The optional prompt feeder object.

        Returns:
            bool: STATUS_OK if the process starts successfully, STATUS_NOK otherwise.
        """
        self._DEBUG_print_top_lvl_cmds()
        
        if self.load_prompt_feeder(pf):
            self.log.debug('Invalid PromptFeeder Object')
        
        # PromptFeeder Has Priority
        if self.get_prompt_feeder().length():
            self.log.debug(f'PromptFeeder, has {self.get_prompt_feeder().length()} entries')
            self._read_prompt_file(self.get_prompt_feeder())
            return STATUS_OK
        
        while True:
            try:
                command = self._get_command()
                
                if not command:
                    continue
                                    
                if self._process_command(command):
                    break

            except KeyboardInterrupt:
                self.log.debug('Keyboard interrupt received, continuing...')
                continue
            
            except EOFError:
                self.log.debug('EOFError received, exiting...')
                break

        return STATUS_OK

    def _get_command(self) -> list:
        """
        Get the user command from the prompt.

        Returns:
            list: The user command split into components.
        """
        command = self.rs_prompt()
        self.log.debug(f'start-cmd: {command}')
        return command

    def _process_command(self, commands: list) -> bool:
        """
        Process the user command.

        Args:
            commands (list): The user command split into components.

        Returns:
            bool: STATUS_OK if the loop should exit, STATUS_NOK otherwise.
        """
        if not commands or not commands[0]:
            self.log.debug('No command input')
            return STATUS_OK

        # TODO Need to provide and overload method
        if 'end' in commands[0]:
            return STATUS_NOK

        if '?' in commands[0]:
            return STATUS_OK
        
        if self._execute_commands(commands[0], commands):
            print(f"Command {commands[0]} not found.")
            
        else:
            self.log.debug(f'Command: {commands} Executed!!!')

        return STATUS_OK

    def _execute_commands(self, cmd: str, args: list) -> bool:
        """
        Execute the given command with its arguments.

        Args:
            cmd (str): The command to execute.
            args (list): The arguments for the command.

        Returns:
            bool: True if the command was executed successfully, False otherwise.
        """
        self.log.debug(f'_execute_commands() -> cmd: {cmd} -> args: {args}')
        
        try:
            cmd_object = self.get_top_level_cmd_object(args)
                        
            return cmd_object.execute(args)
        
        except Exception as e:
            self.log.debug(f'Error _execute_commands() {cmd}: {e}')
            return STATUS_NOK
            
    def _DEBUG_print_top_lvl_cmds(self):
        """
        Print the top-level commands with each key-value pair on a new line.
        """
        # formatted_cmds = "\n".join([f"{key}\t\t\t{value}" for key, value in self._register_top_lvl_cmds.items()])
        # self.log.debug(f"TOP-LVL-CMD:\n{formatted_cmds}")
                   

# FILE: src/routershell/lib/cli/config-bak/bridge_config.py
import logging

import cmd2

from routershell.lib.cli.base.global_operation import GlobalUserCommand
from routershell.lib.cli.common.router_prompt import ExecMode, RouterPrompt
from routershell.lib.common.constants import *
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.network_manager.common.interface import InterfaceType
from routershell.lib.network_manager.common.phy import State
from routershell.lib.network_manager.network_operations.bridge import Bridge


from routershell.lib.common.types import BridgeName
class InvalidBridge(Exception):
    def __init__(self, message):
        super().__init__(message)

class BridgeConfig(cmd2.Cmd, GlobalUserCommand, RouterPrompt, Bridge):
    """Command set for configuring Bridge-Config-Configuration"""

    PROMPT_CMD_ALIAS = InterfaceType.BRIDGE.value
    
    def __init__(self, bridge_name: BridgeName):
        super().__init__()
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.debug(f"__init__() -> Bridge: {bridge_name}")
        self.log.setLevel(RSLS().BRIDGE_CONFIG_CMD)
        self.debug = False
        
        GlobalUserCommand.__init__(self)
        RouterPrompt.__init__(self, ExecMode.CONFIG_MODE, self.PROMPT_CMD_ALIAS)
        Bridge.__init__(self)
        
        self.bridge_ifName = bridge_name
        
        if self.add_bridge_global(bridge_name):
            self.log.debug(f"Unable to add ({bridge_name}) to DB")
                        
        self.prompt = self.set_prompt()
             
    def do_protocol(self, args=None, negate=False):
        return 
    
    def do_stp(self, args=None, negate=False):
        return
    
    def do_shutdown(self, args=None, negate=False) -> bool:
        """
        Change the state of a network interface.

        :param args: Additional arguments (optional).
        :param negate: If True, set the state to UP; otherwise, set it to DOWN.
        :return: STATUS_OK if the interface state was successfully changed, STATUS_OK otherwise.
        """
        self.log.debug(f"do_shutdown() -> Bridge: {self.bridge_ifName} -> negate: {negate}")
        
        state = State.DOWN
        
        if negate:
            state = State.UP
        
        Bridge().set_interface_shutdown(self.bridge_ifName, state)
        
    def complete_no(self, text, line, begidx, endidx):
        completions = ['shutdown', 'name', 'protocol']
        return [comp for comp in completions if comp.startswith(text)]
          
    def do_no(self, line):    
        self.log.debug(f"do_no() -> Line -> {line}")
        
        parts = line.strip().split()
        start_cmd = parts[0]
        
        self.log.debug(f"do_no() -> Start-CMD -> {start_cmd}")        
        
        if start_cmd == 'shutdown':
            self.log.debug(f"Enable interface -> {self.bridge_ifName}")
            self.do_shutdown(None, negate=True)
    
    def default(self, args):
        print('Invalid command')
    

# FILE: src/routershell/lib/cli/config-bak/configure_prompt.py

import logging

from routershell.lib.cli.common.exec_priv_mode import ExecMode
from routershell.lib.cli.common.router_prompt import RouterPrompt
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS


from routershell.lib.common.types import CommandName
class ConfigurePrompt(RouterPrompt):

    def __init__(self, exec_mode: ExecMode = ExecMode.CONFIG_MODE, sub_cmd_name: CommandName | None = None):
        RouterPrompt.__init__(self, exec_mode)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().CONFIGURE_PROMPT)


        

        

# FILE: src/routershell/lib/cli/config-bak/dhcp_server_config.py
import argparse
import logging

from routershell.lib.cli.base.global_operation import GlobalUserCommand
from routershell.lib.cli.common.exec_priv_mode import ExecMode
from routershell.lib.cli.common.router_prompt import RouterPrompt
from routershell.lib.common.common import STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.network_manager.network_operations.dhcp.server.dhcp_server import DhcpPoolFactory
from routershell.lib.network_services.dhcp.common.dhcp_common import DHCPOptionLookup, DHCPVersion
from routershell.lib.network_services.dhcp.dnsmasq.dnsmasq_config_gen import DHCPv6Modes


from routershell.lib.common.types import DhcpPoolName
class DHCPServerConfig(GlobalUserCommand, RouterPrompt):
    
    GLOBAL_CONFIG_MODE = 'global'
    PROMPT_CMD_ALIAS = 'dhcp'    
    
    def __init__(self, dhcp_pool_name: DhcpPoolName, negate=False):
        self.dhcp_pool_name = dhcp_pool_name
        self.negate = negate
        
        super().__init__()        
        GlobalUserCommand.__init__(self)

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DHCP_SERVER_CONFIG)

        
        self.log.debug(f"DHCPServerConfig({dhcp_pool_name}) -> negate: {negate}")
        
        prompt_ext = ""
        if self.isGlobalMode() :
            prompt_ext = f'-{dhcp_pool_name}'
        else:
            self.log.debug("DHCPServerConfig() -> Not in DHCP Global Config Mode")
        
        RouterPrompt.__init__(self, ExecMode.CONFIG_MODE, f'{self.PROMPT_CMD_ALIAS}{prompt_ext}')
        self.prompt = self.set_prompt()
        
        self.dhcp_pool_factory = DhcpPoolFactory(dhcp_pool_name)
                
    def isGlobalMode(self) -> bool:
        return self.dhcp_pool_name == self.GLOBAL_CONFIG_MODE
    
    def do_subnet(self, args: str):
        '''
        Configure a subnet with the specified IP address and subnet mask.

        Args:
            args (str): The arguments for the 'subnet' command, which should include an IP address and a subnet mask.

        Example ULA IPv4 | IPv6 :
            subnet 192.168.1.0/24 | fd00:1::/64
        '''
        self.log.debug(f"do_subnet() -> args: {args} -> negate: {self.negate}")

        parser = argparse.ArgumentParser(
            description="Configure a DHCP server subnet",
            epilog="Use 'subnet <inet-subnet>/<CIDR>' to set the subnet."
        )

        # Define the arguments directly without subcommands
        parser.add_argument("inet_subnet_cidr", help="The IP address/mask of the subnet")

        try:
            if not isinstance(args, list):
                args = parser.parse_args(args.split())
            else:
                args = parser.parse_args(args)
        except SystemExit:
            return

        inet_subnet_cidr = args.inet_subnet_cidr
        self.log.debug(f"Configuring subnet with INET Subnet: {inet_subnet_cidr}")
        if self.dhcp_pool_factory.add_pool_subnet(inet_subnet_cidr):
            print(f"Invalid IP subnet: {inet_subnet_cidr}")
        
    def do_pool(self, args: str):
        '''
        Configure an IP pool with the specified start and end IP addresses and subnet mask.

        Args:
            args (str): The arguments for the 'pools' command, which should include the start IP address, end IP address, and subnet mask.

        Example:
            pools 192.168.1.10 192.168.1.20 255.255.255.0
        '''
        self.log.debug(f"do_pool() -> args: {args}")

        parser = argparse.ArgumentParser(
            description="Configure an IP pool for the DHCP server",
            epilog="Use 'pools <ip-address-start> <ip-address-end> <ip-subnet-mask>' to set the pool."
        )

        # Define the arguments directly without subcommands
        parser.add_argument("inet_start", help="The starting IP address of the pool")
        parser.add_argument("inet_end", help="The ending IP address of the pool")
        parser.add_argument("inet_subnet_cidr", help="The subnet mask for the pool")

        try:
            if not isinstance(args, list):
                args = parser.parse_args(args.split())
            else:
                args = parser.parse_args(args)
        except SystemExit:
            return

        # Access the parsed arguments directly
        inet_start = args.inet_start
        inet_end = args.inet_end
        inet_subnet_cidr = args.inet_subnet_cidr

        # Handle the 'pools' command logic here
        self.log.debug(f"Configuring IP pool with start IP: {inet_start}, end IP: {inet_end}, and subnet mask: {inet_subnet_cidr}")
        if self.dhcp_pool_factory.add_inet_pool_range(inet_start, inet_end, inet_subnet_cidr):
            print('Invalid IP pool range, IP address outside of pool subnet.')
        
    def do_reservations(self, args: str):
        '''
        Configure a reservation for a client with the specified MAC address, IP address, and optional hostname.

        Args:
            args (str): The arguments for the 'reservations' command, which should include the MAC address, IP address, and optional hostname.

        Example:
            reservations hw-address 00:11:22:33:44:55 ip-address 192.168.1.10 hostname client1
        '''
        self.log.debug(f"do_reservations() -> args: {args}")

        parser = argparse.ArgumentParser(
            description="Configure a reservation for a DHCP client",
            epilog="Use 'reservations [hw-address | duid] <mac-address> ip-address <ip-address> [hostname <string>]' to set a reservation."
        )

        # Define the arguments and options
        parser.add_argument("mac_or_duid", choices=["hw-address", "duid"], 
                            help="Specify 'hw-address' or 'duid' to identify the client")
        parser.add_argument("client_identifier", 
                            help="The MAC address or DUID of the client")
        parser.add_argument("ip_identifier", 
                            help="Specify 'ip-address' to set the client's IP address")
        parser.add_argument("ip_address", 
                            help="The reserved IP address for the client")
        parser.add_argument("hostname", nargs="?", 
                            help="An optional hostname for the client")

        try:
            if not isinstance(args, list):
                args = parser.parse_args(args.split())
            else:
                args = parser.parse_args(args)
        except SystemExit:
            return

        # Access the parsed arguments and options
        mac_or_duid = args.mac_or_duid
        client_identifier = args.client_identifier
        ip_identifier = args.ip_identifier
        ip_address = args.ip_address
        hostname = args.hostname

        # Handle the 'reservations' command logic here
        self.log.debug(f"Configuring reservation for client with {mac_or_duid}: {client_identifier}, IP address: {ip_address}, and hostname: {hostname}")
        if self.dhcp_pool_factory.add_reservation(client_identifier, ip_address):
            print('IP address outside of pool subnet.')

    def do_option(self, args:str, negate=False):
        '''args: dhcp_option dhcp_value'''
        
        self.log.debug(f"do_option() -> args: {args} -> negate:{negate}")
        
        args_parts = args.strip().split()
        
        if len(args_parts) == 2:
            
            dhcp_option, dhcp_value = args_parts
            if self.dhcp_pool_factory.get_subnet_inet_version() == DHCPVersion.DHCP_V4:
                if not DHCPOptionLookup().get_dhcpv4_option_code(dhcp_option):
                    print(f"Invalid IPv4 DHCP option: {dhcp_option}")
                    return 
            else:
                if not DHCPOptionLookup().get_dhcpv6_option_code(dhcp_option):
                    print(f"Invalid IPv6 DHCP option: {dhcp_option}")
                    return 
        else:                     
            print(f"Invalid DHCP option: {dhcp_option}")   
        
        if self.isGlobalMode():
            self.log.debug(f"Adding DHCP option to global configuration: {args}")

        self.dhcp_pool_factory.add_option(dhcp_option, dhcp_value)

    def do_mode(self, args:str, negate=False):
        '''
        Set the DHCPv6 Mode.

        Args:
            args (list[str]): list of arguments.
            negate (bool): Whether to negate the mode.

        Example:
            Use 'mode <[slaac | ra-only | ra-names | ra-stateless | ra-advrouter | off-link]>'
            to set the DHCPv6 mode.
        '''

        self.log.debug(f"do_mode() -> args: {args}")

        parser = argparse.ArgumentParser(
            description="Set the DHCPv6 Mode",
            epilog="Example: Use 'mode <[slaac | ra-only | ra-names | ra-stateless | ra-advrouter | off-link]>' to set the DHCPv6 mode."
        )

        # Define the argument directly without subcommands
        parser.add_argument('mode', choices=['ra-only', 'slaac', 'ra-names', 'ra-stateless', 'ra-advrouter', 'off-link'],
                            help='Set the DHCPv6 mode.')

        try:
            if not isinstance(args, list):
                args = parser.parse_args(args.split())
            else:
                args = parser.parse_args(args)
        except SystemExit:
            return     

        if self.dhcp_pool_factory.get_subnet_inet_version() == DHCPVersion.DHCP_V4:
            print('DHCP mode is reserved for a DHCPv6 subnet')
            return

        self.dhcp_pool_factory.add_dhcp_mode(DHCPv6Modes.get_mode(args.mode))

    def do_commit(self) -> bool:
        return STATUS_OK
    

# FILE: src/routershell/lib/cli/config-bak/if_config.py
import argparse
import logging

import cmd2

from routershell.lib.cli.base.global_operation import GlobalUserCommand
from routershell.lib.cli.common.router_prompt import ExecMode, RouterPrompt
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.network_manager.common.interface import InterfaceType
from routershell.lib.network_manager.common.phy import Duplex, Speed, State
from routershell.lib.network_manager.network_operations.arp import Encapsulate
from routershell.lib.network_manager.network_operations.bridge import Bridge
from routershell.lib.network_manager.network_operations.dhcp.client.dhcp_clinet_interface_abc import DHCPInterfaceClient
from routershell.lib.network_manager.network_operations.dhcp.common.dhcp_common import DHCPStackVersion
from routershell.lib.network_manager.network_operations.dhcp.server.dhcp_server import DHCPServer
from routershell.lib.network_manager.network_operations.interface import Interface
from routershell.lib.network_manager.network_operations.nat import NATDirection
from routershell.lib.network_manager.network_operations.wireless_wifi import HardwareMode, WifiChannel, WifiInterface


from routershell.lib.common.types import InterfaceName
class InvalidInterface(Exception):
    def __init__(self, message):
        super().__init__(message)

class InterfaceConfig(cmd2.Cmd, 
                      GlobalUserCommand, 
                      RouterPrompt, 
                      Interface):
    
    def __init__(self, if_config_interface_name: InterfaceName, ifType:str=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().ETHERNET_CONFIG)
        
        GlobalUserCommand.__init__(self)
        Interface.__init__(self)
        
        self.log.debug(f"InterfaceConfig() - ifType: {ifType} -> ifName: {if_config_interface_name}")
        
        if ifType in (member.value for member in (InterfaceType.LOOPBACK, InterfaceType.VLAN)):

            self.interface_type = InterfaceType.LOOPBACK
            
            self.PROMPT_CMD_ALIAS = ifType
            self.log.debug(f"Interface Type is {ifType} - Type-> {InterfaceType.LOOPBACK.value}")
            
            '''Concatenate for Vlan + loopback (Assuming at this point)'''
            if_config_interface_name = ifType + if_config_interface_name
            
            if ifType == InterfaceType.LOOPBACK.value:
                self.log.debug(f"Creating {if_config_interface_name} if it does not exists....")
                
                if not self.does_os_interface_exist(if_config_interface_name):
                    self.log.debug(f"Creating Loopback {if_config_interface_name}")
                    if self.create_os_dummy_interface(if_config_interface_name):
                        return None
                    
                    else:
                        self.log.debug("Adding Loopback to DB")
                        self.add_db_interface_entry(if_config_interface_name, InterfaceType.LOOPBACK)
                
                else:
                    self.log.debug(f"Not Creating Loopback {if_config_interface_name}")
        else:
                    
            if not self.does_os_interface_exist(if_config_interface_name):             
                print(f"Interface {if_config_interface_name} does not exists.")
                RouterPrompt.__init__(self, ExecMode.CONFIG_MODE)
                self.do_end()

            self.log.debug(f"interface: {if_config_interface_name} is not a loopback or vlan....")
            
            if if_config_interface_name in self.get_db_interface_names():
                self.interface_type = self.get_db_interface_type(if_config_interface_name)    
            
            else:
                self.interface_type = self.get_os_interface_type(if_config_interface_name)
                self.log.debug(f'Interface: {if_config_interface_name} -> Type: {self.interface_type}')
                
                if self.add_db_interface_entry(if_config_interface_name, self.interface_type):
                    self.log.debug(f"Unable to add interface: {if_config_interface_name} to DB")

        self.PROMPT_CMD_ALIAS = self.interface_type.value
        RouterPrompt.__init__(self, ExecMode.CONFIG_MODE, self.PROMPT_CMD_ALIAS)
         
        self.ifName = if_config_interface_name
        self.prompt = self.set_prompt()
                
    def _exit_init(self):
        '''Exit for __init__()'''
        return False
            
    def complete_mac(self, text, line, begidx, endidx):
        completions = ['address', 'auto']
        return [comp for comp in completions if comp.startswith(text)]
    
    def do_description(self, line:str, negate=False):
        if negate:
            line = None
        
        if self.update_db_description(self.ifName, line):
            print("Unable to add description to DB")
        
    def do_mac(self, args:str):
        parts = args.strip().split()
        self.log.debug(f"do_mac() -> Parts: {parts}")
        
        if len(parts) == 1 and parts[0] == "auto":
            self.log.debug("do_mac() -> auto")
            self.update_interface_mac(self.ifName)
                            
        elif len(parts) == 2 and parts[0] == "address":
            mac = parts[1]
            self.log.debug(f"do_mac() -> address -> {mac}")
            self.update_interface_mac(self.ifName, mac)
            
        else:
            print("Usage: mac [auto | <mac address>]")
        
    def complete_ipv6(self, text, line, begidx, endidx):
        completions = ['address', 'dhcp-client']
        return [comp for comp in completions if comp.startswith(text)]
    
    def do_ipv6(self, args, negate=False):
 
        parser = argparse.ArgumentParser(
            description="Configure IPv6 settings on the interface",
            epilog="Suboptions:\n"
                "   address <IPv6 Address>/<CIDR>               Set static IPv6 address.\n"
                "   dhcp-client                                 Configure DHCP client.\n"
                "   <suboption> --help                          Get help for specific suboptions."
        )
        subparsers = parser.add_subparsers(dest="subcommand")

        # Subparser for 'ip address' command
        address_cidr_parser = subparsers.add_parser("address",
            help="Set a static IP address on the interface (e.g., 'ipv6 address fd00:1234:5678:abcd::1/64 [secondary]')."
        )
        address_cidr_parser.add_argument("ipv6_address_cidr",
                                help="IPv6 address/subnet to configure.")       
        address_cidr_parser.add_argument("secondary", nargs="?", const=True, default=False, 
                                help="Indicate that this is a secondary IP address.")

        # Subparser for 'ip dhcp' command
        dhcp_parser = subparsers.add_parser("dhcp-client",
            help="Configure DHCP client on the interface (e.g., 'ipv6 dhcp')."
        )

        try:
            if not isinstance(args, list):
                args = parser.parse_args(args.split())
            else:
                args = parser.parse_args(args)       
        except SystemExit:
            return

        if args.subcommand == "address":
            ipv6_address_cidr = args.ipv6_address_cidr
            is_secondary = args.secondary
            is_secondary = True if is_secondary else False

            self.log.debug(f"Configuring {'Secondary' if is_secondary else 'Primary'} IP Address on Interface ({self.ifName}) -> Inet: ({ipv6_address_cidr})")

            action_description = "Removing" if negate else "Setting"
            result = self.update_interface_inet(self.ifName, ipv6_address_cidr, is_secondary, negate)

            if result:
                self.log.error(f"Failed to {action_description} IP: {ipv6_address_cidr} on interface: {self.ifName} secondary: {is_secondary}")
            else:
                self.log.debug(f"{action_description} IP: {ipv6_address_cidr} on interface: {self.ifName} secondary: {is_secondary}")
                
        elif args.subcommand == "dhcp-client":
            self.log.debug("Enable DHCPv6 Client")
            state = State.UP if negate else State.DOWN
            if DHCPInterfaceClient().update_interface_dhcp_client(self.ifName, DHCPStackVersion.DHCP_V6, state):
                self.log.fatal(f"Unable to set DHCPv6 client on interface: {self.ifName}")      

    def complete_ip(self, text, line, begidx, endidx):
        completions = ['address', 'secondary']
        completions.extend(['proxy-arp', 'drop-gratuitous-arp', 'static-arp'])
        completions.extend(['dhcp-server', 'dhcp-client', 'pool-name'])
        completions.extend(['nat', 'inside', 'outside', 'pool'])
        return [comp for comp in completions if comp.startswith(text)]
    
    def do_ip(self, args, negate=False):
        """
        Configure IP settings on the interface.

        Args:
            args (str): Command arguments.
            negate (bool, optional): True to negate the command, False otherwise. Defaults to False.

        Available suboptions:
        - `address <IP Address>/<CIDR> [secondary]`     : Set a static IP address.
        - `dhcp-client`                                 : Enable DHCP client.
        - `dhcp-server pool <dhcp-pool-name>`           : Set DHCP server parameters.
        - `drop-gratuitous-arp`                         : Enable drop gratuitous ARP.
        - `proxy-arp`                                   : Enable proxy ARP.
        - `static-arp <inet> <mac> [arpa]`              : Add/Del static ARP entry.
        - `nat [inside|outside] pool <nat-pool-name>`   : Configure NAT address pool for inside or outside interface.

        Use `<suboption> --help` to get help for specific suboptions.
        """                   
        parser = argparse.ArgumentParser(
            description="Configure IP settings on the interface and NAT.",
            epilog="Available suboptions:\n"
                    "   address <IPv4 Address>/<CIDR> [secondary]               Set IP address/CIDR {optional secondary}.\n"
                    "   drop-gratuitous-arp                                     Enable drop-gratuitous-ARP.\n"
                    "   proxy-arp                                               Enable proxy ARP.\n"
                    "   static-arp <inet> <mac> [arpa]                          Add/Del static ARP entry.\n"
                    "   nat [inside|outside] pool <nat-pool-name> acl <acl-id>  Configure NAT for inside or outside interface."
                    "\n"
                    "Use <suboption> --help to get help for specific suboptions."
        )

        subparsers = parser.add_subparsers(dest="subcommand")

        address_cidr_parser = subparsers.add_parser("address",
            help="Set a static IP address on the interface (e.g., 'ip address 192.168.1.1/24 [secondary]')."
        )
        address_cidr_parser.add_argument("ipv4_address_cidr",
                                help="IPv4 address/subnet to configure.")       
        address_cidr_parser.add_argument("secondary", nargs="?", const=True, default=False, 
            help="Indicate that this is a secondary IP address.")

        subparsers.add_parser("proxy-arp",
            help="Set proxy-arp on the interface 'ip proxy-arp')."
        )
        
        subparsers.add_parser("drop-gratuitous-arp",
            help="Set drop-gratuitous-arp on the interface 'ip drop-gratuitous-arp')."
        )

        static_arp_parser = subparsers.add_parser("static-arp",
            help="Set static-arp on the interface 'ip static-arp <IPv4 Address> <Mac Address> [Encapsulation Type arpa]')."
        )
        static_arp_parser.add_argument("ipv4_addr_arp",         
                                       help="IPv4 address for arp entry.")
        static_arp_parser.add_argument("mac_addr_arp",          
                                       help="Mac address for arp entry.")
        static_arp_parser.add_argument("encap_arp", nargs='?',  
                                       help="Ecapsulation type [arpa].")     
          
        nat_in_out_parser = subparsers.add_parser("nat",
            help="Configure Network Address Translation (NAT) for inside or outside interfaces."
        )
        nat_in_out_parser.add_argument("nat_direction_pool",
            choices=['inside', 'outside'],
            help="Specify 'inside' for configuring NAT on the internal interface or 'outside' for the external interface."
        )
        nat_in_out_parser.add_argument("pool_option",
            nargs='?',
            choices=["pool"],
            help="Specify 'pool' followed by the NAT pool name when configuring NAT."
        )
        nat_in_out_parser.add_argument("pool_name",
            nargs='?',
            help="Specify the NAT pool name when configuring NAT."
        )

        subparsers.add_parser("dhcp-client",
            help="Configure DHCPv4 Client"
        )
        
        dhcp_server_parser = subparsers.add_parser("dhcp-server",
            help="Configure DHCPv4 Server"
        )
        dhcp_server_parser.add_argument("dhcp_server_pool_name",
            choices=['pool'],
            help="Specify the DHCP pool-name defined in the global configuration"
        )        
        dhcp_server_parser.add_argument("pool_name",
            nargs='?',
            help=f"Specify the DHCP pool name when assigning to {self.ifName}"
        )        
                
        try:
            if not isinstance(args, list):
                args = parser.parse_args(args.split())
            else:
                args = parser.parse_args(args)       
        except SystemExit:
            return

        if args.subcommand == "address":
            ipv4_address_cidr = args.ipv4_address_cidr
            is_secondary = args.secondary
            is_secondary = True if is_secondary else False

            self.log.debug(f"Configuring {'Secondary' if is_secondary else 'Primary'} IP Address on Interface ({self.ifName}) -> Inet: ({ipv4_address_cidr})")

            action_description = "Removing" if negate else "Setting"
            result = self.update_interface_inet(self.ifName, ipv4_address_cidr, is_secondary, negate)

            if result:
                self.log.error(f"Failed to {action_description} IP: {ipv4_address_cidr} on interface: {self.ifName} secondary: {is_secondary}")
            else:
                self.log.debug(f"{action_description} IP: {ipv4_address_cidr} on interface: {self.ifName} secondary: {is_secondary}")

        elif args.subcommand == "proxy-arp":
            '''[no] [ip proxy-arp]'''
            self.log.debug(f"Set proxy-arp on Interface {self.ifName} -> negate: {negate}")
            self.update_interface_proxy_arp(self.ifName, negate)
                
        elif args.subcommand == "drop-gratuitous-arp":
            '''[no] [ip drop-gratuitous-arp]'''
            self.log.debug(f"Set drop-gratuitous-arp on Interface {self.ifName}")
            self.update_interface_drop_gratuitous_arp(self.ifName, negate)

        elif args.subcommand == "static-arp":
            '''[no] [ip static-arp ip-address mac-address arpa]'''
            self.log.debug(f"Set static-arp on Interface {self.ifName}")
            
            ipv4_addr_arp = args.ipv4_addr_arp
            mac_addr_arp = args.mac_addr_arp
            encap_arp = Encapsulate.ARPA         
                    
            self.log.debug(f"Set static-arp on Interface {self.ifName} -> negate: {negate}") 
            self.update_interface_static_arp(self.ifName, ipv4_addr_arp, mac_addr_arp, encap_arp, negate)
            
        elif args.subcommand == "nat":
            '''[no] [ip nat [inside | outside] pool <nat-pool-name>]'''
            nat_direction = args.nat_direction_pool
            nat_pool_name = args.pool_name
                        
            try:
                nat_direction = NATDirection(nat_direction)
            except ValueError:
                print(f"Error: Invalid NAT direction '{nat_direction}'. Use 'inside' or 'outside'.")

            self.log.debug(f"Configuring NAT for Interface: {self.ifName} -> NAT Dir: {nat_direction.value} -> Pool: {nat_pool_name}")

            if self.set_nat_domain_status(self.ifName, nat_pool_name, nat_direction):
                self.log.error(f"Unable to add NAT: {nat_pool_name} direction: {nat_direction.value} to interface: {self.ifName}")

        elif args.subcommand == "dhcp-client":
            '''[no] [ip dhcp-client]'''
            state = State.UP if negate else State.DOWN
            if DHCPInterfaceClient().update_interface_dhcp_client(self.ifName, DHCPStackVersion.DHCP_V4, state):
                self.log.fatal(f"Unable to set DHCPv4 client on interface: {self.ifName}")

        elif args.subcommand == "dhcp-server":
            pool_name = args.pool_name
            '''[no] [ip dhcp-server] pool <dhcp-pool-name>'''
            self.log.debug("Enable DHCPv4/6 Server")
            DHCPServer().add_dhcp_pool_to_interface(pool_name, self.ifName, negate)

    def complete_speed(self, text, line, begidx, endidx):
        completions = ['half', 'full', 'auto']        
        return [comp for comp in completions if comp.startswith(text)]

    def do_duplex(self, args):
        '''
        Set the duplex mode of a network interface.
        Usage: duplex <auto | half | full>
        '''
        if not args:
            print("Usage: duplex <auto | half | full>")
            return

        if self.interface_type != InterfaceType.ETHERNET:
            self.update_interface_duplex(self.ifName, Duplex.NONE)
            print("interface must be of ethernet type")
            return
        
        duplex_values = {d.value: d for d in Duplex}
        
        args = args.lower()

        if args in duplex_values:
            duplex = duplex_values[args]
            self.update_interface_duplex(self.ifName, duplex)
                        
        else:
            print(f"Invalid duplex mode ({args}). Use 'auto', 'half', or 'full'.")

    def complete_speed(self, text, line, begidx, endidx):
        completions = ['10', '100', '1000', '10000', 'auto']        
        return [comp for comp in completions if comp.startswith(text)]

    def do_speed(self, args):
        '''
        Set the speed of a network interface.
        Usage: speed <10 | 100 | 1000 | 10000 | auto>
        '''
        if not args:
            print("Usage: speed <10 | 100 | 1000 | 10000 | auto>")
            return

        if self.interface_type != InterfaceType.ETHERNET:
            self.update_interface_speed(self.ifName, Speed.NONE)
            print("interface must be of ethernet type")
            return
        
        self.log.debug(f"do_speed() -> ARGS: {args}")
        
        speed_values = {str(s.value): s for s in Speed}
        args = args.lower()

        if args == "auto":
            self.update_interface_speed(self.ifName, Speed.AUTO_NEGOTIATE)

        elif args in speed_values:
            speed = speed_values[args]
            self.update_interface_speed(self.ifName, speed)
            
        else:
            print("Invalid speed value. Use '10', '100', '1000', '10000', or 'auto'.")

    def complete_bridge(self, text, line, begidx, endidx):
        completions = ['group']
        return [comp for comp in completions if comp.startswith(text)]
        
    def do_bridge(self, args, negate=False):
        """
        Apply a bridge configuration to the interface.

        Args:
            args (str): Command arguments.
            negate (bool, optional): True to negate the command, False otherwise. Defaults to False.

        Debugging information:
            - This method logs debugging information with the provided arguments.

        Suboptions:
            - group <bridge name>: Set the bridge group identifier.
            - <suboption> --help: Get help for specific suboptions.
        """        
        self.log.debug(f"do_bridge() -> ARGS: ({args}) -> Negate: ({negate}))")
        
        parser = argparse.ArgumentParser(
            description="Apply bridge to interface",
            epilog="Suboptions:\n"
                "  group <bridge name>                          Add bridge to interface bridge group\n"
                "  <suboption> --help                           Get help for specific suboptions."
        )
         
        subparsers = parser.add_subparsers(dest="subcommand")
        bridge_parser = subparsers.add_parser("group",
            help="Set the bridge group ID"
        )
        
        bridge_parser.add_argument("br_grp_name", help="Bridge Group")

        try:
            if not isinstance(args, list):
                args = parser.parse_args(args.split())
            else:
                args = parser.parse_args(args)       
        except SystemExit:
            return

        if args.subcommand == 'group':
            bridge_name = args.br_grp_name
            if negate:
                self.log.debug(f"do_bridge().group -> Deleting Bridge {bridge_name}")
                Bridge().del_bridge_from_interface(self.ifName, args.bridge_name)
            else:
                self.log.debug(f"do_bridge().group -> Adding Bridge: {bridge_name} to Interface: {self.ifName}")
                Bridge().add_bridge_to_interface(self.ifName, bridge_name)
        
        return 
    
    def do_shutdown(self, args=None, negate=False):
        """
        This function is used to change the state of an interface to either UP or DOWN.

        Args:
            self: The instance of the class containing this method.
            args (list): A list of arguments. If the list contains only the string 'no', the interface
                        state will be set to DOWN; otherwise, it will be set to UP.

        Returns:
            str: A message indicating the result of the interface state change.
        """
        ifState = State.DOWN
        
        if negate:
            ifState = State.UP

        self.log.debug(f'do_shutdown(negate: {negate}) -> State: {ifState.name}')

        self.update_shutdown(self.ifName, ifState)

    def complete_switchport(self, text, line, begidx, endidx):
        completions = ['access-vlan']
        return [comp for comp in completions if comp.startswith(text)]
 
    def do_switchport(self, args=None, negate=False):
        """
        Configure switchport settings.

        Args:
            args (str, optional): Command arguments. Defaults to None.
            negate (bool, optional): True to negate the command, False otherwise. Defaults to False.

        Debugging information:
            - This method logs debugging information with the provided arguments.

        Commands:
            - switchport access-vlan <vlan-id>
        """
        self.log.debug(f"switchport() -> {args}")

        parser = argparse.ArgumentParser(description="Configure switchport.")
        subparsers = parser.add_subparsers(dest="subcommand")

        # Subparser for 'set-access-vlan' subcommand
        set_access_parser = subparsers.add_parser("access-vlan", help="Configure switchport access settings")
        set_access_parser.add_argument("vlan_id", type=int, help="Set VLAN ID")

        try:
            if not isinstance(args, list):
                args = args.split()
            args = parser.parse_args(args)
        except SystemExit:
            return

        if args.subcommand == "access-vlan":
            vlan_id = args.vlan_id
            self.log.debug(f"Configuring switchport as access with VLAN ID: {vlan_id}")
            
            if self.update_interface_vlan(self.ifName, vlan_id):
                self.log.error(f"Unable to add vlan id: {vlan_id}")
            
        else:
            self.log.error("Unknown subcommand")

    def do_wireless(self, args=None, negate:bool=False):
        self.log.debug(f"do_wireless({args}, negate: {negate})")
        
        parser = argparse.ArgumentParser(
            description="Configure Wireless settings on the interface",
            epilog="Suboptions:\n"
                   "   wifi policy <wifi-policy-name>\n"
                   "   wifi mode <wifi-hardware-mode>\n"
                   "   wifi channel <wireless-policy-name>\n"
                   "   cell policy <cell-policy-name>\n"
                   "   <suboption> --help                          Get help for specific suboptions."
        )
        subparsers = parser.add_subparsers(dest="subcommand")

        wifi_parser = subparsers.add_parser("wifi", help="Configure Wi-Fi settings on the interface")
        wifi_parser.add_argument("wifi_option", choices=["policy", "mode", "channel"], 
                                 help=f"""Suboption for Wi-Fi configuration:
                                         policy <wifi-policy-name>
                                         mode {HardwareMode.display_list()}
                                         channel {WifiChannel.display_list()}
                                        """       
                                )
        wifi_parser.add_argument("wifi_suboption")

        cell_parser = subparsers.add_parser("cell", help="Configure cell settings on the interface")
        cell_parser.add_argument("cell_policy_name", help="The name of the cell policy")

        try:
            if not isinstance(args, list):
                args = parser.parse_args(args.split())
            else:
                args = parser.parse_args(args)
        except SystemExit:
            return
        
        if args.subcommand == "wifi":
            wifi_suboption = args.wifi_suboption
            self.log.debug(f"do_wireless() -> WIFI -> sub-options: {wifi_suboption} -> Interface: {self.ifName} -> Negate: {negate}")
            self._handle_wifi_suboption(args, negate)

        elif args.subcommand == "cell":
            cell_policy_name = args.cell_policy_name
            self.log.debug(f"do_wireless() -> CELL -> sub-options: {cell_policy_name} -> Interface: {self.ifName} -> Negate: {negate}")

    def _handle_wifi_suboption(self, args, negate:bool=False):
        self.log.debug(f"_handle_wifi_suboption() -> WIFI -> sub-options: {args} -> Interface: {self.ifName} -> Negate: {negate}")
        wifi_option = args.wifi_option
        wifi_suboption = args.wifi_suboption
        wi = WifiInterface(self.ifName)

        if wi.is_interface_wifi():

            if wifi_option == "policy":
                self.log.debug(f"_handle_wifi_suboption() -> WIFI -> policy: {wifi_suboption}")
                if wi.update_policy_to_wifi_interface(wifi_suboption):
                    self.log.error(f"Unable to apply wifi-policy: {wifi_suboption} to wifi interface: {self.ifName}")

            elif wifi_option == "mode":
                self.log.debug(f"_handle_wifi_suboption() -> WIFI -> mode: {wifi_suboption}")
                if wi.set_hardware_mode(HardwareMode[str(wifi_suboption).upper()]):
                    self.log.error(f"Unable to apply wifi-mode: {wifi_suboption} to wifi interface: {self.ifName}")

            elif wifi_option == "channel":
                self.log.debug(f"_handle_wifi_suboption() -> WIFI -> channel: {wifi_suboption}")
                if wi.set_channel(WifiChannel[f'CHANNEL_{str(wifi_suboption)}']):
                        self.log.error(f"Unable to apply wifi-hardware: {wifi_suboption} to wifi interface: {self.ifName}")

            else:
                print(f"Invalid command: {wifi_suboption}")

        else:
            self.log.error(f"Interface: {self.ifName} is not a WiFi Interface")

    def complete_no(self, text, line, begidx, endidx):
        completions = ['shutdown', 'bridge', 'group', 'ip', 'ipv6', 'address', 'nat', 'switchport']
        return [comp for comp in completions if comp.startswith(text)]
        
    def do_no(self, line):
        self.log.debug(f"do_no() -> Line -> {line}")
        
        parts = line.strip().split()
        start_cmd = parts[0]
        
        self.log.debug(f"do_no() -> Start-CMD -> {start_cmd}")
        
        if start_cmd == 'shutdown':
            self.log.debug(f"Enable interface -> {self.ifName}")
            self.do_shutdown(None, negate=True)
        
        elif start_cmd == 'bridge':
            self.log.debug(f"Remove bridge -> ({line})")
            self.do_bridge(parts[1:], negate=True)
        
        elif start_cmd == 'ip':
            self.log.debug(f"Remove ip -> ({line})")
            self.do_ip(parts[1:], negate=True)
        
        elif start_cmd == 'ipv6':
            self.log.debug(f"Remove ipv6 -> ({line})")
            self.do_ipv6(parts[1:], negate=True)

        elif start_cmd == 'switchport':
            self.log.debug(f"Remove switchport -> ({line})")
            self.do_switchport(parts[1:], negate=True)
        
        elif start_cmd == 'description':
            self.log.debug(f"Remove description -> ({line})")
            self.do_description(parts[1:], negate=True)
        
        else:
            print(f"No negate option for {start_cmd}")

# FILE: src/routershell/lib/cli/config-bak/vlan_config.py
import logging

import cmd2

from routershell.lib.cli.base.global_operation import GlobalUserCommand
from routershell.lib.cli.common.router_prompt import ExecMode, RouterPrompt
from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.network_manager.network_operations.vlan import Vlan


from routershell.lib.common.types import VlanName
class VlanConfig(cmd2.Cmd, GlobalUserCommand, RouterPrompt, Vlan):
    """Command set for configuring Vlan-Config-Commands"""

    PROMPT_CMD_ALIAS = "vlan"

    def __init__(self, vlan_id:int):
        super().__init__()
        GlobalUserCommand.__init__(self)
        RouterPrompt.__init__(self,ExecMode.CONFIG_MODE, self.PROMPT_CMD_ALIAS)
        Vlan().__init__(self)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().VLAN_CONFIG)

        self.prompt = self.set_prompt()
        self.vlan_id = vlan_id
        
        if self.check_or_add_vlan_to_db(self.vlan_id).status:
            self.log.debug(f"VLAN-ID {self.vlan_id} is already configured")

    def do_name(self, vlan_name: VlanName):
        """
        Change the name of the VLAN.

        Args:
            vlan_name (str): The new name for the VLAN.

        Returns:
            int: STATUS_OK if the name update is successful, STATUS_NOK if it fails.

        """
        if self.update_vlan_name(self.vlan_id, vlan_name).status:
            print(f"Unable to add name: {vlan_name} to Vlan-ID {self.vlan_id}")

    def do_description(self, vlan_descr: str) -> int:
        """
        Change the description of the VLAN.

        Args:
            vlan_descr (str): The new description for the VLAN.

        Returns:
            int: STATUS_OK if the description update is successful, STATUS_NOK if it fails.

        """
        if self.update_vlan_description_to_db(self.vlan_id, vlan_descr).status:
            self.log.error(f"Unable to add description: {vlan_descr} to Vlan-ID {self.vlan_id}")
            return STATUS_NOK
        return STATUS_OK

    def do_show(self, args=None):
        print(f"{self.get_vlan_db()}")

class VlanShow(Vlan):
    """Command set for showing Vlan-Show-Commands"""

    def __init__(self, command=None, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        
        self.command = command
        self.arg = arg
    
    def vlan(self):
        """
        Show VLAN configuration.
        """
        self.get_vlan_info()

# FILE: src/routershell/lib/cli/config/bridge/bridge_config.py

import logging

from routershell.lib.cli.common.command_class_interface import CmdPrompt
from routershell.lib.cli.common.exec_priv_mode import ExecMode
from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import BridgeName
from routershell.lib.network_manager.common.phy import State
from routershell.lib.network_manager.network_interfaces.bridge.bridge_factory import (
    BridgeInterface,
    BridgeInterfaceFactory,
)
from routershell.lib.network_manager.network_interfaces.bridge.bridge_protocols import STP_STATE
from routershell.lib.network_manager.network_operations.bridge import Bridge


class BridgeConfigError(Exception):
    """Custom exception for BridgeConfigError errors."""
    def __init__(self, message: str):
        """Initialize BridgeConfigError with a specific error message.
        
        Args:
            message (str): The error message to be displayed.
        """
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """String representation of the BridgeConfigError.
        
        Returns:
            str: A string describing the error.
        """
        return f'BridgeConfigError: {self.message}'

class BridgeConfig(CmdPrompt):
    """BridgeConfig class for managing network bridges via command-line interface."""

    def __init__(self, bridge_name: BridgeName, negate:bool=False) -> None:
        """Initialize the BridgeConfig class.
        
        Args:
            bridge_name (str): The name of the bridge to be managed.
        """
        super().__init__(global_commands=True, exec_mode=ExecMode.PRIV_MODE)
        Bridge().__init__()

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().BRIDGE_CONFIG)
        self._bridge_name = bridge_name
        self._bridge_config_cmd : BridgeInterface = BridgeInterfaceFactory(self._bridge_name).get_bridge_interface()
               
    def bridgeconfig_help(self, args: list[str]=None) -> None:
        """Display help for all available bridge control commands.
        
        Args:
            args (list, optional): Additional arguments (not used).
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")

    @CmdPrompt.register_sub_commands(nested_sub_cmds=['management'])
    def bridgeconfig_inet(self, args: list[str] = None, negate: bool = False) -> bool:
        """
        Manage the management IP address of the bridge.

        Args:
            args (list, optional): list of arguments for the command.
            negate (bool, optional): If True, negates the command (removes the management IP).

        Returns:
            bool: Status of the command execution.
        """
        if not args or 'management' not in args:
            print("Error: 'management' keyword is required.")
            return STATUS_NOK

        if len(args) < 2:
            print("Error: Management IP address is required.")
            return STATUS_NOK

        management_ip = args[1]

        if negate:
            management_ip = ""  # Clear the management IP if negate is True

        if self._bridge_config_cmd.set_inet_management(inet=management_ip):
            print(f"Unable to set management IP for bridge {self._bridge_name}")
            return STATUS_NOK

        return STATUS_OK

    @CmdPrompt.register_sub_commands()
    def bridgeconfig_description(self, args: list[str] = None, negate: bool = False) -> bool:
        """
        Manage the description of the bridge.

        Args:
            args (list, optional): list of arguments for the description command.
            negate (bool, optional): If True, negates the command (removes the description).

        Returns:
            bool: Status of the command execution.
        """
        description = ""

        if args:
            description = " ".join(args)
        
        if negate:
            description = ""

        if self._bridge_config_cmd.set_description(description):
            print(f"Unable to set description: {description} for bridge {self._bridge_name} ")
            return STATUS_NOK

        return STATUS_OK

    @CmdPrompt.register_sub_commands()         
    def bridgeconfig_protocol(self, args: list[str]=None, negate: bool=False) -> bool:
        """Manage bridge protocol settings.
        
        Args:
            args (list, optional): list of arguments for the command.
            negate (bool, optional): If True, negates the command (removes the protocol).
        
        Returns:
            bool: Status of the command execution.
        """
        print('Not implemented yet')
        return STATUS_OK

    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=['enable','disable'])
    def bridgeconfig_stp(self, args: list[str] = None, negate: bool = False) -> bool:
        """
        Manage Spanning Tree Protocol (STP) settings for the bridge.
        
        Args:
            args (list, optional): list of arguments for the command.
            negate (bool, optional): If True, negates the command (removes STP).
        
        Returns:
            bool: Status of the command execution.
        """
        if not args:
            print("Missing STP argument")
            return STATUS_NOK
        
        if 'disable' not in args and 'enable' not in args:
            print("Invalid STP option")
            return STATUS_NOK
        
        stp = STP_STATE.STP_ENABLE if 'enable' in args else STP_STATE.STP_DISABLE
        
        if self._bridge_config_cmd.set_stp(stp=stp):
            print(f"Unable to set STP to bridge {self._bridge_name}")
            return STATUS_NOK
        
        return STATUS_OK

    @CmdPrompt.register_sub_commands()
    def bridgeconfig_shutdown(self, args: list[str] = None, negate: bool = False) -> bool:
        """
        Shutdown or bring up the bridge interface.
        
        Args:
            args (list, optional): list of arguments for the command.
            negate (bool, optional): If True, shuts down the bridge interface. If False, brings up the bridge interface. Defaults to False.
        
        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        state = State.UP if negate else State.DOWN
        
        self.log.debug(f"bridgeconfig_shutdown() -> Bridge: {self._bridge_name} -> " + 
                        f"current-state: {Bridge().get_shutdown_status_os(self._bridge_name).value} -> state: {state}")

        if self._bridge_config_cmd.set_shutdown_status(state):
            print(f"Error: unable to set bridge: {self._bridge_name}")
            return STATUS_NOK
        
        return STATUS_OK
      
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=['description', 'shutdown'])
    def bridgeconfig_no(self, args: list[str]) -> bool:
        """Negate commands like description, shutdown, stp, or protocol for the bridge.
        
        Args:
            args (list): list of arguments for the command.
        
        Returns:
            bool: Status of the command execution.
        """
        self.log.debug(f"bridgeconfig_no() -> {args}")
        
        negate:bool = True
                
        if 'shutdown' in args:
            self.log.debug(f'up/down interface -> {self._bridge_name}')
            self.bridgeconfig_shutdown(None, negate)
               
        elif 'description' in args:
            self.log.debug(f"Remove protocol -> {args}")
            self.bridgeconfig_description(None, negate)        
        
        else:
            print(f'error: invalid command: {args}')
            return STATUS_NOK
        
        return STATUS_OK

# FILE: src/routershell/lib/cli/config/bridge/bridge_config_cmd.py
import logging

from routershell.lib.cli.config.bridge.bridge_config import BridgeConfig
from routershell.lib.cli.config.configure_prompt import ConfigurePrompt
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import BridgeName


class BridgeConfigCmdError(Exception):
    """Custom exception for BridgeConfigError errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'BridgeConfigError: {self.message}'
   
class BridgeConfigCmd(ConfigurePrompt):
    def __init__(self, bridge_name:BridgeName, negate=False):
        super().__init__(sub_cmd_name='br')
        bridge_name = bridge_name[0]
        self.register_top_lvl_cmds(BridgeConfig(bridge_name, negate))
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().BRIDGE_CONFIG_CMD)
    
    def intro(self) -> str:
        return 'Starting Test Config....'
                    
    def help(self):
        pass

# FILE: src/routershell/lib/cli/config/config_cmds.py
import logging

from routershell.lib.cli.common.command_class_interface import CmdPrompt
from routershell.lib.cli.common.exec_priv_mode import ExecMode
from routershell.lib.cli.config.bridge.bridge_config_cmd import BridgeConfigCmd
from routershell.lib.cli.config.dhcp.pool.dhcp_pool_config_cmd import DhcpPoolConfigCmd
from routershell.lib.cli.config.ethernet.ethernet_config_cmd import EthernetConfigCmd
from routershell.lib.cli.config.loopback.loopback_config_cmd import LoopbackConfigCmd
from routershell.lib.cli.config.vlan.vlan_config_cmd import VlanConfigCmd
from routershell.lib.common.common import Common
from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import InterfaceName
from routershell.lib.network_manager.common.interface import InterfaceType
from routershell.lib.network_manager.network_operations.bridge import Bridge
from routershell.lib.network_manager.network_operations.interface import Interface
from routershell.lib.network_manager.network_operations.nat import Nat
from routershell.lib.network_manager.network_operations.network_mgr import NetworkManager
from routershell.lib.network_services.common.network_ports import NetworkPorts
from routershell.lib.system.system import System


class ConfigCmd(CmdPrompt):

    def __init__(self, args: str=None) -> None:
        super().__init__(global_commands=True, exec_mode=ExecMode.PRIV_MODE)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().CONFIGURE_CMD)
               
    def configcmd_help(self, args: list[str]=None) -> None:
        """
        Display help for available commands.
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=Interface().get_os_network_interfaces() + [InterfaceType.LOOPBACK.value])         
    def configcmd_interface(self, args: list[str]=None) -> bool:
        self.log.debug(f'configcmd_interface -> {args}')
        
        interface_name = args[0]

        if Common().is_loopback_if_name_valid(interface_name, add_loopback_if_name=['lo']):
            self.log.debug(f'configcmd_interface() -> Loopback: {interface_name}')
            LoopbackConfigCmd(loopback_name=args).start()
            
        elif interface_name in Interface().get_os_network_interfaces(InterfaceType.ETHERNET):
            self.log.debug(f'configcmd_interface() -> Ethernet: {interface_name}')
            EthernetConfigCmd(eth_name=args).start()        
           
        elif interface_name in Interface().get_os_network_interfaces(InterfaceType.WIRELESS_WIFI):
            self.log.debug(f'configcmd_interface() -> WireLess WiFI: {interface_name}')
            print('Not implemented yet')
            return STATUS_NOK
                        
        else:
            print(f'Invalid interface: {interface_name}')
            return STATUS_NOK
                
        return STATUS_OK

    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=Bridge().get_bridge_list_os())         
    def configcmd_bridge(self, bridge_name: list[str], negate: bool=False) -> bool:
        self.log.debug(f'configcmd_bridge -> {bridge_name}')
        BridgeConfigCmd(bridge_name, negate).start()        
        return STATUS_OK

    @CmdPrompt.register_sub_commands()         
    def configcmd_vlan(self, vlan_id: list[str], negate: bool=False) -> bool:
        self.log.info(f'configcmd_vlan -> {vlan_id}')
                
        VlanConfigCmd(int(vlan_id[0]), negate).start()        
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['telnet-server', 'port', '23'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['ssh-server', 'port', '22'])  
    def configcmd_system(self, args: list=[str], negate: bool=False) -> bool:
        
        self.log.debug(f'configcmd_system() -> {args} -> negate: {negate}')

        if 'telnet-server' in args:

            if negate:
                self.log.debug('configcmd_system() -> Telnet Server: stopping service')
                return System().update_telnet_server(enable=(not negate))
            
            port = NetworkPorts.TELNET

            if 'port' in args:
                try:
                    port_index = args.index('port') + 1
                    if port_index < len(args):
                        port = int(args[port_index])

                        if port < 1 or port > 65535:
                            self.log.error(f'configcmd_system() -> Invalid port number: {port}')
                            return STATUS_NOK

                        self.log.debug(f'configcmd_system() -> telnet-server -> port: {port} -> negate: {negate}')
                    else:
                        self.log.error('Port number not specified after "port" keyword.')
                        print(f'error: port number not specified in command: {args}')
                        return STATUS_NOK

                except (ValueError, IndexError) as e:
                    self.log.error(f'Invalid port value or index error: {e}')
                    print(f'error: invalid port value in command: {args}')
                    return STATUS_NOK

            if System().update_telnet_server(enable=(not negate), port=port):
                self.log.error('Unable to set telnet server parameter via cli')
                return STATUS_NOK
                                
        elif 'ssh-server' in args:
            self.log.debug(f'configcmd_system() -> ssh-server -> negate: {negate}')
            
        else:
            self.log.error(f'Invalid command: {args}')
            print(f'error: invalid command: {args}')
            return STATUS_NOK
            
        return STATUS_OK

    @CmdPrompt.register_sub_commands()
    def configcmd_hostname(self, args: list = None) -> bool:
        """
        Configures the hostname of the system.

        Sets the hostname both in the operating system and the system database.

        Args:
            args (list, optional): A list containing the new hostname to set.

        Returns:
            bool: STATUS_OK if the hostname is successfully set in both the OS and the database, STATUS_NOK otherwise.
        """
        self.log.debug(f"configcmd_hostname() -> args: {args}")
        if args == None:
            self.log.error('No hostname specified.')
            return STATUS_NOK
        
        return System().update_hostname(args[0])
  
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['if', 'if-alias'])
    def configcmd_rename(self, args: list) -> bool:

        if len(args) != 4:
            print('missing arguments') 
        
        self.log.debug(f"configcmd_rename() -> args: {args}")

        if args[0] == 'if':
            self.log.debug("configcmd_rename() -> if")
            
            if len(args) == 4:
                self.log.debug(f"configcmd_rename() -> args-parts: {args}")
                Interface().rename_interface(args[1], args[3])

            else:
                print(f"Invalid command: rename {args}")
                
        return STATUS_OK

    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=Interface().get_os_network_interfaces())
    def configcmd_flush(self, interface_name:InterfaceName) -> bool:

        """
        Command to flush the configuration of a network interface.

        This command allows the user to flush the configuration of a network interface,
        effectively removing all assigned IP addresses and resetting the interface.

        Args:
            interface_name (str): The name of the network interface to flush.

        Usage:
            flush <interface_name>

        Example:
            flush eth0
        """
        self.log.debug(f'configcmd_flush() -> {interface_name}')

        NetworkManager().flush_interface(interface_name[0])

        return STATUS_OK

    @CmdPrompt.register_sub_commands(nested_sub_cmds=['pool-name'])
    def configcmd_nat(self, args: list[str], negate: bool=False) -> bool:

        if args[0] == 'pool-name':
            if len(args) < 2:
                self.log.error("configcmd_nat() -> Missing pool name.")
                print("Error: Missing pool name.")
                return STATUS_NOK
            
            pool_name = args[1]
            self.log.debug(f"configcmd_nat() -> pool-name: {pool_name}")
            
            if Nat().create_nat_pool(pool_name, negate):
                self.log.error(f'Unable to add NAT pool {pool_name} to DB')
                return STATUS_NOK
            
            self.log.debug(f"Successfully added NAT pool {pool_name} to DB")
        else:
            self.log.error(f"configcmd_nat() -> Invalid subcommand: {args[0]}")
            print(f"Error: Invalid subcommand: {args[0]}")
            return STATUS_NOK

        return STATUS_OK

    @CmdPrompt.register_sub_commands(nested_sub_cmds=['pool-name'])
    def configcmd_dhcp(self, args:list[str], negate: bool=False) -> bool:
        if 'pool-name' in args:
            self.log.debug(f'pool-name: {args[1]}')
            DhcpPoolConfigCmd(args[1], negate).start()
            return STATUS_OK

    @CmdPrompt.register_sub_commands(nested_sub_cmds=['bridge'] , 
                                     append_nested_sub_cmds=Bridge().get_bridge_list_os())
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['system'], append_nested_sub_cmds=['telnet-server', 'ssh-server'])
    def configcmd_no(self, args: list) -> bool:
                
        if args[0] == 'bridge':
            bridge_name = args[1]
            self.log.debug(f"configcmd_no() -> bridge: {bridge_name}")
            if Bridge().del_bridge(bridge_name):
                print(f"Unable to destroy bridge: {bridge_name}")
                return STATUS_NOK

        if args[0] == 'system':
            self.log.debug(f"configcmd_no() -> system: {args[1]}")
            self.configcmd_system(args=args, negate=True)

        return STATUS_OK


# FILE: src/routershell/lib/cli/config/configure_prompt.py
import logging

from routershell.lib.cli.common.exec_priv_mode import ExecMode
from routershell.lib.cli.common.router_prompt import RouterPrompt
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import CommandName


class ConfigurePrompt(RouterPrompt):

    def __init__(self, exec_mode: ExecMode = ExecMode.CONFIG_MODE, sub_cmd_name: CommandName | None = None):
        RouterPrompt.__init__(self, exec_mode, sub_cmd_name=sub_cmd_name)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().CONFIGURE_PROMPT)
        

# FILE: src/routershell/lib/cli/config/dhcp/pool/dhcp_pool_config.py
import logging

from routershell.lib.cli.common.command_class_interface import CmdPrompt
from routershell.lib.cli.common.exec_priv_mode import ExecMode
from routershell.lib.common.constants import STATUS_NOK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import DhcpPoolName, InetCidrText
from routershell.lib.network_manager.network_operations.dhcp.server.dhcp_server import DhcpPoolFactory


class DhcpPoolConfig(CmdPrompt):
    """
    Class to configure DHCP pool settings.
    
    This class extends CmdPrompt to provide command-line interface functionalities 
    for DHCP pool configuration.
    
    Attributes:
        log (Logger): Logger instance for logging messages.
        _dhcp_pool_factory (DhcpPoolFactory): Factory instance for managing DHCP pools.
    """

    def __init__(self, dhcp_pool_name: DhcpPoolName, negate: bool) -> None:
        super().__init__(global_commands=True, exec_mode=ExecMode.USER_MODE)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DHCP_POOL_CONFIG)
        
        if negate:
            DhcpPoolFactory(dhcp_pool_name).delete_pool_name()
            return None
        
        self._dhcp_pool_fact = DhcpPoolFactory(dhcp_pool_name)
                   
    def dhcppoolconfig_help(self, args: list = None) -> None:
        """
        Display help for available commands.
        
        Args:
            args (list, optional): list of arguments (not used).
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")
    
    @CmdPrompt.register_sub_commands()
    def dhcppoolconfig_subnet(self, inet_subnet_cidr: InetCidrText | list[str]) -> bool:
        """
        Configure a subnet for the DHCP pool.
        
        Args:
            inet_subnet_cidr (str | list[str]): The CIDR notation of the subnet or a list containing one CIDR notation.
        
        Returns:
            bool: STATUS_OK if the subnet was added successfully, STATUS_NOK otherwise.
        """
        # Check if inet_subnet_cidr is a list and ensure it has only one entry
        if isinstance(inet_subnet_cidr, list):
            if len(inet_subnet_cidr) != 1:
                self.log.error(f'Invalid subnet list: {inet_subnet_cidr}. The list must contain exactly one entry.')
                return STATUS_NOK
            inet_subnet_cidr = inet_subnet_cidr[0]  # Flatten the list by taking the first entry

        # Proceed with the subnet configuration
        self.log.debug(f'DHCP pool configuration -> subnet: {inet_subnet_cidr}')
        return self._dhcp_pool_fact.add_pool_subnet(inet_subnet_cidr)

    @CmdPrompt.register_sub_commands()
    def dhcppoolconfig_pool(self, args: list[str]) -> bool:
        """
        Configure the IP range for the DHCP pool.
        
        Args:
            args (list, optional): list of arguments [start_ip, end_ip, subnet_cidr].
        
        Returns:
            bool: STATUS_OK if the pool was added successfully, STATUS_NOK otherwise.
        """
        if len(args) != 3:
            self.log.error('pool must have 3 arguments')
            return STATUS_NOK
            
        return self._dhcp_pool_fact.add_inet_pool_range(inet_start=args[0],
                                                        inet_end=args[1],
                                                        inet_subnet_cidr=args[2])

    @CmdPrompt.register_sub_commands()
    def dhcppoolconfig_option(self, args: list[str]) -> bool:
        """
        Configure DHCP options.
        
        Args:
            args (list, optional): list of arguments [option_name, value].
        
        Returns:
            bool: STATUS_OK if the option was added successfully, STATUS_NOK otherwise.
        """
        if len(args) != 2:
            self.log.error('dhcp option must have 2 arguments')
            return STATUS_NOK        
        return self._dhcp_pool_fact.add_option(dhcp_option=args[0],
                                                  value=args[1])

# FILE: src/routershell/lib/cli/config/dhcp/pool/dhcp_pool_config_cmd.py
import logging

from routershell.lib.cli.config.configure_prompt import ConfigurePrompt
from routershell.lib.cli.config.dhcp.pool.dhcp_pool_config import DhcpPoolConfig
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import DhcpPoolName


class DhcpPoolConfigCmdError(Exception):
    """Custom exception for TestConfig errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'DhcpPoolConfigCmdError: {self.message}'
   
class DhcpPoolConfigCmd(ConfigurePrompt):

    def __init__(self, dhcp_pool_name: DhcpPoolName, negate: bool=False):
        super().__init__(sub_cmd_name='dhcp')
                    
        self.register_top_lvl_cmds(DhcpPoolConfig(dhcp_pool_name, negate))
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DHCP_POOL_CONFIG_CMD)
    
    def intro(self) -> str:
        return 'Starting DHCP Pool Config....'
                    
    def help(self):
        pass

# FILE: src/routershell/lib/cli/config/ethernet/if_control-orig.py
import argparse
import logging

from routershell.lib.cli.common.command_class_interface import CmdPrompt
from routershell.lib.cli.common.exec_priv_mode import ExecMode
from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.string_formats import StringFormats
from routershell.lib.network_manager.common.interface import InterfaceType
from routershell.lib.network_manager.common.phy import Duplex, Speed, State
from routershell.lib.network_manager.network_operations.arp import Encapsulate
from routershell.lib.network_manager.network_operations.bridge import Bridge
from routershell.lib.network_manager.network_operations.dhcp.client.dhcp_client import DHCPStackVersion
from routershell.lib.network_manager.network_operations.dhcp.client.dhcp_clinet_interface_abc import DHCPInterfaceClient
from routershell.lib.network_manager.network_operations.dhcp.server.dhcp_server import DHCPServer
from routershell.lib.network_manager.network_operations.interface import Interface
from routershell.lib.network_manager.network_operations.nat import NATDirection


from routershell.lib.common.types import InterfaceName
class InterfaceConfigError(Exception):
    """Custom exception for IfConfig errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'IfConfigError: {self.message}'

class InterfaceConfig(CmdPrompt, Interface):

    def __init__(self, ifName: InterfaceName | None=None, ifType: InterfaceType=InterfaceType.ETHERNET) -> None:
        super().__init__(global_commands=True, exec_mode=ExecMode.PRIV_MODE)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().ETHERNET_CONFIG)
        
        self.ifName = ifName
               
    def interfaceconfig_help(self, args: list=None) -> None:
        """
        Display help for available commands.
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")
            
        return STATUS_OK
            
    @CmdPrompt.register_sub_commands() 
    def interfaceconfig_description(self, line: str | None, negate: bool = False) -> bool:
        """
        Updates the interface configuration description in the database.
        
        Args:
            line (str | None): The description to be added. If None, the description will be empty.
            negate (bool): If True, the line will be set to None.
        
        Returns:
            bool: STATUS_OK indicating the operation was successful.
        
        Raises:
            ValueError: If there is an issue updating the database description.
        """
        if negate:
            self.log.debug(f'Negating description on interface: {self.ifName}')
            line = [""]
        
        if self.update_db_description(self.ifName, StringFormats.list_to_string(line)):
            print("Unable to add description to DB")
            raise ValueError("Failed to update the description in the database.")
        
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['auto'],     help='Auto assign mac address')
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['address'],  help='Assign mac address <xxxx.xxxx.xxxx>')     
    def interfaceconfig_mac(self, args:str) -> bool:
        
        self.log.debug(f"interfaceconfig_mac() -> args: {args}")
        
        if len(args) == 1 and args[0] == "auto":
            self.log.debug("interfaceconfig_mac() -> auto")
            self.update_interface_mac(self.ifName)
                            
        elif len(args) == 2 and args[0] == "address":
            mac = args[1]
            self.log.debug(f"interfaceconfig_mac() -> address -> {mac}")
            self.update_interface_mac(self.ifName, mac)
            
        else:
            print("Usage: mac [auto | <mac address>]")
            
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()    
    def interfaceconfig_ip6(self, args, negate=False) -> bool:
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['address', 'secondary'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['drop-gratuitous-arp'])        
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['proxy-arp'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['static-arp', 'arpa'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['nat', 'inside', 'pool', 'acl'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['nat', 'outside', 'pool', 'acl'])
    def X_ip(self, args: list, negate=False) -> bool:

        self.log.debug(f'interfaceconfig_ip() -> {args}')

        if 'address' in args[0]:
            ipv4_address_cidr = args[1]
            is_secondary = False
            is_secondary = True if is_secondary else False

            self.log.debug(f"Configuring {'Secondary' if is_secondary else 'Primary'} IP Address on Interface ({self.ifName}) -> Inet: ({ipv4_address_cidr})")

            action_description = "Removing" if negate else "Setting"
            result = self.update_interface_inet(self.ifName, ipv4_address_cidr, is_secondary, negate)

            if result:
                self.log.error(f"Failed to {action_description} IP: {ipv4_address_cidr} on interface: {self.ifName} secondary: {is_secondary}")
            else:
                self.log.debug(f"{action_description} IP: {ipv4_address_cidr} on interface: {self.ifName} secondary: {is_secondary}")

        elif "proxy-arp" in args[0]:
            '''[no] [ip proxy-arp]'''
            self.log.debug(f"Set proxy-arp on Interface {self.ifName} -> negate: {negate}")
            self.update_interface_proxy_arp(self.ifName, negate)
                
        elif "drop-gratuitous-arp" in args[0]:
            '''[no] [ip drop-gratuitous-arp]'''
            self.log.debug(f"Set drop-gratuitous-arp on Interface {self.ifName}")
            self.update_interface_drop_gratuitous_arp(self.ifName, negate)

        elif "static-arp" in args[0]:
            '''[no] [ip static-arp ip-address mac-address arpa]'''
            self.log.debug(f"Set static-arp on Interface {self.ifName}")
            
            ipv4_addr_arp = args[1]
            mac_addr_arp = args[2]
            encap_arp = Encapsulate.ARPA         
                    
            self.log.debug(f"Set static-arp on Interface {self.ifName} -> negate: {negate}") 
            self.update_interface_static_arp(self.ifName, ipv4_addr_arp, mac_addr_arp, encap_arp, negate)
            
        elif "nat" in args[0]:
            '''[no] [ip nat [inside | outside] pool <nat-pool-name>]'''
            nat_direction = args.nat_direction_pool
            nat_pool_name = args.pool_name
                        
            try:
                nat_direction = NATDirection(nat_direction)
            except ValueError:
                print(f"Error: Invalid NAT direction '{nat_direction}'. Use 'inside' or 'outside'.")

            self.log.debug(f"Configuring NAT for Interface: {self.ifName} -> NAT Dir: {nat_direction.value} -> Pool: {nat_pool_name}")

            if self.set_nat_domain_status(self.ifName, nat_pool_name, nat_direction):
                self.log.error(f"Unable to add NAT: {nat_pool_name} direction: {nat_direction.value} to interface: {self.ifName}")

        elif "dhcp-client" in args[0]:
            '''[no] [ip dhcp-client]'''
            self.log.debug("Enable DHCPv4 Client")
            state = State.UP if negate else State.DOWN
            if DHCPInterfaceClient().update_interface_dhcp_client(self.ifName, DHCPStackVersion.DHCP_V4, state):
                self.log.fatal(f"Unable to set DHCPv4 client on interface: {self.ifName}")

        elif "dhcp-server" in args[0]:
            pool_name = args.pool_name
            '''[no] [ip dhcp-server] pool <dhcp-pool-name>'''
            self.log.debug("Enable DHCPv4/6 Server")
            DHCPServer().add_dhcp_pool_to_interface(pool_name, self.ifName, negate)
  
        return STATUS_OK

    @CmdPrompt.register_sub_commands(nested_sub_cmds=['address', 'secondary'])
    def interfaceconfig_ip(self, args: list[str], negate=False) -> bool:
        """
        Configure IP settings on the interface.

        Args:
            args (list[str]): Command arguments.
            negate (bool, optional): True to negate the command, False otherwise. Defaults to False.

        Available suboptions:
        - `address <IP Address>/<CIDR> [secondary]`     : Set a static IP address.
        Use `<suboption> --help` to get help for specific suboptions.
        """

        self.log.debug(f'interfaceconfig_ip4() -> ({args})')
        if not args:
            print('Missing command arguments')
            return STATUS_NOK

        if '?' in args:
            args = [arg if arg != '?' else '--help' for arg in args]

        parser = argparse.ArgumentParser(
            description="Configure IP settings on the interface.",
            epilog="Available suboptions:\n"
                   "   address <IPv4 Address>/<CIDR> [secondary]   Set IP address/CIDR (optional secondary).\n"
                   "Use <suboption> --help to get help for specific suboptions."
        )

        subparsers = parser.add_subparsers(dest="subcommand")

        address_parser = subparsers.add_parser("address",
                                               help="Set a static IP address on the interface (e.g., 'ip address 192.168.1.1/24 [secondary]').")
        
        address_parser.add_argument("ipv4_address_cidr",
                                    help="IPv4 address/subnet to configure.")
        address_parser.add_argument("secondary", nargs="?", const=True, default=False,
                                    help="Indicate that this is a secondary IP address.")
        
        # Parse the arguments
        parsed_args = parser.parse_args(args)

        if parsed_args.subcommand == "address":
            ipv4_address_cidr = parsed_args.ipv4_address_cidr
            is_secondary = parsed_args.secondary
            is_secondary = True if is_secondary else False

            self.log.debug(f"Configuring {'Secondary' if is_secondary else 'Primary'} IP Address on Interface ({self.ifName}) -> Inet: ({ipv4_address_cidr})")

            action_description = "Removing" if negate else "Setting"
            result = self.update_interface_inet(self.ifName, ipv4_address_cidr, is_secondary, negate)

            if result:
                self.log.error(f"Failed to {action_description} IP: {ipv4_address_cidr} on interface: {self.ifName} secondary: {is_secondary}")
            else:
                self.log.debug(f"{action_description} IP: {ipv4_address_cidr} on interface: {self.ifName} secondary: {is_secondary}")

        else:
            self.log.debug(f'Invalid subcommand: {parsed_args.subcommand}')
            print('Invalid subcommand')
            return STATUS_NOK

        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=['auto', 'half', 'full'])    
    def interfaceconfig_duplex(self, args: list[str]) -> bool:
        """
        Updates the interface duplex mode based on the provided arguments.
        
        Args:
            args (str | None): The duplex mode argument, expected to be 'auto', 'half', or 'full'.
        
        Returns:
            bool: STATUS_OK (True) indicating the operation was successful.
        
        Raises:
            ValueError: If the duplex mode is invalid.
        """
        
        if not args:
            print("Usage: duplex <auto | half | full>")
            return STATUS_NOK

        if self.interface_type != InterfaceType.ETHERNET:
            self.update_interface_duplex(self.ifName, Duplex.NONE)
            print("interface must be of ethernet type")
            return STATUS_NOK
        
        duplex_values = {d.value: d for d in Duplex}
        self.log.info(f'Interface: {self.ifName} -> Duplex: {args}')
        args = args.lower()

        if args in duplex_values:
            duplex = duplex_values[args]
            self.update_interface_duplex(self.ifName, duplex)
                        
        else:
            print(f"Invalid duplex mode ({args}). Use 'auto', 'half', or 'full'.")
            return STATUS_NOK
                    
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=['10', '100', '1000', '2500', '10000', 'auto'])    
    def interfaceconfig_speed(self, args: str | None) -> bool:
        args = StringFormats.list_to_string(args)
        
        if not args:
            print("Usage: speed <10 | 100 | 1000 | 2500 | 10000 | auto>")
            return

        if self.interface_type != InterfaceType.ETHERNET:
            self.update_interface_speed(self.ifName, Speed.NONE)
            print("interface must be of ethernet type")
            return
        
        self.log.debug(f"do_speed() -> ARGS: {args}")
        
        speed_values = {str(s.value): s for s in Speed}
        args = args.lower()

        if args == "auto":
            self.update_interface_speed(self.ifName, Speed.AUTO_NEGOTIATE)

        elif args in speed_values:
            speed = speed_values[args]
            self.update_interface_speed(self.ifName, speed)
            
        else:
            print("Invalid speed value. Use '10', '100', '1000', '2500', '10000', or 'auto'.")
                    
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['group'], 
                                     append_nested_sub_cmds=Bridge().get_bridge_list_os())    
    def interfaceconfig_bridge(self, args: str | None, negate=False) -> bool:
        
        if 'group' in args:
            
            bridge_name = args[1]
            
            if negate:
                self.log.debug(f"do_bridge().group -> Deleting Bridge {bridge_name}")
                Bridge().del_bridge_from_interface(self.ifName, args.bridge_name)
            else:
                self.log.debug(f"do_bridge().group -> Adding Bridge: {bridge_name} to Interface: {self.ifName}")
                Bridge().add_bridge_to_interface(self.ifName, bridge_name)
        
        else:
            print(f'error: invalid command: {args}')
            STATUS_NOK

        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()    
    def interfaceconfig_shutdown(self, args=None, negate=False) -> bool:
        """
        This function is used to change the state of an interface to either UP or DOWN.

        Args:
            self: The instance of the class containing this method.
            args (list): A list of arguments. If the list contains only the string 'no', the interface
                        state will be set to DOWN; otherwise, it will be set to UP.

        Returns:
            str: A message indicating the result of the interface state change.
        """
        ifState = State.DOWN
        
        if negate:
            ifState = State.UP

        self.log.debug(f'interfaceconfig_shutdown(negate: {negate}) -> State: {ifState.name}')

        self.update_shutdown(self.ifName, ifState)
        
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['access-vlan'])    
    def interfaceconfig_switchport(self, args=None, negate=False) -> bool:
        if 'access-vlan' in args:
            
            vlan_id = args[1]
            self.log.debug(f"Configuring switchport as access with VLAN ID: {vlan_id}")
            
            if self.update_interface_vlan(self.ifName, vlan_id):
                self.log.error(f"Unable to add vlan id: {vlan_id}")
            
        else:
            self.log.error("Unknown subcommand")
            
        return STATUS_OK        

    @CmdPrompt.register_sub_commands()    
    def interfaceconfig_wireless(self, args=None, negate:bool=False) -> bool:
       return STATUS_OK
    
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=['shutdown', 'description', 'bridge', 'ip', 'switchport'])    
    def interfaceconfig_no(self, args: list) -> bool:
        
        self.log.debug(f"interfaceconfig_no() -> Line -> {args}")

        start_cmd = args[0]
                
        if start_cmd == 'shutdown':
            self.log.debug(f"up/down interface -> {self.ifName}")
            self.interfaceconfig_shutdown(None, negate=True)
        
        elif start_cmd == 'bridge':
            self.log.debug(f"Remove bridge -> ({args})")
            self.interfaceconfig_bridge(args[1:], negate=True)
        
        elif start_cmd == 'ip':
            self.log.debug(f"Remove ip -> ({args})")
            self.interfaceconfig_ip(args[1:], negate=True)
        
        elif start_cmd == 'ipv6':
            self.log.debug(f"Remove ipv6 -> ({args})")
            self.interfaceconfig_ipv6(args[1:], negate=True)

        elif start_cmd == 'switchport':
            self.log.debug(f"Remove switchport -> ({args})")
            self.interfaceconfig_switchport(args[1:], negate=True)
        
        elif start_cmd == 'description':
            self.log.debug(f"Remove description -> ({args})")
            self.interfaceconfig_description(args[1:], negate=True)
        
        else:
            print(f"No negate option for {start_cmd}")
        
        return STATUS_OK

# FILE: src/routershell/lib/cli/config/interface/if_control-orig.py
import argparse
import logging

from routershell.lib.cli.common.command_class_interface import CmdPrompt
from routershell.lib.cli.common.exec_priv_mode import ExecMode
from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.string_formats import StringFormats
from routershell.lib.network_manager.common.interface import InterfaceType
from routershell.lib.network_manager.common.phy import Duplex, Speed, State
from routershell.lib.network_manager.network_operations.arp import Encapsulate
from routershell.lib.network_manager.network_operations.bridge import Bridge
from routershell.lib.network_manager.network_operations.dhcp.client.dhcp_client import DHCPStackVersion
from routershell.lib.network_manager.network_operations.dhcp.client.dhcp_clinet_interface_abc import DHCPInterfaceClient
from routershell.lib.network_manager.network_operations.dhcp.server.dhcp_server import DHCPServer
from routershell.lib.network_manager.network_operations.interface import Interface
from routershell.lib.network_manager.network_operations.nat import NATDirection


from routershell.lib.common.types import InterfaceName
class InterfaceConfigError(Exception):
    """Custom exception for IfConfig errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'IfConfigError: {self.message}'

class InterfaceConfig(CmdPrompt, Interface):

    def __init__(self, ifName: InterfaceName | None=None, ifType: InterfaceType=InterfaceType.ETHERNET) -> None:
        super().__init__(global_commands=True, exec_mode=ExecMode.PRIV_MODE)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().ETHERNET_CONFIG)
        
        self.ifName = ifName
               
    def interfaceconfig_help(self, args: list=None) -> None:
        """
        Display help for available commands.
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")
            
        return STATUS_OK
            
    @CmdPrompt.register_sub_commands() 
    def interfaceconfig_description(self, line: str | None, negate: bool = False) -> bool:
        """
        Updates the interface configuration description in the database.
        
        Args:
            line (str | None): The description to be added. If None, the description will be empty.
            negate (bool): If True, the line will be set to None.
        
        Returns:
            bool: STATUS_OK indicating the operation was successful.
        
        Raises:
            ValueError: If there is an issue updating the database description.
        """
        if negate:
            self.log.debug(f'Negating description on interface: {self.ifName}')
            line = [""]
        
        if self.update_db_description(self.ifName, StringFormats.list_to_string(line)):
            print("Unable to add description to DB")
            raise ValueError("Failed to update the description in the database.")
        
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['auto'],     help='Auto assign mac address')
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['address'],  help='Assign mac address <xxxx.xxxx.xxxx>')     
    def interfaceconfig_mac(self, args:str) -> bool:
        
        self.log.debug(f"interfaceconfig_mac() -> args: {args}")
        
        if len(args) == 1 and args[0] == "auto":
            self.log.debug("interfaceconfig_mac() -> auto")
            self.update_interface_mac(self.ifName)
                            
        elif len(args) == 2 and args[0] == "address":
            mac = args[1]
            self.log.debug(f"interfaceconfig_mac() -> address -> {mac}")
            self.update_interface_mac(self.ifName, mac)
            
        else:
            print("Usage: mac [auto | <mac address>]")
            
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()    
    def interfaceconfig_ip6(self, args, negate=False) -> bool:
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['address', 'secondary'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['drop-gratuitous-arp'])        
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['proxy-arp'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['static-arp', 'arpa'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['nat', 'inside', 'pool', 'acl'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['nat', 'outside', 'pool', 'acl'])
    def X_ip(self, args: list, negate=False) -> bool:

        self.log.debug(f'interfaceconfig_ip() -> {args}')

        if 'address' in args[0]:
            ipv4_address_cidr = args[1]
            is_secondary = False
            is_secondary = True if is_secondary else False

            self.log.debug(f"Configuring {'Secondary' if is_secondary else 'Primary'} IP Address on Interface ({self.ifName}) -> Inet: ({ipv4_address_cidr})")

            action_description = "Removing" if negate else "Setting"
            result = self.update_interface_inet(self.ifName, ipv4_address_cidr, is_secondary, negate)

            if result:
                self.log.error(f"Failed to {action_description} IP: {ipv4_address_cidr} on interface: {self.ifName} secondary: {is_secondary}")
            else:
                self.log.debug(f"{action_description} IP: {ipv4_address_cidr} on interface: {self.ifName} secondary: {is_secondary}")

        elif "proxy-arp" in args[0]:
            '''[no] [ip proxy-arp]'''
            self.log.debug(f"Set proxy-arp on Interface {self.ifName} -> negate: {negate}")
            self.update_interface_proxy_arp(self.ifName, negate)
                
        elif "drop-gratuitous-arp" in args[0]:
            '''[no] [ip drop-gratuitous-arp]'''
            self.log.debug(f"Set drop-gratuitous-arp on Interface {self.ifName}")
            self.update_interface_drop_gratuitous_arp(self.ifName, negate)

        elif "static-arp" in args[0]:
            '''[no] [ip static-arp ip-address mac-address arpa]'''
            self.log.debug(f"Set static-arp on Interface {self.ifName}")
            
            ipv4_addr_arp = args[1]
            mac_addr_arp = args[2]
            encap_arp = Encapsulate.ARPA         
                    
            self.log.debug(f"Set static-arp on Interface {self.ifName} -> negate: {negate}") 
            self.update_interface_static_arp(self.ifName, ipv4_addr_arp, mac_addr_arp, encap_arp, negate)
            
        elif "nat" in args[0]:
            '''[no] [ip nat [inside | outside] pool <nat-pool-name>]'''
            nat_direction = args.nat_direction_pool
            nat_pool_name = args.pool_name
                        
            try:
                nat_direction = NATDirection(nat_direction)
            except ValueError:
                print(f"Error: Invalid NAT direction '{nat_direction}'. Use 'inside' or 'outside'.")

            self.log.debug(f"Configuring NAT for Interface: {self.ifName} -> NAT Dir: {nat_direction.value} -> Pool: {nat_pool_name}")

            if self.set_nat_domain_status(self.ifName, nat_pool_name, nat_direction):
                self.log.error(f"Unable to add NAT: {nat_pool_name} direction: {nat_direction.value} to interface: {self.ifName}")

        elif "dhcp-client" in args[0]:
            '''[no] [ip dhcp-client]'''
            self.log.debug("Enable DHCPv4 Client")
            state = State.UP if negate else State.DOWN
            if DHCPInterfaceClient().update_interface_dhcp_client(self.ifName, DHCPStackVersion.DHCP_V4, state):
                self.log.fatal(f"Unable to set DHCPv4 client on interface: {self.ifName}")

        elif "dhcp-server" in args[0]:
            pool_name = args.pool_name
            '''[no] [ip dhcp-server] pool <dhcp-pool-name>'''
            self.log.debug("Enable DHCPv4/6 Server")
            DHCPServer().add_dhcp_pool_to_interface(pool_name, self.ifName, negate)
  
        return STATUS_OK

    @CmdPrompt.register_sub_commands(nested_sub_cmds=['address', 'secondary'])
    def interfaceconfig_ip(self, args: list[str], negate=False) -> bool:
        """
        Configure IP settings on the interface.

        Args:
            args (list[str]): Command arguments.
            negate (bool, optional): True to negate the command, False otherwise. Defaults to False.

        Available suboptions:
        - `address <IP Address>/<CIDR> [secondary]`     : Set a static IP address.
        Use `<suboption> --help` to get help for specific suboptions.
        """

        self.log.debug(f'interfaceconfig_ip4() -> ({args})')
        if not args:
            print('Missing command arguments')
            return STATUS_NOK

        if '?' in args:
            args = [arg if arg != '?' else '--help' for arg in args]

        parser = argparse.ArgumentParser(
            description="Configure IP settings on the interface.",
            epilog="Available suboptions:\n"
                   "   address <IPv4 Address>/<CIDR> [secondary]   Set IP address/CIDR (optional secondary).\n"
                   "Use <suboption> --help to get help for specific suboptions."
        )

        subparsers = parser.add_subparsers(dest="subcommand")

        address_parser = subparsers.add_parser("address",
                                               help="Set a static IP address on the interface (e.g., 'ip address 192.168.1.1/24 [secondary]').")
        
        address_parser.add_argument("ipv4_address_cidr",
                                    help="IPv4 address/subnet to configure.")
        address_parser.add_argument("secondary", nargs="?", const=True, default=False,
                                    help="Indicate that this is a secondary IP address.")
        
        # Parse the arguments
        parsed_args = parser.parse_args(args)

        if parsed_args.subcommand == "address":
            ipv4_address_cidr = parsed_args.ipv4_address_cidr
            is_secondary = parsed_args.secondary
            is_secondary = True if is_secondary else False

            self.log.debug(f"Configuring {'Secondary' if is_secondary else 'Primary'} IP Address on Interface ({self.ifName}) -> Inet: ({ipv4_address_cidr})")

            action_description = "Removing" if negate else "Setting"
            result = self.update_interface_inet(self.ifName, ipv4_address_cidr, is_secondary, negate)

            if result:
                self.log.error(f"Failed to {action_description} IP: {ipv4_address_cidr} on interface: {self.ifName} secondary: {is_secondary}")
            else:
                self.log.debug(f"{action_description} IP: {ipv4_address_cidr} on interface: {self.ifName} secondary: {is_secondary}")

        else:
            self.log.debug(f'Invalid subcommand: {parsed_args.subcommand}')
            print('Invalid subcommand')
            return STATUS_NOK

        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=['auto', 'half', 'full'])    
    def interfaceconfig_duplex(self, args: list[str]) -> bool:
        """
        Updates the interface duplex mode based on the provided arguments.
        
        Args:
            args (str | None): The duplex mode argument, expected to be 'auto', 'half', or 'full'.
        
        Returns:
            bool: STATUS_OK (True) indicating the operation was successful.
        
        Raises:
            ValueError: If the duplex mode is invalid.
        """
        
        if not args:
            print("Usage: duplex <auto | half | full>")
            return STATUS_NOK

        if self.interface_type != InterfaceType.ETHERNET:
            self.update_interface_duplex(self.ifName, Duplex.NONE)
            print("interface must be of ethernet type")
            return STATUS_NOK
        
        duplex_values = {d.value: d for d in Duplex}
        self.log.info(f'Interface: {self.ifName} -> Duplex: {args}')
        args = args.lower()

        if args in duplex_values:
            duplex = duplex_values[args]
            self.update_interface_duplex(self.ifName, duplex)
                        
        else:
            print(f"Invalid duplex mode ({args}). Use 'auto', 'half', or 'full'.")
            return STATUS_NOK
                    
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=['10', '100', '1000', '2500', '10000', 'auto'])    
    def interfaceconfig_speed(self, args: str | None) -> bool:
        args = StringFormats.list_to_string(args)
        
        if not args:
            print("Usage: speed <10 | 100 | 1000 | 2500 | 10000 | auto>")
            return

        if self.interface_type != InterfaceType.ETHERNET:
            self.update_interface_speed(self.ifName, Speed.NONE)
            print("interface must be of ethernet type")
            return
        
        self.log.debug(f"do_speed() -> ARGS: {args}")
        
        speed_values = {str(s.value): s for s in Speed}
        args = args.lower()

        if args == "auto":
            self.update_interface_speed(self.ifName, Speed.AUTO_NEGOTIATE)

        elif args in speed_values:
            speed = speed_values[args]
            self.update_interface_speed(self.ifName, speed)
            
        else:
            print("Invalid speed value. Use '10', '100', '1000', '2500', '10000', or 'auto'.")
                    
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['group'], 
                                     append_nested_sub_cmds=Bridge().get_bridge_list_os())    
    def interfaceconfig_bridge(self, args: str | None, negate=False) -> bool:
        
        if 'group' in args:
            
            bridge_name = args[1]
            
            if negate:
                self.log.debug(f"do_bridge().group -> Deleting Bridge {bridge_name}")
                Bridge().del_bridge_from_interface(self.ifName, args.bridge_name)
            else:
                self.log.debug(f"do_bridge().group -> Adding Bridge: {bridge_name} to Interface: {self.ifName}")
                Bridge().add_bridge_to_interface(self.ifName, bridge_name)
        
        else:
            print(f'error: invalid command: {args}')
            STATUS_NOK

        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()    
    def interfaceconfig_shutdown(self, args=None, negate=False) -> bool:
        """
        This function is used to change the state of an interface to either UP or DOWN.

        Args:
            self: The instance of the class containing this method.
            args (list): A list of arguments. If the list contains only the string 'no', the interface
                        state will be set to DOWN; otherwise, it will be set to UP.

        Returns:
            str: A message indicating the result of the interface state change.
        """
        ifState = State.DOWN
        
        if negate:
            ifState = State.UP

        self.log.debug(f'interfaceconfig_shutdown(negate: {negate}) -> State: {ifState.name}')

        self.update_shutdown(self.ifName, ifState)
        
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['access-vlan'])    
    def interfaceconfig_switchport(self, args=None, negate=False) -> bool:
        if 'access-vlan' in args:
            
            vlan_id = args[1]
            self.log.debug(f"Configuring switchport as access with VLAN ID: {vlan_id}")
            
            if self.update_interface_vlan(self.ifName, vlan_id):
                self.log.error(f"Unable to add vlan id: {vlan_id}")
            
        else:
            self.log.error("Unknown subcommand")
            
        return STATUS_OK        

    @CmdPrompt.register_sub_commands()    
    def interfaceconfig_wireless(self, args=None, negate:bool=False) -> bool:
       return STATUS_OK
    
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=['shutdown', 'description', 'bridge', 'ip', 'switchport'])    
    def interfaceconfig_no(self, args: list) -> bool:
        
        self.log.debug(f"interfaceconfig_no() -> Line -> {args}")

        start_cmd = args[0]
                
        if start_cmd == 'shutdown':
            self.log.debug(f"up/down interface -> {self.ifName}")
            self.interfaceconfig_shutdown(None, negate=True)
        
        elif start_cmd == 'bridge':
            self.log.debug(f"Remove bridge -> ({args})")
            self.interfaceconfig_bridge(args[1:], negate=True)
        
        elif start_cmd == 'ip':
            self.log.debug(f"Remove ip -> ({args})")
            self.interfaceconfig_ip(args[1:], negate=True)
        
        elif start_cmd == 'ipv6':
            self.log.debug(f"Remove ipv6 -> ({args})")
            self.interfaceconfig_ipv6(args[1:], negate=True)

        elif start_cmd == 'switchport':
            self.log.debug(f"Remove switchport -> ({args})")
            self.interfaceconfig_switchport(args[1:], negate=True)
        
        elif start_cmd == 'description':
            self.log.debug(f"Remove description -> ({args})")
            self.interfaceconfig_description(args[1:], negate=True)
        
        else:
            print(f"No negate option for {start_cmd}")
        
        return STATUS_OK

# FILE: src/routershell/lib/cli/show/dump_db_show.py
from tabulate import tabulate

from routershell.lib.common.types import DbTableName
from routershell.lib.db.sqlite_db.router_shell_db import RouterShellDB as DB


class DbDumpShow:
    
    def __init__(self):
        """
        Initializes the DbDumpShow with a connection to the SQLite database.
        """
        self._connection_cursor = DB().connection.cursor()
        print(f"DbDumpShow()->init()->{self._connection_cursor.__str__()}")

    def _fetch_tables(self, search_term: str = ''):
        """
        Fetches the list of all table names in the database, optionally filtered by a search term.

        Args:
            search_term (str): A term to filter table names by.

        Returns:
            list: A list of table names that match the search term.
        """
        cursor = self._connection_cursor
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        
        if search_term:
            search_term = f"%{search_term}%"
            query += " AND name LIKE ?"
            cursor.execute(query, (search_term,))
        else:
            query += ";"
            cursor.execute(query)
        
        return cursor.fetchall()

    def _fetch_schema(self, table_name: DbTableName):
        """
        Fetches the schema of a specific table.

        Args:
            table_name (str): The name of the table.

        Returns:
            list: A list of schema information for the table.
        """
        cursor = self._connection_cursor
        cursor.execute(f"PRAGMA table_info({table_name});")
        return cursor.fetchall()

    def _fetch_data(self, table_name: DbTableName):
        """
        Fetches the data of a specific table.

        Args:
            table_name (str): The name of the table.

        Returns:
            tuple: A tuple containing the column names and rows of data.
        """
        cursor = self._connection_cursor
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        return column_names, rows

    def _print_schema(self, table_name: DbTableName, schema):
        """
        Prints the schema of a table in a human-readable format.

        Args:
            table_name (str): The name of the table.
            schema (list): The schema information to print.
        """
        print(f"\nSchema: {table_name}")
        schema_table = [["Column", "Type", "Not Null", "Default Value"]]
        schema_table.extend([[col[1], col[2], col[3], col[4]] for col in schema])
        print(tabulate(schema_table, headers='firstrow', tablefmt='grid'))

    def _print_data(self, table_name: DbTableName, column_names, rows):
        """
        Prints the data of a table in a human-readable format.

        Args:
            table_name (str): The name of the table.
            column_names (list): The column names of the table.
            rows (list): The rows of data to print.
        """
        print(f"\nTable: {table_name}")
        data_table = [column_names] + rows
        try:
            print(tabulate(data_table, headers='firstrow', tablefmt='grid'))
        except Exception as e:
            print(f"Error printing data for table {table_name}: {e}")

    def dump_db(self, include_schema: bool = False, search_term: str = ''):
        """
        Dumps the contents of the SQLite database to the console in a human-readable format.
        Optionally includes schema information and filters tables based on a search term.

        Args:
            include_schema (bool): If True, includes schema information in the output.
            search_term (str): A term to filter table names by.
        """
        tables = self._fetch_tables(search_term)
        
        if not tables:
            print("No tables found in the database.")
            return

        for (table_name,) in tables:
            if include_schema:
                try:
                    schema = self._fetch_schema(table_name)
                    self._print_schema(table_name, schema)
                except Exception as e:
                    print(f"Error fetching schema for table {table_name}: {e}")

            try:
                column_names, rows = self._fetch_data(table_name)
                self._print_data(table_name, column_names, rows)
            except Exception as e:
                print(f"Error fetching data for table {table_name}: {e}")

# FILE: src/routershell/lib/common/common.py
import datetime
import ipaddress
import logging
import os
import random
import re
import socket
import subprocess
from datetime import datetime

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.types import EnvironmentVariableName, HostnameText, InterfaceName
from routershell.lib.network_manager.common.interface import InterfaceType


class Common:
    '''Commonly used Static Methods'''

    def __init__(self) -> None:
        self.log = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def getHostName() -> str:
        try:
            # Get the hostname of the computer
            hostname = socket.gethostname()
            return hostname
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    @staticmethod
    def get_reboot_command() -> str:
        ''''''
        # Check if the /etc/init directory exists (indicating SysV init)
        if os.path.exists('/etc/init'):
            return 'sudo init 6'  # Use SysV init reboot command

        # Check if the /run/systemd/system directory exists (indicating systemd)
        if os.path.exists('/run/systemd/system'):
            return 'sudo systemctl reboot'  # Use systemd reboot command

        # Default to 'sudo reboot' if neither init system is found
        return 'sudo reboot'
    
    @staticmethod
    def get_shutdown_command() -> str:

        # Check if the /etc/init directory exists (indicating SysV init)
        if os.path.exists('/etc/init'):
            return 'sudo init 0'  # Use SysV init reboot command

        # Check if the /run/systemd/system directory exists (indicating systemd)
        if os.path.exists('/run/systemd/system'):
            return 'sudo systemctl shutdown'  # Use systemd reboot command

        # Default to 'sudo shutdown' if neither init system is found
        return 'sudo shutdown'
    
    @staticmethod
    def getclock(line) -> str:
        ''''''
        # Split the line to extract the format argument (if provided)
        args = line.split()
        if args:
            format_argument = args[0]
        else:
            format_argument = None

        # Get the current date and time
        current_time = datetime.datetime.now()

        # Determine the format based on the argument (or use a default format)
        if format_argument:
            try:
                formatted_time = current_time.strftime(format_argument)
                print(formatted_time)
            except ValueError:
                print("Invalid format argument.")
        else:
            # Default format if no argument is provided
            formatted_time = current_time.strftime("%H:%M:%S.%f PST %a %b %d %Y")
            print(formatted_time)
    
    @staticmethod        
    def get_network_hardware(self) -> list:
        ''''''
        ifName_info = []

        try:
            # Run the 'lshw -c network' command and capture the output
            network_info = subprocess.check_output(['sudo', 'lshw', '-c', 'network'], text=True)

            # Split the output into sections for each network interface
            sections = network_info.split('*-network')

            for section in sections[1:]:
                lines = section.strip().split('\n')

                # Initialize a dictionary to store information for this interface
                ifName_data = {
                    'Logical Name': "N/A",
                    'Bus Info': "N/A",
                    'Serial': "N/A",
                    'Capacity': "N/A",
                    'Type': 'Unknown'
                }

                # Parse the lines for relevant information
                for line in lines:
                    if "bus info:" in line:
                        ifName_data['Bus Info'] = line.split("bus info:")[1].strip()
                    elif "logical name:" in line:
                        ifName_data['Logical Name'] = line.split("logical name:")[1].strip()
                    elif "serial:" in line:
                        ifName_data['Serial'] = line.split("serial:")[1].strip()
                    elif "configuration:" in line:
                        configuration = line.split("configuration:")[1].strip()
                        if "pci@" in ifName_data['Bus Info'] and "wireless" in configuration.lower():
                            ifName_data['Type'] = "Wireless"
                    elif "capacity:" in line:
                        ifName_data['Capacity'] = line.split("capacity:")[1].strip()

                # Determine the interface type based on bus info
                if "usb@" in ifName_data['Bus Info']:
                    ifName_data['Type'] = "USB-Ethernet"
                elif "pci@" in ifName_data['Bus Info'] and "Wireless" not in ifName_data['Type']:
                    ifName_data['Type'] = "PCI-Ethernet"

                # Append the interface information to the list
                ifName_info.append(ifName_data)

        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

        return ifName_info
    
    @staticmethod
    def is_valid_interface(self, ifName):
        
        try:
            # Use subprocess to run the 'ifconfig -a' command
            output = subprocess.check_output(['ifconfig', '-a'], text=True)

            # Check if the interface_name appears in the output
            if ifName in output:
                return STATUS_OK
            
            return STATUS_NOK
        except subprocess.CalledProcessError:
            return STATUS_NOK
    
    @staticmethod
    def generate_random_mac_address(self):
        '''Generate a random Mac Address that is not a Multicast'''
        # The first byte should be an even number (locally administered)
        first_byte = random.randint(0, 127) * 2

        # Generate the remaining 5 bytes randomly
        random_bytes = [random.randint(0, 255) for _ in range(5)]

        # Combine the bytes into a MAC address string
        mac_address = "{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}".format(
            first_byte, *random_bytes
        )

        return mac_address
 
    @staticmethod
    def is_valid_ip(ip_str: str) -> bool:
        '''Check both IPv4 and IPv6 is properly formatted'''
        try:
            ipaddress.IPv4Address(ip_str)  # Check if it's a valid IPv4 address
            return STATUS_OK
        except ipaddress.AddressValueError:
            try:
                ipaddress.IPv6Address(ip_str)  # Check if it's a valid IPv6 address
                return STATUS_OK
            except ipaddress.AddressValueError:
                return STATUS_NOK
    
    @staticmethod    
    def flatten_list(simple_list):
        return [item for item in simple_list]

    @staticmethod
    def remove_substrings_and_concatenate(input_list: list[str], substrings: list[str]) -> str:
        """
        Removes all specified substrings from each element in the input list and concatenates the results into a single string.

        Args:
            input_list (list[str]): The list of strings to be processed.
            substrings (list[str]): The substrings to be removed from each element.

        Returns:
            str: A single string with substrings removed and elements concatenated.
        """
        # Check if input_list and substrings are lists and contain the right types
        if not all(isinstance(i, str) for i in input_list):
            raise TypeError("All elements in input_list must be strings.")
        if not all(isinstance(sub, str) for sub in substrings):
            raise TypeError("All elements in substrings must be strings.")
        
        # Process each element in the list
        processed_elements = []
        for element in input_list:
            for sub in substrings:
                element = element.replace(sub, '')
            processed_elements.append(element)
        
        # Concatenate all processed elements into a single string
        result_string = ''.join(processed_elements)
        return result_string
    
    @staticmethod
    def convert_timestamp(timestamp:int):
        """
        Convert Unix timestamp to human-readable date and time.
        """
        if timestamp:
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        else:
            return "N/A" 

    @staticmethod
    def is_valid_hostname(hostname: HostnameText) -> bool:
        """
        Check if a hostname is valid based on DNS standards.

        Args:
            hostname (str): The hostname to be validated.

        Returns:
            bool: True if the hostname is valid, False otherwise.
        """
        if not hostname or len(hostname) > 255:
            return False

        # Check if the hostname contains only valid characters
        if not re.match("^[a-zA-Z0-9.-]+$", hostname):
            return False

        # Check if the hostname does not start or end with a hyphen
        if hostname.startswith("-") or hostname.endswith("-"):
            return False

        # Check if there are no consecutive periods (..)
        if ".." in hostname:
            return False

        return True
    
    @staticmethod
    def get_env(var_name: EnvironmentVariableName) -> str:
        """
        Get the value of an environment variable.
        
        Args:
            var_name (str): The name of the environment variable.
        
        Returns:
            str: The value of the environment variable, or None if it is not found.
        """
        return os.environ.get(var_name)

    @staticmethod
    def is_loopback_if_name_valid(interface_name: InterfaceName, add_loopback_if_name: list[str] = None) -> bool:
        """
        Check if the given interface name is in the loopback format or starts with any of the specified prefixes.

        Args:
            interface_name (str): The name of the network interface.
            loopback_if_check_list (list[str], optional): list of additional interface name prefixes to check against. Default is None.

        Returns:
            bool: True if the interface name matches the loopback format or any prefix in if_check_list, False otherwise.
        """
        if add_loopback_if_name is None:
            add_loopback_if_name = []
        
        loopback_pattern = rf'^{InterfaceType.LOOPBACK.value}\d+$'
        
        if re.match(loopback_pattern, interface_name):
            return True
        
        for prefix in add_loopback_if_name:
            if re.match(rf'^{prefix}\d*$', interface_name):
                return True
            
        return False

# FILE: src/routershell/lib/common/types.py
"""Shared RouterShell type definitions."""

from __future__ import annotations

from pathlib import Path
from typing import TypeAlias

CommandArgs: TypeAlias = list[str]
EnvironmentMap: TypeAlias = dict[str, str]
FilePath: TypeAlias = str | Path
JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]
LogLevelName: TypeAlias = str

BridgeName: TypeAlias = str
ClientIdText: TypeAlias = str
ClientName: TypeAlias = str
CommandName: TypeAlias = str
DbTableName: TypeAlias = str
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

# FILE: src/routershell/lib/db/bridge_db.py
import logging

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import BridgeName, InterfaceName
from routershell.lib.db.sqlite_db.router_shell_db import RouterShellDB as DB
from routershell.lib.network_manager.common.phy import State
from routershell.lib.network_manager.network_interfaces.bridge.bridge_protocols import STP_STATE, BridgeProtocol


class BridgeDatabase:
    
    rsdb = DB()
    
    def __init__(cls):
        cls.log = logging.getLogger(cls.__class__.__name__)
        cls.log.setLevel(RSLS().BRIDGE_DB)
                
        if not cls.rsdb:
            cls.log.debug("Connecting RouterShell Database")
            cls.rsdb = DB()   
    
    def does_bridge_exists_db(cls, bridge_name: BridgeName) -> bool:
        """
        Check if a bridge with the given name exists in the database.

        Args:
            cls: The class reference.
            bridge_name (str): The name of the bridge to check.

        Returns:
            bool: True if the bridge exists, False otherwise.
        """
    
        status = cls.rsdb.bridge_exist_db(bridge_name).status
        cls.log.debug(f"does_bridge_exists_db() -> Bridge: {bridge_name} - status: {status}")
        return status

    def add_bridge_db(cls, bridge_name: BridgeName) -> bool:
        """
        Add a new bridge to the database.
        
        Args:
            bridge_name (str): The name of the bridge to be added.

        Returns:
            bool: STATUS_OK if the bridge was successfully added or updated, STATUS_NOK otherwise.
        """
        cls.log.debug(f"add_bridge_db() -> BridgeName: {bridge_name}")

        if cls.rsdb.insert_interface_bridge(bridge_name).status:
            cls.log.debug(f"Bridge {bridge_name} FAILED add to DB")
        
        return cls.rsdb.update_bridge(bridge_name=bridge_name).status
        
    def del_bridge_db(cls, bridge_name: BridgeName) -> bool:
        """
        Delete a bridge by its name from the firewall configuration.

        Args:
            bridge_name (str): The name of the bridge to delete.

        Returns:
            bool: STATUS_OK if the bridge is deleted successfully, STATUS_NOK if deletion fails.
        """
        cls.log.debug(f"del_bridge() -> BridgeName: {bridge_name}")

        result = cls.rsdb.delete_bridge(bridge_name)
        if result.status:
            cls.log.error(f"Unable to delete Bridge: {bridge_name} from DB, error: {result.reason}")
            return STATUS_NOK
        
        return STATUS_OK

    def insert_protocol_db(cls, bridge_name: BridgeName, br_protocol: str) -> bool:
        """
        Insert a protocol for a bridge in the firewall configuration.

        Args:
            bridge_name (str): The name of the bridge to add a protocol to.
            br_protocol (str): The protocol to add to the bridge.

        Returns:
            bool: STATUS_OK if the protocol is added successfully, STATUS_NOK otherwise.
        """
        cls.log.debug(f"insert_protocol() -> BridgeName: {bridge_name}")

        if not cls.does_bridge_exists_db(bridge_name):
            cls.log.error(f"Unable to add protocol to bridge {bridge_name}, bridge does not exist")
            return STATUS_NOK

        return STATUS_OK

    def add_interface(cls, bridge_name: BridgeName, interface_name: InterfaceName) -> bool:
        """
        Add an interface to a bridge in the firewall configuration.

        Args:
            bridge_name (str): The name of the bridge to add the interface to.
            interface_name (str): The name of the interface to add to the bridge.

        Returns:
            bool: STATUS_OK if the interface is added successfully, STATUS_NOK if the bridge does not exist.
        """
        cls.log.debug(f"add_interface() -> BridgeName: {bridge_name}")

        if not cls.does_bridge_exists_db(bridge_name):
            cls.log.error(f"Unable to add interface {interface_name} to bridge {bridge_name}, bridge does not exist")
            return STATUS_NOK

        return STATUS_OK

    def get_bridge_summary(cls, bridge_name: BridgeName | None = None) -> bool:
        """
        Get a summary of a bridge in the firewall configuration.

        Args:
            bridge_name (str, optional): The name of the bridge to get a summary of. Defaults to None.

        Returns:
            bool: STATUS_OK (False) if the summary is retrieved successfully or if bridge_name is None,
            STATUS_NOK (True) if bridge_name is provided but the bridge does not exist.
        """
        cls.log.debug(f"get_bridge_summary() -> BridgeName: {bridge_name}")

        if bridge_name is not None and not cls.does_bridge_exists_db(bridge_name):
            cls.log.error(f"Unable to get summary for bridge {bridge_name}, bridge does not exist")
            return STATUS_NOK

        return STATUS_OK

    def remove_interface(cls, bridge_name: BridgeName, interface_name: InterfaceName) -> bool:
        """
        Remove an interface from a bridge in the firewall configuration.

        Args:
            bridge_name (str): The name of the bridge to remove the interface from.
            interface_name (str): The name of the interface to remove from the bridge.

        Returns:
            bool: STATUS_OK (False) if the interface is removed successfully, STATUS_NOK (True) if the bridge does not exist.
        """
        cls.log.debug(f"remove_interface() -> BridgeName: {bridge_name}")

        if not cls.does_bridge_exists_db(bridge_name):
            cls.log.error(f"Unable to remove interface {interface_name} from bridge {bridge_name}, bridge does not exist")
            return STATUS_NOK

        return STATUS_OK

    def get_interfaces(cls, bridge_name:BridgeName) -> list:
        cls.log.debug(f"bridge_exists() -> BridgeName: {bridge_name}")
        pass

    def update_interface_bridge_group_db(cls, interface_name: InterfaceName, bridge_group: BridgeName, remove: bool = False) -> bool:
        """
        Update the bridge group for an interface.

        Args:
            interface_name (str): The name of the interface to update.
            bridge_group (str): The name of the bridge group to assign or remove.
            remove (bool optional): If True, remove the interface from the bridge group. 
                                    If False, assign the interface to the bridge group.

        Returns:
            bool: STATUS_OK if the update was successful, STATUS_NOK otherwise.
        """
        if remove:
            result = cls.rsdb.delete_interface_bridge_group(interface_name, bridge_group)
            cls.log.debug(f"Removed interface '{interface_name}' from bridge group '{bridge_group}'")
        else:
            result = cls.rsdb.insert_interface_bridge_group(interface_name, bridge_group)
            cls.log.debug(f"Assigned interface '{interface_name}' to bridge group '{bridge_group}'")

        return STATUS_OK if result.status == STATUS_OK else STATUS_NOK
    
    def update_bridge_db(cls, bridge_name: BridgeName, 
                        protocol: BridgeProtocol | None = None, 
                        stp_status: STP_STATE | None = None,
                        management_inet: str | None = None,
                        description: str | None = None,
                        shutdown_status: State | None = None) -> bool:
        """
        Update an existing bridge in the Bridges, Interfaces, and InterfaceIpAddress tables.

        Args:
            bridge_name (str): The name of the bridge to update.
            protocol (BridgeProtocol | None): The new protocol for the bridge (if changing).
            stp_status (STP_STATE | None): The new STP status (if changing).
            management_inet (str | None): The management IP address for the bridge (if changing).
            description (str | None): The new description for the bridge interface (if changing).
            shutdown_status (bool | None): The new shutdown status for the bridge interface (if changing).

        Returns:
            bool: STATUS_OK if the update was successful, STATUS_NOK otherwise.
        """
        result = cls.rsdb.update_bridge(
            bridge_name=bridge_name,
            protocol=protocol,
            stp_status=stp_status,
            management_inet=management_inet,
            description=description,
            shutdown_status=shutdown_status
        )
        
        cls.log.debug(f"update_bridge_db() -> BridgeName: {bridge_name}, Result: {result.reason}, Status: {result.status}")

        return result.status


# FILE: src/routershell/lib/db/dhcp_client_db.py
import logging

from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import InterfaceName
from routershell.lib.db.sqlite_db.router_shell_db import RouterShellDB as DB
from routershell.lib.network_manager.network_operations.dhcp.common.dhcp_common import DHCPStackVersion
from routershell.lib.network_services.dhcp.common.dhcp_common import DHCPVersion


class DHCPClientDatabase:
    rsdb = DB()
    log = logging.getLogger(__name__)

    def __init__(self):
        """
        Initializes the DHCPClientDatabase instance and sets up logging.
        """
        self.log.setLevel(RSLS().INTERFACE_DB)

    @classmethod
    def add_db_dhcp_client(
        cls, interface_name: InterfaceName, dhcp_stack_version: DHCPStackVersion) -> bool:
        """
        Adds a DHCP client entry to the database for a specified interface.

        Args:
            interface_name (str): The name of the network interface to update.
            dhcp_stack_version (DHCPStackVersion): The version of the DHCP stack to add.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        cls.log.debug(f'add_db_dhcp_client() -> interface; {interface_name} -> dhcp_stack: {dhcp_stack_version.value}')
        return cls.rsdb.insert_interface_dhcp_client(interface_name, dhcp_stack_version.value)

    @classmethod
    def update_db_dhcp_client(
        cls, interface_name: InterfaceName, dhcp_stack_version: DHCPStackVersion) -> bool:
        """
        Updates the DHCP client entry in the database for a specified interface.

        Args:
            interface_name (str): The name of the network interface to update.
            dhcp_stack_version (DHCPStackVersion): The version of the DHCP stack to set.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        cls.log.debug(f'update_db_dhcp_client() -> interface; {interface_name} -> dhcp_stack: {dhcp_stack_version.value}')
        return cls.rsdb.update_interface_dhcp_client(interface_name, dhcp_stack_version.value).status

    @classmethod
    def remove_db_dhcp_client(
        cls, interface_name: InterfaceName, dhcp_stack_version: DHCPVersion) -> bool:
        """
        Removes a DHCP client entry from the database for a specified interface.

        Args:
            interface_name (str): The name of the network interface to update.
            dhcp_stack_version (DHCPStackVersion): The version of the DHCP stack to remove.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        cls.log.debug(f'remove_db_dhcp_client() -> interface; {interface_name} -> dhcp_stack: {dhcp_stack_version.value}')
        return cls.rsdb.remove_interface_dhcp_client(interface_name, dhcp_stack_version.value).status

# FILE: src/routershell/lib/db/dhcp_server_db.py
import logging

from routershell.lib.common.constants import STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import DhcpPoolName, InetAddressText, InetCidrText, InterfaceName, MacAddressText
from routershell.lib.db.sqlite_db.router_shell_db import RouterShellDB as DB
from routershell.lib.network_services.dhcp.common.dhcp_common import DHCPVersion
from routershell.lib.network_services.dhcp.dnsmasq.dnsmasq_config_gen import DHCPv6Modes


class DHCPServerDatabase:
    """
    A class for interacting with the DHCP server database.
    """
    def __init__(self):
        """
        Initialize the DHCPServerDatabase class.

        This constructor sets up the class logger and connects to the RouterShell database if not already connected.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DHCP_SERVER_DB)

    def dhcp_pool_name_dhcp_version_db(self, dhcp_pool_name: DhcpPoolName) -> DHCPVersion:
        """
        Retrieve the DHCP version for a specified DHCP pool name from the database.

        Parameters:
            dhcp_pool_name (str): The name of the DHCP pool for which to retrieve the version.

        Returns:
            DHCPVersion: An enum representing the DHCP version ('DHCP_V4', 'DHCP_V6', or 'UNKNOWN').

        Example:
            dhcp_version = your_instance.dhcp_pool_name_dhcp_version_db('your_dhcp_pool_name')
            print(f"The DHCP version for pool 'your_dhcp_pool_name' is {dhcp_version}")
        """
        try:
            sql_result = DB().dhcp_pool_dhcp_version(dhcp_pool_name)

            if sql_result.status == STATUS_OK:
                if sql_result.result.get('DHCPVersion') == DHCPVersion.DHCP_V4.value:
                    return DHCPVersion.DHCP_V4
                elif sql_result.result.get('DHCPVersion') == DHCPVersion.DHCP_V6.value:
                    return DHCPVersion.DHCP_V6
            return DHCPVersion.UNKNOWN

        except Exception as e:
            self.log.error(f"Failed to retrieve DHCP version for '{dhcp_pool_name}'. Error: {str(e)}")
            return DHCPVersion.UNKNOWN

    def dhcp_pool_name_exists_db(self, dhcp_pool_name: DhcpPoolName) -> bool:
        """
        Check if a DHCP pool name exists in the database.

        Args:
            dhcp_pool_name (str): The DHCP pool name to check.

        Returns:
            bool: True if the DHCP pool name exists, False otherwise.
        """
        return DB().dhcp_pool_name_exist(dhcp_pool_name).status

    def dhcp_pool_name_list(self) -> list[str]:
        """
        Retrieve a list of DHCP pool names from the database.

        This method queries the RSDB to get the list of DHCP server pools,
        and filters the results based on the status. Only pools with STATUS_OK
        are included in the returned list.

        Returns:
            list[str]: A list of DHCP pool names with STATUS_OK.
        """
        
        dhcp_pool_names = []
        
        for result in DB().select_dhcp_server_pool_list():
            if result.status == STATUS_OK:
                dhcp_pool_names.append(result.result['DhcpPoolname'])
        
        return dhcp_pool_names

    def dhcp_pool_subnet_exist_db(self, inet_subnet_cidr: InetCidrText) -> bool:
        """
        Check if a DHCP pool subnet with the given subnet CIDR exists in the database.

        Args:
            inet_subnet_cidr (str): The subnet CIDR to check for existence.

        Returns:
            bool: True if the DHCP pool subnet exists, False otherwise.
        """
        return DB().dhcp_pool_subnet_exist(inet_subnet_cidr).status

    def get_dhcp_pool_subnet_name_db(self, dhcp_pool_name: DhcpPoolName) -> str:
        """
        Retrieve the DHCP pool subnet from the RouterShell database using the provided DHCP pool name.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool.

        Returns:
            str or None: The DHCP pool subnet information retrieved from the RouterShell database, or None if no match is found.
        """        
        result = DB().select_dhcp_pool_subnet_via_dhcp_pool_name(dhcp_pool_name)
        if not result.status:
            return result.result['InetSubnet']
        else:
            return None

    def add_dhcp_pool_name_db(self, dhcp_pool_name: DhcpPoolName) -> bool:
        """
        Add a DHCP pool name to the database.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool to add.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        return DB().insert_dhcp_pool_name(dhcp_pool_name).status

    def add_dhcp_pool_subnet_db(self, dhcp_pool_name: DhcpPoolName, inet_subnet_cidr: InetCidrText) -> bool:
        """
        Add a DHCP pool subnet to the database.

        Args:
            dhcp_pool_name (str): The DHCP pool name.
            inet_subnet_cidr (str): The subnet CIDR to add to the pool.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        return DB().insert_dhcp_pool_subnet(dhcp_pool_name, inet_subnet_cidr).status

    def add_dhcp_subnet_inet_address_range_db(self, inet_subnet_cidr: InetCidrText, 
                                              inet_address_start: InetAddressText, 
                                              inet_address_end: InetAddressText, 
                                              inet_address_subnet_cidr: InetCidrText) -> bool:
        """
        Add an address range to a DHCP subnet in the database.

        Args:
            inet_subnet_cidr (str): The subnet CIDR to add the address range to.
            inet_address_start (str): The start address of the range.
            inet_address_end (str): The end address of the range.
            inet_address_subnet_cidr (str): The subnet CIDR of the address range.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        return DB().insert_dhcp_subnet_inet_address_range(inet_subnet_cidr, 
                                                          inet_address_start, 
                                                          inet_address_end, 
                                                          inet_address_subnet_cidr).status

    def add_dhcp_subnet_reservation_db(self, inet_subnet_cidr: InetCidrText, hw_address: MacAddressText, inet_address: InetAddressText) -> bool:
        """
        Add a DHCP subnet reservation to the database.

        Args:
            inet_subnet_cidr (str): The subnet CIDR to add the reservation to.
            hw_address (str): The hardware address of the reservation.
            inet_address (str): The reserved IP address.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        return DB().insert_dhcp_subnet_reservation(inet_subnet_cidr, hw_address, inet_address).status

    def add_dhcp_subnet_option_db(self, inet_subnet_cidr: InetCidrText, dhcp_option: str, option_value: str) -> bool:
        """
        Add a DHCP subnet option to the database.

        Args:
            inet_subnet_cidr (str): The subnet CIDR to add the option to.
            dhcp_option (str): The DHCP option to add.
            option_value (str): The value of the DHCP option.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        return DB().insert_dhcp_subnet_option(inet_subnet_cidr, dhcp_option, option_value).status

    def add_dhcp_subnet_reservation_option_db(self, inet_subnet_cidr: InetCidrText, hw_address: MacAddressText, dhcp_option: str, option_value: str) -> bool:
        """
        Add a DHCP subnet reservation option to the database.

        Args:
            inet_subnet_cidr (str): The subnet CIDR of the reservation.
            hw_address (str): The hardware address of the reservation.
            dhcp_option (str): The DHCP option to add.
            option_value (str): The value of the DHCP option.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        return DB().insert_dhcp_subnet_reservation_option(inet_subnet_cidr, hw_address, dhcp_option, option_value).status
    
    def del_dhcp_pool_name(self, dhcp_pool_name: DhcpPoolName) -> bool:
        """
        Delete a DHCP pool by its name from the DB.
        
        Args:
            dhcp_pool_name (str): The name of the DHCP pool to be deleted.
        
        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        return DB().delete_dhcp_pool_name(dhcp_pool_name).status

    def update_dhcp_pool_name_interface(self, dhcp_pool_name: DhcpPoolName, interface_name: InterfaceName, negate: bool=False) -> bool:
        """
        Update the interface associated with a DHCP pool in the database.

        Args:
            dhcp_pool_name (str): The DHCP pool name.
            interface_name (str): The new interface name.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        return DB().update_dhcp_pool_name_interface(dhcp_pool_name, interface_name, negate).status

    def update_dhcp_pool_mode_db(self, dhcp_pool_name: DhcpPoolName, mode: DHCPv6Modes) -> bool:
        """
        Update the DHCP version mode for a specific DHCP pool.

        Parameters:
            dhcp_pool_name (str): The name of the DHCP pool.
            mode (DHCPv6Modes): The DHCP version mode to set.

        Returns:
            bool: STATUS_OK if the update is successful, STATUS_NOK otherwise.
        """
        return DB().update_dhcp_pool_dhcp_version_mode(dhcp_pool_name, mode.value).status

    '''
                                DHCP-DNSMasq - Configuration Building
    '''

    def get_global_options(self) -> list[list]:
        return []
    
    def get_dhcp_pool_interfaces_db(self, dhcp_pool_name: DhcpPoolName) -> list[dict]:
        """
        Retrieve the interfaces associated with a DHCP pool name from the database.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool.

        Returns:
            list[dict]: A list of dictionaries, each representing an interface with the 'interface_name' field,
            or an empty list if none are found.
        """
        sql_result = DB().select_dhcp_pool_interfaces(dhcp_pool_name)
                
        results = []

        for result in sql_result:
            if result.status == STATUS_OK:
                result_data = result.result
                entry = {
                    'interface_name': result_data['interface_name'],
                }
                results.append(entry)

        return results

    def get_dhcp_pool_inet_range_db(self, dhcp_pool_name: DhcpPoolName) -> list[dict]:
        """
        Retrieve the DHCP pool's internet range information from the database.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool to query.

        Returns:
            list[dict]: A list of dictionaries containing internet range information.
                Each dictionary has the following keys:
                - 'inet_start' (str): The start of the internet range.
                - 'inet_end' (str): The end of the internet range.
                - 'inet_subnet' (str): The subnet of the internet range.
        """
        sql_result = DB().select_dhcp_pool_inet_range(dhcp_pool_name)
        results = []

        for result in sql_result:
            if result.status == STATUS_OK:
                result_data = result.result
                entry = {
                    'inet_start': result_data['inet_start'],
                    'inet_end': result_data['inet_end'],
                    'inet_subnet': result_data['inet_subnet'],
                }
                results.append(entry)

        return results

    def get_dhcp_pool_reservation_db(self, dhcp_pool_name: DhcpPoolName) -> list[dict]:
        """
        Retrieve the DHCP pool's reservation information from the database.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool to query.

        Returns:
            list[dict]: A list of dictionaries containing reservation information.
                Each dictionary has the following keys:
                - 'mac_address' (str): The MAC address of the reserved device.
                - 'inet_address' (str): The internet address reserved for the device.
        """
        sql_result = DB().select_dhcp_pool_reservation(dhcp_pool_name)
        results = []

        for result in sql_result:
            if result.status == STATUS_OK:
                result_data = result.result
                entry = {
                    'mac_address': result_data['mac_address'],
                    'inet_address': result_data['inet_address'],
                }
                results.append(entry)

        return results

    def get_dhcp_pool_options_db(self, dhcp_pool_name: DhcpPoolName) -> list[dict]:
        """
        Retrieve the DHCP pool's options information from the database.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool to query.

        Returns:
            list[dict]: A list of dictionaries containing DHCP options information.
                Each dictionary has the following keys:
                - 'option' (str): The DHCP option.
                - 'value' (str): The value associated with the option.
        """
        sql_result = DB().select_dhcp_pool_options(dhcp_pool_name)
        results = []
        
        for result in sql_result:
            self.log.debug(f"get_dhcp_pool_options_db({dhcp_pool_name}) -> SQL-RESULT: {result.result}")
            if result.status == STATUS_OK:
                result_data = result.result
                entry = {
                    'option': result_data['option'],
                    'value': result_data['value'],
                }
                results.append(entry)

        return results

    

# FILE: src/routershell/lib/db/dhcpd_db-bak.py
import ipaddress
import json
import logging
from enum import Enum

from routershell.lib.common.common import STATUS_NOK, STATUS_OK


from routershell.lib.common.types import DhcpPoolName, FilePath, HostnameText, InetAddressText, InetCidrText, MacAddressText, NatPoolName
class DhcpVersion(Enum):
    DHCP_V4 = 4
    DHCP_V6 = 6

class DHCPDatabaseFactory:
    
    def __init__(self, 
                 dhcp_pool_name: DhcpPoolName, 
                 ip_subnet_mask: ipaddress.IPv4Network,
                 negate=False):
        
        self.log = logging.getLogger(self.__class__.__name__)

        self.dhcp_pool_name = dhcp_pool_name
        self.ip_subnet_mask = ip_subnet_mask
        
        self.log.debug(f"DHCPDatabaseFactory() -> dhcp_pool_name: {self.dhcp_pool_name} -> ip_subnet_mask: {self.ip_subnet_mask}")
        
        self.dhcp_version = DhcpVersion.DHCP_V4

        if not DHCPDatabase().pool_name_exists(dhcp_pool_name):
            
            pool_name_id = DHCPDatabase().get_pool_name_id(dhcp_pool_name)
            
            self.dhcp_pool_db = DHCPDatabase().get_dhcp_pool()
            print(f"DHCP-POOL-DB: {self.dhcp_pool_db}")
                
            self.kea_v4_db = DHCPDatabase().get_kea_config()
            print(f"KEA-DB: {self.kea_v4_db}")
        
            if negate:
                self.log.debug(f"Removing DHCP pool: {dhcp_pool_name}")
                
                # Delete pool-name
                if DHCPDatabase().delete_pool_name(dhcp_pool_name):
                    self.log.error(f"Unable to delete DHCP pool name: {dhcp_pool_name}")
                    return STATUS_NOK
                
                # Delete subnet associated to pool-name
                if DHCPDatabase().delete_subnet(pool_name_id):
                    self.log.error(f"Unable to delete or does not exists DHCP Subnet-ID: {pool_name_id}")
                    return STATUS_NOK
                
                self.log.debug("Remove references pointers to preserve db")
                self.kea_v4_db, self.dhcp_pool_db = None

            else:                    
                self.subnet_id = (DHCPDatabase().get_number_of_subnets(self.dhcp_version) + 1)
                
                if self._set_pool_name(dhcp_pool_name, self.subnet_id):
                    self.log.error(f"Unable to add DHCP Pool {dhcp_pool_name}")
                else:
                    self._set_subnet(ip_subnet_mask, self.dhcp_version, self.subnet_id)  
        else:
            pass

    def _set_pool_name(self, pool_name: NatPoolName, subnet_id: int = -1) -> bool:
        """
        Add a pool name to the DHCP configuration and associate it with a subnet ID.

        Args:
            pool_name (str): The name of the pool to add.
            subnet_id (int): The ID of the subnet to associate the pool with.
                Default subnet_id = -1, if subnet ID is not know at the time of add

        Returns:
            bool: STATUS_OK if the pool name was added successfully, STATUS_NOK if it already exists.
        """
        # Check if the pool name already exists
        for pool_entry in self.dhcp_pool_db["DhcpPool"]["pool-name"]:
            if pool_entry["name"] == pool_name:
                return STATUS_NOK

        # If the pool name doesn't exist, add it
        new_pool_entry = {
            "subnet-id": subnet_id,
            "name": pool_name
        }
        self.dhcp_pool_db["DhcpPool"]["pool-name"].append(new_pool_entry)
        return STATUS_OK
        
    def _set_subnet(self, ip_subnet_mask: ipaddress.IPv4Network, dhcp_version: int, subnet_id: int = 0) -> bool:
        """
        Add a new subnet to the DHCP configuration.

        Args:
            ip_subnet_mask (ipaddress.IPv4Network): The IPv4 subnet and mask in CIDR notation (e.g., "192.168.1.0/24").
            dhcp_version (int): The DHCP version (e.g., 4 for DHCPv4 or 6 for DHCPv6).
            subnet_id (int, optional): The ID of the subnet you're adding. If not provided, it will be automatically assigned based on existing subnets.

        Returns:
            bool: STATUS_OK if the subnet was successfully added to the configuration, STATUS_NOK otherwise.
        """
        if not subnet_id:
            subnet_id = (DHCPDatabase.get_number_of_subnets(dhcp_version) + 1)

        new_subnet = {
            "id": subnet_id,
            "subnet": str(ip_subnet_mask)
        }

        # Add the new subnet to the existing configuration
        self.kea_v4_db["Dhcp4"]["subnet4"].append(new_subnet)

        return STATUS_OK

    def get_subnet_pool_ID(self):
        """
        Get the ID of the subnet associated with the DHCP pool.

        Returns:
            int: The ID of the subnet, or -1 if no subnet is associated.
        """
        if hasattr(self, 'subnet_id'):
            return self.subnet_id
        else:
            self.log.error("No subnet associated with the DHCP pool.")
            return -1
    
    def get_subnet_pool(self):
        """
        Get the subnet for the DHCP pool.

        Returns:
            ipaddress.IPv4Network or ipaddress.IPv6Network: The subnet in CIDR notation.
            None: If the subnet is not defined or an error occurs.
        """
        try:
            if self.ip_subnet_mask is not None:
                return self.ip_subnet_mask
            else:
                self.log.error("Subnet is not defined.")
        except Exception as e:
            self.log.error(f"Error while getting the subnet: {str(e)}")
        
        return None

    def add_pool(self, pool_id: int, ip_address_start, ip_address_end, subnet_mask):
        """
        Add a new IP address pool to the DHCP configuration, supporting both IPv4 and IPv6.

        Args:
            pool_id (int): The ID of the pool to be added.
            ip_address_start (str): The start IP address of the pool.
            ip_address_end (str): The end IP address of the pool.
            subnet_mask (str): The subnet mask in CIDR notation (e.g., "24" for a /24 subnet).

        Returns:
            bool: STATUS_OK if the pool was successfully added, STATUS_NOK if there was an error.
        """
        subnet_pool = self.get_subnet_pool()  # Check if a subnet is defined
        if subnet_pool is None:
            self.log.error("Cannot add a pool. Subnet is not defined.")
            return STATUS_NOK
        
        try:
            ip_subnet_pool = ipaddress.ip_address(subnet_pool)
            ip_start = ipaddress.ip_address(ip_address_start)
            ip_end = ipaddress.ip_address(ip_address_end)

            if ip_start.version == ip_end.version == ip_subnet_pool.version:
                
                dhcp_version = DhcpVersion.DHCP_V4 if subnet_pool.version == 4 else DhcpVersion.DHCP_V6
                subnet_key = f"subnet{dhcp_version}"
                
                if ip_subnet_pool.network_address <= ip_start <= ip_end <= ip_subnet_pool.broadcast_address:
                    
                    subnet_pool_id = self.get_subnet_pool_ID()

                    # Create the dhcp pool entry
                    dhcp_pool_entry = {
                        "pool": f"{ip_address_start} - {ip_address_end}",
                        "option-data": f"[subnet-mask: {subnet_mask}]"
                    }
                                   
                    if "pools" not in self.kea_v4_db["Dhcp4"][subnet_key][subnet_pool_id]:
                        self.log.debug("add_pool() -> pools entry not found -> adding pools array entry")
                        self.kea_v4_db["Dhcp4"][subnet_key][subnet_pool_id]["pools"] = []

                    self.kea_v4_db["Dhcp4"][subnet_key][subnet_pool_id]["pools"].append(pool_entry)

                    # Add the pool_id entry to dhcp_pool_db
                    dhcp_pool_entry = {
                        "pool-id": pool_id,
                        "pool-name": pool_name
                    }
                    self.dhcp_pool_db["DhcpPool"]["pool-name"].append(pool_entry)

                    return STATUS_OK
                else:
                    self.log.error("IP address range is not within the specified subnet.")
            else:
                self.log.error("Invalid IP address types. Ensure they are all IPv4 or IPv6.")
        except (ipaddress.AddressValueError, ValueError):
            self.log.error("Invalid IP address or subnet mask format.")

        return STATUS_NOK


class DHCPDatabase:
    """
    DHCPDatabase class for managing DHCP configuration.
    """

    dhcp_pool_default = {
        "DhcpPool": {
            "pool-name": [
                {
                    "name" : "dhcp-pool-1",
                    "pools" : [
                        {
                            "id" : 0,
                            "subnet-range": "",
                        }
                    ]
                }
            ]     
        }
    }
        
    dhcp_pool = {
        "DhcpPool": {
            "pool-name": [
            ]
        }
    }

    kea_v4_db = {
        "Dhcp4": {
            "valid-lifetime": 4000,
            "renew-timer": 1000,
            "rebind-timer": 2000,
            "interfaces-config": {
                "interfaces": [""],
                "service-sockets-max-retries": 5,
                "service-sockets-retry-wait-time": 5000
            },
            "lease-database": {
                "type": "memfile",
                "persist": True,
                "name": "/var/lib/kea/dhcp4.leases"
            },
            "subnet4": []
        }
    }
 
    kea_v6_db = {
        "Dhcp6": {
            "valid-lifetime": 4000,
            "renew-timer": 1000,
            "rebind-timer": 2000,
            "interfaces-config": {
                "interfaces": [""],
                "service-sockets-max-retries": 5,
                "service-sockets-retry-wait-time": 5000
            },
            "lease-database": {
                "type": "memfile",
                "persist": True,
                "name": "/var/lib/kea/dhcp4.leases"
            },
            "subnet6": []
        }
    }
    
    def __init__(self, config_file: FilePath | None = None):
        """
        Initialize the DHCPDatabase instance.

        Args:
            config_file (str, optional): The path to the DHCP configuration file.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.config_file = config_file

    def add_subnet(self, subnet_id: int, subnet_range: InetCidrText, client_class: str="", relay_ip: InetAddressText=""):
        """
        Add a subnet to the DHCP configuration.

        Args:
            subnet_id (int): The unique ID of the subnet.
                pass
        subnet_range (str): The range of IP addresses for the subnet.
            client_class (str): The client class for the subnet.
            relay_ip (str): The IP address of the relay agent for the subnet.
        """
        # Create a new subnet configuration
        new_subnet = {
            "id": subnet_id,
            "subnet": subnet_range,
            "pools": [],
            "client-class": client_class,
            "relay": {
                "ip-addresses": [relay_ip]
            }
        }

        # Add the new subnet to the existing configuration
        self.kea_v4_db["Dhcp4"]["subnet4"].append(new_subnet)

    def add_reservation_to_subnet(self, subnet_id: int, mac: MacAddressText, ip: str, hostname: HostnameText = ""):
        """
        Add a reservation to a subnet.

        Args:
            subnet_id (int): The ID of the subnet to add the reservation to.
            mac (str): The MAC address of the reserved client.
            ip (str): The reserved IP address.
            hostname (str, optional): The hostname for the reserved client.
        """
        ip_address = ipaddress.IPv4Address(ip)

        new_reservation = {
            "hw-address": mac,
            "ip-address": str(ip_address),  # Convert the IP address back to a string
            "hostname": hostname
        }

        # Find the subnet with the given ID
        for subnet in self.kea_v4_db["Dhcp4"]["subnet4"]:
            if subnet["id"] == subnet_id:
                # Append the new reservation to the reservations list in the pool
                subnet["pools"][0]["reservations"].append(new_reservation)
                break  # Exit the loop once the subnet is found

    def add_pool_to_subnet(self, subnet_id: int, ip_pool_start: InetAddressText, ip_pool_end: InetAddressText):
        """
        Add an IP pool to a subnet.

        Args:
            subnet_id (int): The ID of the subnet to add the pool to.
            ip_pool_start (str): The start IP address of the pool.
            ip_pool_end (str): The end IP address of the pool.
        """
        # Find the subnet with the given ID
        for subnet in self.kea_v4_db["Dhcp4"]["subnet4"]:
            if subnet["id"] == subnet_id:
                # Create a new pool configuration
                new_pool = {
                    "pool": f"{ip_pool_start} - {ip_pool_end}",
                    "reservations": []
                }
                # Append the new pool to the subnet's pools list
                subnet["pools"].append(new_pool)
                break  # Exit the loop once the subnet is found

    def add_pool_name(self, pool_name: NatPoolName, subnet_id: int = -1) -> bool:
        """
        Add a pool name to the DHCP configuration and associate it with a subnet ID.

        Args:
            pool_name (str): The name of the pool to add.
            subnet_id (int): The ID of the subnet to associate the pool with.
                Default subnet_id = -1, if subnet ID is not know at the time of add

        Returns:
            bool: STATUS_OK if the pool name was added successfully, STATUS_NOK if it already exists.
        """
        # Check if the pool name already exists
        for pool_entry in self.dhcp_pool["DhcpPool"]["pool-name"]:
            if pool_entry["name"] == pool_name:
                return STATUS_NOK  # Pool name already exists

        # If the pool name doesn't exist, add it
        new_pool_entry = {
            "subnet-id": subnet_id,
            "name": pool_name
        }
        self.dhcp_pool["DhcpPool"]["pool-name"].append(new_pool_entry)
        return STATUS_OK  # Pool name added successfully

    def update_pool_name(self, pool_name: NatPoolName, new_subnet_id: int) -> bool:
        """
        Update the subnet ID associated with a pool name in the DHCP configuration.

        Args:
            pool_name (str): The name of the pool to update.
            new_subnet_id (int): The new subnet ID to associate with the pool.

        Returns:
            bool: STATUS_OK if the pool name was updated successfully, STATUS_NOK if the pool name doesn't exist.
        """
        # Find the pool entry by name
        for pool_entry in self.dhcp_pool["DhcpPool"]["pool-name"]:
            if pool_entry["name"] == pool_name:
                # Update the subnet ID
                pool_entry["subnet-id"] = new_subnet_id
                return STATUS_OK  # Pool name updated successfully

        # If the pool name doesn't exist, return False
        return STATUS_NOK

    def get_number_of_subnets(self, dhcp_version: DhcpVersion = DhcpVersion.DHCP_V4) -> int:
        """
        Get the number of subnets based on the DHCP version.

        Args:
            dhcp_version (DhcpVersion, optional): Enum representing the DHCP version (DhcpVersion.DHCPv4 or DhcpVersion.DHCPv6).
                Defaults to DhcpVersion.DHCPv4.

        Returns:
            int: The number of subnets based on the specified DHCP version.
        """
        # Determine the appropriate key based on the DHCP version
        subnet_key = "subnet4" if dhcp_version == DhcpVersion.DHCP_V4 else "subnet6"
        
        self.log.debug(f"get_number_of_subnets() -> dhcp-version: {dhcp_version} -> Key: {subnet_key}")

        # Check if the specified key exists in the configuration
        if subnet_key in self.kea_v4_db["Dhcp4"]:
            return len(self.kea_v4_db["Dhcp4"][subnet_key])
        else:
            return 0

    def pool_name_exists(self, pool_name: NatPoolName) -> bool:
        """
        Check if a pool name exists in the DHCP configuration.

        Args:
            pool_name (str): The pool name to check.

        Returns:
            bool: True if the pool name exists, False otherwise.
        """
        # Check if the pool name exists
        for pool_entry in self.dhcp_pool["DhcpPool"]["pool-name"]:
            if pool_entry["name"] == pool_name:
                return True  # Pool name exists
        return False  # Pool name does not exist

    def update_global_config(self, dhcp_option: str, value: str | int | bool, dhcp_version: int = 0):
        """
        Update a key-value pair in the global DHCP configuration.

        Args:
            dhcp_option (str): The DHCP option to update in the global configuration.
            value (str | int | bool): The new value for the DHCP option.
            dhcp_version (int, optional): 0 for DHCPv4, 1 for DHCPv6.

        Raises:
            ValueError: If the specified DHCP version is invalid.
        """
        # Check if the DHCP version is valid
        if dhcp_version not in [0, 1]:
            raise ValueError("Invalid DHCP version. Use 0 for DHCPv4 or 1 for DHCPv6.")

        # Get the appropriate DHCP configuration based on the version
        dhcp_config = self.kea_v4_db if dhcp_version == 0 else self.kea_dhcpv6_config

        # Check if the key exists in the global configuration
        if dhcp_option in dhcp_config["Dhcp4"]:
            dhcp_config["Dhcp4"][dhcp_option] = value
        else:
            # Append the new key-value pair to the global configuration
            dhcp_config["Dhcp4"][dhcp_option] = value

    def save_config_to_file(self):
        """
        Save the current DHCP configuration to the specified configuration file.
        """
        # Save the updated configuration back to the file
        with open(self.config_file, 'w') as file:
            json.dump(self.kea_v4_db, file, indent=4)

    def get_copy_dhcp_pool(self) -> str:
        """
        Get a deep copy of the DHCP pool configuration as a JSON string.

        Returns:
            str: A JSON string representing the DHCP pool configuration.
        """
        return json.dumps(self.dhcp_pool)

    def get_copy_kea_dhcpv4_config(self) -> str:
        """
        Get a deep copy of the KEA DHCPv4 configuration as a JSON string.

        Returns:
            str: A JSON string representing the KEA DHCPv4 configuration.
        """
        return json.dumps(self.kea_v4_db)
    
    def get_dhcp_pool(self):
        """
        Get the DHCP pool configuration.

        Returns:
            dict: The DHCP pool configuration.
        """
        return self.dhcp_pool

    def get_kea_config(self):
        """
        Get the Kea DHCPv4 configuration.

        Returns:
            dict: The Kea DHCPv4 configuration.
        """
        return self.kea_v4_db

    def delete_pool_name(self, pool_name:NatPoolName) -> bool:
        """
        Delete a DHCP pool by name.

        Args:
            pool_name (str): The name of the DHCP pool to delete.

        Returns:
            bool: STATUS_OK if the pool was successfully deleted, STATUS_NOK if the pool was not found.
        """
        if pool_name in self.dhcp_pool["DhcpPool"]["pool-name"]:
            self.dhcp_pool["DhcpPool"]["pool-name"].remove(pool_name)
            return STATUS_OK
        return STATUS_NOK

    def delete_subnet(self, subnet_id: int) -> bool:
        """
        Delete a DHCP subnet by ID.

        Args:
            subnet_id (int): The ID of the DHCP subnet to delete.

        Returns:
            bool: STATUS_OK if the subnet was successfully deleted, STATUS_NOK if the subnet was not found.
        """
        for subnet in self.kea_v4_db["Dhcp4"]["subnet4"]:
            if subnet["id"] == subnet_id:
                self.kea_v4_db["Dhcp4"]["subnet4"].remove(subnet)
                return STATUS_OK
        return STATUS_NOK

    def get_pool_name_id(self, pool_name:NatPoolName) -> int:
        """
        Get the ID of a DHCP pool by its name.

        Args:
            pool_name (str): The name of the DHCP pool to retrieve the ID for.

        Returns:
            int: The ID of the DHCP pool if found, or None if the pool was not found, Error = -1.
        """
        if not pool_name:
            self.log.error(f"get_pool_name_id -> {pool_name}")
            return -1
        
        pool_names = self.dhcp_pool["DhcpPool"]["pool-name"]
        if pool_name in pool_names:
            return pool_names.index(pool_name)
        return None

class DhcpOptionsLUT:
    '''https://kea.readthedocs.io/en/latest/arm/dhcp4-srv.html#interface-configuration'''
    
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        
        self.dhcp_options = {
            "time-offset": "int",
            "routers": "ipaddress",
            "time-servers": "ipaddress",
            "name-servers": "ipaddress",
            "domain-name-servers": "ipaddress",
            "log-servers": "ipaddress",
            "cookie-servers": "ipaddress",
            "lpr-servers": "ipaddress",
            "impress-servers": "ipaddress",
            "resource-location-servers": "ipaddress",
            "boot-size": "int",
            "merit-dump": "string",
            "domain-name": "fqdn",
            "swap-server": "ipaddress",
            "root-path": "string",
            "extensions-path": "string",
            "ip-forwarding": "boolean",
            "non-local-source-routing": "boolean",
            "policy-filter": "ipaddress",
            "max-dgram-reassembly": "int",
            "default-ip-ttl": "int",
            "path-mtu-aging-timeout": "int",
            "path-mtu-plateau-table": "int",
            "interface-mtu": "int",
            "all-subnets-local": "boolean",
            "broadcast-address": "ipaddress",
            "perform-mask-discovery": "boolean",
            "mask-supplier": "boolean",
            "router-discovery": "boolean",
            "router-solicitation-address": "ipaddress",
            "static-routes": "ipaddress",
            "trailer-encapsulation": "boolean",
            "arp-cache-timeout": "int",
            "ieee802-3-encapsulation": "boolean",
            "default-tcp-ttl": "int",
            "tcp-keepalive-interval": "int",
            "tcp-keepalive-garbage": "boolean",
            "nis-domain": "string",
            "nis-servers": "ipaddress",
            "ntp-servers": "ipaddress",
            "vendor-encapsulated-options": "empty",
            "netbios-name-servers": "ipaddress",
            "netbios-dd-server": "ipaddress",
            "netbios-node-type": "int",
            "netbios-scope": "string",
            "font-servers": "ipaddress",
            "x-display-manager": "ipaddress",
            "dhcp-option-overload": "int",
            "dhcp-server-identifier": "ipaddress",
            "dhcp-message": "string",
            "dhcp-max-message-size": "int",
            "vendor-class-identifier": "string",
            "nwip-domain-name": "string",
            "nwip-suboptions": "binary",
            "nisplus-domain-name": "string",
            "nisplus-servers": "ipaddress",
            "tftp-server-name": "string",
            "boot-file-name": "string",
            "mobile-ip-home-agent": "ipaddress",
            "smtp-server": "ipaddress",
            "pop-server": "ipaddress",
            "nntp-server": "ipaddress",
            "www-server": "ipaddress",
            "finger-server": "ipaddress",
            "irc-server": "ipaddress",
            "streettalk-server": "ipaddress",
            "streettalk-directory-assistance-server": "ipaddress",
            "user-class": "binary",
            "slp-directory-agent": "record (boolean, ipaddress)",
            "slp-service-scope": "record (boolean, string)",
            "nds-server": "ipaddress",
            "nds-tree-name": "string",
            "nds-context": "string",
            "bcms-controller-names": "fqdn",
            "bcms-controller-address": "ipaddress",
            "client-system": "int",
            "client-ndi": "record (int, int, int)",
            "uuid-guid": "record (int, binary)",
            "uap-servers": "string",
            "geoconf-civic": "binary",
            "pcode": "string",
            "tcode": "string",
            "v6-only-preferred": "int",
            "netinfo-server-address": "ipaddress",
            "netinfo-server-tag": "string",
            "v4-captive-portal": "string",
            "auto-config": "int",
            "name-service-search": "int",
            "domain-search": "fqdn",
            "vivco-suboptions": "record (int, binary)",
            "vivso-suboptions": "int",
            "pana-agent": "ipaddress",
            "v4-lost": "fqdn",
            "capwap-ac-v4": "ipaddress",
            "sip-ua-cs-domains": "fqdn",
            "v4-sztp-redirect": "tuple",
            "rdnss-selection": "record (int, ipaddress, ipaddress, fqdn)",
            "v4-portparams": "record (int, psid)",
            "v4-dnr": "record (int, int, int, fqdn, binary)",
            "option-6rd": "record (int, int, ipv6-address, ipaddress)",
            "v4-access-domain": "fqdn"
        }

    def dhcp_option_exists(self, dhcp_option: str) -> bool:
        """
        Verify if DHCP option exists in the DHCP configuration options.

        Args:
            key (str): The key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        return dhcp_option in self.dhcp_options

    def get_data_type(self, dhcp_option: str) -> None | str:
        """
        Get the data type associated with a key in the DHCP configuration options.

        Args:
            key (str): The key to retrieve the data type for.

        Returns:
            None | str: The data type of the key, or None if the key does not exist.
        """
        if self.dhcp_option_exists(dhcp_option):
            return self.dhcp_options[dhcp_option]
        else:
            return None


# FILE: src/routershell/lib/db/interface_db.py
import logging
import re

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import (
    BridgeName,
    InetAddressText,
    InterfaceName,
    InterfaceTypeName,
    MacAddressText,
    NatPoolName,
)
from routershell.lib.db.sqlite_db.router_shell_db import Result
from routershell.lib.db.sqlite_db.router_shell_db import RouterShellDB as DB
from routershell.lib.network_manager.common.interface import InterfaceType
from routershell.lib.network_manager.network_operations.nat import NATDirection


class InterfaceDatabase:

    rsdb = DB()
    
    def __init__(cls):
        cls.log = logging.getLogger(cls.__class__.__name__)
        cls.log.setLevel(RSLS().INTERFACE_DB)
        
        if not cls.rsdb:
            cls.log.debug("Connecting RouterShell Database")
            cls.rsdb = DB()  
            
    def db_lookup_interface_exists(cls, interface_name: InterfaceName) -> Result:
        """
        Check if an interface with the given name exists in the database.

        Args:
            interface_name (str): The name of the interface to check.

        Returns:
            Result: A Result object with the status and row ID of the existing interface.

        Example:
            You can use this method to determine whether a specific interface exists in the database.
            For instance, you might check if 'GigabitEthernet0/1' exists.

        Note:
            - The 'Result' object returned indicates the status of the interface existence.
            - 'status' True means the interface exists, and 'status' False means it does not.
        """
        return cls.rsdb.interface_exists(interface_name)

    def add_db_interface(
        cls, interface_name: InterfaceName, interface_type: InterfaceType, shutdown_status: bool = True) -> bool:
        """
        Add an interface to the database.

        Args:
            interface_name (str): The name of the interface to add.
            interface_type (str): The type of the interface.
            shutdown_status (bool, optional): True if the interface is shutdown, False otherwise (default is True).

        Returns:
            bool: STATUS_OK if the interface was successfully added, STATUS_NOK if there was an issue.
        """
        cls.log.debug(f"add_interface() -> {interface_name} -> {interface_type} -> {shutdown_status}")
        
        result = cls.rsdb.insert_interface(interface_name, interface_type, shutdown_status)

        if result.status:
            cls.log.debug(f"add_interface() - Unable to add interface to DB -> {result.reason}")
            return STATUS_NOK
        
        return STATUS_OK

    def del_db_interface(cls, interface_name: InterfaceName) -> bool:
        """
        Delete an interface from the 'Interfaces' table.

        Args:
            interface_name (str): The name of the interface to delete.

        Returns:
            bool: STATUS_OK if the deletion was successful, STATUS_OK otherwise.
        """
        result = cls.rsdb.delete_interface(interface_name)
        
        return result.status
 
    def update_db_shutdown_status(cls, interface_name: InterfaceName, shutdown_status: bool) -> bool:
        """
        Update the shutdown status of an interface in the 'Interfaces' table.

        Args:
            interface_name (str): The name of the interface to update.
            shutdown_status (bool): The new shutdown status.

        Returns:
            bool: STATUS_OK if the update was successful, STATUS_NOK otherwise.
        """
        result = cls.rsdb.update_interface_shutdown(interface_name, shutdown_status)
        return result.status

    def update_db_duplex(cls, interface_name: InterfaceName, duplex: str) -> bool:
        """
        Update the duplex status of an interface in the 'Interfaces' table.

        Args:
            interface_name (str): The name of the interface to update.
            duplex (str): The new duplex status.

        Returns:
            bool: STATUS_OK if the update was successful, STATUS_NOK otherwise.
        """
        return cls.rsdb.update_interface_duplex(interface_name, duplex).status
    
    def update_db_mac_address(cls, interface_name: InterfaceName, mac_address: MacAddressText) -> bool:
        """
        Update the MAC address setting of an interface in the 'InterfaceSubOptions' table.

        Args:
            interface_name (str): The name of the interface to update.
            mac_address (str): MAC address in the format xx:xx:xx:xx:xx:xx.

        Returns:
            bool: STATUS_OK if the MAC address was successfully updated, STATUS_NOK otherwise.
        """

        # Check MAC address format using a regular expression
        mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')

        if not mac_pattern.match(mac_address):
            cls.log.error(f"Invalid mac address format: {mac_address} -> xx:xx:xx:xx:xx:xx")
            return STATUS_NOK

        result = cls.rsdb.update_interface_mac_address(interface_name, mac_address)
        return result.status

    def update_db_ifSpeed(cls, interface_name: InterfaceName, speed: str) -> bool:
        """
        Update the speed setting of an interface in the 'InterfaceSubOptions' table.

        Args:
            interface_name (str): The name of the interface to update.
            speed (str): The speed setting (e.g., '10', '100', '1000', '10000', 'auto', None).

        Returns:
            bool: STATUS_OK if the speed was successfully updated, STATUS_NOK otherwise.
        """
        cls.log.debug(f"update_speed() -> Interface: {interface_name} -> Speed: {speed}")
        
        result = cls.rsdb.update_interface_speed(interface_name, speed)
        return result.status

    def update_db_inet_address(
        cls, interface_name, inet_address_cidr, secondary=False, negate=False) -> bool:
        """
        Update or delete an IP address setting for an interface.

        Args:
            interface_name (str): The name of the interface.
            inet_address_cidr (str): The IP address/mask to update or delete.
            secondary (bool): True if the IP address is secondary, False otherwise.
            negate (bool): True to delete the IP address, False to update.

        Returns:
            bool: bool: STATUS_OK if the speed was successfully updated, STATUS_NOK otherwise.
        """
        if not negate:
            result = cls.rsdb.insert_interface_inet_address(interface_name, inet_address_cidr, secondary)
        else:
            result = cls.rsdb.delete_interface_inet_address(interface_name, inet_address_cidr)

        return result.status
    
    def add_line_to_interface(cls, line: str) -> bool:
        """
        Add a router CLI command to the database to save as a configuration.

        Args:
            line (str): The router CLI command to be added to the database.

        Returns:
            bool: STATUS_OK if the command was successfully added to the database, STATUS_NOK otherwise.

        Example:
            You can use this method to save router CLI commands to the database for configuration management.
            For instance, you might add a line like 'interface GigabitEthernet0/0' to configure an interface.

        Usage:
            if add_line_to_interface('interface GigabitEthernet0/0'):
                print("Command added to the database.")
            else:
                print("Failed to add the command.")

        Note:
            - This method stores router CLI commands for configuration purposes.
            - STATUS_OK indicates a successful addition, while STATUS_NOK indicates a failure.
        """
        return STATUS_OK
    
    def update_db_proxy_arp(cls, interface_name: InterfaceName, status: bool) -> bool:
        """
        Update the Proxy ARP status for a network interface to DB

        Args:
            interface_name (str): The name of the network interface.
            status (bool): The new Proxy ARP status (True for enabled, False for disabled).

        Returns:
            Result: STATUS_OK if the update was successful, STATUS_NOK otherwise.
        """
        cls.log.debug(f"update_proxy_arp_db() -> Interface: {interface_name} -> status:{status}")
        result = cls.rsdb.update_interface_proxy_arp(interface_name, status)
        return result.status

    def update_db_drop_gratuitous_arp(cls, interface_name: InterfaceName, status: bool) -> bool:
        """
        Update the Drop Gratuitous ARP status for a network interface.

        Args:
            interface_name (str): The name of the network interface.
            status (bool): The new Drop Gratuitous ARP status (True for enabled, False for disabled).

        Returns:
            bool: STATUS_OK if the update was successful, STATUS_NOK otherwise.
        """
        result = cls.rsdb.update_interface_drop_gratuitous_arp(interface_name, status)
        return result.status
    
    def update_db_static_arp(
        cls, interface_name: InterfaceName, ip_address: InetAddressText, mac_address: MacAddressText, encapsulation: str='arpa', negate=False) -> bool:
        """
        Update a static ARP record in the 'InterfaceStaticArp' table.

        Args:
            ip_address (str): The IP address to update.
            mac_address (str): The new MAC address in the format: xx:xx:xx:xx:xx:xx.
            encapsulation (str): The new encapsulation type, e.g., 'arpa' or 'TBD'.
            negate (bool): True to negate the update (i.e., remove the record), False to perform the update.

        Returns:
            bool: STATUS_OK if the update (or deletion) was successful, STATUS_NOK otherwise.
        """
        if not negate:
            cls.log.debug(f"update_static_arp(INSERT) Interface: {interface_name} -> Arp: -> inet: {ip_address} mac: {mac_address}")
            result = cls.rsdb.update_interface_static_arp(interface_name, ip_address, mac_address, encapsulation)
        else:
            cls.log.debug(f"update_static_arp(DELETE) Interface: {interface_name} -> Arp: -> inet: {ip_address}")
            result = cls.rsdb.delete_interface_static_arp(interface_name, ip_address)

        return result.status

    def update_db_nat_direction(
        cls, interface_name: InterfaceName, nat_pool_name: NatPoolName, nat_direction: NATDirection, negate: bool = False) -> bool:
        """
        Update a NAT direction configuration for a specified interface and NAT pool.

        Args:
            interface_name (str): The name of the interface for the NAT direction.
            nat_pool_name (str): The name of the NAT pool associated with the direction.
            nat_direction (NATDirection): The NAT direction to update.
            negate (bool): Whether to negate the update (i.e., remove the direction if True) (default: False).

        Returns:
            bool: True if the update was successful, False otherwise.

        This method allows you to update a NAT direction configuration for a specific interface and NAT pool. 
        You can either add or remove a NAT direction, based on the `negate` parameter.

        Args:
            - interface_name (str): The name of the interface for the NAT direction.
            - nat_pool_name (str): The name of the NAT pool associated with the direction.
            - nat_direction (NATDirection): The NAT direction to update.
            - negate (bool): If True, the method will remove the NAT direction. If False, it will add the direction (default: False).

        Returns:
            - bool: STATUS_OK if the update was successful, STATUS_NOK if there was an error during the update.

        """
        try:
            if not cls.rsdb.global_nat_pool_name_exists(nat_pool_name):
                cls.log.debug(f"NAT pool '{nat_pool_name}' not found. Update aborted.")
                return STATUS_NOK

            interface_result = cls.db_lookup_interface_exists(interface_name)
            if not interface_result.status:
                cls.log.debug(f"Interface '{interface_name}' not found. Update aborted.")
                return STATUS_NOK

            if negate:
                cls.log.debug(f"Deleting NAT direction: {nat_direction.value} -> interface '{interface_name}' -> NAT Pool '{nat_pool_name}'")
                result = cls.rsdb.delete_interface_nat_direction(interface_name, nat_pool_name)
                if result.status:
                    cls.log.error(f"Unable to delete NAT direction: {nat_direction.value} -> interface '{interface_name}' -> NAT Pool '{nat_pool_name}' error: {result.reason}")
                    return STATUS_NOK
            else:
                cls.log.debug(f"Inserting NAT direction: {nat_direction.value} -> Interface '{interface_name}' -> NAT Pool '{nat_pool_name}'")
                result = cls.rsdb.insert_interface_nat_direction(interface_name, nat_pool_name, nat_direction.value)
                if result.status:
                    cls.log.error(f"Unable to Insert NAT direction: {nat_direction.value} -> interface '{interface_name}' -> NAT Pool '{nat_pool_name}' error: {result.reason}")
                    return STATUS_NOK
            
            return result.status == STATUS_OK

        except Exception as e:
            error_message = f"Error updating NAT direction: {e}"
            cls.log.error(error_message)
            return STATUS_NOK

    def update_db_bridge_group(cls, interface_name: InterfaceName, bridge_group: BridgeName, negate: bool = False) -> bool:
        """
        Update the bridge group for an interface.

        Args:
            interface_name (str): The name of the interface to update.
            bridge_group (str): The name of the bridge group to assign or remove.
            negate (bool):  If True, remove the interface from the bridge group. 
                            If False, assign the interface to the bridge group.

        Returns:
            bool: STATUS_OK if the update was successful, STATUS_NOK otherwise.
        """
        if negate:
            result = cls.rsdb.delete_interface_bridge_group(interface_name, bridge_group)
            cls.log.debug(f"Removed interface '{interface_name}' from bridge group '{bridge_group}'")
        else:
            result = cls.rsdb.insert_interface_bridge_group(interface_name, bridge_group)
            cls.log.debug(f"Assigned interface '{interface_name}' to bridge group '{bridge_group}'")

        return STATUS_OK if result.status == STATUS_OK else STATUS_NOK

    def update_db_vlan_to_interface_type(cls, vlan_id: int, interface_type_name: InterfaceTypeName, interface_type: InterfaceType, negate: bool = False) -> bool:
        """
        Update the VLAN configuration for a specific interface type.

        Args:
            vlan_id (int): The VLAN ID to configure.
            interface_type_name (str): The name of the interface type (BridgeName or InterfaceName) to update.
            interface_type (InterfaceType): The new interface type (BRIDGE or ETHERNET).
            negate (bool, optional): True to negate the configuration, False otherwise. Defaults to False.

        Returns:
            bool: STATUS_OK if the update was successful, STATUS_NOK otherwise.
        """
        pass

    def update_db_rename_alias(cls, bus_info: str, initial_interface_name: InterfaceName, alias_interface_name: InterfaceName) -> bool:
        """
        Update or create an alias for an initial interface and check if they match.

        Args:
            initial_interface_name (str): The name of the initial interface.
            alias_interface_name (str): The name of the alias interface.

        Returns:
            bool: STATUS_OK if the alias was successfully updated or created and the names match, STATUS_NOK otherwise.

        """
        alias_result = cls.rsdb.is_initial_interface_alias_exist(initial_interface_name)

        if alias_result.status:
            if alias_result.result['AliasInterface'] == alias_interface_name:
                return STATUS_OK
            else:
                return STATUS_NOK
        
        return cls.rsdb.update_interface_alias(bus_info, initial_interface_name, alias_interface_name).status

    def get_db_interface_aliases(cls) -> list[dict]:
        """
        Get a list of dictionaries representing interface aliases from the InterfaceAlias table.

        Returns:
            list[dict]: A list of dictionaries containing interface alias information.
                Each dictionary includes the following key-value pairs:
                - 'InterfaceName' (str): The name of the primary network interface.
                - 'AliasInterface' (str): The alias name associated with the primary network interface.
        """
        result_list = cls.rsdb.select_interface_aliases()

        aliases_data = [{'InterfaceName': result.result['InterfaceName'], 'AliasInterface': result.result['AliasInterface']} 
                        for result in result_list if result.status == STATUS_OK]

        return aliases_data

    def db_lookup_interface_alias_exist(cls, initial_interface_name: InterfaceName, alias_interface_name: InterfaceName) -> bool:
        """
        Check if an alias exists for the given initial interface and alias name.

        Args:
            initial_interface_name (str): The name of the initial interface.
            alias_interface_name (str): The name of the alias interface.

        Returns:
            bool: True if an alias exists for the initial interface with the provided alias name, False otherwise.
        """
        alias_result = cls.rsdb.is_initial_interface_alias_exist(initial_interface_name)

        return alias_result.status and alias_result.result == alias_interface_name

    def update_db_interface_name(cls, old_interface_name:InterfaceName, new_interface_name:InterfaceName) -> bool:
        """
        Update the database with a new name for a network interface.

        This class method delegates the task of updating the interface name to the underlying
        network interface manager's 'update_interface_name' method.

        Args:
            old_interface_name (str): The current name of the network interface to be updated.
            new_interface_name (str): The new name to assign to the network interface.

        Returns:
            bool: True if the update process is successful, False otherwise.
        """        
        return cls.rsdb.update_interface_name(old_interface_name, new_interface_name).status

    def update_db_description(cls, interface_name:InterfaceName, description:str) -> bool:
        """
        Update the description of an interface in the database.

        Args:
            interface_name (str): The name of the interface to update.
            description (str): The new description to set for the interface.

        Returns:
            bool: STATUS_OK if the update operation is successful, STATUS_NOK otherwise.
        """
        if not description:
            description = ""
                    
        result = cls.rsdb.update_interface_description(interface_name, description)
        return result.status

    def get_db_interface_names(cls) -> list[str]:
        """
        Get a list of all interface names from the database.

        Returns:
            list[str]: A list containing the names of all interfaces in the database.
        """
        results = cls.rsdb.select_interfaces()

        interfaces = []

        for result in results:
            interfaces.append(result.result['InterfaceName'])

        return interfaces

    def get_interface_details(cls) -> list[dict]:
        """
        Retrieve comprehensive details for all network interfaces defined in the DB.

        Returns:
            list[dict]: A list of dictionaries containing interface details.

        Description:
            This method fetches detailed information for all network interfaces stored in the database.
            The information is organized into a list of dictionaries, each representing the details for an individual interface.

        Structure of Each Dictionary:
            {
                'Interfaces': {
                    'InterfaceName': str,
                    'ShutdownStatus': str,
                    'Description': str,
                },
                'Properties': {
                    'InterfaceType': str,
                    'MacAddress': str,
                    'Duplex': str,
                    'Speed': str,
                    'ProxyArp': str,
                    'DropGratArp': str,
                },
                'Alias': {
                    'InitialInterface': str,
                    'AliasInterface': str,
                }
            }
        """
        
        results = cls.rsdb.select_interface_details()

        interface_details_list = []

        for result in results:
            interface_dict = {
                'Interfaces': {
                    'InterfaceName': result.result.get('InterfaceName', ''),
                    'Description': result.result.get('Description', ''),
                    'ShutDownStatus': result.result.get('ShutdownStatus', ''),
                    
                    'Properties': {
                        'InterfaceType': result.result.get('InterfaceType', ''),
                        'MacAddress': result.result.get('MacAddress', ''),
                        'Duplex': result.result.get('Duplex', ''),
                        'Speed': result.result.get('Speed', ''),
                        'ProxyArp': result.result.get('ProxyArp', ''),
                        'DropGratArp': result.result.get('DropGratuitousArp', ''),
                    },
                    
                    'Alias': {
                        'InitialInterface': result.result.get('InitialInterface', ''),
                        'AliasInterface': result.result.get('AliasInterface', ''),
                    }
                }
            }
         
            interface_details_list.append(interface_dict)

        return interface_details_list
        

# FILE: src/routershell/lib/db/nat_db.py
import logging

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import InterfaceName, NatPoolName
from routershell.lib.db.sqlite_db.router_shell_db import Result
from routershell.lib.db.sqlite_db.router_shell_db import RouterShellDB as DB


class NatDB:

    rsdb = DB()
    
    def __init__(cls):
        cls.log = logging.getLogger(cls.__class__.__name__)
        cls.log.setLevel(RSLS().NAT_DB)
        
        if not cls.rsdb:
            cls.log.debug("Connecting RouterShell Database")
            cls.rsdb = DB()  

    def pool_name_exists(cls, pool_name: NatPoolName) -> bool:
        """
        Check if a NAT pool with the given name exists in the NAT database.

        Args:
            pool_name (str): The name of the NAT pool to check for existence.

        Returns:
            bool: True if a NAT pool with the specified name exists, False otherwise.

        """
        cls.log.debug(f"pool_name_exists() Pool-Name: {pool_name}")
        return cls.rsdb.global_nat_pool_name_exists(pool_name).status
       
    def insert_global_nat_pool_name(cls, pool_name: NatPoolName) -> bool:
        """
        Create a new global NAT pool configuration in the NAT database.

        Args:
            pool_name (str): The name of the NAT pool to create.

        Returns:
            bool: True if the NAT pool is created successfully, False otherwise.

        """
        try:
            if cls.pool_name_exists(pool_name):
                cls.log.debug(f"insert_global_pool_name() Check -> '{pool_name}' already exists.")
                cls.log.error(f"Global NAT pool '{pool_name}' already exists.")
                return STATUS_NOK

            result = cls.rsdb.insert_global_nat_pool(pool_name)

            if result.status == STATUS_OK:
                cls.log.debug(f"insert_global_pool_name() -> Created global NAT pool: {pool_name}")
                return STATUS_OK
            else:
                cls.log.error(f"Failed to create global NAT pool: {pool_name}")
                return STATUS_NOK

        except Exception as e:
            cls.log.error(f"An error occurred while creating global NAT pool: {e}")
            return STATUS_NOK

    def delete_global_nat_pool_name(cls, pool_name: NatPoolName) -> bool:
        """
        Delete a global NAT pool configuration from the NAT database.

        Args:
            pool_name (str): The name of the NAT pool to be deleted.

        Returns:
            bool: True if the NAT pool is deleted successfully, False otherwise.
        """
        try:
            if not cls.pool_name_exists(pool_name):
                cls.log.error(f"Global NAT pool '{pool_name}' does not exist.")
                return STATUS_NOK

            result = cls.rsdb.delete_global_nat_pool_name(pool_name)

            if result.status == STATUS_OK:
                cls.log.debug(f"Deleted global NAT pool: {pool_name}")
                return STATUS_OK
            else:
                cls.log.error(f"Failed to delete global NAT pool: {pool_name}")
                return STATUS_NOK

        except Exception as e:
            cls.log.error(f"An error occurred while deleting global NAT pool: {e}")
            return STATUS_NOK

    def get_global_nat_pool_names(cls) -> list:
        """
        Retrieve a list of global NAT pool names from the NAT database.

        Returns:
            list: A list of NAT pool names.
        """
        try:
            pool_names = cls.rsdb.select_global_nat_pool_names()

            cls.log.debug("Retrieved global NAT pool names: %s", pool_names)
            return pool_names

        except Exception as e:
            cls.log.error(f"An error occurred while retrieving global NAT pool names: {e}")
            return []

    def is_interface_direction_in_nat_pool(cls, interface_name: InterfaceName, nat_pool_name: NatPoolName, direction: str) -> Result:
        """
        Check if the specified interface is associated with the given NAT pool and direction.

        Args:
            interface_name (str): The name of the interface to check.
            nat_pool_name (str): The name of the NAT pool to check.
            direction (str): The direction to check (inside or outside).

        Returns:
            Result: A Result object with the following fields:
            - status (bool): True if the interface is found in the specified NAT pool and direction, False otherwise.
            - row_id (int): The row ID of the found entry, or 0 if not found.

        Raises:
            sqlite3.Error: If there is an error with the database query.

        """
        cls.log.debug(f"is_interface_direction_in_nat_pool({interface_name} -> {nat_pool_name} -> {direction})")
        return cls.rsdb.select_nat_interface_direction(interface_name, nat_pool_name, direction)

    def get_interface_direction_in_nat_pool_list(cls, nat_pool_name: NatPoolName, direction: str) -> list[Result]:
        """
        Get list of interfaces is associated with the given NAT pool and direction.

        Args:
            nat_pool_name (str): The name of the NAT pool to check.
            direction (str): The direction to check (inside or outside).

        Returns list:
            Result: A Result object with the following fields:
            - status (bool): True if the interface is found in the specified NAT pool and direction, False otherwise.
            - row_id (int): The row ID of the found entry, or 0 if not found.

        Raises:
            sqlite3.Error: If there is an error with the database query.

        """
        cls.log.debug(f"get_interface_direction_in_nat_pool_list({nat_pool_name} -> {direction})")
        
        return cls.rsdb.select_nat_interface_direction_list(nat_pool_name, direction)

    def add_inside_interface(cls, nat_pool_name: NatPoolName, interface_name: InterfaceName) -> bool:
        """
        Add an inside interface to a NAT pool configuration.

        Args:
            pool_name (str): The name of the NAT pool.
            interface_name (str): The name of the inside interface to add.

        Returns:
            bool: STATUS_OK if the inside interface is added successfully, STATUS_NOK otherwise.
        """
        from routershell.lib.network_manager.network_operations.nat import NATDirection
        
        cls.log.debug(f"add_inside_interface({nat_pool_name}, {interface_name})")
        
        try:
            pool_id_result = cls.rsdb.global_nat_pool_name_exists(nat_pool_name)

            if not pool_id_result.status:
                cls.log.error(f"Failed to retrieve NAT pool ID for '{nat_pool_name}': {pool_id_result.reason}")
                return STATUS_NOK

            if not cls.rsdb.interface_exists(interface_name):
                cls.log.error(f"Inside interface '{interface_name}' does not exist.")
                return STATUS_NOK

            if cls.rsdb.inside_interface_exists(nat_pool_name, interface_name).status:
                cls.log.error(f"Inside interface '{interface_name}' is already associated with '{nat_pool_name}'.")
                return STATUS_NOK

            result = cls.rsdb.insert_interface_nat_direction(interface_name, nat_pool_name, NATDirection.INSIDE.value)

            if result.status:
                cls.log.error(f"Failed to add inside interface '{interface_name}' to '{nat_pool_name}': {result.reason}")
                return STATUS_NOK
            else:
                cls.log.debug(f"Inserted inside interface '{interface_name}' to '{nat_pool_name}'.")
                return STATUS_OK

        except Exception as e:
            cls.log.error(f"An error occurred while adding inside interface to '{nat_pool_name}': {e}")
            return STATUS_NOK

    def delete_inside_interface(cls, pool_name: NatPoolName, interface_name: InterfaceName) -> bool:
        pass
    
    def add_outside_interface(cls, nat_pool_name: NatPoolName, interface_name: InterfaceName) -> bool:
        """
        Add an outside interface to a NAT pool configuration DB.

        Args:
            nat_pool_name (str): The name of the NAT pool.
            interface_name (str): The name of the outside interface to add.

        Returns:
            bool: STATUS_OK if the outside interface is added successfully, STATUS_NOK otherwise.
        """
        from routershell.lib.network_manager.network_operations.nat import NATDirection
        
        cls.log.debug(f"add_outside_interface({nat_pool_name}, {interface_name})")
        
        try:
            pool_id_result = cls.rsdb.global_nat_pool_name_exists(nat_pool_name)
            
            if not pool_id_result.status:
                cls.log.error(f"Failed to retrieve NAT pool ID for '{nat_pool_name}': {pool_id_result.reason}")
                return STATUS_NOK
                        
            result = cls.rsdb.insert_interface_nat_direction(interface_name, nat_pool_name, NATDirection.OUTSIDE.value)

            if result.status:
                cls.log.error(f"Failed to insert outside interface '{interface_name}' to '{nat_pool_name}': {result.reason}")
                return STATUS_NOK
            else:
                cls.log.debug(f"Inserted outside interface '{interface_name}' to '{nat_pool_name}'.")
                return STATUS_OK

        except Exception as e:
            cls.log.error(f"An error occurred while inserting outside interface to '{nat_pool_name}': {e}")
            return STATUS_NOK
                    
    def delete_outside_interface(cls, pool_name: NatPoolName, interface_name: InterfaceName) -> str:
        pass
    

# FILE: src/routershell/lib/db/router_config_db.py
import logging
from itertools import count

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import InterfaceName
from routershell.lib.db.sqlite_db.router_shell_db import RouterShellDB as DB
from routershell.lib.network_manager.common.interface import InterfaceType


class RouterConfigurationDatabase:

    rsdb = DB()
    counter = count(start=1)
    
    def __init__(cls):
        cls.log = logging.getLogger(cls.__class__.__name__)
        cls.log.setLevel(RSLS().ROUTER_CONFIG_DB)
        
        if not cls.rsdb:
            cls.log.debug("Connecting RouterShell Database")
            cls.rsdb = DB()
            
    def get_interface_name_list(cls, interface_type: InterfaceType = InterfaceType.UNKNOWN) -> list[str]:
        """
        Get a list of interface names based on the specified interface type.

        Args:
            interface_type (InterfaceType): The type of interface to filter by.

        Returns:
            list[str]: A list of interface names.
        """
        interface_list = []

        if interface_type == InterfaceType.UNKNOWN:
            interface_result_list = cls.rsdb.select_interfaces()
        else:
            interface_result_list = cls.rsdb.select_interfaces_by_interface_type(interface_type)

        for interface in interface_result_list:
            cls.log.debug(f"get_interface_name_list() -> {interface}")
            if interface.status == STATUS_OK:
                interface_names = interface.result.get('InterfaceName')

                # Ensure interface_names is a list, even if it contains a single value
                if isinstance(interface_names, str):
                    interface_list.append(interface_names)
                elif isinstance(interface_names, list):
                    interface_list.extend(interface_names)

        return interface_list
    
    def get_interface_configuration(cls, interface_name: InterfaceName) -> tuple[bool, dict]:
        """
        Get the configuration for a specific interface.

        Args:
            interface_name (str): The name of the interface.

        Returns:
            tuple[bool, dict]: A tuple containing a boolean indicating the status and a dictionary with the interface configuration.
        """
        if_result = cls.rsdb.select_interface_configuration(interface_name)
        
        cls.log.debug(f'Interface-Base-Config: {if_result}')
        
        return if_result.status, if_result.result

    def get_interface_dhcp_client_configuration(cls, interface_name: InterfaceName) -> tuple[bool, list[dict]]:
        """
        Retrieve DHCP client configuration information associated with a specific interface.

        Parameters:
            interface_name (str): The name of the interface for which to retrieve DHCP client configuration information.

        Returns:
            tuple[bool, list[dict]]: A tuple containing a boolean indicating the success of the operation (True for success, False for failure)
                and a list of dictionaries representing the DHCP client configuration information.
                Each dictionary contains the DHCP client version information.

        Example:
            - (STATUS_OK, [{'DhcpClientVersion': 'ip dhcp-client'}, {'DhcpClientVersion': 'ipv6 dhcp-client '}])
            - (STATUS_NOK, [])  # In case of an error
        """
        sql_result = cls.rsdb.select_interface_dhcp_client_configuration(interface_name)

        if any(result.status for result in sql_result):
            error_messages = [result.reason for result in sql_result if result.status]
            cls.log.debug(f"Error retrieving interface {interface_name} DHCP client status. Skipping. Error messages: {', '.join(error_messages)}")
            return STATUS_NOK, []

        dhcp_config_list = [result.result for result in sql_result]

        return STATUS_OK, dhcp_config_list
        
    def get_interface_ip_address_configuration(cls, interface_name: InterfaceName) -> tuple[bool, list[dict]]:
        """
        Retrieve IP address configuration for a specific interface.

        Args:
            interface_name (str): The name of the interface.

        Returns:
            tuple[bool, list[dict]]: 
                A tuple containing a boolean indicating the success of the operation
                    and a list of dictionaries with IP address configuration data.
                If the operation is successful, the boolean will be True, and the list
                    will contain dictionaries with IP address details.
                If there is an error, the boolean will be False, and the list will be empty.
        """
        if_ip_result = cls.rsdb.select_interface_ip_address_configuration(interface_name)

        # Check if any errors occurred during the retrieval
        if any(result.status for result in if_ip_result):
            error_messages = [result.reason for result in if_ip_result if result.status]
            cls.log.debug(f"Error retrieving IP address configuration, skipping: {', '.join(error_messages)}")
            return STATUS_NOK, []

        # Extract data from the result list and build the list of dictionaries
        ip_config_list = [result.result for result in if_ip_result]

        return STATUS_OK, ip_config_list

    def get_interface_dhcp_server_polices(cls, interface_name: InterfaceName) -> tuple[bool, list[dict[str, str]]]:
        """
        Retrieve DHCP server policies for a specific interface.

        Args:
            interface_name (str): The name of the interface.

        Returns:
            tuple[bool, list[dict[str, str]]]: 
                A tuple containing a boolean indicating the success of the operation
                    and a list of dictionaries with DHCP server policies data.
                If the operation is successful, the boolean will be True, and the list
                    will contain dictionaries with DHCP server policy details.
                If there is an error, the boolean will be False, and the list will be empty.
        """
        if_dhcp_serv_policy_result = cls.rsdb.select_interface_ip_dhcp_server_policies(interface_name)

        if any(result.status for result in if_dhcp_serv_policy_result):
            error_messages = [result.reason for result in if_dhcp_serv_policy_result if result.status]
            cls.log.debug(f"Error retrieving DHCP server policies, skipping: {', '.join(error_messages)}")
            return STATUS_NOK, []

        dhcp_server_policies = [result.result for result in if_dhcp_serv_policy_result]

        return STATUS_OK, dhcp_server_policies

    def get_interface_switchport_access_vlan(cls, interface_name: InterfaceName) -> tuple[bool, list[dict[str, str]]]:
        
        if_switch_port_access_vlan_id_result = cls.rsdb.select_interface_switchport_access_vlan_id(interface_name)

        if any(result.status for result in if_switch_port_access_vlan_id_result):
            error_messages = [result.reason for result in if_switch_port_access_vlan_id_result if result.status]
            cls.log.debug(f"Error retrieving switchport access-vlan-id, skipping: {', '.join(error_messages)}")
            return STATUS_NOK, []

        if_switch_port_access_vlan_id = [result.result for result in if_switch_port_access_vlan_id_result]
        
        return STATUS_OK, if_switch_port_access_vlan_id

    def get_interface_ip_static_arp_configuration(cls, interface_name: InterfaceName) -> tuple[bool, list[dict]]:
        """
        Retrieve IP static ARP configuration for a specific interface.

        Args:
            interface_name (str): The name of the interface.

        Returns:
            tuple[bool, list[dict]]: A tuple containing a boolean indicating the success of the operation
                                    and a list of dictionaries with IP static ARP configuration data.
                                    If the operation is successful, the boolean will be True, and the list
                                    will contain dictionaries with IP static ARP details.
                                    If there is an error, the boolean will be False, and the list will be empty.
        """
        if_static_arp_result = cls.rsdb.select_interface_ip_static_arp_configuration(interface_name)

        # Check if any errors occurred during the retrieval
        if any(result.status for result in if_static_arp_result):
            error_messages = [result.reason for result in if_static_arp_result if result.status]
            cls.log.debug(f"Error retrieving IP static ARP configuration, skipping: {', '.join(error_messages)}")
            return STATUS_NOK, []

        # Extract data from the result list and build the list of dictionaries
        static_arp_config_list = [result.result for result in if_static_arp_result]

        return STATUS_OK, static_arp_config_list

    def get_interface_wifi_configuration(cls, interface_name: InterfaceName) -> tuple[bool, list[dict]]:
        """
        Get the wireless wifi configuration for a specified interface.

        Args:
            interface_name (str): The name of the interface.

        Returns:
            tuple[bool, list[dict]]: A tuple containing a boolean status and a list of dictionaries
            representing the wireless wifi configuration for the given interface.
        """
        wifi_config_result = cls.rsdb.select_interface_wifi_configuration(interface_name)

        # Extract data from the result list and build the list of dictionaries
        wifi_config_list = [result.result for result in wifi_config_result]

        cls.log.debug(f"WiFi Interface Config: {wifi_config_list}")

        return STATUS_OK, wifi_config_list
     
    def get_interface_rename_configuration(cls) -> tuple[bool, list[dict]]:
        """
        Retrieve data from the 'RenameInterface' table.

        Returns:
            tuple[bool, list[dict]]:
            - A tuple containing a boolean indicating the success of the operation
                    and a list of dictionaries with data from the 'RenameInterface' table.
            - If the operation is successful, the boolean will be True, and the list will contain dictionaries
                    with 'InitialInterface' and 'AliasInterface' values.
            - If there is an error, the boolean will be False, and the list will be empty.
        """
        cls.log.debug('get_interface_rename_configuration()')

        rename_list = []

        rename_result = cls.rsdb.select_global_interface_rename_configuration()

        # Check if any errors occurred during the retrieval
        if any(result.status for result in rename_result):
            error_messages = [result.reason for result in rename_result if result.status]
            cls.log.debug(f"Error retrieving rename-interface-line, skipping: {', '.join(error_messages)}")
            return STATUS_NOK, []

        # Extract data from the result list and build the list of dictionaries
        for result in rename_result:
            rename_list.append(result.result)

        return STATUS_OK, rename_list

    def get_bridge_configuration(cls) -> tuple[bool, list[dict]]:
        """
        Retrieve bridge configuration data.

        Returns:
            tuple[bool, list[dict]]:
            - A tuple containing a boolean indicating the success of the operation
              and a list of dictionaries with bridge configuration data.
            - If the operation is successful, the boolean will be True, and the list will contain dictionaries
              with 'BridgeName', 'Protocol', 'StpStatus', and 'Shutdown' keys.
            - If there is an error, the boolean will be False, and the list will be empty.
        """
        cls.log.debug('get_bridge_configuration()')

        bridge_config_list = []

        bridge_result = cls.rsdb.select_global_bridge_configuration()

        # Check if any errors occurred during the retrieval
        if any(result.status for result in bridge_result):
            error_messages = [result.reason for result in bridge_result if result.status]
            cls.log.debug(f"Error retrieving bridge configuration, skipping: {', '.join(error_messages)}")
            return STATUS_NOK, []

        # Extract data from the result list and build the list of dictionaries
        for result in bridge_result:
            bridge_config_list.append(result.result)

        return STATUS_OK, bridge_config_list

    def get_vlan_configuration(cls) -> tuple[bool, list[dict]]:
        """
        Retrieve VLAN configuration data.

        Returns:
            tuple[bool, list[dict]]:CONFIG_MODE
            - A tuple containing a boolean indicating the success of the operation
              and a list of dictionaries with VLAN configuration data.
            - If the operation is successful, the boolean will be True, and the list will contain dictionaries
              with 'VlanID', 'VlanDescription', and 'VlanName' keys.
            - If there is an error, the boolean will be False, and the list will be empty.
        """
        cls.log.debug('get_vlan_configuration()')

        vlan_config_list = []

        vlan_result = cls.rsdb.select_global_vlan_configuration()

        # Check if any errors occurred during the retrieval
        if any(result.status for result in vlan_result):
            error_messages = [result.reason for result in vlan_result if result.status]
            cls.log.debug(f"Error retrieving VLAN configuration, skipping: {', '.join(error_messages)}")
            return STATUS_NOK, []

        # Extract data from the result list and build the list of dictionaries
        for result in vlan_result:
            vlan_config_list.append(result.result)

        return STATUS_OK, vlan_config_list

    def get_nat_configuration(cls) -> tuple[bool, list[dict]]:
        """
        Get the NAT configurations.

        Returns:
        tuple[bool, list[dict]]: A tuple containing a boolean indicating success and a list of NAT configurations as dictionaries.
        """
        cls.log.debug('get_nat_configuration()')

        nat_config_list = []

        nat_result = cls.rsdb.select_global_nat_configuration()

        if all(result.status == STATUS_OK for result in nat_result):
            nat_config_list = [result.result for result in nat_result]
            cls.log.debug(f"Retrieved NAT configurations: {nat_config_list}")
            return STATUS_OK, nat_config_list

        else:
            cls.log.error("Failed to retrieve NAT configurations.")
            return STATUS_NOK, []

    def get_dhcp_server_configuration(cls) -> tuple[bool, list[dict]]:
        """
        Retrieve global DHCP server configuration data, including pool details, reservations, and subnet options.

        Returns:
            tuple[bool, list[dict]]: A tuple containing a boolean status and a list of dictionaries representing DHCP server configuration data.
            - The boolean status is STATUS_OK if the retrieval is successful, and STATUS_NOK otherwise.
            - The list includes dictionaries for each type of data, making it easy to distinguish between pool details,
              reservations, and subnet options.

        Note:
        - The returned list includes dictionaries for each type of data, providing a structured format for the DHCP server configuration.
        - If the retrieval is unsuccessful, the method returns a tuple with a status of STATUS_NOK and an empty list.
        """
        dhcp_server_config_result = cls.rsdb.select_global_dhcp_server_configuration()
        config_data = []

        if all(result.status == STATUS_OK for result in dhcp_server_config_result):
            
            for dsc_result in dhcp_server_config_result:
                
                #config line -> dhcp pool-name <dhcp-pool-name> -> index 2
                dhcp_pool_name_index = 2
                pool_name = dsc_result.result.get('DhcpServerPoolName').split()[dhcp_pool_name_index]
                
                combined_data = dsc_result.result

                dhcp_server_pool_results = cls.rsdb.select_global_dhcp_server_pool(pool_name)
                for data in dhcp_server_pool_results:
                    for key, value in data.result.items():
                        combined_data.update({f"{key}-{str(next(cls.counter))}": value})

                dhcp_server_reservation_results = cls.rsdb.select_global_dhcp_server_reservation_pool(pool_name)
                for data in dhcp_server_reservation_results:
                    for key, value in data.result.items():
                        combined_data.update({f"{key}-{str(next(cls.counter))}": value})

                dhcp_server_option_subnet_results = cls.rsdb.select_global_dhcp_server_subnet_option_pool(pool_name)
                for data in dhcp_server_option_subnet_results:
                    for key, value in data.result.items():
                        combined_data.update({f"{key}-{str(next(cls.counter))}": value})

                dhcp_server_option_results = cls.rsdb.select_global_dhcpv6_server_options(pool_name)
                for data in dhcp_server_option_results:
                    for key, value in data.result.items():
                        combined_data.update({f"{key}-{str(next(cls.counter))}": value})                
                
                config_data.append(combined_data)

        else:
            return STATUS_NOK, config_data
        
        return STATUS_OK, config_data

    def get_banner(cls) -> tuple[bool, dict]:
        """
        Retrieve the banner Message of the Day (Motd) from the database.

        Args:
            cls: The RouterShellDB class.

        Returns:
            tuple[bool, dict]: A tuple containing a boolean indicating the operation's success or failure,
            and a dictionary with the banner Motd if found.

        """
        result = cls.rsdb.select_banner_motd()

        if result.status:
            cls.log.debug("Banner not found in the database.")
            return STATUS_NOK, {}
        
        return STATUS_OK, result.result

    def get_wifi_policy_configuration(cls) -> tuple[bool, dict]:
        """
        Retrieves WiFi policy configuration data including global policy information and associated security policies.

        Returns:
        - tuple[bool, dict]: A tuple containing a boolean status and a dictionary with WiFi policy configuration data.

        """
        wifi_policy_result = cls.rsdb.select_wifi_policies()
        config_data = {}

        if all(result.status == STATUS_OK for result in wifi_policy_result):
            
            for wp_result in wifi_policy_result:
                wifi_policy = wp_result.result.get('WifiPolicyName')

                wp_config = cls.rsdb.select_global_wireless_wifi_policy(wifi_policy)
                temp_config = wp_config.result

                wifi_sec_policy_list = cls.rsdb.select_global_wireless_wifi_security_policy(wifi_policy)
                wifi_sec_policy_data = []

                for wifi_sec_policy_item in wifi_sec_policy_list:
                    ssid = wifi_sec_policy_item.get('Ssid')
                    passphrase = wifi_sec_policy_item.get('WpaPassPhrase')
                    version = wifi_sec_policy_item.get('WpaVersion')

                    wifi_sec_policy_data.append({
                        'Ssid': ssid,
                        'Passphrase': passphrase,
                        'Version': version
                    })

                temp_config['WifiSecurityPolicy'] = wifi_sec_policy_data

                config_data[wifi_policy] = temp_config

        cls.log.debug(f'{config_data}')

        return STATUS_OK if config_data else STATUS_NOK, config_data

# FILE: src/routershell/lib/db/sqlite_db/router_shell_db.py
import logging
import os
import sqlite3

from tabulate import tabulate

from routershell.lib.common.constants import ROUTER_SHELL_DB, ROUTER_SHELL_SQL_STARTUP, STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.singleton import Singleton
from routershell.lib.common.types import (
    BridgeName,
    DhcpPoolName,
    HostnameText,
    InetAddressText,
    InetCidrText,
    InterfaceName,
    MacAddressText,
    NatPoolName,
    SsidText,
    VlanName,
    WifiPassphraseText,
    WifiPolicyName,
)
from routershell.lib.network_manager.common.interface import InterfaceType
from routershell.lib.network_manager.common.phy import State
from routershell.lib.network_manager.network_interfaces.bridge.bridge_protocols import STP_STATE, BridgeProtocol
from routershell.lib.network_services.dhcp.common.dhcp_common import DHCPVersion


class Result:
    """
    Represents the result of an operation in the database.

    This class is designed to encapsulate the outcome of various database operations, providing information
    about the status, associated row ID, and an optional result message.

    Attributes:
        status (bool): A boolean indicating the operation's success: STATUS_OK (0) for success, STATUS_NOK (1) for failure.
        row_id (int, optional): The row ID associated with the database operation.
        reason (str, optional): An optional result message that provides additional information about the operation.
        result (dict, optional): SQL query result dict{SQL-COLUMN_NAME:value}

    Example:
    You can use the Result class to handle the outcome of database operations, such as insertions, updates, or deletions.
    For example, after inserting a new record into the database, you can create a Result object to represent the outcome.

    Note:
    - 'status' attribute SHOULD be set to STATUS_OK (0) for successful operations and STATUS_NOK (1) for failed ones OR can be any boolean, refer to method documentation.
    - 'row_id' represents the unique identifier of the affected row, any integer > 0 for STATUS_OK or 0 for STATUS_NOK
    - 'reason' provides additional information about the operation, which is particularly useful for error messages.
    - 'result' SQL query result single row {sql_table_column_name:value}
    """

    def __init__(self, status: bool, row_id: int = None, reason: str = None, result=dict):
        self.status = status
        self.row_id = row_id
        self.reason = reason
        self.result = result

    def __str__(self):
        return f"Status: {self.status}, Row ID: {self.row_id}, Reason: {self.reason}, Result: {self.result}"

    @staticmethod
    def sql_result_to_value_list(results: list['Result']) -> list[list]:
        """
        Extract values from a list of Result objects into a list of lists for Result objects with a 'result' attribute containing a dictionary.

        Args:
            results (list[Result]): A list of Result objects.

        Returns:
            list[list]: A list of lists containing values from Result objects with a 'result' attribute containing a dictionary.
        """
        value_lists = []
        for result in results:
            if result.result and isinstance(result.result, dict):
                value_list = list(result.result.values())
                value_lists.append(value_list)
        return value_lists


class RouterShellDB(metaclass=Singleton):

    connection = None
    connection_created = False

    ROW_ID_NOT_FOUND = 0
    FK_NOT_FOUND = -1

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().ROUTER_SHELL_DB)

        self.db_file_path = os.path.join(
            os.path.dirname(__file__), ROUTER_SHELL_DB)
        self.sql_file_path = os.path.join(
            os.path.dirname(__file__), ROUTER_SHELL_SQL_STARTUP)

        self.log.debug(
            f"__init__() -> db-connection: {self.connection} -> db-connection-created: {self.connection_created}")

        if not self.connection_created:

            if not os.path.exists(self.db_file_path):
                self.log.debug(
                    f"Creating DB file: {self.db_file_path}, does not exist.")
                self.create_database()
            else:
                self.log.debug(f"Database file {self.db_file_path} exists.")
                self.open_connection()

            self.connection_created = True
        else:
            self.log.debug(f"Already Connected to DB {self.db_file_path}")

    def create_database(self) -> bool:
        """
        Create an SQLite database file and populate it with tables and data from an SQL file.

        Returns:
            bool: STATUS_OK if the database is created successfully, STATUS_NOK if there is an error.
        """
        self.log.debug("create_database()")

        try:
            self.connection = sqlite3.connect(
                self.db_file_path, check_same_thread=True)

            cursor = self.connection.cursor()

            with open(self.sql_file_path) as sql_file:
                sql_script = sql_file.read()

            cursor.executescript(sql_script)

            self.connection.commit()

            self.log.debug("SQLite database created successfully.")

        except sqlite3.Error as e:
            self.log.error(f"Error: {e}")
            return STATUS_NOK

        return STATUS_OK

    def open_connection(self) -> bool:
        """
        Open a connection to the SQLite database.

        Returns:
            bool: STATUS_OK if the connection is successful, STATUS_NOK if there is an error.
        """
        self.log.debug("open_connection()")

        if not self.connection:
            try:
                self.connection = sqlite3.connect(
                    self.db_file_path, check_same_thread=True)

                self.log.debug(f"Connected to DB {ROUTER_SHELL_DB}")
                return STATUS_OK

            except sqlite3.Error as e:
                self.log.error(f"Error: {e}")
                return STATUS_NOK

        return STATUS_OK

    def close_connection(self):
        """
        Close the database connection.
        """
        if self.connection:
            self.connection.close()

    def reset_database(self) -> bool:
        """
        Remove the existing database file and create a new one.

        Returns:
            bool: STATUS_OK if the reset is successful, STATUS_NOK if there is an error.
        """
        self.log.debug("reset_database")

        # Reset some OS hardware and network features
        from routershell.lib.system.system_start_up import SystemReset
        SystemReset().database()

        if self.connection:
            self.connection.close()

        try:
            if os.path.exists(self.db_file_path):
                os.remove(self.db_file_path)
                self.log.debug(
                    f"Removed existing database file: {ROUTER_SHELL_DB}")

        except Exception as e:
            self.log.error(
                f"Error while removing the existing database file: {e}")
            return STATUS_NOK

        return self.create_database()

    def dump_db(self, include_schema:bool=False):
        """
        Dumps the contents of the SQLite database to the console in a human-readable format.
        This includes dumping the schema and data for all tables in the database.
        
        Args:
            include_schema (bool): Whether to include schema information in the output.
        """
        cursor = self.connection.cursor()

        # Get a list of all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if not tables:
            print("No tables found in the database.")
            return

        for (table_name,) in tables:
            if include_schema:
                print(f"\nTable: {table_name}")

                # Dump the table schema
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                schema = [["Column", "Type", "Not Null", "Default Value"]]
                schema.extend([[column[1], column[2], column[3], column[4]] for column in columns])
                
                print(f"Schema: {table_name}")
                print(tabulate(schema, headers='firstrow', tablefmt='grid'))

            # Dump the table data
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()
            column_names = [description[0] for description in cursor.description]
            data = [column_names] + rows
            
            print(f"\nTable: {table_name}")
            print(tabulate(data, headers='firstrow', tablefmt='grid'))

    '''
                        ROUTER SYSTEM/GLOBAL CONFIGURATION DATABASE
    '''

    def update_banner_motd(self, motd: str) -> Result:
        """
        Update the BannerMotd in the SystemConfiguration table.

        Args:
            motd (str): The new message of the day.

        Returns:
            Result: A Result object indicating the operation's success or failure and the affected row_id.
        """
        try:
            cursor = self.connection.cursor()

            # Check if a row with ID = 1 exists
            cursor.execute("SELECT COUNT(*) FROM SystemConfiguration")
            row_count = cursor.fetchone()[0]

            if row_count > 0:
                cursor.execute(
                    "UPDATE SystemConfiguration SET BannerMotd = ? WHERE ID = 1", (motd,))
            else:
                # Insert new row
                cursor.execute(
                    "INSERT INTO SystemConfiguration (BannerMotd) VALUES (?)", (motd,))

            self.connection.commit()
            row_id = cursor.lastrowid  # Retrieve the row_id of the affected row
            self.log.debug(
                "Update operation: BannerMotd updated successfully in the 'SystemConfiguration' table.")
            return Result(status=STATUS_OK, row_id=row_id, result={'BannerMotd': motd})

        except sqlite3.IntegrityError as integrity_error:
            self.log.error(
                "IntegrityError updating BannerMotd: %s", integrity_error)
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=str(integrity_error))

        except sqlite3.Error as sql_error:
            self.log.error("Error updating BannerMotd: %s", sql_error)
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=str(sql_error))

        except Exception as e:
            self.log.error("Unexpected error updating BannerMotd: %s", e)
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=str(e))

    def select_banner_motd(self) -> Result:
        """
        Select the BannerMotd from the SystemConfiguration table.

        Returns:
            Result: A Result object indicating the operation's success or failure and the BannerMotd value.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT BannerMotd FROM SystemConfiguration WHERE ID = 1")
            result = cursor.fetchone()

            if not result:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason="No entry found in 'SystemConfiguration' table.")

            return Result(status=STATUS_OK, row_id=1, result={'BannerMotd': result[0]})

        except sqlite3.Error as e:
            self.log.error("Error selecting BannerMotd: %s", e)
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=str(e))

    def hostname_exists(self, hostname: HostnameText) -> Result:
        """
        Check if a hostname already exists in the 'SystemConfiguration' table.

        Args:
            hostname (str): The hostname to check.

        Returns:
            Result: A Result object with the status and row ID of the existing hostname.
                - If the hostname exists, the Result object will have 'status' set to STATUS_OK,
                'row_id' set to the unique identifier of the existing hostname, and 'result' containing the existing hostname.
                - If the hostname doesn't exist, the Result object will have 'status' set to STATUS_NOK,
                'row_id' set to None, and 'reason' providing information about the absence of the hostname.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        log_message = f"hostname_exists: HOSTNAME={hostname}"
        self.log.debug(log_message)

        try:
            query = "SELECT ID, Hostname FROM SystemConfiguration WHERE Hostname = ?"
            parameters = (hostname,)

            cursor = self.connection.cursor()
            cursor.execute(query, parameters)

            result = cursor.fetchone()

            if result is not None:
                existing_row_id = result[0]
                existing_hostname = result[1]
                self.log.debug(
                    f"Hostname '{existing_hostname}' already exists with ID: {existing_row_id}")
                return Result(status=True, row_id=existing_row_id, result={"Hostname": existing_hostname})
            else:
                self.log.debug(
                    f"Hostname '{hostname}' does not exist in 'SystemConfiguration'")
                return Result(status=False, row_id=None, reason=f"Hostname '{hostname}' does not exist.")

        except sqlite3.Error as e:
            error_message = f"Error checking hostname existence in 'SystemConfiguration': {e}"
            self.log.error(error_message)
            return Result(status=False, row_id=None, reason=error_message)

    def update_hostname(self, hostname: HostnameText) -> Result:
        """
        Insert data into the 'SystemConfiguration' table for the hostname.

        Args:
            hostname (str): The hostname to be inserted.

        Returns:
            Result: A Result object with the status and row ID of the inserted hostname.
                - If the operation is successful, the Result object will have 'status' set to STATUS_OK and 'row_id' set to the
                unique identifier of the inserted hostname.
                - If the hostname already exists, the Result object will have 'status' set to STATUS_NOK, 'row_id' set to None,
                and 'reason' providing information about the existing hostname.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        log_message = f"insert_hostname: HOSTNAME={hostname}"
        self.log.debug(log_message)

        try:

            result_hostname = self.hostname_exists(hostname)

            if result_hostname.status:
                return Result(status=STATUS_OK,
                              row_id=result_hostname.row_id,
                              reason=f"Hostname '{hostname}' already exists.",
                              result=result_hostname.result)

            query = "UPDATE SystemConfiguration SET Hostname = ? WHERE ID = 1"
            parameters = (hostname,)

            cursor = self.connection.cursor()
            cursor.execute(query, parameters)

            self.connection.commit()
            self.log.debug(
                "Hostname inserted into the 'SystemConfiguration' table successfully")
            return Result(status=STATUS_OK, row_id=cursor.lastrowid)

        except sqlite3.Error as e:
            error_message = f"Error inserting hostname into 'SystemConfiguration': {e}"
            self.log.error(error_message)
            return Result(status=STATUS_NOK, row_id=None, reason=error_message)

    def select_hostname(self) -> Result:
        """
        Select the hostname from the 'SystemConfiguration' table.

        Returns:
            Result: A Result object with the status and the selected hostname.
                - If the operation is successful, the Result object will have 'status' set to STATUS_OK,
                'row_id' set to None, and 'result' containing the selected hostname.
                - If no hostname is found, the Result object will have 'status' set to STATUS_NOK,
                'row_id' set to None, and 'reason' providing information about the absence of a hostname.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT Hostname FROM SystemConfiguration LIMIT 1")
            row = cursor.fetchone()

            if row and row[0]:
                return Result(status=STATUS_OK, row_id=None, result={'Hostname': row[0]})
            else:
                return Result(status=STATUS_NOK, row_id=None, reason="No hostname found in the database")

        except sqlite3.Error as e:
            error_message = f"Error selecting hostname: {e}"
            self.log.error(error_message)
            return Result(status=STATUS_NOK, row_id=None, reason=error_message)

    '''
                        BRIDGE DATABASE
    '''

    def bridge_exist_db(self, bridge_name: BridgeName) -> Result:
        """
        Check if a bridge with the given name exists in the Interfaces table.

        Args:
            bridge_name (str): The name of the bridge to check.

        Returns:
            Result: A Result object indicating if the bridge exists.
                - If the bridge exists, the Result object will have 'status' set to True, otherwise False.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT b.ID 
                FROM Bridges b
                JOIN Interfaces i ON b.Interfaces_FK = i.ID
                WHERE i.InterfaceName = ? AND i.InterfaceType = ?
            """, (bridge_name, InterfaceType.BRIDGE.value))
            
            row = cursor.fetchone()
            
            if row:
                bridge_id = row[0]
                return Result(status=True, row_id=bridge_id)
            else:
                return Result(status=False, reason=f"Bridge with name '{bridge_name}' does not exist")
                
        except sqlite3.Error as e:
            return Result(status=False, reason=str(e))

    def is_bridge_in_bridge_group(self, bridge_name: BridgeName) -> Result:
        """
        Check if a bridge with the given name exists in the BridgeGroups table.

        Args:
            bridge_name (str): The name of the bridge to check.

        Returns:
            Result: A Result object indicating if the bridge exists in the BridgeGroups table.
                - If the bridge exists, the Result object will have 'status' set to True, otherwise False.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT BG.Bridges_FK
                FROM BridgeGroups BG
                JOIN Bridges B ON BG.Bridges_FK = B.ID
                WHERE B.BridgeName = ?
            """, (bridge_name,))
            row = cursor.fetchone()

            if row:
                bridge_id = row[0]
                self.log.debug(f'Bridge: {bridge_name} is found in BridgeGroup with row-id: {bridge_id}')
                return Result(status=True, row_id=bridge_id)
            
            else:
                self.log.debug(f'Bridge: {bridge_name} is not attached to any interface')
                return Result(status=False, reason=f"Bridge with name '{bridge_name}' does not exist in the BridgeGroups table")

        except sqlite3.Error as e:
            return Result(status=False, reason=str(e))

    def insert_interface_bridge(self, bridge_name: BridgeName, shutdown_status: bool = True) -> Result:
        """
        Insert a new bridge interface into the 'Interfaces' and 'Bridges' tables.

        This method first checks if a bridge with the given name already exists. 
        If it exists, it returns a failure result. If it does not exist, it inserts
        a new entry into the 'Interfaces' and 'Bridges' tables.

        Args:
            bridge_name (str): The name of the bridge interface.
            shutdown_status (bool): True if the interface is shutdown, False otherwise.

        Returns:
            Result: A Result object with the status of the insertion.
        """
        ifType = InterfaceType.BRIDGE.value

        existing_result = self.bridge_exist_db(bridge_name)

        if existing_result.status:
            self.log.debug(f"Bridge with name '{bridge_name}' already exists, not inserting bridge")
            return Result(status=STATUS_NOK, reason=f"Bridge with name '{bridge_name}' already exists")

        try:
            cursor = self.connection.cursor()

            cursor.execute(
                "INSERT INTO Interfaces (InterfaceName, InterfaceType, ShutdownStatus) VALUES (?, ?, ?)",
                (bridge_name, ifType, shutdown_status)
            )
            interface_id = cursor.lastrowid

            cursor.execute(
                "INSERT INTO Bridges (BridgeName, Interfaces_FK) VALUES (?, ?)",
                (bridge_name, interface_id)
            )
            self.connection.commit()

            self.log.debug(
                f"Bridge interface {bridge_name} inserted with interface ID {interface_id}")
            return Result(status=STATUS_OK, row_id=interface_id)

        except sqlite3.Error as e:
            self.log.error(
                f"Error inserting bridge interface {bridge_name}: {e}")
            return Result(status=STATUS_NOK, row_id=0, reason=f"{e}")

    def delete_interface_bridge(self, bridge_name: BridgeName) -> Result:
        """
        Delete a bridge interface from the 'Bridges' table, the corresponding entry from the 'Interfaces' table,
        and any related IP address entries from the 'InterfaceIpAddress' table.

        Args:
            bridge_name (str): The name of the bridge interface to delete.

        Returns:
            Result: A Result object with the status of the deletion.
        """
        try:
            # Check if the bridge exists using the existing method
            bridge_interface_result = self.bridge_exist_db(bridge_name)

            if not bridge_interface_result.status:
                self.log.debug(
                    f"Bridge interface {bridge_name} does not exist")
                return Result(status=STATUS_NOK, row_id=0, reason=f"Bridge interface {bridge_name} does not exist")
            
            result = self.is_bridge_in_bridge_group(bridge_name)
            if result.status:
                fail_reason = f"Bridge interface {bridge_name} found in BridgeGroup, need to delete interfaces before deleting bridge"
                return Result(status=STATUS_NOK, row_id=0, reason=fail_reason)
            
            bridge_interface_row_id = bridge_interface_result.row_id

            cursor = self.connection.cursor()

            # Delete from InterfaceIpAddress table
            cursor.execute(
                "DELETE FROM InterfaceIpAddress WHERE Interfaces_FK = ?",
                (bridge_interface_row_id,)
            )

            # Delete from Bridges table
            cursor.execute(
                "DELETE FROM Bridges WHERE Interfaces_FK = ?",
                (bridge_interface_row_id,)
            )

            # Delete from Interfaces table
            cursor.execute(
                "DELETE FROM Interfaces WHERE InterfaceName = ? AND InterfaceType = ?",
                (bridge_name, InterfaceType.BRIDGE.value)
            )

            self.connection.commit()

            self.log.debug(
                f"Bridge interface {bridge_name} and related entries deleted successfully")
            return Result(status=STATUS_OK, row_id=0)

        except sqlite3.Error as e:
            self.log.error(
                f"Error deleting bridge interface {bridge_name}: {e}")
            return Result(status=STATUS_NOK, row_id=0, reason=f"{e}")

    def update_bridge(self, bridge_name: BridgeName,
                      protocol: BridgeProtocol | None = None,
                      stp_status: STP_STATE | None = None,
                      management_inet: str | None = None,
                      description: str | None = None,
                      shutdown_status: State | None = None) -> Result:
        """
        Update an existing bridge in the Bridges, Interfaces, and InterfaceIpAddress tables.

        Args:
            bridge_name (str): The name of the bridge to update.
            protocol (BridgeProtocol | None): The new protocol for the bridge (if changing).
            stp_status (STP_STATE | None): The new STP status (if changing).
            management_inet (str | None): The management IP address for the bridge (if changing).
            description (str | None): The new description for the bridge interface (if changing).
            shutdown_status (bool | None): The new shutdown status for the bridge interface (if changing).

        Returns:
            Result: A Result object with the status of the update.
        """
        try:
            cursor = self.connection.cursor()

            cursor.execute(
                "SELECT B.Interfaces_FK, I.ID FROM Bridges B JOIN Interfaces I ON B.Interfaces_FK = I.ID WHERE B.BridgeName = ?",
                (bridge_name,)
            )
            bridge_row = cursor.fetchone()

            if not bridge_row:
                return Result(status=STATUS_NOK, reason=f"Bridge {bridge_name} does not exist")

            interface_id = bridge_row[0]

            update_columns = []
            parameters = []

            if protocol is not None:
                update_columns.append("Protocol = ?")
                parameters.append(protocol.name)

            if stp_status is not None:
                update_columns.append("StpStatus = ?")
                parameters.append(stp_status.value)

            if update_columns:
                update_query = f"UPDATE Bridges SET {', '.join(update_columns)} WHERE Interfaces_FK = ?"
                parameters.append(interface_id)
                cursor.execute(update_query, tuple(parameters))

            update_columns = []
            parameters = []

            if description is not None:
                update_columns.append("Description = ?")
                parameters.append(description)

            if shutdown_status is not None:
                update_columns.append("ShutdownStatus = ?")
                shutdown_status_value = False if shutdown_status == State.UP else True
                parameters.append(shutdown_status_value)

            if update_columns:
                update_query = f"UPDATE Interfaces SET {', '.join(update_columns)} WHERE ID = ?"
                parameters.append(interface_id)
                cursor.execute(update_query, tuple(parameters))

            if management_inet is not None:
                cursor.execute(
                    "SELECT ID FROM InterfaceIpAddress WHERE IpAddress = ? AND Interfaces_FK = ?", (management_inet, interface_id))
                inet_row = cursor.fetchone()

                if inet_row:
                    inet_id = inet_row[0]
                    cursor.execute(
                        "UPDATE InterfaceIpAddress SET IpAddress = ? WHERE ID = ?",
                        (management_inet, inet_id)
                    )
                else:
                    cursor.execute(
                        "INSERT INTO InterfaceIpAddress (IpAddress, Interfaces_FK) VALUES (?, ?)",
                        (management_inet, interface_id)
                    )
                    inet_id = cursor.lastrowid

            self.connection.commit()

            if cursor.rowcount == 0:
                return Result(status=STATUS_NOK, reason="No bridge found with the given name")

            return Result(status=STATUS_OK, row_id=interface_id)

        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, reason=str(e))

    def delete_bridge(self, bridge_name:BridgeName) -> Result:
        
        if not self.bridge_exist_db(bridge_name).status:
            return Result(status=STATUS_OK, reason=f"No need to delete bridge: {bridge_name}, does not exists")
        
        if self.is_bridge_in_bridge_group(bridge_name).status:
            return Result(status=STATUS_NOK, reason=f"Unable te delete bridge: {bridge_name}, still attached to a bridge group")
        
        return self.delete_interface(interface_name=bridge_name)
        
    '''
                        VLAN DATABASE
    '''

    def vlan_id_exists(self, vlan_id: int) -> Result:
        """
        Check if a VLAN with the given ID exists in the database.

        Args:
            vlan_id (int): The unique ID of the VLAN to check.

        Returns:
            Result: A Result object indicating the operation's success or failure.
            - If the VLAN with the specified ID is found, 'status' is set to True,
                    'row_id' contains the ID of the found VLAN, and 'reason' is not applicable.
            - If the VLAN with the specified ID is not found, 'status' is set to False,
                    'row_id' is set to self.ROW_ID_NOT_FOUND, and 'reason' provides a detailed message.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT ID FROM Vlans WHERE VlanID = ?", (vlan_id,))
            result = cursor.fetchone()

            if result is None:
                self.log.debug(f"vlan_id_exists() -> VLAN with ID {vlan_id} NOT FOUND")
                return Result(status=False, row_id=self.ROW_ID_NOT_FOUND, reason=f"VLAN with ID {vlan_id} not found")
            
            else:                
                self.log.debug(f"vlan_id_exists() -> VLAN with ID {vlan_id} FOUND -> row-id: {result[0]}")
                return Result(status=True, row_id=result[0])

        except sqlite3.Error as e:
            self.log.error("Error checking VLAN existence: %s", e)
            return Result(status=False, row_id=self.ROW_ID_NOT_FOUND, reason=str(e))

    def insert_vlan_id(self, vlan_id: int) -> Result:
        """
        Insert a VLAN ID into the 'Vlans' table if it does not already exist.

        Args:
            vlan_id (int): The VLAN ID to be inserted.

        Returns:
            Result: A Result object containing the status of the operation, 
                    the row ID of the inserted record (if applicable), 
                    and an optional reason for failure.
        """

        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO Vlans (VlanID) VALUES (?)",
                (vlan_id,)
            )

            self.connection.commit()
            self.log.debug(f"VlanID: {vlan_id} inserted sucessfully")
            return Result(status=STATUS_OK, row_id=cursor.lastrowid)

        except sqlite3.Error as e:
            self.log.error(f"VlanID: {vlan_id} inserted sucessfully, error: {e}")
            return Result(status=STATUS_NOK, row_id=None, reason=str(e))
        
    def insert_vlan(self, vlanid: int, vlan_name: VlanName, vlan_interfaces_fk: int = ROW_ID_NOT_FOUND) -> Result:
        """
        Insert data into the 'Vlans' table.

        Args:
            vlanid (int): The unique ID of the VLAN.
            vlan_name (str): The name of the VLAN.
            vlan_interfaces_fk (int, optional): The foreign key referencing VLAN interfaces.

        Returns:
            Result: A Result object with the status and row ID of the inserted VLAN.
                - If the operation is successful, the Result object will have 'status' set to STATUS_OK and 'row_id' set to the
                  unique identifier of the inserted VLAN.
                - If the VLAN with the provided 'vlanid' already exists, the Result object will have 'status' set to STATUS_NOK,
                  'row_id' set to None, and 'reason' providing information about the existing VLAN.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        self.log.debug(
            f"insert_vlan() -> vlanid: {vlanid}, vlan-if-fkey: {vlan_interfaces_fk}, vlan-name: {vlan_name}")

        try:
            # Check if VLAN with the provided 'vlanid' already exists
            result_vlan_id = self.vlan_id_exists(vlanid)

            if result_vlan_id.status:
                return Result(status=STATUS_NOK, 
                              row_id=result_vlan_id.row_id, 
                              reason=f"VLAN with ID {vlanid} already exists.", result=result_vlan_id.result)

            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO Vlans (VlanID, VlanInterfaces_FK, VlanName) VALUES (?, ?, ?)",
                (vlanid, vlan_interfaces_fk, vlan_name)
            )

            self.connection.commit()
            self.log.debug(
                "Data inserted into the 'Vlans' table successfully.")
            return Result(status=STATUS_OK, 
                          row_id=cursor.lastrowid)

        except sqlite3.Error as e:
            self.log.error("Error inserting data into 'Vlans': %s", e)
            return Result(status=STATUS_NOK, row_id=None, reason=str(e))

    def update_vlan_name_by_vlan_id(self, vlan_id: int, vlan_name: VlanName) -> Result:
        """
        Update the Vlan-Name of a VLAN in the database.

        Args:
            vlan_id (int): The unique ID of the VLAN to update.
            vlan_name (str): The new VLAN name for the VLAN.

        Returns:
            Result: A Result object indicating the operation's success or failure and the affected row_id.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE Vlans SET VlanName = ? WHERE VlanID = ?",
                (vlan_name, vlan_id)
            )
            self.connection.commit()
            row_id = cursor.lastrowid  # Retrieve the row_id of the affected row
            self.log.debug(
                f"VLAN Name -> {vlan_name} of VlanID -> {vlan_id} updated successfully.")
            return Result(status=STATUS_OK, row_id=row_id, result={'VlanName': vlan_name})

        except sqlite3.Error as e:
            self.log.error("Error updating VLAN name: %s", e)
            return Result(status=STATUS_NOK, row_id=vlan_id, reason=str(e))

    def update_vlan_description_by_vlan_id(self, vlan_id: int, vlan_description: str) -> Result:
        """
        Update the description of a VLAN in the database.

        Args:
            vlan_id (int): The unique ID of the VLAN to update.
            vlan_description (str): The new description for the VLAN.

        Returns:
            Result: A Result object indicating the operation's success or failure and the affected row.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE Vlans SET VlanDescription = ? WHERE ID = ?",
                (vlan_description, vlan_id)
            )
            self.connection.commit()
            cursor.execute("SELECT * FROM Vlans WHERE ID = ?", (vlan_id,))
            updated_row = cursor.fetchone()

            self.log.debug(
                f"Description of VLAN {vlan_id} updated successfully.")
            return Result(status=STATUS_OK, row_id=updated_row, result=f"Description of VLAN {vlan_id} updated successfully")

        except sqlite3.Error as e:
            self.log.error("Error updating VLAN description: %s", e)
            return Result(status=STATUS_NOK, row_id=vlan_id, reason=str(e))

    def insert_vlan_interface(self, vlan_id: int, interface_name: InterfaceName) -> Result:
        """
        Inserts a VLAN interface into the database.
        """
        try:
            cursor = self.connection.cursor()

            # Retrieve the Interface ID using the InterfaceName
            cursor.execute("SELECT ID FROM Interfaces WHERE InterfaceName = ?", (interface_name,))
            interface_id_row = cursor.fetchone()

            if interface_id_row is None:
                err_msg = f"Interface '{interface_name}' not found"
                return Result(status=STATUS_NOK, row_id=RouterShellDB.FK_NOT_FOUND, reason=err_msg)

            interface_id = interface_id_row[0]
            bridge_fk = RouterShellDB.FK_NOT_FOUND
            
            # Check if the VLAN ID already exists in the VlanInterfaces table
            cursor.execute(
                "SELECT ID FROM VlanInterfaces WHERE VlanID = ? AND Interfaces_FK = ?", 
                (vlan_id, interface_id)
            )
            existing_row = cursor.fetchone()

            if existing_row:
                err_msg = f"Interface '{interface_name}' is already linked to VLAN {vlan_id}"
                self.log.info(err_msg)
                return Result(status=STATUS_OK, row_id=vlan_id, reason=err_msg)

            self.log.info(f'insert_vlan_interface() -> VlanID: {vlan_id} -> InterfaceID: {interface_id} -> Bridge-FK: {bridge_fk}')

            # Insert the new VLAN-Interface association
            cursor.execute(
                "INSERT INTO VlanInterfaces (VlanID, Interfaces_FK, Bridge_FK) VALUES (?, ?, ?)",
                (vlan_id, interface_id, bridge_fk)
            )
            self.connection.commit()
            inserted_row_id = cursor.lastrowid

            success_msg = f"Interface '{interface_name}' linked to VLAN {vlan_id} successfully."
            self.log.info(success_msg)
            return Result(status=STATUS_OK, row_id=inserted_row_id, reason=success_msg)

        except sqlite3.IntegrityError as e:
            self.log.error("Integrity error linking VLAN to interface: %s", e)
            return Result(status=STATUS_NOK, row_id=RouterShellDB.FK_NOT_FOUND, reason="Integrity error occurred.")

        except sqlite3.Error as e:
            self.log.error("Database error linking VLAN to interface: %s", e)
            return Result(status=STATUS_NOK, row_id=RouterShellDB.FK_NOT_FOUND, reason="Database error occurred.")

        except Exception as e:
            self.log.error("Unexpected error linking VLAN to interface: %s", e)
            return Result(status=STATUS_NOK, row_id=RouterShellDB.FK_NOT_FOUND, reason="Unexpected error occurred.")

    def delete_vlan_interface(self, vlan_id: int, interface_name: InterfaceName) -> Result:
        """
        Deletes an interface from a VLAN in the database.
        
        :param vlan_id: The ID of the VLAN to dissociate from the interface.
        :param interface_name: The name of the interface to remove from the VLAN.
        :return: Result object indicating the status, row ID, and reason for the operation.
        """
        try:
            cursor = self.connection.cursor()

            # Retrieve the Interface ID using the InterfaceName
            cursor.execute("SELECT ID FROM Interfaces WHERE InterfaceName = ?", (interface_name,))
            interface_id_row = cursor.fetchone()

            if interface_id_row is None:
                err_msg = f"Interface '{interface_name}' not found"
                return Result(status=STATUS_NOK, row_id=RouterShellDB.FK_NOT_FOUND, reason=err_msg)

            interface_id = interface_id_row[0]

            # Check if the interface is linked to the VLAN in the VlanInterfaces table
            cursor.execute(
                "SELECT ID FROM VlanInterfaces WHERE VlanID = ? AND Interfaces_FK = ?", 
                (vlan_id, interface_id)
            )
            existing_row = cursor.fetchone()

            if not existing_row:
                err_msg = f"Interface '{interface_name}' is not linked to VLAN {vlan_id}"
                return Result(status=STATUS_OK, row_id=RouterShellDB.FK_NOT_FOUND, reason=err_msg)

            # Delete the VLAN-Interface association
            cursor.execute(
                "DELETE FROM VlanInterfaces WHERE VlanID = ? AND Interfaces_FK = ?",
                (vlan_id, interface_id)
            )
            self.connection.commit()

            success_msg = f"Interface '{interface_name}' removed from VLAN {vlan_id} successfully."
            self.log.debug(success_msg)
            return Result(status=STATUS_OK, row_id=existing_row[0], reason=success_msg)

        except sqlite3.Error as e:
            self.log.error("Database error deleting VLAN interface: %s", e)
            return Result(status=STATUS_NOK, row_id=RouterShellDB.FK_NOT_FOUND, reason="Database error occurred.")

        except Exception as e:
            self.log.error("Unexpected error deleting VLAN interface: %s", e)
            return Result(status=STATUS_NOK, row_id=RouterShellDB.FK_NOT_FOUND, reason="Unexpected error occurred.")

    def show_vlans(self):
        try:

            # SQL query to retrieve VLAN information
            query = """
                SELECT
                    Vlans.ID AS VLAN_ID,
                    Vlans.VlanName AS VLAN_NAME,
                    Vlans.VlanDescription AS VLAN_DESCRIPTION,
                    VlanInterfaces.ID AS INTERFACE_ID,
                    VlanInterfaces.VlanName AS INTERFACE_VLAN_NAME,
                    VlanInterfaces.Interfaces_FK AS INTERFACE_ID,
                    VlanInterfaces.Bridge_FK AS BRIDGE_ID
                FROM
                    Vlans
                LEFT JOIN
                    VlanInterfaces
                ON
                    Vlans.VlanInterfaces_FK = VlanInterfaces.ID;
            """
            cursor = self.connection.cursor()
            cursor.execute(query)
            vlan_data = cursor.fetchall()

            return vlan_data

        except sqlite3.Error as e:
            self.log.error("Error:", e)
            return []

    def select_vlan_interfaces_id(self, vlan_name: VlanName) -> int:
        """
        Retrieve the ID of VLAN interfaces by the VLAN name.

        Args:
            vlan_name (str): The name of the VLAN.

        Returns:
            int: The ID of the VLAN interfaces if found, or None if not found.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT ID FROM VlanInterfaces WHERE VlanName = ?", (vlan_name,))
            row = cursor.fetchone()
            if row:
                return row[0]

        except sqlite3.Error as e:
            self.log.error("Error retrieving 'VlanInterfaces' ID: %s", e)
        return None

    def select_vlan_name_by_vlan_id(self, vlan_id: int) -> Result:
        """
        Retrieve the VLAN name based on the VLAN ID from the 'Vlans' table.

        Args:
            vlan_id (int): The VLAN ID to search for.

        Returns:
            Result | None: A Result object representing the outcome of the database operation.
                - If the operation is successful, the Result object will have 'status' set to True,
                  'row_id' representing the unique identifier of the affected row, and 'result' containing the dict: {'VlanName'}.
                - If there is an error, the Result object will have 'status' set to False, 'reason' providing additional
                  information about the error, and 'row_id' and 'result' set to None.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT ID, VlanName FROM Vlans WHERE VlanID = ?", (vlan_id,))
            row = cursor.fetchone()

            if row:
                return Result(status=STATUS_OK, row_id=row[0], result={'VlanName': row[1]})
            else:
                return Result(status=STATUS_NOK, row_id=None, reason=f"No VLAN found with ID: {vlan_id}")

        except sqlite3.Error as e:
            error_message = f"Error retrieving VLAN name for ID {vlan_id}: {e}"
            self.log.error(error_message)
            return Result(status=STATUS_NOK, row_id=None, reason=error_message)

    def select_vlan_name_by_vlan_id(self, vlan_id: int) -> Result:
        """
        Retrieve the VLAN name based on the VLAN ID from the 'Vlans' table.

        Args:
            vlan_id (int): The VLAN ID to search for.

        Returns:
            Result | None: A Result object representing the outcome of the database operation.
                - If the operation is successful, the Result object will have 'status' set to True,
                  'row_id' representing the unique identifier of the affected row, and 'result' containing the dict: {'VlanName'}.
                - If there is an error, the Result object will have 'status' set to False, 'reason' providing additional
                  information about the error, and 'row_id' and 'result' set to None.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT ID, VlanName FROM Vlans WHERE VlanID = ?", (vlan_id,))
            row = cursor.fetchone()

            if row:
                return Result(status=STATUS_OK, row_id=row[0], result={'VlanName': row[1]})
            else:
                return Result(status=STATUS_NOK, row_id=None, reason=f"No VLAN found with ID: {vlan_id}")

        except sqlite3.Error as e:
            error_message = f"Error retrieving VLAN name for ID {vlan_id}: {e}"
            self.log.error(error_message)
            return Result(status=STATUS_NOK, row_id=None, reason=error_message)

    def select_vlan_id_by_vlan_name(self, vlan_name: VlanName) -> Result:
        """
        Retrieves the VLAN ID associated with a given VLAN name from the database.

        Args:
            vlan_name (str): The name of the VLAN.

        Returns:
            Result: An instance of the Result class.
                - status (bool): STATUS_OK if the VLAN ID is found, STATUS_NOK otherwise.
                - row_id (int | None): The row ID of the VLAN entry if found, None otherwise.
                - result (dict | None): A dictionary containing the VLAN ID if found, None otherwise.
                - reason (str | None): A reason for the failure if STATUS_NOK.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT ID, VlanID FROM Vlans WHERE VlanName = ?", (vlan_name,))
            row = cursor.fetchone()

            if row:
                return Result(status=STATUS_OK, row_id=row[0], result={'VlanID': row[1]})
            else:
                return Result(status=STATUS_NOK, row_id=None, reason=f"No VlanID found with VlanName: {vlan_name}")

        except sqlite3.Error as e:
            error_message = f"Error retrieving VlanID for VlanName {vlan_name}: {e}"
            self.log.error(error_message)
            return Result(status=STATUS_NOK, row_id=None, reason=error_message)

    def select_interfaces_by_vlan_id(self, vlan_id: int) -> list[Result]:
        """
        Retrieves a list of interfaces associated with a given VLAN ID from the database.
        The list contains Result objects with interface information.
        The interface information includes the interface name, VLAN ID
        If the VLAN ID is not found, an empty list is returned.
        If an error occurs, an empty list is returned.
        """
        try:
            cursor = self.connection.cursor()

            # Query to retrieve the interfaces linked to the specified VLAN ID
            cursor.execute(
                """
                SELECT I.InterfaceName, VI.VlanID,
                FROM VlanInterfaces VI
                JOIN Interfaces I ON VI.Interfaces_FK = I.ID
                JOIN Vlans V ON VI.VlanID = V.ID
                WHERE VI.VlanID = ?
                """, 
                (vlan_id,)
            )
            
            rows = cursor.fetchall()
            
            if not rows:
                self.log.info(f"No interfaces found for VLAN ID {vlan_id}.")
                return []

            # Create a list of Result objects to return
            result_list = [
                Result(
                    status=STATUS_OK,
                    row_id=row[1],
                    reason=f"Interface '{row[0]}' linked to VLAN '{row[2]}'",
                    result={
                        "InterfaceName": row[0],
                        "VlanID": row[1],
                    }
                )
                for row in rows
            ]

            return result_list

        except sqlite3.Error as e:
            self.log.error(f"Database error retrieving interfaces by VLAN ID: {str(e)}")
            return []

        except Exception as e:
            self.log.error(f"Unexpected error retrieving interfaces by VLAN ID: {str(e)}")
            return []


    '''
                        NAT DATABASE
    '''

    def global_nat_pool_name_exists(self, pool_name: NatPoolName) -> Result:
        """
        Check if a NAT pool with the given name exists in the NAT database.

        Args:
            pool_name (str): The name of the NAT pool to check for existence.

        Returns:
            Result: A Result object with the status and a boolean value indicating if the NAT pool exists.
                    `status`: True is successful, False otherwise
                    `row_id`: Row-ID of the found NAT Pool, Row-ID of 0 is Not Found

        This method queries the NAT database to determine whether a NAT pool with the provided name exists.
        If any matching pool is found, it returns a Result with STATUS_OK and True; otherwise, it returns
        a Result with STATUS_OK and False.

        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM Nats WHERE NatPoolName = ?", (pool_name,))
            result = cursor.fetchone()

            if result and result[0] > 0:
                self.log.debug(
                    f"global_nat_pool_name_exists({pool_name}) Exists")
                return Result(True, row_id=result[0])
            else:
                self.log.debug(
                    f"global_nat_pool_name_exists({pool_name}) NOT Exists")
                return Result(False, row_id=0)

        except sqlite3.Error as e:
            error_message = f"Error checking NAT pool existence: {e}"
            return Result(False, row_id=0, reason=error_message)

    def insert_global_nat_pool(self, nat_pool_name: NatPoolName) -> Result:
        """
        Insert a new global NAT configuration into the 'Nats' table.

        Args:
            nat_pool_name (str): The name of the NAT pool.

        Returns:
            Result: A Result object with the status of the insertion and the row ID.
                    - 'status' STATUS_OK if successful, STATUS_NOK otherwise
        """
        self.log.debug(f"insert_global_nat_pool({nat_pool_name})")

        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO Nats (NatPoolName) VALUES (?)", (nat_pool_name,))
            self.connection.commit()

            row_id = cursor.lastrowid
            self.log.debug(
                f"Inserted global NAT pool '{nat_pool_name}' with row ID: {row_id}")

            return Result(status=STATUS_OK, row_id=row_id)

        except sqlite3.Error as e:
            error_message = f"Error inserting global NAT: {e}"
            self.log.error(error_message)
            return Result(status=STATUS_NOK, reason=error_message)

    def delete_global_nat_pool_name(self, nat_pool_name: NatPoolName) -> Result:
        """
        Delete a global NAT configuration from the 'Nats' table by NAT pool name.

        Args:
            nat_pool_name (str): The name of the NAT pool to be deleted.

        Returns:
            Result: A Result object with the status of the deletion and additional information.
                    Result.status = STATUS_OK if successful, STATUS_NOK otherwise
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM Nats WHERE NatPoolName = ?",
                           (nat_pool_name,))
            self.connection.commit()

            if cursor.rowcount > 0:
                return Result(STATUS_OK, reason="Global NAT configuration deleted successfully")
            else:
                return Result(STATUS_NOK, reason="No matching NAT pool found for deletion")

        except sqlite3.Error as e:
            error_message = f"Error deleting global NAT configuration: {e}"
            self.log.error(error_message)
            return Result(STATUS_NOK, reason=error_message)

    def update_nat_interface_direction(self, nat_pool_name: NatPoolName, interface_name: InterfaceName, direction: str) -> Result:
        """
        Update the association between a global NAT pool and an inside interface in the 'NatDirections' table.

        Args:
            nat_pool_name (str): The name of the global NAT pool.
            interface_name (str): The name of the inside interface to associate with the NAT pool.
            direction (str): The inside/outside direction interface to associate with the NAT pool.
        Returns:
            Result: A Result object with the status of the update and the row_id of the inserted entry.

        This method updates the association between a global NAT pool and an inside interface in the 'NatDirections' table
        by inserting a new entry with the specified NAT pool, inside interface, and direction. The 'Direction' is set to 'inside' by default.

        Args:
        - nat_pool_name (str): The name of the global NAT pool.
        - interface_name (str): The name of the inside interface to associate with the NAT pool.

        Returns:
        - Result: An object that encapsulates the result of the update operation, including:
            - The status (STATUS_OK for success, STATUS_NOK for failure).
            - The 'row_id' of the newly inserted entry in the 'NatDirections' table.
        """
        try:
            nat_pool_result = self.select_global_nat_row_id(nat_pool_name)

            if not nat_pool_result.status:
                return nat_pool_result

            nat_pool_id = nat_pool_result.row_id

            interface_result = self.interface_exists(interface_name)

            if not interface_result.status:
                return interface_result

            interface_id = interface_result.row_id

            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO NatDirections (NAT_FK, INTERFACE_FK, Direction) VALUES (?, ?, ?)",
                           (nat_pool_id, interface_id, direction))

            # Get the row_id of the newly inserted entry
            row_id = cursor.lastrowid

            self.connection.commit()

            return Result(STATUS_OK, row_id=row_id)

        except sqlite3.Error as e:
            error_message = f"Error updating global NAT interface FK: {e}"
            self.log.error(error_message)
            return Result(STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)

    def select_global_nat_row_id(self, nat_pool_name: NatPoolName) -> Result:
        """
        Retrieve the row ID of a global NAT configuration in the 'Nats' table based on its name.

        Args:
            nat_pool_name (str): The name of the NAT pool.

        Returns:
            Result: A Result object with the status and the row ID of the NAT pool if found.

            status: STATUS_OK successful, STATUS_NOK otherwise
            row_id: STATUS_OK = row-id, STATUS_NOK = row-id=0
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT ID FROM Nats WHERE NatPoolName = ?", (nat_pool_name,))
            row = cursor.fetchone()

            if row is not None:
                row_id = row[0]
                return Result(STATUS_OK, row_id=row_id)
            else:
                error_message = f"Global NAT pool '{nat_pool_name}' not found."
                self.log.error(error_message)
                return Result(STATUS_NOK, reason=error_message)

        except sqlite3.Error as e:
            error_message = f"Error retrieving global NAT row ID: {e}"
            self.log.error(error_message)
            return Result(STATUS_NOK, reason=error_message)

    def insert_interface_nat_direction(self, interface_name: InterfaceName, nat_pool_name: NatPoolName, direction: str) -> Result:
        """
        Insert a new NAT direction configuration into the 'NatDirections' table.

        Args:
            interface_name (str): The name of the interface for the NAT direction.
            nat_pool_name (str): The name of the NAT pool associated with the direction.
            direction (str): The direction (e.g., 'inside' or 'outside').

        Returns:
            Result: A Result object with the status of the insertion.
        """
        try:
            self.log.debug(
                f"insert_interface_nat_direction(Parameters: {interface_name} -> {nat_pool_name} -> {direction})")

            nat_pool_result = self.select_global_nat_row_id(nat_pool_name)

            if nat_pool_result.status:
                nat_pool_error = f"Unable to insert Interface-Nap-Pool, nat-pool-name: ({nat_pool_name}) does not exists"
                self.log.error(f"{nat_pool_error}")
                return Result(STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=nat_pool_error)

            nat_pool_id = nat_pool_result.row_id

            interface_result = self.interface_exists(interface_name)

            if not interface_result.status:
                if_pool_error = f"Unable to insert Interface-Nap-Pool, interface: ({interface_name}) does not exists"
                self.log.error(f"{if_pool_error}")
                return Result(STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=if_pool_error)

            interface_id = interface_result.row_id

            self.log.debug(
                f"insert_interface_nat_direction(if-id: {interface_id} -> nat-pool-id: {nat_pool_id} -> {direction})")

            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO NatDirections (NAT_FK, Interfaces_FK, Direction) VALUES (?, ?, ?)",
                           (nat_pool_id, interface_id, direction))

            self.connection.commit()
            inserted_row_id = cursor.lastrowid

            return Result(STATUS_OK, row_id=inserted_row_id)

        except sqlite3.Error as e:
            error_message = f"Error inserting NAT direction: {e}"
            self.log.error(error_message)
            return Result(STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)

    def delete_interface_nat_direction(self, interface_name: InterfaceName, nat_pool_name: NatPoolName) -> Result:
        """
        Delete all NAT direction configurations for a specified interface and NAT pool.

        Args:
            interface_name (str): The name of the interface for which NAT directions should be deleted.
            nat_pool_name (str): The name of the NAT pool associated with the directions.

        Returns:
            Result: A Result object with the status of the deletion.
        """
        try:
            nat_pool_result = self.select_global_nat_row_id(nat_pool_name)

            if not nat_pool_result.status:
                return nat_pool_result

            nat_pool_id = nat_pool_result.row_id

            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM NatDirections WHERE NAT_FK = ? AND INTERFACE_FK = ?",
                           (nat_pool_id, interface_name))
            self.connection.commit()
            return Result(STATUS_OK)

        except sqlite3.Error as e:
            error_message = f"Error deleting NAT directions: {e}"
            self.log.error(error_message)
            return Result(STATUS_NOK, reason=error_message)

    def select_global_nat_pool_names(self) -> list:
        """
        Retrieve a list of global NAT pool names from the NAT database.

        Returns:
            list: A list of NAT pool names.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT NatPoolName FROM Nats")
            pool_names = [row[0] for row in cursor.fetchall()]
            return pool_names

        except sqlite3.Error as e:
            self.log.error(
                f"An error occurred while retrieving global NAT pool names: {e}")
            return []

    def inside_interface_exists(self, pool_name: NatPoolName, interface_name: InterfaceName) -> Result:
        """
        Check if an inside interface is associated with a NAT pool configuration.

        Args:
            pool_name (str): The name of the NAT pool.
            interface_name (str): The name of the inside interface to check.

        Returns:
            Result: A Result object with the status and a boolean value indicating if the inside interface is associated with the NAT pool.
            status: True if inside interface exist, otherwise False
        """

        '''avoid circular imports'''
        from routershell.lib.network_manager.network_operations.nat import NATDirection

        try:
            if not pool_name or not interface_name:
                error_message = "Invalid input: Pool name and interface name must be provided."
                return Result(STATUS_NOK, reason=error_message)

            pool_exists_result = self.global_nat_pool_name_exists(pool_name)

            if not pool_exists_result.status:
                return pool_exists_result

            if not pool_exists_result.reason:
                return Result(False, reason=False)

            interface_exists_result = self.interface_exists(interface_name)

            if not interface_exists_result.status:
                return interface_exists_result

            if not interface_exists_result.reason:
                return Result(False, reason=False)

            nat_pool_id_result = self.select_global_nat_row_id(pool_name)
            interface_id_result = self.select_interface_id(interface_name)

            if not nat_pool_id_result.status:
                return nat_pool_id_result

            if not interface_id_result.status:
                return interface_id_result

            nat_pool_id = nat_pool_id_result.row_id
            interface_id = interface_id_result.row_id

            direction_exists = self._interface_nat_direction_exists(
                nat_pool_id, interface_id, NATDirection.INSIDE)

            return Result(True, reason=direction_exists)

        except Exception as e:
            error_message = f"An error occurred while checking inside interface association: {e}"
            return Result(False, reason=error_message)

    def nat_direction_interface_exists(self, pool_name: NatPoolName, interface_name: InterfaceName, direction: str) -> Result:

        try:
            if not pool_name or not interface_name:
                error_message = "Invalid input: Pool name and interface name must be provided."
                return Result(STATUS_NOK, reason=error_message)

            pool_exists_result = self.global_nat_pool_name_exists(pool_name)

            if not pool_exists_result.status:
                return pool_exists_result

            if not pool_exists_result.reason:
                return Result(False, reason=False)

            interface_exists_result = self.interface_exists(interface_name)

            if not interface_exists_result.status:
                return interface_exists_result

            if not interface_exists_result.reason:
                return Result(False, reason=False)

            nat_pool_id_result = self.select_global_nat_row_id(pool_name)
            interface_id_result = self.select_interface_id(interface_name)

            if not nat_pool_id_result.status:
                return nat_pool_id_result

            if not interface_id_result.status:
                return interface_id_result

            nat_pool_id = nat_pool_id_result.row_id
            interface_id = interface_id_result.row_id

            direction_exists = self._interface_nat_direction_exists(
                nat_pool_id, interface_id, direction)

            return Result(True, reason=direction_exists)

        except Exception as e:
            error_message = f"An error occurred while checking inside interface association: {e}"
            return Result(False, reason=error_message)

    def _interface_nat_direction_exists(self, nat_id: int, interface_id: int, direction: str) -> Result:
        """
        Check if a specific NAT direction exists for a given NAT pool and inside/outside interface.

        Args:
            nat_id (int): The ID of the NAT pool.
            interface_id (int): The ID of the inside/outside interface.
            direction (str): The direction to check (e.g., 'inside' or 'outside').

        Returns:
            bool: True if the specified NAT direction exists, False otherwise.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM NatDirections WHERE NAT_FK = ? AND INTERFACE_FK = ? AND Direction = ?",
                           (nat_id, interface_id, direction))
            result = cursor.fetchone()

            return result[0] > 0

        except sqlite3.Error as e:
            self.log.error(
                f"An error occurred while checking NAT direction existence: {e}")
            return False

    def select_nat_interface_direction(self, interface_name: InterfaceName, nat_pool_name: NatPoolName, direction: str) -> Result:
        """
        Check if the specified interface is associated with the given NAT pool and direction.

        Args:
            interface_name (str): The name of the interface to check.
            nat_pool_name (str): The name of the NAT pool to check.
            direction (str): The direction to check (inside or outside).

        Returns:
            Result: A Result object with the following fields:
                - status (bool): True if the interface is found in the specified NAT pool and direction, False otherwise.
                - row_id (int): The row ID of the found entry, or 0 if not found.

        Raises:
            sqlite3.Error: If there is an error with the database query.

        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT ID FROM Nats WHERE NatPoolName = ?", (nat_pool_name,))
            nat_pool_result = cursor.fetchone()

            if nat_pool_result is None:
                return Result(status=False, row_id=0)  # NAT pool not found

            nat_pool_id = nat_pool_result[0]

            cursor.execute(
                "SELECT ID FROM Interfaces WHERE InterfaceName = ?", (interface_name,))
            interface_result = cursor.fetchone()
            interface_id = interface_result[0]

            self.log.debug(
                f"get_nat_interface_direction_list() - NAT-POOL-ID: {nat_pool_id} - InterfaceID: ({interface_result[0]})")

            if interface_result is None:
                return Result(status=False, row_id=0)  # Interface not found

            cursor.execute("SELECT ID FROM NatDirections WHERE NAT_FK = ? AND Interfaces_FK = ? AND Direction = ?",
                           (nat_pool_id, interface_id, direction))
            nat_direction_result = cursor.fetchone()

            if nat_direction_result is not None:
                self.log.debug(
                    f"get_nat_interface_direction() - interface: {interface_name} -> nat-pool: {nat_pool_name} - direction: {direction} -> Result: Found")
                return Result(status=True, row_id=nat_direction_result[0])
            else:
                msg = f"interface: {interface_name} -> nat-pool: {nat_pool_name} - direction: {direction} -> Result: Not-Found"
                self.log.debug(f"get_nat_interface_direction() - {msg}")
                return Result(status=False, row_id=0, reason=msg)

        except sqlite3.Error as e:
            error_message = f"Error checking NAT interface direction: {e}"
            self.log.error(error_message)
            return Result(status=False, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)

    def select_nat_interface_direction_list(self, nat_pool_name: NatPoolName, direction: str) -> list[Result]:
        """
        Selects a list of interfaces associated with a specific NAT pool and direction.

        Args:
            nat_pool_name: The name of the NAT pool.
            direction: The direction (inbound or outbound) for which to select interfaces.

        Returns:
            A list of `Result` objects. Each `Result` object contains the following information:
            * `status`: True if successful, False if an error occurred.
            * `row_id`: The primary key of the selected record (interface_fk) or `ROW_ID_NOT_FOUND` if an error occurred.
            * `result`: A dictionary containing the following key-value pairs:
                * `Interfaces_FK`: The primary key of the interface record.
                * `InterfaceName`: The name of the interface.

        Raises:
            sqlite3.Error: If an error occurs while interacting with the database.
        """

        try:
            cursor = self.connection.cursor()
            results = []

            cursor.execute("""
                SELECT ND.Interfaces_FK, I.InterfaceName
                FROM NatDirections AS ND
                JOIN Interfaces AS I ON ND.Interfaces_FK = I.ID
                JOIN Nats AS N ON ND.NAT_FK = N.ID
                WHERE N.NatPoolName = ? AND ND.Direction = ?
            """, (nat_pool_name, direction))

            rows = cursor.fetchall()
            for row in rows:
                interface_fk, interface_name = row
                result = Result(status=STATUS_OK, row_id=interface_fk, result={
                                'Interfaces_FK': interface_fk, 'InterfaceName': interface_name})
                results.append(result)

            if len(results) == 0:
                return Result(status=STATUS_NOK,
                              row_id=self.ROW_ID_NOT_FOUND,
                              reason=f'No Interface Found for Nat-Pool: {nat_pool_name} for direction: {direction}',
                              result={'Interfaces_FK': None, 'InterfaceName': None})

            return results

        except sqlite3.Error as e:
            error_message = f"Error selecting NAT interface direction list: {e}"
            self.log.error(error_message)
            return Result(status=STATUS_OK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)

    '''
                        DHCP-SERVER DATABASE
    '''

    def select_dhcp_server_pool_list(self) -> list['Result']:
        """
        Retrieve a list of DHCP server pool names from the 'DHCPServer' table.

        Returns:
            list[Result]: A list of Result objects, each representing a row from the 'DHCPServer' table.
                          Each Result contains a dictionary with the key 'DhcpPoolname' and its value.

        Note:
        - This method assumes that the 'DHCPServer' table exists with the specified schema.
        """
        try:
            # Define the SQL query to retrieve DHCP server pool names.
            query = "SELECT ID, DhcpPoolname FROM DHCPServer;"
            cursor = self.connection.cursor()
            cursor.execute(query)

            # Fetch all rows from the executed query
            rows = cursor.fetchall()

            # Build Result objects for each DHCP server pool name.
            results = [
                Result(
                    status=STATUS_OK,
                    row_id=row[0],
                    reason=f"Retrieved DHCP server pool '{row[1]}' successfully",
                    result={"DhcpPoolname": row[1]}
                )
                for row in rows
            ]

            return results

        except sqlite3.Error as e:
            error_message = f"Failed to retrieve DHCP server pool names. Error: {str(e)}"
            self.log.error(error_message)
            return [Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)]

    def insert_dhcp_pool_name(self, dhcp_pool_name: DhcpPoolName) -> Result:
        """
        Inserts a DHCP pool name into the DHCPServer table.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool to insert.

        Returns:
            Result: A Result object representing the outcome of the operation.

        Note:
        - 'status' attribute in the returned Result object will be STATUS_OK for successful insertions, and STATUS_NOK for failed ones.
        - 'row_id' represents the unique identifier of the inserted row if the insertion is successful, or 0 if it fails.
        - 'reason' in the Result object provides additional information about the operation, which is particularly useful for error messages.
        """
        try:
            query = "INSERT INTO DHCPServer (DhcpPoolname) VALUES (?)"
            cursor = self.connection.cursor()
            cursor.execute(query, (dhcp_pool_name,))
            self.connection.commit()
            row_id = cursor.lastrowid
            return Result(status=STATUS_OK, row_id=row_id, reason=f"Inserted '{dhcp_pool_name}' pool successfully.")

        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to insert '{dhcp_pool_name}' pool. Error: {str(e)}")

    def dhcp_pool_name_exist(self, dhcp_pool_name: DhcpPoolName) -> Result:
        """
        Checks if a DHCP pool name exists in the DHCPServer table.

        Args:
            dhcp_pool_name (str): The DHCP pool name to check.

        Returns:
            Result: A Result object representing the outcome of the operation.

        Note:
        - 'status' attribute in the returned Result object will be True if the pool name exists, and False if it doesn't.
        - 'row_id' represents the unique identifier of the existing row if the pool name exists, or ROW_ID_NOT_FOUND if it doesn't.
        - 'reason' in the Result object provides additional information about the operation, which is particularly useful for result messages.
        """
        try:
            query = "SELECT ID FROM DHCPServer WHERE DhcpPoolname = ?"
            cursor = self.connection.cursor()
            cursor.execute(query, (dhcp_pool_name,))
            row = cursor.fetchone()

            if row:
                return Result(status=True, row_id=row[0], reason=f"Pool name '{dhcp_pool_name}' exists.")
            else:
                return Result(status=False, row_id=self.ROW_ID_NOT_FOUND, reason=f"Pool name '{dhcp_pool_name}' does not exist.")

        except sqlite3.Error as e:
            return Result(status=False, row_id=self.ROW_ID_NOT_FOUND, reason=f"Error while checking pool name existence: {str(e)}")

    def insert_dhcp_pool_subnet(self, dhcp_pool_name: DhcpPoolName, inet_subnet_cidr: InetCidrText) -> Result:
        """
        Inserts a DHCP subnet associated with a DHCP pool name into the DHCPSubnet table if it does not exist.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool to associate the subnet with.
            inet_subnet_cidr (str): The subnet in CIDR notation to insert.

        Returns:
            Result: A Result object representing the outcome of the operation.

        Note:
        - 'status' attribute in the returned Result object will be STATUS_OK for successful insertions, and STATUS_NOK for failed ones.
        - 'row_id' represents the unique identifier of the inserted row if the insertion is successful, or ROW_ID_NOT_FOUND if it fails.
        - 'reason' in the Result object provides additional information about the operation, which is particularly useful for error messages.
        """
        try:
            if not inet_subnet_cidr:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Subnet '({None})' not defined")

            # Check if the subnet already exists
            subnet_exist_result = self.dhcp_pool_subnet_exist(inet_subnet_cidr)
            if subnet_exist_result.status:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Subnet '{inet_subnet_cidr}' already exists.")

            # The subnet does not exist, proceed to check the DHCP pool name
            pool_exist_result = self.dhcp_pool_name_exist(dhcp_pool_name)
            if not pool_exist_result.status:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=pool_exist_result.reason)

            # The pool name exists, proceed to insert the DHCP subnet
            query = "INSERT INTO DHCPSubnet (DHCPServer_FK, InetSubnet) VALUES (?, ?)"
            cursor = self.connection.cursor()
            cursor.execute(query, (pool_exist_result.row_id, inet_subnet_cidr))
            self.connection.commit()
            row_id = cursor.lastrowid
            return Result(status=STATUS_OK, row_id=row_id, reason=f"Inserted subnet '{inet_subnet_cidr}' into '{dhcp_pool_name}' pool successfully.")

        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to insert subnet into '{dhcp_pool_name}' pool. Error: {str(e)}")

    def dhcp_pool_subnet_exist(self, inet_subnet_cidr: InetCidrText) -> Result:
        """
        Checks if a DHCP subnet with a specific CIDR notation exists in the DHCPSubnet table.

        Args:
            inet_subnet_cidr (str): The CIDR notation of the DHCP subnet to check.

        Returns:
            Result: A Result object representing the outcome of the operation.

        Note:
        - 'status' attribute in the returned Result object will be True if the subnet exists, and False if it doesn't.
        - 'row_id' represents the unique identifier of the existing row if the subnet exists, or ROW_ID_NOT_FOUND if it doesn't.
        - 'reason' in the Result object provides additional information about the operation, which is particularly useful for result messages.
        """
        if not inet_subnet_cidr:
            self.log.error(
                f"dhcp_pool_subnet_exist() -> inet_subnet_cidr: {inet_subnet_cidr}, not defined")
            return Result(status=False, row_id=self.ROW_ID_NOT_FOUND, reason=f"inet_subnet_cidr: {inet_subnet_cidr}, not defined")

        try:
            query = "SELECT ID FROM DHCPSubnet WHERE InetSubnet = ?"
            cursor = self.connection.cursor()
            cursor.execute(query, (inet_subnet_cidr,))
            row = cursor.fetchone()

            self.log.debug(
                f"dhcp_pool_subnet_exist({inet_subnet_cidr}) -> row: ({0})")

            if row:
                return Result(status=True, row_id=row[0], reason=f"Subnet '{inet_subnet_cidr}' exists.")
            else:
                return Result(status=False, row_id=self.ROW_ID_NOT_FOUND, reason=f"Subnet '{inet_subnet_cidr}' does not exist.")

        except sqlite3.Error as e:
            return Result(status=False, row_id=self.ROW_ID_NOT_FOUND, reason=f"Error while checking subnet existence: {str(e)}")

    def insert_dhcp_subnet_inet_address_range(self, inet_subnet_cidr: InetCidrText, inet_address_start: InetAddressText, inet_address_end: InetAddressText, inet_address_subnet_cidr: InetCidrText) -> Result:
        """
        Inserts an address range associated with a DHCP subnet specified by its CIDR notation.

        Args:
            inet_subnet_cidr (str): The CIDR notation of the DHCP subnet to associate the address range with.
            inet_address_start (str): The starting IP address of the range.
            inet_address_end (str): The ending IP address of the range.
            inet_address_subnet_cidr (str): The CIDR notation of the subnet for the address range.

        Returns:
            Result: A Result object representing the outcome of the operation.

        Note:
        - 'status' attribute in the returned Result object will be STATUS_OK for successful insertions, and STATUS_NOK for failed ones.
        - 'row_id' represents the unique identifier of the inserted row if the insertion is successful, or ROW_ID_NOT_FOUND if it fails.
        - 'reason' in the Result object provides additional information about the operation, which is particularly useful for error messages.
        """
        try:

            subnet_exist_result = self.dhcp_pool_subnet_exist(inet_subnet_cidr)
            if not subnet_exist_result.status:
                self.log.debug(
                    f"insert_dhcp_subnet_inet_address_range() ERROR-Reason: {subnet_exist_result.reason}")
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=subnet_exist_result.reason)

            query = "INSERT INTO DHCPSubnetPools (DHCPSubnet_FK, InetAddressStart, InetAddressEnd, InetSubnet) VALUES (?, ?, ?, ?)"
            cursor = self.connection.cursor()
            cursor.execute(query, (subnet_exist_result.row_id,
                           inet_address_start, inet_address_end, inet_address_subnet_cidr))
            self.connection.commit()

            row_id = cursor.lastrowid
            return Result(status=STATUS_OK, row_id=row_id, reason=f"Inserted address range '{inet_address_start}-{inet_address_end}' into subnet '{inet_subnet_cidr}' successfully.")

        except sqlite3.Error as e:
            self.log.debug(
                f"insert_dhcp_subnet_inet_address_range() ERROR-Reason: Failed to insert address range into subnet '{inet_subnet_cidr}'. Error: {str(e)}")
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to insert address range into subnet '{inet_subnet_cidr}'. Error: {str(e)}")

    def insert_dhcp_subnet_reservation(self, inet_subnet_cidr: InetCidrText, hw_address: MacAddressText, inet_address: InetAddressText) -> Result:
        """
        Inserts a DHCP reservation for a specific subnet.

        Args:
            inet_subnet_cidr (str): The CIDR notation of the DHCP subnet for the reservation.
            hw_address (str): The hardware address (MAC address) for the reservation.
            inet_address (str): The reserved IP address.

        Returns:
            Result: A Result object representing the outcome of the operation.

        Note:
        - 'status' attribute in the returned Result object will be STATUS_OK for successful insertions, and STATUS_NOK for failed ones.
        - 'row_id' represents the unique identifier of the inserted row if the insertion is successful, or ROW_ID_NOT_FOUND if it fails.
        - 'reason' in the Result object provides additional information about the operation, which is particularly useful for error messages.
        """
        try:
            # Check if the DHCP subnet exists
            subnet_exist_result = self.dhcp_pool_subnet_exist(inet_subnet_cidr)
            if not subnet_exist_result.status:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=subnet_exist_result.reason)

            # Check if the reservation already exists
            reservation_exist_result = self.dhcp_subnet_reservation_exist(
                hw_address, inet_address)
            if reservation_exist_result.status:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=reservation_exist_result.reason)

            # The subnet exists, and the reservation does not exist, proceed to insert the reservation
            query = "INSERT INTO DHCPSubnetReservations (DHCPSubnet_FK, MacAddress, InetAddress) VALUES (?, ?, ?)"
            cursor = self.connection.cursor()
            cursor.execute(query, (subnet_exist_result.row_id,
                           hw_address, inet_address))
            self.connection.commit()
            row_id = cursor.lastrowid
            return Result(status=STATUS_OK, row_id=row_id, reason=f"Inserted reservation for '{hw_address}' with IP '{inet_address}' into subnet '{inet_subnet_cidr}' successfully.")

        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to insert reservation into subnet '{inet_subnet_cidr}'. Error: {str(e)}")

    def dhcp_subnet_reservation_exist(self, hw_address: MacAddressText, inet_address: InetAddressText) -> Result:
        """
        Checks if a DHCP reservation with a specific MAC address and IP address exists in the DHCPSubnetReservations table.

        Args:
            hw_address (str): The MAC address of the reservation.
            inet_address (str): The reserved IP address.

        Returns:
            Result: A Result object representing the outcome of the operation.

        Note:
        - 'status' attribute in the returned Result object will be True if the reservation exists, and False if it doesn't.
        - 'row_id' represents the unique identifier of the existing row if the reservation exists, or ROW_ID_NOT_FOUND if it doesn't.
        - 'reason' in the Result object provides additional information about the operation, which is particularly useful for result messages.
        """
        try:
            query = "SELECT ID FROM DHCPSubnetReservations WHERE MacAddress = ? AND InetAddress = ?"
            cursor = self.connection.cursor()
            cursor.execute(query, (hw_address, inet_address))
            row = cursor.fetchone()

            if row:
                return Result(status=True, row_id=row[0], reason=f"Reservation for MAC '{hw_address}' with IP '{inet_address}' exists.")
            else:
                return Result(status=False, row_id=self.ROW_ID_NOT_FOUND, reason=f"Reservation for MAC '{hw_address}' with IP '{inet_address}' does not exist.")

        except sqlite3.Error as e:
            return Result(status=False, row_id=self.ROW_ID_NOT_FOUND, reason=f"Error while checking reservation existence: {str(e)}")

    def insert_dhcp_subnet_option(self, inet_subnet_cidr: InetCidrText, dhcp_option: str, option_value: str) -> Result:
        """
        Inserts DHCP options associated with a specific DHCP subnet specified by its CIDR notation.

        Args:
            inet_subnet_cidr (str): The CIDR notation of the DHCP subnet for the options.
            dhcp_option (str): The DHCP option name.
            option_value (str): The value of the DHCP option.

        Returns:
            Result: A Result object representing the outcome of the operation.

        Note:
        - 'status' attribute in the returned Result object will be STATUS_OK for successful insertions, and STATUS_NOK for failed ones.
        - 'row_id' represents the unique identifier of the inserted row if the insertion is successful, or ROW_ID_NOT_FOUND if it fails.
        - 'reason' in the Result object provides additional information about the operation, which is particularly useful for error messages.
        """
        try:
            # Check if the DHCP subnet exists
            subnet_exist_result = self.dhcp_pool_subnet_exist(inet_subnet_cidr)
            if not subnet_exist_result.status:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=subnet_exist_result.reason)

            # Check if the option already exists
            option_exist_result = self.dhcp_subnet_option_exist(
                subnet_exist_result.row_id, dhcp_option, option_value)
            if option_exist_result.status:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=option_exist_result.reason)

            # The subnet exists, and the option does not exist, proceed to insert the option
            query = "INSERT INTO DHCPOptions (DhcpOption, DhcpValue, DHCPSubnetPools_FK, DHCPSubnetReservations_FK) VALUES (?, ?, ?, ?)"
            cursor = self.connection.cursor()
            cursor.execute(query, (dhcp_option, option_value,
                           subnet_exist_result.row_id, self.FK_NOT_FOUND))
            self.connection.commit()
            row_id = cursor.lastrowid
            return Result(status=STATUS_OK, row_id=row_id, reason=f"Inserted DHCP option '{dhcp_option}' with value '{option_value}' into subnet '{inet_subnet_cidr}' successfully.")

        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to insert DHCP option into subnet '{inet_subnet_cidr}'. Error: {str(e)}")

    def dhcp_subnet_option_exist(self, subnet_id: int, dhcp_option: str, option_value: str) -> Result:
        """
        Checks if a DHCP option with a specific name and value exists for a specific DHCP subnet.

        Args:
            subnet_id (int): The unique identifier of the DHCP subnet.
            dhcp_option (str): The DHCP option name.
            option_value (str): The value of the DHCP option.

        Returns:
            Result: A Result object representing the outcome of the operation.

        Note:
        - 'status' attribute in the returned Result object will be True if the option exists, and False if it doesn't.
        - 'row_id' represents the unique identifier of the existing row if the option exists, or ROW_ID_NOT_FOUND if it doesn't.
        - 'reason' in the Result object provides additional information about the operation, which is particularly useful for result messages.
        """
        try:
            query = "SELECT ID FROM DHCPOptions WHERE DHCPSubnetPools_FK = ? AND DhcpOption = ? AND DhcpValue = ?"
            cursor = self.connection.cursor()
            cursor.execute(query, (subnet_id, dhcp_option, option_value))
            row = cursor.fetchone()

            if row:
                return Result(status=True, row_id=row[0], reason=f"DHCP option '{dhcp_option}' with value '{option_value}' exists for subnet ID {subnet_id}.")
            else:
                return Result(status=False, row_id=self.ROW_ID_NOT_FOUND, reason=f"DHCP option '{dhcp_option}' with value '{option_value}' does not exist for subnet ID {subnet_id}.")
        except sqlite3.Error as e:
            return Result(status=False, row_id=self.ROW_ID_NOT_FOUND, reason=f"Error while checking DHCP option existence: {str(e)}")

    def insert_dhcp_subnet_reservation_option(self, inet_subnet_cidr: InetCidrText, hw_address: MacAddressText, dhcp_option: str, option_value: str) -> Result:
        """
        Inserts DHCP options associated with a specific DHCP reservation for a specified DHCP subnet.

        Args:
            inet_subnet_cidr (str): The CIDR notation of the DHCP subnet for the reservation.
            hw_address (str): The hardware address (MAC address) for the reservation.
            dhcp_option (str): The DHCP option name.
            option_value (str): The value of the DHCP option.

        Returns:
            Result: A Result object representing the outcome of the operation.

        Note:
        - 'status' attribute in the returned Result object will be STATUS_OK for successful insertions, and STATUS_NOK for failed ones.
        - 'row_id' represents the unique identifier of the inserted row if the insertion is successful, or ROW_ID_NOT_FOUND if it fails.
        - 'reason' in the Result object provides additional information about the operation, which is particularly useful for error messages.
        """
        try:
            # Check if the DHCP reservation exists
            reservation_exist_result = self.dhcp_subnet_reservation_exist(
                inet_subnet_cidr, hw_address)
            if not reservation_exist_result.status:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=reservation_exist_result.reason)

            # Check if the option already exists
            option_exist_result = self.dhcp_reservation_option_exist(
                reservation_exist_result.row_id, dhcp_option, option_value)
            if option_exist_result.status:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=option_exist_result.reason)

            # The reservation exists, and the option does not exist, proceed to insert the option
            query = "INSERT INTO DHCPOptions (DhcpOption, DhcpValue, DHCPSubnetPools_FK, DHCPSubnetReservations_FK) VALUES (?, ?, ?, ?)"
            cursor = self.connection.cursor()
            cursor.execute(query, (dhcp_option, option_value,
                           self.FK_NOT_FOUND, reservation_exist_result.row_id))
            self.connection.commit()
            row_id = cursor.lastrowid
            return Result(status=STATUS_OK, row_id=row_id, reason=f"Inserted DHCP option '{dhcp_option}' with value '{option_value}' for reservation '{hw_address}' in subnet '{inet_subnet_cidr}' successfully.")

        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to insert DHCP option for reservation '{hw_address}' in subnet '{inet_subnet_cidr}'. Error: {str(e)}")

    def dhcp_reservation_option_exist(self, reservation_id: int, dhcp_option: str, option_value: str) -> Result:
        """
        Checks if a DHCP option with a specific name and value exists for a specific DHCP reservation.

        Args:
            reservation_id (int): The unique identifier of the DHCP reservation.
            dhcp_option (str): The DHCP option name.
            option_value (str): The value of the DHCP option.

        Returns:
            Result: A Result object representing the outcome of the operation.

        Note:
        - 'status' attribute in the returned Result object will be True if the option exists, and False if it doesn't.
        - 'row_id' represents the unique identifier of the existing row if the option exists, or ROW_ID_NOT_FOUND if it doesn't.
        - 'reason' in the Result object provides additional information about the operation, which is particularly useful for result messages.
        """
        try:
            query = "SELECT ID FROM DHCPOptions WHERE DHCPSubnetReservations_FK = ? AND DhcpOption = ? AND DhcpValue = ?"
            cursor = self.connection.cursor()
            cursor.execute(query, (reservation_id, dhcp_option, option_value))
            row = cursor.fetchone()

            if row:
                return Result(status=True, row_id=row[0], reason=f"DHCP option '{dhcp_option}' with value '{option_value}' exists for reservation ID {reservation_id}.")
            else:
                return Result(status=False, row_id=self.ROW_ID_NOT_FOUND, reason=f"DHCP option '{dhcp_option}' with value '{option_value}' does not exist for reservation ID {reservation_id}.")

        except sqlite3.Error as e:
            return Result(status=False, row_id=self.ROW_ID_NOT_FOUND, reason=f"Error while checking DHCP option existence: {str(e)}")

    def update_dhcp_pool_name_interface(self, dhcp_pool_name: DhcpPoolName, interface_name: InterfaceName, negate: bool = False) -> Result:
        """
        Update the interface associated with a specific DHCP pool name in the DHCPServer table.

        Parameters:
            dhcp_pool_name (str): The name of the DHCP pool.
            interface_name (str): The name of the interface to associate with the DHCP pool.
            negate (bool, optional): If True, removes the association between the DHCP pool and any interface.
                                    If False (default), associates the DHCP pool with the specified interface.

        Returns:
            Result: A Result object representing the outcome of the operation.

        Note:
            - 'status' attribute in the returned Result object will be STATUS_OK for successful updates,
                and STATUS_NOK for failed ones.
            - 'row_id' represents the unique identifier of the updated row if the update is successful,
                or ROW_ID_NOT_FOUND if it fails.
            - 'reason' in the Result object provides additional information about the operation,
                which is particularly useful for error messages.
        """
        try:
            # Check if the DHCP pool name exists
            pool_exist_result = self.dhcp_pool_name_exist(dhcp_pool_name)

            if not pool_exist_result.status:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=pool_exist_result.reason)

            # Check if the interface name exists in the Interfaces table
            interface_exist_result = self.interface_exists(interface_name)
            if not interface_exist_result.status:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=interface_exist_result.reason)

            # The DHCP pool name exists, and the interface exists, proceed to update the interface
            query = "UPDATE DHCPServer SET Interfaces_FK = ? WHERE DhcpPoolname = ?"
            cursor = self.connection.cursor()

            if negate:
                cursor.execute(query, (None, dhcp_pool_name))
            else:
                cursor.execute(
                    query, (interface_exist_result.row_id, dhcp_pool_name))

            self.connection.commit()

            # Check if any rows were updated
            if cursor.rowcount > 0:
                success_msg = f"Updated interface for DHCP pool '{dhcp_pool_name}' to '{interface_name}' successfully."
                return Result(status=STATUS_OK, row_id=self.ROW_ID_NOT_FOUND, reason=success_msg)
            else:
                failure_msg = f"Failed to update interface for DHCP pool '{dhcp_pool_name}' to '{interface_name}'."
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=failure_msg)

        except sqlite3.Error as e:
            error_msg = f"Failed to update interface for DHCP pool '{dhcp_pool_name}' to '{interface_name}'. Error: {str(e)}"
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_msg)

    def update_dhcp_pool_dhcp_version_mode(self, dhcp_pool_name: DhcpPoolName, mode: str) -> Result:
        """
        Update the DHCP version mode for a specific DHCP pool.

        Parameters:
            dhcp_pool_name (str): The name of the DHCP pool.
            mode (str): The DHCP version mode to set.

        Returns:
            Result: A Result object representing the outcome of the operation.
        """
        try:
            query = """
                UPDATE DHCPv6ServerOption
                SET Mode = ?
                WHERE DHCPv6ServerOption.DHCPVersionServerOptions_FK IN (
                    SELECT DHCPVersionServerOptions.ID
                    FROM DHCPVersionServerOptions
                    JOIN DHCPSubnet ON DHCPVersionServerOptions.DHCPSubnet_FK = DHCPSubnet.ID
                    JOIN DHCPServer ON DHCPSubnet.DHCPServer_FK = DHCPServer.ID
                    JOIN Interfaces ON DHCPServer.Interfaces_FK = Interfaces.ID
                    WHERE DHCPServer.DhcpPoolname = ?
                );
            """

            cursor = self.connection.cursor()
            cursor.execute(query, (mode, dhcp_pool_name,))
            self.connection.commit()

            if cursor.rowcount > 0:
                return Result(status=STATUS_OK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Updated DHCP version mode for DHCP pool '{dhcp_pool_name}' to '{mode}' successfully.")
            else:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to update DHCP version mode for DHCP pool '{dhcp_pool_name}' to '{mode}'.")

        except sqlite3.Error as e:
            error_message = f"Failed to update DHCP version mode. Error: {str(e)}"
            self.log.error(error_message)
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)

    def delete_dhcp_subnet_inet_address_range(self, inet_subnet_cidr: InetCidrText, inet_address_start: InetAddressText, inet_address_end: InetAddressText, inet_address_subnet_cidr: InetCidrText) -> Result:
        """
        Deletes a range of IP addresses associated with a specific DHCP subnet.

        Args:
            inet_subnet_cidr (str): The CIDR notation of the DHCP subnet for the IP address range.
            inet_address_start (str): The starting IP address of the range to delete.
            inet_address_end (str): The ending IP address of the range to delete.
            inet_address_subnet_cidr (str): The subnet CIDR notation to verify the range.

        Returns:
            Result: A Result object representing the outcome of the operation.

        Note:
        - 'status' attribute in the returned Result object will be STATUS_OK for successful deletions, and STATUS_NOK for failed ones.
        - 'row_id' represents the unique identifier of the deleted row if the deletion is successful, or ROW_ID_NOT_FOUND if it fails.
        - 'reason' in the Result object provides additional information about the operation, which is particularly useful for error messages.
        """
        try:
            # Check if the DHCP subnet exists
            subnet_exist_result = self.dhcp_pool_subnet_exist(inet_subnet_cidr)
            if not subnet_exist_result.status:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=subnet_exist_result.reason)

            # Check if the specified IP address range exists within the subnet
            range_exist_result = self.dhcp_subnet_range_exist(
                subnet_exist_result.row_id, inet_address_start, inet_address_end, inet_address_subnet_cidr)
            if not range_exist_result.status:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=range_exist_result.reason)

            # The subnet exists, and the specified IP address range exists, proceed to delete the range
            query = "DELETE FROM DHCPSubnetPools WHERE ID = ?"
            cursor = self.connection.cursor()
            cursor.execute(query, (range_exist_result.row_id,))
            self.connection.commit()

            # Check if any rows were deleted
            if cursor.rowcount > 0:
                return Result(status=STATUS_OK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Deleted IP address range from '{inet_address_start}' to '{inet_address_end}' in subnet '{inet_subnet_cidr}' successfully.")
            else:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to delete IP address range from '{inet_address_start}' to '{inet_address_end}' in subnet '{inet_subnet_cidr}'.")

        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to delete IP address range from '{inet_address_start}' to '{inet_address_end}' in subnet '{inet_subnet_cidr}'. Error: {str(e)}")

    def delete_dhcp_pool_name(self, dhcp_pool_name: DhcpPoolName) -> Result:
        """
        Deletes a DHCP pool name from the DHCPServer table.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool to delete.

        Returns:
            Result: A Result object representing the outcome of the operation.

        Note:
        - 'status' attribute in the returned Result object will be STATUS_OK for successful deletions, and STATUS_NOK for failed ones.
        - 'row_id' represents the unique identifier of the deleted row if the deletion is successful, or ROW_ID_NOT_FOUND if it fails.
        - 'reason' in the Result object provides additional information about the operation, which is particularly useful for error messages.
        """
        try:
            # Check if the DHCP pool name exists
            pool_exist_result = self.dhcp_pool_name_exist(dhcp_pool_name)
            if not pool_exist_result.status:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=pool_exist_result.reason)

            # The pool name exists, proceed to delete it
            query = "DELETE FROM DHCPServer WHERE DhcpPoolname = ?"
            cursor = self.connection.cursor()
            cursor.execute(query, (dhcp_pool_name,))
            self.connection.commit()

            # Check if any rows were deleted
            if cursor.rowcount > 0:
                return Result(status=STATUS_OK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Deleted DHCP pool name '{dhcp_pool_name}' successfully.")
            else:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to delete DHCP pool name '{dhcp_pool_name}'.")

        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to delete DHCP pool name '{dhcp_pool_name}'. Error: {str(e)}")

    def delete_dhcp_subnet_reservation_option(self, inet_subnet_cidr: InetCidrText, hw_address: MacAddressText, dhcp_option: str, option_value: str) -> Result:
        try:

            option_exist_result = self.dhcp_subnet_reservation_option_exist(
                inet_subnet_cidr, hw_address, dhcp_option, option_value)
            if not option_exist_result.status:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=option_exist_result.reason)

            query = "DELETE FROM DHCPOptions WHERE DhcpOption = ? AND DhcpValue = ?"
            cursor = self.connection.cursor()
            cursor.execute(query, (dhcp_option, option_value))
            self.connection.commit()

            if cursor.rowcount > 0:
                return Result(status=STATUS_OK, row_id=self.ROW_ID_NOT_FOUND, reason="Deleted DHCP subnet reservation option successfully.")
            else:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason="Failed to delete DHCP subnet reservation option.")

        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to delete DHCP subnet reservation option. Error: {str(e)}")

    def dhcp_subnet_reservation_option_exist(self, inet_subnet_cidr: InetCidrText, hw_address: MacAddressText, dhcp_option: str, option_value: str) -> Result:
        """
        Checks if a DHCP subnet reservation option exists in the DHCPOptions table.

        Args:
            inet_subnet_cidr (str): The subnet in CIDR notation.
            hw_address (str): The MAC address of the reservation.
            dhcp_option (str): The DHCP option to check.
            option_value (str): The value of the DHCP option to check.

        Returns:
            Result: A Result object indicating the existence of the reservation option.

        Note:
        - 'status' attribute in the returned Result object will be STATUS_OK if the option exists, and STATUS_NOK if it does not.
        - 'row_id' is set to the unique identifier of the reservation option if it exists, or ROW_ID_NOT_FOUND if it does not.
        - 'reason' in the Result object provides additional information about the existence check.
        """
        try:
            query = "SELECT DHCPOptions.ID FROM DHCPOptions " \
                    "JOIN DHCPSubnetPools ON DHCPOptions.DHCPSubnetPools_FK = DHCPSubnetPools.ID " \
                    "JOIN DHCPSubnetReservations ON DHCPSubnetPools.DHCPSubnet_FK = DHCPSubnetReservations.DHCPSubnet_FK " \
                    "JOIN DHCPSubnet ON DHCPSubnetReservations.DHCPSubnet_FK = DHCPSubnet.ID " \
                    "WHERE DHCPSubnet.InetSubnet = ? AND DHCPSubnetReservations.MacAddress = ? AND DHCPOptions.DhcpOption = ? AND DHCPOptions.DhcpValue = ?"

            cursor = self.connection.cursor()
            cursor.execute(query, (inet_subnet_cidr, hw_address,
                           dhcp_option, option_value))
            row = cursor.fetchone()

            if row:
                return Result(status=STATUS_OK, row_id=row[0], reason="DHCP subnet reservation option exists.")
            else:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason="DHCP subnet reservation option does not exist.")
        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Error checking DHCP subnet reservation option existence: {str(e)}")

    def delete_dhcp_subnet_option(self, inet_subnet_cidr: InetCidrText, dhcp_option: str, option_value: str) -> Result:
        """
        Deletes a DHCP subnet option from the DHCPOptions table.

        Args:
            inet_subnet_cidr (str): The subnet in CIDR notation.
            dhcp_option (str): The DHCP option to delete.
            option_value (str): The value of the DHCP option to delete.

        Returns:
            Result: A Result object representing the outcome of the operation.

        Note:
        - 'status' attribute in the returned Result object will be STATUS_OK for successful deletions, and STATUS_NOK for failed ones.
        - 'row_id' represents the unique identifier of the deleted row if the deletion is successful, or ROW_ID_NOT_FOUND if it fails.
        - 'reason' in the Result object provides additional information about the operation, which is particularly useful for error messages.
        """
        try:
            # Check if the DHCP subnet option exists
            option_exist_result = self.dhcp_subnet_option_exist(
                inet_subnet_cidr, dhcp_option, option_value)
            if not option_exist_result.status:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=option_exist_result.reason)

            # The subnet option exists, proceed to delete it
            query = "DELETE FROM DHCPOptions WHERE DHCPSubnetPools_FK IN (SELECT ID FROM DHCPSubnetPools WHERE DHCPSubnet_FK = (SELECT ID FROM DHCPSubnet WHERE InetSubnet = ?) AND InetAddressStart IS NULL) AND DhcpOption = ? AND DhcpValue = ?"
            cursor = self.connection.cursor()
            cursor.execute(
                query, (inet_subnet_cidr, dhcp_option, option_value))
            self.connection.commit()

            # Check if any rows were deleted
            if cursor.rowcount > 0:
                return Result(status=STATUS_OK, row_id=self.ROW_ID_NOT_FOUND, reason="Deleted DHCP subnet option successfully.")
            else:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason="Failed to delete DHCP subnet option.")

        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to delete DHCP subnet option. Error: {str(e)}")

    def select_dhcp_pool_subnet_via_dhcp_pool_name(self, dhcp_pool_name: DhcpPoolName) -> Result:
        """
        Retrieve the DHCP pool subnet information associated with a DHCP pool name from the database.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool.

        Returns:
            Result: A Result object containing the subnet information if found, or an error message if not found.
        """
        try:
            cursor = self.connection.cursor()

            query = "SELECT ID, InetSubnet FROM DHCPSubnet " \
                    "WHERE DHCPServer_FK = (SELECT ID FROM DHCPServer WHERE DhcpPoolname = ?)"

            cursor.execute(query, (dhcp_pool_name,))
            sql_result = cursor.fetchone()

            if sql_result:
                subnet_id, inet_subnet = sql_result

                return Result(status=STATUS_OK, row_id=subnet_id, result={'InetSubnet': inet_subnet})
            else:
                return Result(status=STATUS_NOK, reason="Subnet information not found for DHCP pool name: " + dhcp_pool_name)

        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to retrieve DHCP subnet information. Error: {str(e)}")

    def dhcp_pool_dhcp_version(self, dhcp_pool_name: DhcpPoolName) -> Result:
        """
        Retrieve the DHCP version for a specified DHCP pool.

        Parameters:
            dhcp_pool_name (str): The name of the DHCP pool for which to retrieve the version.

        Returns:
            Result: A Result object representing the outcome of the operation.
            - If successful, status is STATUS_OK, and 'DHCPVersion' in the result dictionary
                contains the DHCP version ('DHCPv6', 'DHCPv4', or 'UNKNOWN').
            - If unsuccessful, status is STATUS_NOK, and the 'reason' field provides an error message.

        """
        try:
            query = f"""
                SELECT DHCPServer.DhcpPoolname,
                    CASE
                        WHEN DHCPv6ServerOption.ID IS NOT NULL THEN '{DHCPVersion.DHCP_V6.value}'
                        WHEN DHCPv4ServerOption.ID IS NOT NULL THEN '{DHCPVersion.DHCP_V4.value}'
                        ELSE 'Unknown'
                    END AS DHCPVersion
                FROM DHCPServer
                LEFT JOIN DHCPSubnet ON DHCPServer.ID = DHCPSubnet.DHCPServer_FK
                LEFT JOIN DHCPVersionServerOptions ON DHCPSubnet.ID = DHCPVersionServerOptions.DHCPSubnet_FK
                LEFT JOIN DHCPv6ServerOption ON DHCPVersionServerOptions.ID = DHCPv6ServerOption.DHCPVersionServerOptions_FK
                LEFT JOIN DHCPv4ServerOption ON DHCPVersionServerOptions.ID = DHCPv4ServerOption.DHCPVersionServerOptions_FK
                WHERE DHCPServer.DhcpPoolname = ?;
            """

            cursor = self.connection.cursor()
            cursor.execute(query, (dhcp_pool_name,))

            result = cursor.fetchone()

            if result is not None:
                dhcp_version = result[1]
                result_data = {'DHCPVersion': dhcp_version}
                return Result(status=STATUS_OK, row_id=None, result=result_data)
            else:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"DHCP version for pool '{dhcp_pool_name}' not found.")

        except sqlite3.Error as e:
            error_message = f"Failed to retrieve DHCP version. Error: {str(e)}"
            self.log.error(error_message)
            return Result(status=STATUS_NOK, row_id=None, reason=error_message, result={'DHCPVersion': DHCPVersion.UNKNOWN})

    '''
                        DHCP-SERVER CONFIGURATION BUILDING
    '''

    def select_global_options(self) -> list[Result]:
        '''TODO'''
        return []

    def select_dhcp_pool_interfaces(self, dhcp_pool_name: DhcpPoolName) -> list[Result]:
        """
        Retrieve the interfaces associated with a DHCP pool name from the database.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool.

        Returns:
            list[Result]: A list of Result objects, each representing an interface, or an empty list if none are found.
        """
        try:
            cursor = self.connection.cursor()

            query = "SELECT ID, InterfaceName FROM Interfaces WHERE ID = ("\
                "SELECT Interfaces_FK FROM DHCPServer WHERE DhcpPoolname = ?)"
            self.log.debug(f"{query}")
            cursor.execute(query, (dhcp_pool_name,))
            sql_results = cursor.fetchall()

            results = []

            for id, interface_name in sql_results:
                results.append(Result(status=STATUS_OK, row_id=id, result={
                               'interface_name': interface_name}))

            return results

        except sqlite3.Error as e:
            return [Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to retrieve DHCP pool interfaces. Error: {str(e)}")]

    def select_dhcp_pool_inet_range(self, dhcp_pool_name: DhcpPoolName) -> list[Result]:
        """
        Retrieve the IP address range associated with a DHCP pool name from the database.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool.

        Returns:
            list[Result]: A list of Result objects, each representing an IP address range, or an empty list if none are found.
        """
        try:
            cursor = self.connection.cursor()

            query = "SELECT ID, InetAddressStart, InetAddressEnd , InetSubnet FROM DHCPSubnetPools " \
                    "WHERE DHCPSubnet_FK = (SELECT ID FROM DHCPSubnet WHERE DHCPServer_FK = (SELECT ID FROM DHCPServer WHERE DhcpPoolname = ?))"

            cursor.execute(query, (dhcp_pool_name,))
            sql_results = cursor.fetchall()

            results = []

            for id, inet_start, inet_end, inet_subnet in sql_results:
                results.append(Result(status=STATUS_OK, row_id=id,
                                      result={'inet_start': inet_start, 'inet_end': inet_end, 'inet_subnet': inet_subnet}))

            return results

        except sqlite3.Error as e:
            return [Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to retrieve IP address ranges. Error: {str(e)}")]

    def select_dhcp_pool_reservation(self, dhcp_pool_name: DhcpPoolName) -> list[Result]:
        """
        Retrieve DHCP reservations associated with a DHCP pool name from the database.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool.

        Returns:
            list[Result]: A list of Result objects, each representing a DHCP reservation, or an empty list if none are found.
        """
        try:
            cursor = self.connection.cursor()

            query = "SELECT ID, MacAddress, InetAddress FROM DHCPSubnetReservations " \
                    "WHERE DHCPSubnet_FK = (SELECT ID FROM DHCPSubnet WHERE DHCPServer_FK = (SELECT ID FROM DHCPServer WHERE DhcpPoolname = ?))"

            cursor.execute(query, (dhcp_pool_name,))
            sql_results = cursor.fetchall()

            results = []

            for id, mac, inet_address in sql_results:
                results.append(Result(status=STATUS_OK, row_id=id, result={
                               'mac_address': mac, 'inet_address': inet_address}))

            return results

        except sqlite3.Error as e:
            return [Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to retrieve DHCP reservations. Error: {str(e)}")]

    def select_dhcp_pool_options(self, dhcp_pool_name: DhcpPoolName) -> list[Result]:
        """
        Retrieve DHCP options associated with a DHCP pool name from the database.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool.

        Returns:
            list[Result]: A list of Result objects, each representing a DHCP option, or an empty list if none are found.

        """
        try:
            self.log.debug(f"get_dhcp_pool_options({dhcp_pool_name})")

            cursor = self.connection.cursor()

            query = """
                SELECT DISTINCT
                    DHCPO.ID,
                    DHCPO.DhcpOption,
                    DHCPO.DhcpValue
                FROM
                    DHCPOptions DHCPO
                WHERE
                    DHCPO.DHCPSubnetPools_FK IN (
                        SELECT DISTINCT DSP.DHCPSubnet_FK
                        FROM DHCPSubnetPools DSP
                        WHERE DSP.DHCPSubnet_FK IN (
                            SELECT DISTINCT DSN.ID
                            FROM DHCPSubnet DSN
                            WHERE DSN.DHCPServer_FK IN (
                                SELECT DISTINCT DSRV.ID
                                FROM DHCPServer DSRV
                                WHERE DSRV.DhcpPoolname = ?
                            )
                        )
                    );
            """

            cursor.execute(query, (dhcp_pool_name,))
            sql_results = cursor.fetchall()

            results = []

            for id, option, value in sql_results:
                self.log.debug(f"OPTION: {option} -> VALUE: {value}")
                results.append(Result(status=STATUS_OK, row_id=id, result={
                               'option': option, 'value': value}))

            return results

        except sqlite3.Error as e:
            return [Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to retrieve DHCP options. Error: {str(e)}")]

    '''
                        DHCP-CLIENT DATABASE
    '''

    def insert_interface_dhcp_client(self, interface_name: InterfaceName, dhcp_version: str) -> Result:
        """
        Insert a new DHCP client entry into the database.

        Args:
            interface_name (str): The name of the network interface.
            dhcp_version (str): The DHCP version (DHCP_V4 or DHCP_V6).

        Returns:
            Result: A Result object with the status of the insertion and the row ID.
                    status = STATUS_OK for success, STATUS_NOK for failure.
        """
        result = self.interface_exists(interface_name)

        if not result.status:
            err = f"Unable to insert DHCP client to interface: {interface_name} does not exist"
            self.log.error(err)
            return Result(STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=err)

        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO DHCPClient (Interfaces_FK, DHCPVersion) VALUES (?, ?)", (result.row_id, dhcp_version))
            self.connection.commit()
            row_id = cursor.lastrowid
            return Result(STATUS_OK, row_id=row_id)

        except Exception as e:
            self.log.error(f"Failed to add DHCP client: {e}")
            return Result(STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=str(e))

    def update_interface_dhcp_client(self, interface_name: InterfaceName, dhcp_version: str) -> Result:
        """
        Update the DHCP version for an existing DHCP client entry in the database.
        If the update fails because the entry does not exist, insert a new entry.

        Args:
            interface_name (str): The name of the network interface.
            dhcp_version (str): The updated DHCP version (DHCP_V4 or DHCP_V6).

        Returns:
            Result: A Result object with the status of the update and the row ID.
                    status = STATUS_OK for success, STATUS_NOK for failure.
        """
        result = self.interface_exists(interface_name)

        if not result.status:
            err = f"Unable to update DHCP client because interface '{interface_name}' does not exist in the DB"
            self.log.error(err)
            return Result(STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=err)

        interface_row_id = result.row_id

        try:
            cursor = self.connection.cursor()
            # Begin a transaction
            self.connection.execute('BEGIN')

            # Try to update the existing entry
            cursor.execute(
                "UPDATE DHCPClient SET DHCPVersion = ? WHERE Interfaces_FK = ?",
                (dhcp_version, interface_row_id)
            )

            if cursor.rowcount == 0:
                # If no rows were updated, the entry does not exist, insert a new entry
                cursor.execute(
                    "INSERT INTO DHCPClient (Interfaces_FK, DHCPVersion) VALUES (?, ?)",
                    (interface_row_id, dhcp_version)
                )

            self.connection.commit()
            row_id = cursor.lastrowid
            return Result(STATUS_OK, row_id=row_id)

        except Exception as e:
            self.connection.rollback()
            err = f"Failed to update or insert DHCP client: {e}"
            self.log.error(err)
            return Result(STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=str(e))

    def remove_interface_dhcp_client(self, interface_name: InterfaceName, dhcp_version: str) -> Result:
        """
        Remove a DHCP client entry from the database.

        Args:
            interface_name (str): The name of the network interface.
            dhcp_version (str): The DHCP version to be removed (DHCP_V4 or DHCP_V6).

        Returns:
            Result: A Result object with the status of the removal and the row ID.
                    status = STATUS_OK for success, STATUS_NOK for failure.
        """
        result = self.interface_exists(interface_name)

        if result.status:
            err = f"Unable to remove DHCP client from interface: {interface_name} does not exist"
            self.log.error(err)
            return Result(STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=err)

        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "DELETE FROM DHCPClient WHERE Interfaces_FK = ? AND DHCPVersion = ?", (result.row_id, dhcp_version))
            self.connection.commit()
            row_id = cursor.lastrowid
            return Result(STATUS_OK, row_id=row_id)

        except Exception as e:
            self.log.error(f"Failed to remove DHCP client: {e}")
            return Result(STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=str(e))

    '''
                        INTERFACE DATABASE
    '''

    def select_interface_details(self, interface_name: InterfaceName | None = None) -> list[Result]:
        """
        Select details for the specified interface or all interfaces.

        Args:
            interface_name (str, optional): The name of the interface to retrieve details for.
                If None, details for all interfaces will be retrieved.

        Returns:
            list[Result]: A list of Result objects containing the interface details.
        """
        try:
            cursor = self.connection.cursor()

            query = '''
                SELECT
                    Interfaces.ID AS InterfaceID,
                    Interfaces.InterfaceName,
                    Interfaces.InterfaceType,
                    Interfaces.ShutdownStatus,
                    Interfaces.Description,
                    InterfaceSubOptions.MacAddress,
                    InterfaceSubOptions.Duplex,
                    InterfaceSubOptions.Speed,
                    InterfaceSubOptions.ProxyArp,
                    InterfaceSubOptions.DropGratuitousArp,
                    RenameInterface.BusInfo,
                    RenameInterface.InitialInterface,
                    RenameInterface.AliasInterface
                FROM
                    Interfaces
                JOIN
                    InterfaceSubOptions ON Interfaces.ID = InterfaceSubOptions.Interfaces_FK
                LEFT JOIN
                    RenameInterface ON Interfaces.InterfaceName = RenameInterface.AliasInterface
            '''

            parameters = ""

            if interface_name is not None:
                query += ' WHERE Interfaces.InterfaceName = ?;'
                parameters = (interface_name,)  # Use a tuple for parameters

            cursor.execute(query, parameters)

            result_list = []
            rows = cursor.fetchall()

            for row in rows:
                result_list.append(Result(
                    status=STATUS_OK,
                    row_id=row[0],
                    result={
                        'InterfaceID': row[0],
                        'InterfaceName': row[1],
                        'InterfaceType': row[2],
                        'ShutdownStatus': row[3],
                        'Description': row[4],
                        'MacAddress': row[5],
                        'Duplex': row[6],
                        'Speed': row[7],
                        'ProxyArp': row[8],
                        'DropGratuitousArp': row[9],
                        'BusInfo': row[10],
                        'InitialInterface': row[11],
                        'AliasInterface': row[12],
                    }
                ))

            return result_list

        except sqlite3.Error as e:
            error_message = f"Error selecting interface details: {e}"
            self.log.error(error_message)
            return [Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)]

    def select_interface_type(self, interface_name: InterfaceName) -> InterfaceType:
        """
        Retrieve the type of an interface by its name.

        Args:
            interface_name (str): The name of the interface.

        Returns:
            InterfaceType: The type of the interface if found, or None if not found.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT InterfaceType FROM Interfaces WHERE InterfaceName = ?", (interface_name,))
            row = cursor.fetchone()
            if row:
                interface_type = InterfaceType(row[0])
                return interface_type
        except sqlite3.Error as e:
            self.log.error("Error retrieving 'Interfaces' type: %s", e)
        return None

    def select_interface_id(self, if_name: InterfaceName) -> int:
        """
        Retrieve the ID of an interface by its name.

        Args:
            if_name (str): The name of the interface.

        Returns:
            int: The ID of the interface if found, or None if not found.

        Raises:
            sqlite3.Error: If there's an error during the database operation.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT ID FROM Interfaces WHERE InterfaceName = ?", (if_name,))
            row = cursor.fetchone()
            if row:
                return row[0]
        except sqlite3.Error as e:
            self.log.error("Error retrieving 'Interfaces' ID: %s", e)
        return None

    def interface_exists(self, if_name: InterfaceName) -> Result:
        """
        Check if an interface with the given name exists in the 'Interfaces' table.

        Args:
            if_name (str): The name of the interface to check.

        Returns:
            Result: A Result object with the status and row ID of the existing interface.
            status: True = exists, otherwise False
            row_id: row-id of interface when status=true
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT ID FROM Interfaces WHERE InterfaceName = ?", (if_name,))
            self.connection.commit()
            existing_row = cursor.fetchone()

            if existing_row:
                self.log.debug(f'Interface {if_name} exists on row-id: {existing_row[0]}')
                return Result(status=True, row_id=existing_row[0])
            else:
                return Result(status=False, row_id=0)

        except sqlite3.Error as e:
            self.log.error("Error checking if interface exists: %s", e)
            return Result(status=False, row_id=0)

    def insert_interface(self, if_name, interface_type: InterfaceType, shutdown_status=True) -> Result:
        """
        Insert data into the 'Interfaces' table.

        Args:
            if_name (str): The name of the interface.
            interface_type (InterfaceType): The type of the interface.
            shutdown_status (bool, optional): True if the interface is shutdown, False otherwise.

        Returns:
            Result: A Result object with the status of the insertion and the row ID.
                    status = STATUS_OK success, STATUS_NOK otherwise
        """

        existing_result = self.interface_exists(if_name)

        if existing_result.status:
            return Result(status=STATUS_NOK,
                          row_id=existing_result.row_id,
                          reason=f"Interface: {if_name} already exists")

        try:
            self.log.debug(
                f"insert_interface() -> Interface: {if_name} -> Interface-Type: {interface_type.value} -> shutdown: {shutdown_status}")

            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO Interfaces (InterfaceName, InterfaceType, ShutdownStatus) VALUES (?, ?, ?)",
                (if_name, interface_type.value, shutdown_status)
            )

            self.connection.commit()

            self.log.debug(
                "Data inserted into the 'Interfaces' table successfully.")

            self.delete_global_nat_pool_name

            self._insert_default_row_in_interface_sub_option(if_name)

            return Result(status=STATUS_OK, row_id=cursor.lastrowid)

        except sqlite3.Error as e:
            self.log.error("Error inserting data into 'Interfaces': %s", e)
            return Result(status=STATUS_NOK, row_id=0, reason=f"{e}")

    def delete_interface(self, interface_name: InterfaceName) -> Result:
        """
        Delete an interface from the 'Interfaces' table.

        Args:
            if_name (str): The name of the interface to delete.

        Returns:
            Result: A Result object with the status of the deletion.
        """
        try:
            existing_result = self.interface_exists(interface_name)

            if existing_result.status:
                cursor = self.connection.cursor()
                cursor.execute(
                    "DELETE FROM Interfaces WHERE InterfaceName = ?", (interface_name,))
                self.connection.commit()
                self.log.debug(
                    f"Deleted interface '{interface_name}' from the 'Interfaces' table.")
                return Result(status=STATUS_OK, row_id=0, reason=f"Interface '{interface_name}' deleted successfully.")
            else:
                self.log.debug(f"Interface '{interface_name}' does not exist.")
                return Result(status=STATUS_NOK, row_id=0, reason=f"Interface '{interface_name}' does not exist.")
        except sqlite3.Error as e:
            self.log.error("Error deleting interface: %s", e)
            return Result(status=STATUS_NOK, row_id=0, reason=f"{e}")

    def update_interface_shutdown(self, interface_name: InterfaceName, shutdown_status: bool) -> Result:
        """
        Update the shutdown status of an interface in the 'Interfaces' table.

        Args:
            if_name (str): The name of the interface to update.
            shutdown_status (bool): True =  shutdown interface
                                    False = no shutdown interface     

        Returns:
            Result: A Result object with the status of the update.
        """
        existing_result = self.interface_exists(interface_name)

        if not existing_result.status:
            return Result(status=STATUS_NOK, row_id=0, reason=f"Interface: {interface_name} does not exist")

        try:
            cursor = self.connection.cursor()

            cursor.execute(
                "UPDATE Interfaces SET ShutdownStatus = ? WHERE InterfaceName = ?",
                (shutdown_status, interface_name)
            )

            self.connection.commit()

            self.log.debug(
                f"Shutdown status ({shutdown_status}) updated for interface: {interface_name}")

            return Result(status=STATUS_OK, row_id=existing_result.row_id)

        except sqlite3.Error as e:
            self.log.error(
                f"Error updating shutdown status for interface {interface_name}: {e}")
            return Result(status=STATUS_NOK, row_id=existing_result.row_id, reason=f"{e}")

    def update_interface_duplex(self, interface_name: InterfaceName, duplex: str) -> Result:
        """
        Update the duplex setting of an interface in the 'InterfaceSubOptions' table.

        Args:
            if_name (str): The name of the interface to update.
            duplex (str): The new duplex setting.

        Returns:
            Result: A Result object with the status of the update.
                    - status:   STATUS_OK successful, STATUS_NOK otherwise
                    - row_id:   STATUS_OK row_id > 0, STATUS_NOK row_id = 0
        """
        existing_result = self.interface_exists(interface_name)

        if not existing_result.status:
            return Result(status=STATUS_NOK, row_id=0, reason=f"Interface: {interface_name} does not exist")

        interface_id = existing_result.row_id

        try:

            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT ID FROM InterfaceSubOptions WHERE Interfaces_FK = ?", (interface_id,))
            sub_options_row = cursor.fetchone()

            if sub_options_row:
                # If an entry exists, update the duplex setting
                cursor.execute(
                    "UPDATE InterfaceSubOptions SET Duplex = ? WHERE Interfaces_FK = ?",
                    (duplex, interface_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO InterfaceSubOptions (Interfaces_FK, Duplex) VALUES (?, ?)",
                    (interface_id, duplex)
                )

            self.connection.commit()
            self.log.debug(
                f"Duplex setting updated for interface: {interface_name}")
            return Result(status=STATUS_OK, row_id=interface_id)

        except sqlite3.Error as e:
            self.log.error(
                f"Error updating duplex setting for interface {interface_name}: {e}")
            return Result(status=STATUS_NOK, row_id=interface_id, reason=str(e))

    def update_interface_mac_address(self, interface_name: InterfaceName, mac_address: MacAddressText) -> Result:
        """
        Update the MAC address setting of an interface in the 'InterfaceSubOptions' table.

        Args:
            interface_name (str): The name of the interface to update.
            mac_address (str): MAC address in the format xx:xx:xx:xx:xx:xx.

        Returns:
            Result: A Result object with the status of the update.
        """
        existing_result = self.interface_exists(interface_name)

        if not existing_result.status:
            return Result(status=STATUS_NOK, row_id=0, reason=f"Interface: {interface_name} does not exist")

        try:
            interface_id = existing_result.row_id

            cursor = self.connection.cursor()  # Create a cursor object
            cursor.execute(
                "SELECT ID FROM InterfaceSubOptions WHERE Interfaces_FK = ?", (interface_id,))
            sub_options_row = cursor.fetchone()

            if sub_options_row:
                cursor.execute(
                    "UPDATE InterfaceSubOptions SET MacAddress = ? WHERE Interfaces_FK = ?",
                    (mac_address, interface_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO InterfaceSubOptions (Interfaces_FK, MacAddress) VALUES (?, ?)",
                    (interface_id, mac_address)
                )

            self.connection.commit()
            self.log.debug(
                f"MAC address setting updated for interface: {interface_name}")
            return Result(status=STATUS_OK, row_id=interface_id)

        except sqlite3.Error as e:
            self.log.error(
                f"Error updating MAC address setting for interface {interface_name}: {e}")
            return Result(status=STATUS_NOK, row_id=interface_id, reason=str(e))

    def update_interface_speed(self, interface_name: InterfaceName, speed: str) -> Result:
        """
        Update the speed setting of an interface in the 'InterfaceSubOptions' table.

        Args:
            interface_name (str): The name of the interface to update.
            speed (str): Speed setting, one of ['10', '100', '1000', '10000', 'auto'].

        Returns:
            Result: A Result object with the status of the update.
        """
        existing_result = self.interface_exists(interface_name)

        if not existing_result.status:
            self.log.error(f"Interface: {interface_name} does not exists.")
            return Result(status=STATUS_NOK, row_id=0, reason=f"Interface: {interface_name} does not exist")

        try:
            interface_id = existing_result.row_id

            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT ID FROM InterfaceSubOptions WHERE Interfaces_FK = ?", (interface_id,))

            sub_options_row = cursor.fetchone()

            if sub_options_row:
                cursor.execute(
                    "UPDATE InterfaceSubOptions SET Speed = ? WHERE Interfaces_FK = ?",
                    (speed, interface_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO InterfaceSubOptions (Interfaces_FK, Speed) VALUES (?, ?)",
                    (interface_id, speed)
                )

            self.connection.commit()
            self.log.debug(
                f"Speed {speed} setting updated for interface: {interface_name}")
            return Result(status=STATUS_OK, row_id=interface_id)

        except sqlite3.Error as e:
            self.log.error(
                f"Error updating speed: {speed} setting for interface {interface_name}: {e}")
            return Result(status=STATUS_NOK, row_id=interface_id, reason=f"{e}")

    def update_interface_description(self, interface_name: InterfaceName, description: str) -> Result:
        """
        Update the description of a network interface in the database.

        This method allows you to update the user-defined description of a specific network interface in the database.

        Args:
            interface_name (str): The name of the network interface.
            description (str): The new description to assign to the network interface.

        Returns:
            Result: An instance of the Result class indicating the status of the update.
                - status (bool): True if the description is successfully updated, False otherwise.
                - row_id (int): The row ID of the updated interface in the database.
                - reason (str, optional): A descriptive message indicating the reason for failure, if any.
        """

        existing_result = self.interface_exists(interface_name)

        if not existing_result.status:
            return Result(status=STATUS_NOK, row_id=0, reason=f"Interface: {interface_name} does not exist")

        self.log.debug(
            f"Description: ({description}) UPDATING for interface: {interface_name}")

        try:
            cursor = self.connection.cursor()

            cursor.execute(
                "UPDATE Interfaces SET Description = ? WHERE InterfaceName = ?",
                (description, interface_name)
            )

            self.connection.commit()

            self.log.debug(
                f"Description: ({description}) UPDATED for interface: {interface_name}")

            return Result(status=STATUS_OK, row_id=existing_result.row_id)

        except sqlite3.Error as e:
            self.log.error(
                f"Error updating description for interface {interface_name}: {e}")
            return Result(status=STATUS_NOK, row_id=existing_result.row_id, reason=f"{e}")

    def update_interface_name(self, existing_interface_name: InterfaceName, new_interface_name: InterfaceName) -> Result:
        """
        Update the name of a network interface in the database.

        This method allows you to update the name of a specific network interface in the database.

        Args:
            existing_interface_name (str): The current name of the network interface.
            new_interface_name (str): The new name to assign to the network interface.

        Returns:
            Result: An instance of the Result class indicating the status of the update.
                - status (bool): True if the name is successfully updated, False otherwise.
                - row_id (int): The row ID of the updated interface in the database.
                - reason (str, optional): A descriptive message indicating the reason for failure, if any.
        """
        existing_result = self.interface_exists(existing_interface_name)

        if not existing_result.status:
            return Result(status=STATUS_NOK, row_id=0, reason=f"Interface: {existing_interface_name} does not exist")

        try:
            cursor = self.connection.cursor()

            cursor.execute(
                "UPDATE Interfaces SET InterfaceName = ? WHERE InterfaceName = ?",
                (new_interface_name, existing_interface_name)
            )

            self.connection.commit()

            self.log.debug(
                f"Interface name updated: {existing_interface_name} -> {new_interface_name}")

            return Result(status=STATUS_OK, row_id=existing_result.row_id, result={'InterfaceName': new_interface_name})

        except sqlite3.Error as e:
            self.log.error(
                f"Error updating interface name for {existing_interface_name}: {e}")
            return Result(status=STATUS_NOK, row_id=existing_result.row_id, reason=f"{e}")

    '''
                    INTERFACE-IP-ADDRESS DATABASE
    '''

    def insert_interface_inet_address(self, interface_name: InterfaceName, ip_address: InetAddressText, is_secondary: bool) -> Result:
        """
        Insert an IP address entry for an interface into the 'InterfaceIpAddress' table.

        Args:
            interface_name (str): The name of the interface to associate the IP address with.
            ip_address (str): The IP address in the format IPv4 or IPv6 Address/Mask-Prefix.
            is_secondary (bool): True if the IP address is secondary, False otherwise.

        Returns:
            Result: A Result object with the status of the insertion.
        """
        existing_result = self.interface_exists(interface_name)

        if not existing_result.status:
            # Interface does not exist
            return Result(status=STATUS_NOK, row_id=0, reason=f"Interface: {interface_name} does not exist")

        try:
            interface_id = existing_result.row_id

            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO InterfaceIpAddress (Interfaces_FK, IpAddress, SecondaryIp) VALUES (?, ?, ?)",
                (interface_id, ip_address, is_secondary)
            )

            self.connection.commit()
            self.log.debug(
                f"IP address {ip_address} inserted for interface: {interface_name}")
            return Result(status=STATUS_OK, row_id=interface_id)

        except sqlite3.Error as e:
            self.log.error(
                f"Error inserting IP address for interface {interface_name}: {e}")
            return Result(status=STATUS_NOK, row_id=interface_id, reason=f"{e}")

    def delete_interface_inet_address(self, interface_name: InterfaceName, ip_address: InetAddressText) -> Result:
        """
        Delete the entire row associated with an IP address for an interface from the 'InterfaceIpAddress' table.

        Args:
            interface_name (str): The name of the interface.
            ip_address (str): The IP address to delete.

        Returns:
            Result: A Result object with the status of the deletion.
        """
        existing_result = self.interface_exists(interface_name)

        if not existing_result.status:
            # Interface does not exist
            return Result(status=STATUS_NOK, row_id=0, reason=f"Interface: {interface_name} does not exist")

        try:
            interface_id = existing_result.row_id

            cursor = self.connection.cursor()
            cursor.execute(
                "DELETE FROM InterfaceIpAddress WHERE Interfaces_FK = ? AND IpAddress = ?",
                (interface_id, ip_address)
            )
            self.connection.commit()
            self.log.debug(
                f"IP address {ip_address} row deleted for interface: {interface_name}")
            return Result(status=STATUS_OK, row_id=interface_id)

        except sqlite3.Error as e:
            self.log.error(
                f"Error deleting IP address for interface {interface_name}: {e}")
            return Result(status=STATUS_NOK, row_id=interface_id, reason=f"{e}")

    def _sub_option_row_exists(self, interface_fk: int) -> Result:
        """
        Check if a row with the given Interfaces_FK exists in the 'InterfaceSubOptions' table.

        Args:
            interface_fk (int): The foreign key (Interfaces_FK) to check.

        Returns:
            Result: A Result object with the 'row_id' field indicating the found 'ID' or 0 if not found.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT ID FROM InterfaceSubOptions WHERE Interfaces_FK = ?", (interface_fk,))
            row = cursor.fetchone()
            return Result(status=True, row_id=row[0] if row else 0)
        except sqlite3.Error:
            return Result(status=True, row_id=0)

    '''
                    INTERFACE-SUB-OPTIONS DATABASE
    '''

    def interface_and_sub_option_exist(self, interface_name: InterfaceName) -> Result:
        """
        Check if an interface with the given name exists in the 'Interfaces' table and if a corresponding row exists in
        the 'InterfaceSubOptions' table.

        Args:
            interface_name (str): The name of the interface to check.

        Returns:
            Result: A Result object indicating the outcome of the checks.
                    'status' : True if both exist, False otherwise
                    'row_id' : If exist, row_id > 0, 0 if not found
                    'result' : Result of SQL query
        """
        interface_exists_result = self.interface_exists(interface_name)

        if not interface_exists_result.status:
            return Result(status=False, reason=f"Interface: {interface_name} doesn't exist")

        sub_option_row_result = self._sub_option_row_exists(
            interface_exists_result.row_id)

        if sub_option_row_result.row_id:
            return Result(status=True, row_id=sub_option_row_result.row_id)
        else:
            return Result(status=False, reason="Interface exists, but no corresponding row in InterfaceSubOptions")

    def update_interface_proxy_arp(self, interface_name: InterfaceName, status: bool) -> Result:
        """
        Update the Proxy ARP setting of an interface in the 'InterfaceSubOptions' table.

        Args:
            interface_name (str): The name of the interface to update.
            status (bool): True to enable Proxy ARP, False to disable it.

        Returns:
            Result: A Result object with the status of the update.
                    'status' : STATUS_OK if successful, STATUS_NOK otherwise
                    'row_id' : If exists, row_id > 0
                    'result' : Result of SQL query
        """

        if_exists = self.interface_exists(interface_name)

        if not if_exists.status:
            return Result(STATUS_NOK, self.ROW_ID_NOT_FOUND, reason=if_exists.reason)

        if_sub_opt = self.interface_and_sub_option_exist(interface_name)

        if not if_sub_opt.status:
            insert_if_sub_option = self._insert_default_row_in_interface_sub_option(
                interface_name)
            if not insert_if_sub_option.status:
                return Result(STATUS_NOK, self.ROW_ID_NOT_FOUND, reason=insert_if_sub_option.reason)

        try:

            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE InterfaceSubOptions SET ProxyArp = ? WHERE Interfaces_FK = ?",
                (status, if_exists.row_id)
            )

            self.connection.commit()
            self.log.debug(
                f"update_interface_proxy_arp() -> Proxy ARP setting updated for interface: {interface_name}")
            return Result(STATUS_OK, row_id=if_sub_opt.row_id)

        except sqlite3.Error as e:
            self.log.error(
                f"update_interface_proxy_arp() -> Error updating Proxy ARP setting for interface {interface_name}: {e}")
            return Result(STATUS_NOK, row_id=if_sub_opt.row_id, reason=str(e))

    def update_interface_drop_gratuitous_arp(self, interface_name: InterfaceName, status: bool) -> Result:
        """
        Update the 'Drop Gratuitous ARP' setting of an interface in the 'InterfaceSubOptions' table.

        Args:
            interface_name (str): The name of the interface to update.
            status (bool): True to enable 'Drop Gratuitous ARP,' False to disable it.

        Returns:
            Result: A Result object with the status of the update.
                    'status' : STATUS_OK if successful, STATUS_NOK otherwise
                    'row_id' : If exists, row_id > 0
                    'result' : Result of SQL query
        """

        # Check if the interface exists
        if_exists = self.interface_exists(interface_name)

        if not if_exists.status:
            return Result(STATUS_NOK, self.ROW_ID_NOT_FOUND, reason=if_exists.reason)

        # Check if the sub-option row exists
        if_sub_opt = self.interface_and_sub_option_exist(interface_name)

        if not if_sub_opt.status:
            # If the sub-option row doesn't exist, insert a default row
            insert_if_sub_option = self._insert_default_row_in_interface_sub_option(
                interface_name)

        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE InterfaceSubOptions SET DropGratuitousArp = ? WHERE Interfaces_FK = ?",
                (status, if_exists.row_id)
            )

            self.connection.commit()
            self.log.debug(
                f"update_interface_drop_gratuitous_arp() -> 'Drop Gratuitous ARP' setting updated for interface: {interface_name}")
            return Result(STATUS_OK, row_id=if_sub_opt.row_id)

        except sqlite3.Error as e:
            self.log.error(
                f"update_interface_drop_gratuitous_arp() -> Error updating 'Drop Gratuitous ARP' setting for interface {interface_name}: {e}")
            return Result(STATUS_NOK, row_id=if_sub_opt.row_id, reason=str(e))

    def update_interface_static_arp(self, interface_name: InterfaceName, ip_address: InetAddressText, mac_address: MacAddressText, encapsulation: str) -> Result:
        """
        Create a default entry in the 'InterfaceStaticArp' table if it does not already exist, or update it if it exists.

        Args:
            interface_name (str): The name of the interface to associate the static ARP record with.
            ip_address (str): The IP address in IPv4 or IPv6 format.
            mac_address (str): The MAC address in the format: xx:xx:xx:xx:xx:xx.
            encapsulation (str): The encapsulation type, e.g., 'arpa' or 'TBD'.

        Returns:
            Result: A Result object with the status of the operation.
        """
        self.log.debug(
            f"update_interface_static_arp() If: {interface_name} , IP: {ip_address} , mac: {mac_address} , encap: {encapsulation}")
        try:
            # Check if the interface exists and get its ID
            interface_exists_result = self.interface_exists(interface_name)
            if not interface_exists_result.status:
                return Result(STATUS_NOK, row_id=0, reason=f"Interface: {interface_name} does not exist")

            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT ID FROM InterfaceStaticArp WHERE Interfaces_FK = ? AND IpAddress = ?",
                (interface_exists_result.row_id, ip_address)
            )
            existing_entry = cursor.fetchone()

            if existing_entry:
                self.log.debug(
                    f"update_interface_static_arp() -> Entry Exist, Updating IP: {ip_address} -> Mac: {mac_address}")
                cursor.execute(
                    "UPDATE InterfaceStaticArp SET MacAddress = ?, Encapsulation = ? WHERE ID = ?",
                    (mac_address, encapsulation, existing_entry[0])
                )
                self.connection.commit()
                self.log.debug(
                    f"Static ARP entry updated for interface: {interface_name}")
            else:
                self.log.debug(
                    f"update_interface_static_arp() -> Entry NOT Found, inserting IP: {ip_address} -> Mac: {mac_address}")
                cursor.execute(
                    "INSERT INTO InterfaceStaticArp (Interfaces_FK, IpAddress, MacAddress, Encapsulation) VALUES (?, ?, ?, ?)",
                    (interface_exists_result.row_id,
                     ip_address, mac_address, encapsulation)
                )
                self.connection.commit()
                self.log.debug(
                    f"Static ARP entry added for interface: {interface_name}")

            return Result(STATUS_OK, row_id=existing_entry[0] if existing_entry else cursor.lastrowid)

        except sqlite3.Error as e:
            self.log.error(
                f"Error creating or updating static ARP entry for interface {interface_name}: {e}")
            return Result(STATUS_NOK, row_id=0, reason=str(e))

    def delete_interface_static_arp(self, interface_name: InterfaceName, ip_address: InetAddressText) -> Result:
        """
        Delete a static ARP record from the 'InterfaceStaticArp' table.

        Args:
            interface_name (str): The name of the interface to associate with the static ARP record.
            ip_address (str): The IP address to delete.

        Returns:
            Result: A Result object with the status of the deletion.
        """
        self.log.debug(
            f"delete_interface_static_arp() If: {interface_name} , IP: {ip_address}")

        existing_result = self.interface_exists(interface_name)

        if not existing_result.status:
            return Result(STATUS_NOK, row_id=0, reason=f"Interface: {interface_name} does not exist")

        try:
            interface_id = existing_result.row_id

            cursor = self.connection.cursor()

            self.log.debug(
                f"delete_interface_static_arp() Deleting Row -> Interface-FK: {interface_name} , IP: {ip_address}")

            cursor.execute(
                "DELETE FROM InterfaceStaticArp WHERE Interfaces_FK = ? AND IpAddress = ?",
                (interface_id, ip_address)
            )

            self.connection.commit()

            self.log.debug(
                f"Static ARP record deleted for interface: {interface_name}")

            return Result(STATUS_OK, row_id=interface_id)

        except sqlite3.Error as e:
            self.log.error(
                f"Error deleting static ARP record for interface {interface_name}: {e}")
            return Result(STATUS_NOK, row_id=interface_id, reason=str(e))

    def insert_interface_bridge_group(self, interface_name: InterfaceName, bridge_name: BridgeName) -> Result:
        """
        Insert an interface into a bridge group in the 'BridgeGroups' table.

        Args:
            interface_name (str): The name of the interface.
            bridge_name (str): The name of the bridge group.

        Returns:
            Result: A Result object with the status of the insertion.
        """
        interface_result = self.interface_exists(interface_name)

        if not interface_result.status:
            self.log.debug(f''
                f"insert_interface_bridge_group() -> interface: {interface_name} does not exist, Exiting")
            return Result(STATUS_NOK, reason=f"Interface: {interface_name} does not exist")

        bridge_result = self.bridge_exist_db(bridge_name)

        if not bridge_result.status:
            self.log.debug(
                f"insert_interface_bridge_group() -> Bridge group: {bridge_name} does not exist, Exiting")
            return Result(STATUS_NOK, reason=f"Bridge group: {bridge_name} does not exist")

        interface_id = interface_result.row_id
        bridge_id = bridge_result.row_id

        self.log.debug(f'insert_interface_bridge_group() -> InterfaceRowID: {interface_id} BridgeRowID:{bridge_id}')

        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO BridgeGroups (Interfaces_FK, Bridges_FK) VALUES (?, ?)",
                (interface_id, bridge_id)
            )
            row_id = cursor.lastrowid
            self.connection.commit()
            return Result(STATUS_OK, row_id=row_id, reason="Interface added to the bridge group successfully")

        except sqlite3.Error as e:
            error_message = f"Error inserting data into 'BridgeGroups': {e}"
            self.log.error(error_message)
            return Result(STATUS_NOK, self.ROW_ID_NOT_FOUND, reason=error_message)

    def delete_interface_bridge_group(self, interface_name: InterfaceName, bridge_name: BridgeName) -> Result:
        """
        Remove an interface from a bridge group in the 'BridgeGroups' table.

        Args:
            interface_name (str): The name of the interface.
            bridge_name (str): The name of the bridge group.

        Returns:
            Result: A Result object with the status of the deletion.
        """
        # Look up the interface and bridge group by name
        interface_result = self.interface_exists(interface_name)

        if not interface_result.status:
            return Result(STATUS_NOK, 
                          reason=f"Unable to delelte Interface: {interface_name} from bridge-group {interface_name} interface does not exist")

        bridge_result = self.bridge_exist_db(bridge_name)

        if not bridge_result.status:
            return Result(STATUS_NOK, 
                          reason=f"Unable to delelte bridge-group: {bridge_name} from interface {interface_name}, bridge does not exist")

        interface_id = interface_result.row_id
        bridge_id = bridge_result.row_id

        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "DELETE FROM BridgeGroups WHERE Interfaces_FK = ? AND Bridges_FK = ?",
                (interface_id, bridge_id)
            )
            self.connection.commit()
            return Result(STATUS_OK, reason="Interface removed from the bridge group successfully")

        except sqlite3.Error as e:
            error_message = f"Error deleting data from 'BridgeGroups': {e}"
            self.log.error(error_message)
            return Result(STATUS_NOK, reason=error_message)

    def _insert_default_row_in_interface_sub_option(self, interface_name: InterfaceName) -> Result:
        """
        Insert a default row into the InterfaceSubOptions table if it does not already exist.

        Args:
            interface_name (str): The name of the network interface.

        Returns:
            Result: An instance of Result if the row is successfully or not inserted.
        """
        try:
            cursor = self.connection.cursor()

            interface_exists_result = self.interface_exists(interface_name)
            if not interface_exists_result.status:
                return Result(status=False, reason=f"Interface:{interface_name} does not exists")

            cursor.execute("SELECT ID FROM InterfaceSubOptions WHERE Interfaces_FK = ?",
                           (interface_exists_result.row_id,))
            existing_row = cursor.fetchone()

            if existing_row is not None:
                return Result(status=False, reason="Row already exists")

            cursor.execute("INSERT INTO InterfaceSubOptions (Interfaces_FK) VALUES (?)",
                           (interface_exists_result.row_id,))
            row_id = cursor.lastrowid  # Get the inserted row's ID
            self.connection.commit()

            return Result(status=True, row_id=row_id, reason="Row inserted successfully")

        except sqlite3.Error:
            return Result(status=False, reason="Database error")

    '''
                        INTERFACE-RENAME-ALIAS
    '''

    def update_interface_alias(self, bus_info: str, initial_interface: InterfaceName, alias_interface: InterfaceName) -> Result:
        """
        Update or insert a record in the RenameInterface table to associate an alias interface with the initial interface.

        Parameters:
        - bus_info (str): The bus information of the interface.
        - initial_interface (str): The initial name of the interface.
        - alias_interface (str): The desired alias name for the interface.

        Returns:
        - Result: An instance of the Result class indicating the status of the operation.
          - status (str): STATUS_OK if the operation is successful, STATUS_NOK otherwise.
          - row_id (int): The ID of the updated/inserted record in the RenameInterface table.
          - reason (str): The error message, if any (only applicable if status is STATUS_NOK).
        """
        self.log.debug(
            f"update_interface_alias({bus_info}, {initial_interface}, {alias_interface})")
        try:
            cursor = self.connection.cursor()

            # Insert or replace the record in the RenameInterface table
            cursor.execute("""
                INSERT OR REPLACE INTO RenameInterface (BusInfo, InitialInterface, AliasInterface)
                VALUES (?, ?, ?)
            """, (bus_info, initial_interface, alias_interface))

            self.connection.commit()

            # Retrieve the ID of the updated/inserted record
            cursor.execute(
                "SELECT ID FROM RenameInterface WHERE InitialInterface = ?", (initial_interface,))
            row_id = cursor.fetchone()[0]

            self.update_interface_name(initial_interface, alias_interface)

            return Result(status=STATUS_OK, row_id=row_id, reason="Alias set successfully")

        except sqlite3.Error as e:
            # Handle database-related errors and return the Result instance with the error details
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=str(e))

    def is_initial_interface_alias_exist(self, initial_interface: InterfaceName) -> Result:
        """
        Check if an alias exists for the given initial interface.

        Args:
            initial_interface (str): The name of the initial interface to check.

        Returns:
            Result: A Result object with the following fields:
            - status (bool): True if an alias exists for the initial interface, False otherwise.
            - row_id (int, optional): The row ID of the alias entry if an alias exists, or None if no alias exists.
            - reason (str, optional): A reason for the result, which may include additional information.
            - result (str, optional): The alias name if an alias exists, or None if no alias exists.

        Raises:
            sqlite3.Error: If there is an error with the database query.
        """
        try:
            cursor = self.connection.cursor()

            cursor.execute(
                "SELECT AliasInterface, ID FROM RenameInterface WHERE InitialInterface = ?", (initial_interface,))
            row = cursor.fetchone()

            if row is not None:
                alias_name, row_id = row
                return Result(status=True, row_id=row_id, result={'AliasInterface': alias_name})
            else:
                return Result(status=False, row_id=None, result=None)

        except sqlite3.Error as e:
            return Result(status=False, row_id=None, reason=str(e))

    def select_interface_aliases(self) -> list[Result]:
        """
        Select all interface aliases from the InterfaceAlias table.

        Returns:
            list[Result]: A list of Result objects representing the entries in the InterfaceAlias table.
                Each Result object contains:
                - status (bool): True if the selection is successful, False otherwise.
                - data (dict, optional): A dictionary containing the selected data if successful.
                - reason (str, optional): A descriptive message indicating the reason for failure, if any.
        """
        try:
            cursor = self.connection.cursor()

            cursor.execute(
                "SELECT InitialInterface, AliasInterface FROM RenameInterface")
            rows = cursor.fetchall()

            result_list = []
            for row in rows:
                interface_name = row[0]
                alias_name = row[1]
                result_list.append(Result(status=STATUS_OK, row_id=0, result={
                                   'InterfaceName': interface_name, 'AliasInterface': alias_name}))

            return result_list

        except sqlite3.Error as e:
            self.log.error(f"Error selecting interface aliases: {e}")
            return [Result(status=STATUS_NOK, reason=f"{e}")]

    '''
                        WIRELESS-POLICY-WIFI
    '''

    def wifi_policy_exist(self, wireless_wifi_policy: WifiPolicyName) -> Result:
        """
        Check if a wireless Wi-Fi policy exists in the database.

        Args:
            wireless_wifi_policy (str): The name of the wireless Wi-Fi policy to check for existence.

        Returns:
            Result: An instance of the Result class representing the outcome of the operation.
            - `status` is set to True if the policy exists, or False if it doesn't.
            - `row_id` is the row ID of the policy if it exists, or 0 if it doesn't.
            - `reason` contains an optional result message providing additional information about the operation.
            - `result` contains the SQL query result, which includes the policy ID.
        """
        try:
            # Define the SQL query to check for the existence of the policy.
            query = "SELECT ID FROM WirelessWifiPolicy WHERE WifiPolicyName = ?"
            cursor = self.connection.cursor()
            cursor.execute(query, (wireless_wifi_policy,))
            row = cursor.fetchone()

            if row:
                policy_id = row[0]
                return Result(status=True, row_id=policy_id, reason=f"Policy '{wireless_wifi_policy}' exists.", result={"WifiPolicyName": wireless_wifi_policy})
            else:
                return Result(status=False, row_id=self.ROW_ID_NOT_FOUND, reason=f"Policy '{wireless_wifi_policy}' does not exist.", result=None)

        except sqlite3.Error as e:
            return Result(status=False, row_id=self.ROW_ID_NOT_FOUND, reason=f"Error while checking policy existence: {str(e)}", result=None)

    '''
                        WIRELESS-POLICY-WIFI DELETE
    '''

    def delete_wifi_policy(self, wireless_wifi_policy: WifiPolicyName) -> Result:
        """
        Delete a wireless Wi-Fi policy from the database.

        Args:
            wireless_wifi_policy (str): The name of the wireless Wi-Fi policy to delete.

        Returns:
            Result: A Result object representing the outcome of the operation.
                - `status` is set to STATUS_OK for successful deletions and STATUS_NOK for failed ones.
                - `row_id` contains the row ID of the deleted policy if the deletion is successful, or 0 if it fails.
                - `reason` provides an optional result message with additional information about the operation.
                - `result` is set to None for delete operations.

        Note:
        - The method deletes the wireless Wi-Fi policy with the provided name from the database.
        - If the deletion is successful, `status` is set to True, `row_id` contains the deleted policy's ID, and `reason` indicates success.
        - If the deletion fails, `status` is set to False, `row_id` is 0, and `reason` explains the reason for the failure.

        """
        try:
            # Define the SQL query to delete the wireless Wi-Fi policy.
            query = "DELETE FROM WirelessWifiPolicy WHERE WifiPolicyName = ?"
            cursor = self.connection.cursor()
            cursor.execute(query, (wireless_wifi_policy,))
            self.connection.commit()

            # Check the number of rows affected by the deletion.
            if cursor.rowcount > 0:
                return Result(status=STATUS_OK, row_id=cursor.rowcount, reason=f"Deleted wireless Wi-Fi policy '{wireless_wifi_policy}' successfully.")
            else:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"No policy with name '{wireless_wifi_policy}' found for deletion.")

        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to delete wireless Wi-Fi policy '{wireless_wifi_policy}'. Error: {str(e)}", result=None)

    def delete_wifi_ssid(self, wireless_wifi_policy: WifiPolicyName, ssid: SsidText) -> Result:
        """
        Delete a row from the 'WirelessWifiSecurityPolicy' table for a specific wireless Wi-Fi policy and SSID.

        Args:
            wireless_wifi_policy (str): The name of the wireless Wi-Fi policy that the SSID belongs to.
            ssid (str): The SSID to be deleted.

        Returns:
            Result: A Result object representing the outcome of the operation.
            - `status` is set to STATUS_OK for successful row deletions and STATUS_NOK for failed ones.
            - `row_id` contains the row ID of the deleted row if the deletion is successful, or 0 if it fails.
            - `reason` provides an optional result message with additional information about the operation.
            - `result` is set to None for delete operations.

        Note:
        - The method deletes a specific row from the 'WirelessWifiSecurityPolicy' table, which represents the association of an SSID with a wireless Wi-Fi policy.
        - If the deletion is successful, `status` is set to True, `row_id` contains the row ID of the deleted row, and `reason` indicates success.
        - If the deletion fails (e.g., due to a database error or if the row does not exist), `status` is set to False, `row_id` is 0, and `reason` explains the reason for the failure.

        """
        try:
            # Define the SQL query to delete the row from 'WirelessWifiSecurityPolicy' for the specified policy and SSID.
            query = "DELETE FROM WirelessWifiSecurityPolicy WHERE WirelessWifiPolicy_FK = (SELECT ID FROM WirelessWifiPolicy WHERE WifiPolicyName = ?) AND Ssid = ?"
            cursor = self.connection.cursor()
            cursor.execute(query, (wireless_wifi_policy, ssid))
            self.connection.commit()

            # Check the number of rows affected by the deletion.
            if cursor.rowcount > 0:
                return Result(status=STATUS_OK, row_id=cursor.rowcount, reason=f"Deleted row for SSID '{ssid}' from policy '{wireless_wifi_policy}' successfully.")
            else:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason="No matching row found for deletion.")

        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to delete row for SSID '{ssid}' from policy '{wireless_wifi_policy}'. Error: {str(e)}", result=None)

    def delete_wifi_hostapd_option(self, wireless_wifi_policy: WifiPolicyName, hostapd_option: str, hostapd_value: str) -> Result:
        """
        Delete a Hostapd option associated with a specific wireless Wi-Fi policy.

        Args:
            wireless_wifi_policy (str): The name of the wireless Wi-Fi policy to disassociate the Hostapd option from.
            hostapd_option (str): The name of the Hostapd option to delete.
            hostapd_value (str): The value associated with the Hostapd option (used for additional verification).

        Returns:
        Result: A Result object representing the outcome of the operation.
            - `status` is set to STATUS_OK for successful deletions and STATUS_NOK for failed ones.
            - `row_id` is set to 0 regardless of success.
            - `reason` provides an optional result message with additional information about the operation.
            - `result` is set to None for delete operations.

        Note:
        - The method deletes a Hostapd option associated with the specified wireless Wi-Fi policy, verifying the option value.
        - If the deletion is successful, `status` is set to True, and `reason` indicates success.
        - If the deletion fails (e.g., due to a database error, no matching policy found, or incorrect option value), `status` is set to False, and `reason` explains the reason for the failure.

        """
        try:
            # Define the SQL query to delete the Hostapd option for the specified policy, verifying the option value.
            query = """
                        DELETE FROM WirelessWifiHostapdOptions
                        WHERE WirelessWifiPolicy_FK = (SELECT ID FROM WirelessWifiPolicy WHERE WifiPolicyName = ?)
                        AND OptionName = ?
                        AND OptionValue = ?
                    """
            cursor = self.connection.cursor()
            cursor.execute(query, (wireless_wifi_policy,
                           hostapd_option, hostapd_value))
            self.connection.commit()

            # Check the number of rows affected by the deletion.
            affected_rows = cursor.rowcount

            if affected_rows > 0:
                return Result(status=STATUS_OK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Deleted Hostapd option for policy '{wireless_wifi_policy}' successfully.")
            else:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason="No matching policy and Hostapd option found for the deletion or the option value is incorrect.")

        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to delete Hostapd option for policy '{wireless_wifi_policy}'. Error: {str(e)}", result=None)

    '''
                        WIRELESS-POLICY-WIFI SELECT
    '''

    def select_wifi_policies(self) -> list[Result]:
        """
        Retrieves information about all wireless WiFi policies.

        Returns:
        - list[Result]: A list of Result objects containing information about wireless WiFi policies.
        """
        results = []

        try:
            query = """
                SELECT ID, WifiPolicyName, Channel, HardwareMode
                FROM WirelessWifiPolicy;
            """
            cursor = self.connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

            for row in rows:
                id, policy_name, channel, hardware_mode = row
                results.append(Result(
                    status=STATUS_OK,
                    row_id=id,
                    reason=f"Retrieved information for wireless WiFi policy '{policy_name}'",
                    result={"WifiPolicyName": policy_name,
                            "Channel": channel, "HardwareMode": hardware_mode}
                ))

            return results

        except sqlite3.Error as e:
            error_message = f"Failed to retrieve information for wireless WiFi policies. Error: {str(e)}"
            results.append(
                Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message))
            return results

    def select_all_wifi_hostapd_options(self, wireless_wifi_policy: WifiPolicyName) -> list[Result]:
        """
        Retrieve a list of all Hostapd options associated with a specific wireless Wi-Fi policy.

        Args:
        wireless_wifi_policy (str): The name of the wireless Wi-Fi policy to retrieve Hostapd options for.

        Returns:
        list[Result]: A list of Result objects representing the outcome of the operation for each Hostapd option.
            - Each Result object has:
                - `status` set to STATUS_OK for successful retrievals and STATUS_NOK for failed ones.
                - `row_id` contains the Hostapd option's unique ID if the retrieval is successful, or 0 if it fails.
                - `reason` provides an optional result message with additional information about the operation.
                - `result` contains Hostapd option details, including the option name and value.

        Note:
        - The method retrieves a list of all Hostapd options associated with the specified wireless Wi-Fi policy.
        - For each Hostapd option retrieved successfully, a Result object is created with `status` set to True, `row_id` containing the option's ID, and `result` providing option details.
        - If a Hostapd option retrieval fails (e.g., due to a database error or no matching policy found), a Result object is created with `status` set to False and `row_id` set to 0, and `reason` explains the reason for the failure.

        """
        results = []

        try:
            # Define the SQL query to retrieve all Hostapd options for the specified policy.
            query = """
                        SELECT OptionName, OptionValue, ID
                        FROM WirelessWifiHostapdOptions
                        WHERE WirelessWifiPolicy_FK = (SELECT ID FROM WirelessWifiPolicy WHERE WifiPolicyName = ?)
                    """
            cursor = self.connection.cursor()
            cursor.execute(query, (wireless_wifi_policy,))
            rows = cursor.fetchall()

            for row in rows:
                option_name, option_value, id = row
                results.append(Result(status=STATUS_OK, row_id=id, reason=f"Retrieved Hostapd option for policy '{wireless_wifi_policy}'", result={
                               "OptionName": option_name, "OptionValue": option_value}))

            return results

        except sqlite3.Error as e:
            results.append(Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND,
                           reason=f"Failed to retrieve Hostapd options for policy '{wireless_wifi_policy}'. Error: {str(e)}"))
            return results

    def select_wifi_hostapd_option(self, wireless_wifi_policy: WifiPolicyName, hostapd_option: str, hostapd_value: str) -> list[Result]:
        """
        Retrieve a list of Hostapd options associated with a specific wireless Wi-Fi policy and matching option.

        Args:
        wireless_wifi_policy (str): The name of the wireless Wi-Fi policy to retrieve Hostapd options for.
        hostapd_option (str): The name of the Hostapd option to retrieve.
        hostapd_value (str): The value associated with the Hostapd option.

        Returns:
        list[Result]: A list of Result objects representing the outcome of the operation for each matching Hostapd option.
            - Each Result object has:
                - `status` set to STATUS_OK for successful retrievals and STATUS_NOK for failed ones.
                - `row_id` contains the Hostapd option's unique ID if the retrieval is successful, or 0 if it fails.
                - `reason` provides an optional result message with additional information about the operation.
                - `result` contains Hostapd option details, including the option name and value.

        Note:
        - The method retrieves a list of Hostapd options associated with the specified wireless Wi-Fi policy and matching option.
        - For each matching Hostapd option retrieved successfully, a Result object is created with `status` set to True, `row_id` containing the option's ID, and `result` providing option details.
        - If a Hostapd option retrieval fails (e.g., due to a database error, no matching policy found, or incorrect option value), a Result object is created with `status` set to False and `row_id` set to 0, and `reason` explains the reason for the failure.

        """
        results = []

        try:
            # Define the SQL query to retrieve matching Hostapd options for the specified policy and option.
            query = """
                        SELECT OptionName, OptionValue, ID
                        FROM WirelessWifiHostapdOptions
                        WHERE WirelessWifiPolicy_FK = (SELECT ID FROM WirelessWifiPolicy WHERE WifiPolicyName = ?)
                        AND OptionName = ?
                        AND OptionValue = ?
                    """
            cursor = self.connection.cursor()
            cursor.execute(query, (wireless_wifi_policy,
                           hostapd_option, hostapd_value))
            rows = cursor.fetchall()

            for row in rows:
                option_name, option_value, id = row
                results.append(Result(status=STATUS_OK, row_id=id, reason=f"Retrieved matching Hostapd option for policy '{wireless_wifi_policy}'", result={
                               "OptionName": option_name, "OptionValue": option_value}))

            return results

        except sqlite3.Error as e:
            results.append(Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND,
                           reason=f"Failed to retrieve matching Hostapd options for policy '{wireless_wifi_policy}'. Error: {str(e)}"))
            return results

    def select_wifi_policy_interfaces(self, wireless_wifi_policy: WifiPolicyName) -> list[Result]:
        """
        Retrieve a list of network interfaces associated with a specific wireless Wi-Fi policy.

        Args:
        wireless_wifi_policy (str): The name of the wireless Wi-Fi policy to retrieve associated network interfaces for.

        Returns:
        list[Result]: A list of Result objects representing the outcome of the operation for each associated network interface.
            - Each Result object has:
                - `status` set to STATUS_OK for successful retrievals and STATUS_NOK for failed ones.
                - `row_id` contains the network interface's unique ID if the retrieval is successful, or 0 if it fails.
                - `reason` provides an optional result message with additional information about the operation.
                - `result` contains network interface details, e.g., the interface name and type.

        Note:
        - The method retrieves a list of network interfaces associated with the specified wireless Wi-Fi policy.
        - For each associated network interface retrieved successfully, a Result object is created with `status` set to True, `row_id` containing the interface's ID, and `result` providing interface details.
        - If a network interface retrieval fails (e.g., due to a database error or no matching policy found), a Result object is created with `status` set to False and `row_id` set to 0, and `reason` explains the reason for the failure.

        """
        results = []

        try:
            # Define the SQL query to retrieve associated network interfaces for the specified policy.
            query = """
                        SELECT Interfaces.InterfaceName, Interfaces.InterfaceType, Interfaces.ID
                        FROM Interfaces
                        JOIN WirelessWifiPolicyInterface ON Interfaces.ID = WirelessWifiPolicyInterface.Interfaces_FK
                        JOIN WirelessWifiPolicy ON WirelessWifiPolicyInterface.WirelessWifiPolicy_FK = WirelessWifiPolicy.ID
                        WHERE WirelessWifiPolicy.WifiPolicyName = ?
                    """
            cursor = self.connection.cursor()
            cursor.execute(query, (wireless_wifi_policy,))
            rows = cursor.fetchall()

            for row in rows:
                interface_name, interface_type, id = row
                results.append(Result(status=STATUS_OK, row_id=id, reason=f"Retrieved associated network interface for policy '{wireless_wifi_policy}'", result={
                               "InterfaceName": interface_name, "InterfaceType": interface_type}))

            return results

        except sqlite3.Error as e:
            results.append(Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND,
                           reason=f"Failed to retrieve associated network interfaces for policy '{wireless_wifi_policy}'. Error: {str(e)}"))
            return results

    def select_wifi_security_policy(self, wireless_wifi_policy: WifiPolicyName) -> list[Result]:
        """
        Retrieve a list of security policies associated with a specific wireless Wi-Fi policy.

        Args:
            wireless_wifi_policy (str): The name of the wireless Wi-Fi policy to retrieve security policies for.

        Returns:
            list[Result]: A list of Result objects representing the outcome of the operation for each security policy.
            - `status` set to STATUS_OK for successful retrievals and STATUS_NOK for failed ones.
            - `row_id` containing the policy ID if the retrieval is successful, or 0 if it fails.
            - `reason` provides an optional result message with additional information about the operation.
            - `result` contains the security policy information, e.g., SSID, WPA passphrase, and WPA version.

        Note:
        - The method retrieves a list of security policies associated with the specified wireless Wi-Fi policy.
        - For each security policy retrieved successfully, a Result object is created with `status` set to True, `row_id` containing the policy ID, and `result` providing security policy details.
        - If a security policy retrieval fails (e.g., due to a database error or no matching policy found), a Result object is created with `status` set to False and `row_id` set to 0, and `reason` explains the reason for the failure.
        """
        results = []

        try:
            # Define the SQL query to retrieve security policies for the specified policy.
            query = """
                        SELECT Ssid, WpaPassPhrase, WpaVersion, WpaKeyManagment, WpaPairwise, ID
                        FROM WirelessWifiSecurityPolicy
                        WHERE WirelessWifiPolicy_FK = (SELECT ID FROM WirelessWifiPolicy WHERE WifiPolicyName = ?)
                    """
            cursor = self.connection.cursor()
            cursor.execute(query, (wireless_wifi_policy,))
            rows = cursor.fetchall()

            for row in rows:
                ssid, passphrase, wpa_version, key_management, pairwise, id = row
                results.append(Result(status=STATUS_OK, row_id=id,
                                      reason=f"Retrieved security policy for policy '{wireless_wifi_policy}'",
                                      result={"Ssid": ssid,
                                              "WpaPassPhrase": passphrase,
                                              "WpaVersion": wpa_version,
                                              "WpaKeyManagment": key_management,
                                              "WpaPairwise": pairwise}))

            return results

        except sqlite3.Error as e:
            results.append(Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND,
                           reason=f"Failed to retrieve security policies for policy '{wireless_wifi_policy}'. Error: {str(e)}"))
            return results

    def select_wifi_security_policy_via_ssid(self, wireless_wifi_policy: WifiPolicyName, ssid: SsidText) -> list[Result]:
        """
        Select Wi-Fi security policies based on wireless Wi-Fi policy and SSID.

        Args:
            wireless_wifi_policy (str): The name of the wireless Wi-Fi policy to retrieve security policies for.
            ssid (str): The SSID (Service Set Identifier) to use for filtering.

        Returns:
            list[Result]: A list of Result objects representing the outcome of the operation for each matching security policy.
            - `status` set to STATUS_OK for successful retrievals and STATUS_NOK for failed ones.
            - `row_id` containing the policy ID if the retrieval is successful, or 0 if it fails.
            - `reason` provides an optional result message with additional information about the operation.
            - `result` contains the security policy information, e.g., SSID, WPA passphrase, and WPA version.

        Note:
        - The method retrieves a list of security policies based on the specified wireless Wi-Fi policy and SSID.
        - For each security policy retrieved successfully, a Result object is created with `status` set to True, `row_id` containing the policy ID, and `result` providing security policy details.
        - If a security policy retrieval fails (e.g., due to a database error or no matching policy found), a Result object is created with `status` set to False and `row_id` set to 0, and `reason` explains the reason for the failure.
        """
        results = []

        try:
            # Define the SQL query to retrieve security policies based on wireless Wi-Fi policy and SSID.
            query = """
                        SELECT Ssid, WpaPassPhrase, WpaVersion, WpaKeyManagment, WpaPairwise, ID
                        FROM WirelessWifiSecurityPolicy
                        WHERE WirelessWifiPolicy_FK = (SELECT ID FROM WirelessWifiPolicy WHERE WifiPolicyName = ?)
                        AND Ssid = ?
                    """
            cursor = self.connection.cursor()
            cursor.execute(query, (wireless_wifi_policy, ssid))
            rows = cursor.fetchall()

            for row in rows:
                ssid, passphrase, wpa_version, key_management, pairwise, id = row
                results.append(Result(status=STATUS_OK, row_id=id,
                                      reason=f"Retrieved security policy for policy '{wireless_wifi_policy}' and SSID '{ssid}'",
                                      result={"Ssid": ssid,
                                              "WpaPassPhrase": passphrase,
                                              "WpaVersion": wpa_version,
                                              "WpaKeyManagment": key_management,
                                              "WpaPairwise": pairwise}))

            return results

        except sqlite3.Error as e:
            results.append(Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND,
                                  reason=f"Failed to retrieve security policies for policy '{wireless_wifi_policy}' and SSID '{ssid}'. Error: {str(e)}"))
            return results

    '''
                        WIRELESS-POLICY-WIFI UPDATE
    '''

    def update_wifi_wpa_passphrase(self, wireless_wifi_policy: WifiPolicyName, ssid: SsidText, passphrase: str, wpa_version: int) -> Result:
        """
        Update the WPA passphrase for a specific wireless Wi-Fi policy and SSID.

        Args:
            wireless_wifi_policy (str): The name of the wireless Wi-Fi policy to associate the updated passphrase with.
            ssid (str): The SSID to associate the updated passphrase with.
            passphrase (str): The new WPA passphrase to update.
            wpa_version (int): The new WPA version to associate with the updated passphrase (1 for WPA, 2 for WPA2, 3 for WPA3).

        Returns:
            Result: A Result object representing the outcome of the operation.
                - `status` is set to STATUS_OK for successful updates and STATUS_NOK for failed ones.
                - `row_id` contains the number of rows affected by the update if it is successful, or 0 if it fails.
                - `reason` provides an optional result message with additional information about the operation.
                - `result` is set to None for update operations.

        Note:
        - The method updates the WPA passphrase and version associated with the specified wireless Wi-Fi policy and SSID.
        - If the update is successful, `status` is set to True, `row_id` contains the number of rows affected by the update, and `reason` indicates success.
        - If the update fails (e.g., due to a database error), `status` is set to False, `row_id` is 0, and `reason` explains the reason for the failure.

        """
        try:
            # Define the SQL query to update the WPA passphrase and version for the specified policy and SSID.
            query = """
                        UPDATE WirelessWifiSecurityPolicy
                        SET WpaPassPhrase = ?, WpaVersion = ?
                        WHERE WirelessWifiPolicy_FK = (SELECT ID FROM WirelessWifiPolicy WHERE WifiPolicyName = ?)
                        AND Ssid = ?
                    """
            cursor = self.connection.cursor()
            cursor.execute(query, (passphrase, wpa_version,
                           wireless_wifi_policy, ssid))
            self.connection.commit()

            # Check the number of rows affected by the update.
            affected_rows = cursor.rowcount

            if affected_rows > 0:
                return Result(status=STATUS_OK, row_id=affected_rows, reason=f"Updated WPA passphrase and version for policy '{wireless_wifi_policy}' and SSID '{ssid}' successfully.")
            else:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason="No matching policy and SSID found for the update.")

        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to update WPA passphrase and version for policy '{wireless_wifi_policy}' and SSID '{ssid}'. Error: {str(e)}", result=None)

    def update_wifi_ssid(self, wireless_wifi_policy: WifiPolicyName, ssid: SsidText) -> Result:
        """
        Update an existing wireless Wi-Fi SSID in the database for a specific policy.

        Args:
            wireless_wifi_policy (str): The name of the wireless Wi-Fi policy to associate the updated SSID with.
            ssid (str): The new SSID value to update.

        Returns:
            Result: A Result object representing the outcome of the operation.
                - `status` is set to STATUS_OK for successful updates and STATUS_NOK for failed ones.
                - `row_id` contains the row ID of the updated SSID if the update is successful, or 0 if it fails.
                - `reason` provides an optional result message with additional information about the operation.
                - `result` is set to None for update operations.

        Note:
        - The method updates an existing SSID associated with the specified wireless Wi-Fi policy to the new value.
        - If the update is successful, `status` is set to True, `row_id` contains the updated SSID's ID, and `reason` indicates success.
        - If the update fails (e.g., due to a database error), `status` is set to False, `row_id` is 0, and `reason` explains the reason for the failure.

        """
        try:
            # Define the SQL query to update the wireless Wi-Fi SSID for the specified policy.
            query = "UPDATE WirelessWifiSecurityPolicy SET Ssid = ? WHERE WirelessWifiPolicy_FK = (SELECT ID FROM WirelessWifiPolicy WHERE WifiPolicyName = ?)"
            cursor = self.connection.cursor()
            cursor.execute(query, (ssid, wireless_wifi_policy))
            self.connection.commit()

            # Check the number of rows affected by the update.
            if cursor.rowcount > 0:
                return Result(status=STATUS_OK, row_id=cursor.rowcount, reason=f"Updated SSID for policy '{wireless_wifi_policy}' to '{ssid}' successfully.")
            else:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason="No matching policy found for the update.")

        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to update SSID for policy '{wireless_wifi_policy}' to '{ssid}'. Error: {str(e)}", result=None)

    def update_wifi_hostapd_option(self, wireless_wifi_policy: WifiPolicyName, hostapd_option: str, hostapd_value: str) -> Result:
        """
        Update the value of a Hostapd option for a specific wireless Wi-Fi policy.

        Args:
            wireless_wifi_policy (str): The name of the wireless Wi-Fi policy to associate the updated Hostapd option with.
            hostapd_option (str): The name of the Hostapd option to update.
            hostapd_value (str): The new value to associate with the Hostapd option.

        Returns:
            Result: A Result object representing the outcome of the operation.
                - `status` is set to STATUS_OK for successful updates and STATUS_NOK for failed ones.
                - `row_id` contains the number of rows affected by the update if it is successful, or 0 if it fails.
                - `reason` provides an optional result message with additional information about the operation.
                - `result` is set to None for update operations.

        Note:
        - The method updates the value of a Hostapd option associated with the specified wireless Wi-Fi policy.
        - If the update is successful, `status` is set to True, `row_id` contains the number of rows affected by the update, and `reason` indicates success.
        - If the update fails (e.g., due to a database error or no matching policy found), `status` is set to False, `row_id` is 0, and `reason` explains the reason for the failure.

        """
        try:
            # Define the SQL query to update the value of the Hostapd option for the specified policy.
            query = """
                        UPDATE WirelessWifiHostapdOptions
                        SET OptionValue = ?
                        WHERE WirelessWifiPolicy_FK = (SELECT ID FROM WirelessWifiPolicy WHERE WifiPolicyName = ?)
                        AND OptionName = ?
                    """
            cursor = self.connection.cursor()
            cursor.execute(
                query, (hostapd_value, wireless_wifi_policy, hostapd_option))
            self.connection.commit()

            # Check the number of rows affected by the update.
            affected_rows = cursor.rowcount

            if affected_rows > 0:
                return Result(status=STATUS_OK, row_id=affected_rows, reason=f"Updated Hostapd option value for policy '{wireless_wifi_policy}' successfully.")
            else:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason="No matching policy and Hostapd option found for the update.")

        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to update Hostapd option value for policy '{wireless_wifi_policy}'. Error: {str(e)}", result=None)

    def update_wifi_channel(self, wireless_wifi_policy: WifiPolicyName, channel: str) -> Result:
        """
        Update the Wi-Fi channel associated with a wireless Wi-Fi policy.

        Args:
            wireless_wifi_policy (str): The name of the wireless Wi-Fi policy to update.
            channel (str): The new Wi-Fi channel to set for the policy.

        Returns:
            Result: A Result object representing the outcome of the operation.
            - `status` is set to True for successful updates and False for failed ones.
            - `row_id` contains the row ID of the updated policy if the update is successful, or 0 if it fails.
            - `reason` provides an optional result message with additional information about the operation.

        Note:
        - The method updates the Wi-Fi channel for the specified wireless Wi-Fi policy.
        - If the update is successful, `status` is set to True, `row_id` contains the updated policy's ID, and `reason` indicates success.
        - If the update STATUS_NOK, `status` is set to False, `row_id` is 0, and `reason` explains the reason for the failure.
        """
        try:
            # Check if the wireless Wi-Fi policy exists
            policy_exist_result = self.wifi_policy_exist(wireless_wifi_policy)
            if not policy_exist_result.status:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=policy_exist_result.reason)

            # Define the SQL query to update the Wi-Fi channel.
            query = "UPDATE WirelessWifiPolicy SET Channel = ? WHERE WifiPolicyName = ?"
            cursor = self.connection.cursor()
            cursor.execute(query, (channel, wireless_wifi_policy))
            self.connection.commit()

            # Check if any rows were affected by the update
            if cursor.rowcount > 0:
                return Result(status=STATUS_OK, row_id=policy_exist_result.row_id, reason=f"Updated Wi-Fi channel for policy '{wireless_wifi_policy}' successfully.")
            else:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"No matching policy found for update: '{wireless_wifi_policy}'")

        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to update Wi-Fi channel for policy '{wireless_wifi_policy}'. Error: {str(e)}")

    def update_wifi_hardware_mode(self, wireless_wifi_policy: WifiPolicyName, hw_mode: str) -> Result:
        """
        Update the Wi-Fi hardware mode associated with a wireless Wi-Fi policy.

        Args:
            wireless_wifi_policy (str): The name of the wireless Wi-Fi policy to update.
            hw_mode (str): The new Wi-Fi hardware mode to set for the policy.

        Returns:
            Result: A Result object representing the outcome of the operation.
            - `status` is set to True for successful updates and False for failed ones.
            - `row_id` contains the row ID of the updated policy if the update is successful, or 0 if it fails.
            - `reason` provides an optional result message with additional information about the operation.

        Note:
        - The method updates the Wi-Fi hardware mode for the specified wireless Wi-Fi policy.
        - If the update is successful, `status` is set to True, `row_id` contains the updated policy's ID, and `reason` indicates success.
        - If the update fails, `status` is set to False, `row_id` is 0 (self.ROW_ID_NOT_FOUND), and `reason` explains the reason for the failure.
        """
        try:
            # Check if the wireless Wi-Fi policy exists
            policy_exist_result = self.wifi_policy_exist(wireless_wifi_policy)
            if not policy_exist_result.status:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=policy_exist_result.reason)

            # Define the SQL query to update the Wi-Fi hardware mode.
            query = "UPDATE WirelessWifiPolicy SET HardwareMode = ? WHERE WifiPolicyName = ?"
            cursor = self.connection.cursor()
            cursor.execute(query, (hw_mode, wireless_wifi_policy))
            self.connection.commit()

            # Check if any rows were affected by the update
            if cursor.rowcount > 0:
                return Result(status=STATUS_OK, row_id=policy_exist_result.row_id, reason=f"Updated Wi-Fi hardware mode for policy '{wireless_wifi_policy}' successfully.")
            else:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"No matching policy found for update: '{wireless_wifi_policy}' - query: {query}")

        except sqlite3.Error:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to update Wi-Fi hardware mode for policy {wireless_wifi_policy} - query: {query}")

    '''
                        WIRELESS-POLICY-WIFI INSERT
    '''

    def insert_wifi_policy(self, wireless_wifi_policy: WifiPolicyName) -> Result:
        """
        Insert a new wireless Wi-Fi policy into the database.

        Args:
            wireless_wifi_policy (str): The name of the wireless Wi-Fi policy to insert.

        Returns:
            Result: A Result object representing the outcome of the operation.
            - `status` is set to STATUS_OK for successful insertions and STATUS_NOK for failed ones.
            - `row_id` contains the row ID of the inserted policy if the insertion is successful, or 0 if it fails.
            - `reason` provides an optional result message with additional information about the operation.

        Note:
        - The method inserts a new wireless Wi-Fi policy with the provided name into the database.
        - If the insertion is successful, `status` is set to True, `row_id` contains the inserted policy's ID, and `reason` indicates success.
        - If the insertion fails, `status` is set to False, `row_id` is 0, and `reason` explains the reason for the failure.
        """
        try:
            # Define the SQL query to insert the wireless Wi-Fi policy.
            query = "INSERT INTO WirelessWifiPolicy (WifiPolicyName) VALUES (?)"
            cursor = self.connection.cursor()
            cursor.execute(query, (wireless_wifi_policy,))
            self.connection.commit()
            row_id = cursor.lastrowid

            return Result(status=STATUS_OK, row_id=row_id, reason=f"Inserted wireless Wi-Fi policy '{wireless_wifi_policy}' successfully.")

        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to insert wireless Wi-Fi policy '{wireless_wifi_policy}'. Error: {str(e)}")

    def insert_wifi_ssid(self, wireless_wifi_policy: WifiPolicyName, ssid: SsidText) -> Result:
        """
        Insert a new wireless Wi-Fi SSID into the database for a specific policy.

        Args:
            wireless_wifi_policy (str): The name of the wireless Wi-Fi policy to associate the SSID with.
            ssid (str): The SSID to insert.

        Returns:
            Result: A Result object representing the outcome of the operation.
                - `status` is set to STATUS_OK for successful insertions and STATUS_NOK for failed ones.
                - `row_id` contains the row ID of the inserted SSID if the insertion is successful, or 0 if it fails.
                - `reason` provides an optional result message with additional information about the operation.
                - `result` is set to None for insert operations.

        Note:
        - The method inserts a new SSID with the provided name and associates it with the specified wireless Wi-Fi policy.
        - If the insertion is successful, `status` is set to True, `row_id` contains the inserted SSID's ID, and `reason` indicates success.
        - If the insertion fails (e.g., due to a database error), `status` is set to False, `row_id` is 0, and `reason` explains the reason for the failure.

        """
        try:
            # Define the SQL query to insert the wireless Wi-Fi SSID for the specified policy.
            query = "INSERT INTO WirelessWifiSecurityPolicy (WirelessWifiPolicy_FK, Ssid) VALUES ((SELECT ID FROM WirelessWifiPolicy WHERE WifiPolicyName = ?), ?)"
            cursor = self.connection.cursor()
            cursor.execute(query, (wireless_wifi_policy, ssid))
            self.connection.commit()
            row_id = cursor.lastrowid

            return Result(status=STATUS_OK, row_id=row_id, reason=f"Inserted SSID '{ssid}' for policy '{wireless_wifi_policy}' successfully.")

        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to insert SSID '{ssid}' for policy '{wireless_wifi_policy}'. Error: {str(e)}", result=None)

    def insert_wifi_access_security_group(self, wireless_wifi_policy: WifiPolicyName, ssid: SsidText, pass_phrase: WifiPassphraseText, mode: str) -> Result:
        """
        Insert a new Wi-Fi access security group into the database associated with a wireless Wi-Fi policy.

        Args:
            wireless_wifi_policy (str): The name of the wireless Wi-Fi policy to associate the security group with.
            ssid (str): The SSID (Service Set Identifier) for the security group.
            pass_phrase (str): The WPA passphrase for the security group.
            mode (str): The security mode (e.g., WPA, WPA2, WPA3) for the security group.

        Returns:
            Result: A Result object representing the outcome of the operation.
            - `status` is set to True for successful insertions and False for failed ones.
            - `row_id` contains the row ID of the inserted security group if the insertion is successful, or 0 if it fails.
            - `reason` provides an optional result message with additional information about the operation.

        Note:
        - The method inserts a new Wi-Fi access security group associated with the specified wireless Wi-Fi policy.
        - If the insertion is successful, `status` is set to True, `row_id` contains the inserted security group's ID, and `reason` indicates success.
        - If the insertion fails due to an existing combination of `wireless_wifi_policy` and `ssid`, `status` is set to False, `row_id` is 0, and `reason` explains the reason for the failure.
        """
        try:
            # Check if the wireless Wi-Fi policy exists
            policy_exist_result = self.wifi_policy_exist(wireless_wifi_policy)
            if not policy_exist_result.status:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=policy_exist_result.reason)

            # Check if the combination of wireless_wifi_policy and ssid already exists
            combination_exist_result = self.select_wifi_security_policy_via_ssid(
                wireless_wifi_policy, ssid)
            if combination_exist_result:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Security group for SSID '{ssid}' already exists in policy '{wireless_wifi_policy}'.")

            # Define the SQL query to insert the Wi-Fi access security group
            query = "INSERT INTO WirelessWifiSecurityPolicy (WirelessWifiPolicy_FK, Ssid, WpaPassPhrase, WpaVersion) VALUES (?, ?, ?, ?)"
            cursor = self.connection.cursor()
            cursor.execute(
                query, (policy_exist_result.row_id, ssid, pass_phrase, mode))
            self.connection.commit()
            row_id = cursor.lastrowid

            return Result(status=STATUS_OK, row_id=row_id, reason=f"Inserted Wi-Fi access security group for policy '{wireless_wifi_policy}' successfully.")

        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to insert Wi-Fi access security group for policy '{wireless_wifi_policy}'. Error: {str(e)}")

    def insert_wifi_access_security_group_default(self, wireless_wifi_policy: WifiPolicyName) -> Result:
        """
        Insert the default Wi-Fi access security group settings into the database for a wireless Wi-Fi policy.

        Args:
            wireless_wifi_policy (str): The name of the wireless Wi-Fi policy to associate with the default access security group settings.

        Returns:
            Result: A Result object representing the outcome of the operation.
            - `status` is set to True for successful insertions and False for failed ones.
            - `row_id` contains the row ID of the inserted settings if the insertion is successful, or 0 if it fails.
            - `reason` provides an optional result message with additional information about the operation.

        Note:
        - The method inserts default Wi-Fi access security group settings associated with the specified wireless Wi-Fi policy.
        - If the insertion is successful, `status` is set to STATUS_OK, `row_id` contains the inserted settings' ID, and `reason` indicates success.
        - If the insertion fails, `status` is set to STATUS_NOK, `row_id` is 0 (self.ROW_ID_NOT_FOUND), and `reason` explains the reason for the failure.
        """
        try:

            policy_exist_result = self.wifi_policy_exist(wireless_wifi_policy)

            if not policy_exist_result.status:
                return Result(status=STATUS_NOK,
                              row_id=self.ROW_ID_NOT_FOUND,
                              reason=policy_exist_result.reason)

            query = "INSERT INTO WirelessWifiSecurityPolicy (WirelessWifiPolicy_FK) VALUES (?)"
            cursor = self.connection.cursor()
            cursor.execute(query, (policy_exist_result.row_id,))
            self.connection.commit()
            row_id = cursor.lastrowid

            return Result(status=STATUS_OK,
                          row_id=row_id,
                          reason=f"Inserted default Wi-Fi access security group settings for policy '{wireless_wifi_policy}' successfully.")

        except sqlite3.Error as e:
            return Result(status=STATUS_NOK,
                          row_id=self.ROW_ID_NOT_FOUND,
                          reason=f"Failed to insert default Wi-Fi access security group settings for policy '{wireless_wifi_policy}'. Error: {str(e)}")

    def insert_wifi_wpa_passphrase(self, wireless_wifi_policy: WifiPolicyName, ssid: SsidText, passphrase: str, wpa_version: int) -> Result:
        """
        Insert a new WPA passphrase for a specific wireless Wi-Fi policy and SSID.

        Args:
            wireless_wifi_policy (str): The name of the wireless Wi-Fi policy to associate the passphrase with.
            ssid (str): The SSID to associate the passphrase with.
            passphrase (str): The WPA passphrase to insert.
            wpa_version (int): The WPA version to associate with the passphrase (1 for WPA, 2 for WPA2, 3 for WPA3).

        Returns:
            Result: A Result object representing the outcome of the operation.
                - `status` is set to STATUS_OK for successful insertions and STATUS_NOK for failed ones.
                - `row_id` contains the row ID of the inserted passphrase if the insertion is successful, or 0 if it fails.
                - `reason` provides an optional result message with additional information about the operation.
                - `result` is set to None for insert operations.

        Note:
        - The method inserts a new WPA passphrase associated with the specified wireless Wi-Fi policy and SSID.
        - If the insertion is successful, `status` is set to True, `row_id` contains the inserted passphrase's ID, and `reason` indicates success.
        - If the insertion fails (e.g., due to a database error), `status` is set to False, `row_id` is 0, and `reason` explains the reason for the failure.

        """
        try:
            # Define the SQL query to insert the WPA passphrase for the specified policy and SSID.
            query = """
                        INSERT INTO WirelessWifiSecurityPolicy (
                            WirelessWifiPolicy_FK, Ssid, WpaPassPhrase, WpaVersion) VALUES ((
                                SELECT ID FROM WirelessWifiPolicy WHERE WifiPolicyName = ?), ?, ?, ?)
                    """
            cursor = self.connection.cursor()
            cursor.execute(query, (wireless_wifi_policy,
                           ssid, passphrase, wpa_version))
            self.connection.commit()
            row_id = cursor.lastrowid

            return Result(status=STATUS_OK, row_id=row_id, reason=f"Inserted WPA passphrase for policy '{wireless_wifi_policy}' and SSID '{ssid}' successfully.")

        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to insert WPA passphrase for policy '{wireless_wifi_policy}' and SSID '{ssid}'. Error: {str(e)}", result=None)

    def insert_wifi_policy_to_wifi_interface(self, wireless_wifi_policy: WifiPolicyName, wifi_interface: InterfaceName) -> Result:
        """
        Associate a wireless Wi-Fi policy with a specific network interface.

        Args:
        wireless_wifi_policy (str): The name of the wireless Wi-Fi policy to associate with the network interface.
        wifi_interface (str): The name of the network interface to associate with the wireless Wi-Fi policy.

        Returns:
        Result: A Result object representing the outcome of the operation.
            - `status` is set to STATUS_OK for successful associations and STATUS_NOK for failed ones.
            - `row_id` contains the row ID of the association if it is successful, or 0 if it fails.
            - `reason` provides an optional result message with additional information about the operation.

        Note:
        - The method associates a wireless Wi-Fi policy with the specified network interface.
        - If the association is successful, `status` is set to True, `row_id` contains the row ID of the association, and `reason` indicates success.
        - If the association fails (e.g., due to a database error, no matching policy, or no matching interface), `status` is set to False, `row_id` is 0, and `reason` explains the reason for the failure.

        """
        try:
            # Define the SQL query to associate the wireless Wi-Fi policy with the network interface.
            query = """
                        INSERT INTO WirelessWifiPolicyInterface (Interfaces_FK, WirelessWifiPolicy_FK)
                        VALUES (
                            (SELECT ID FROM Interfaces WHERE InterfaceName = ?),
                            (SELECT ID FROM WirelessWifiPolicy WHERE WifiPolicyName = ?)
                        )
                    """
            cursor = self.connection.cursor()
            cursor.execute(query, (wifi_interface, wireless_wifi_policy))
            self.connection.commit()
            row_id = cursor.lastrowid

            return Result(status=STATUS_OK, row_id=row_id, reason=f"Associated wireless Wi-Fi policy '{wireless_wifi_policy}' with network interface '{wifi_interface}' successfully.")

        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to associate wireless Wi-Fi policy '{wireless_wifi_policy}' with network interface '{wifi_interface}'. Error: {str(e)}")

    def insert_wifi_hostapd_option(self, wireless_wifi_policy: WifiPolicyName, hostapd_option: str, hostapd_value: str) -> Result:
        """
        Insert a new Hostapd option for a specific wireless Wi-Fi policy.

        Args:
            wireless_wifi_policy (str): The name of the wireless Wi-Fi policy to associate the Hostapd option with.
            hostapd_option (str): The name of the Hostapd option to insert.
            hostapd_value (str): The value to associate with the Hostapd option.

        Returns:
            Result: A Result object representing the outcome of the operation.
                - `status` is set to STATUS_OK for successful insertions and STATUS_NOK for failed ones.
                - `row_id` contains the row ID of the inserted Hostapd option if the insertion is successful, or 0 if it fails.
                - `reason` provides an optional result message with additional information about the operation.
                - `result` is set to None for insert operations.

        Note:
        - The method inserts a new Hostapd option associated with the specified wireless Wi-Fi policy.
        - If the insertion is successful, `status` is set to True, `row_id` contains the inserted Hostapd option's ID, and `reason` indicates success.
        - If the insertion fails (e.g., due to a database error), `status` is set to False, `row_id` is 0, and `reason` explains the reason for the failure.

        """
        try:
            # Define the SQL query to insert the Hostapd option for the specified policy.
            query = """
                        INSERT INTO WirelessWifiHostapdOptions (
                            WirelessWifiPolicy_FK, OptionName, OptionValue) VALUES ((
                                SELECT ID FROM WirelessWifiPolicy WHERE WifiPolicyName = ?), ?, ?)
                    """
            cursor = self.connection.cursor()
            cursor.execute(query, (wireless_wifi_policy,
                           hostapd_option, hostapd_value))
            self.connection.commit()
            row_id = cursor.lastrowid

            return Result(status=STATUS_OK, row_id=row_id, reason=f"Inserted Hostapd option for policy '{wireless_wifi_policy}' successfully.")

        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to insert Hostapd option for policy '{wireless_wifi_policy}'. Error: {str(e)}", result=None)

    def insert_wifi_channel(self, wireless_wifi_policy: WifiPolicyName, channel: str) -> Result:
        """
        Insert a Wi-Fi channel into the database associated with a wireless Wi-Fi policy.

        Args:
            wireless_wifi_policy (str): The name of the wireless Wi-Fi policy to associate the channel with.
            channel (str): The Wi-Fi channel to insert.

        Returns:
            Result: A Result object representing the outcome of the operation.
            - `status` is set to True for successful insertions and False for failed ones.
            - `row_id` contains the row ID of the inserted channel if the insertion is successful, or 0 if it fails.
            - `reason` provides an optional result message with additional information about the operation.

        Note:
        - The method inserts a new Wi-Fi channel associated with the specified wireless Wi-Fi policy.
        - If the insertion is successful, `status` is set to True, `row_id` contains the inserted channel's ID, and `reason` indicates success.
        - If the insertion STATUS_NOK, `status` is set to STATUS_NOK, `row_id` is 0 (self.ROW_ID_NOT_FOUND), and `reason` explains the reason for the failure.
        """
        try:
            # Check if the wireless Wi-Fi policy exists
            policy_exist_result = self.wifi_policy_exist(wireless_wifi_policy)
            if not policy_exist_result.status:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=policy_exist_result.reason)

            # Define the SQL query to insert the Wi-Fi channel.
            query = "INSERT INTO WirelessWifiPolicy (WifiPolicyName, Channel) VALUES (?, ?)"
            cursor = self.connection.cursor()
            cursor.execute(query, (wireless_wifi_policy, channel))
            self.connection.commit()
            row_id = cursor.lastrowid

            return Result(status=STATUS_OK, row_id=row_id, reason=f"Inserted Wi-Fi channel '{channel}' for policy '{wireless_wifi_policy}' successfully.")

        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to insert Wi-Fi channel for policy '{wireless_wifi_policy}'. Error: {str(e)}")

    def insert_wifi_hardware_mode(self, wireless_wifi_policy: WifiPolicyName, hw_mode: str) -> Result:
        """
        Insert a Wi-Fi hardware mode into the database associated with a wireless Wi-Fi policy.

        Args:
            wireless_wifi_policy (str): The name of the wireless Wi-Fi policy to associate the hardware mode with.
            hw_mode (str): The Wi-Fi hardware mode to insert.

        Returns:
            Result: A Result object representing the outcome of the operation.
            - `status` is set to True for successful insertions and False for failed ones.
            - `row_id` contains the row ID of the inserted hardware mode if the insertion is successful, or 0 if it fails.
            - `reason` provides an optional result message with additional information about the operation.

        Note:
        - The method inserts a new Wi-Fi hardware mode associated with the specified wireless Wi-Fi policy.
        - If the insertion is successful, `status` is set to True, `row_id` contains the inserted hardware mode's ID, and `reason` indicates success.
        - If the insertion fails, `status` is set to False, `row_id` is 0 (self.ROW_ID_NOT_FOUND), and `reason` explains the reason for the failure.
        """
        try:
            # Check if the wireless Wi-Fi policy exists
            policy_exist_result = self.wifi_policy_exist(wireless_wifi_policy)
            if not policy_exist_result.status:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=policy_exist_result.reason)

            # Define the SQL query to insert the Wi-Fi hardware mode.
            query = "INSERT INTO WirelessWifiPolicy (WifiPolicyName, HardwareMode) VALUES (?, ?)"
            cursor = self.connection.cursor()
            cursor.execute(query, (wireless_wifi_policy, hw_mode))
            self.connection.commit()
            row_id = cursor.lastrowid

            return Result(status=STATUS_OK, row_id=row_id, reason=f"Inserted Wi-Fi hardware mode '{hw_mode}' for policy '{wireless_wifi_policy}' successfully.")

        except sqlite3.Error as e:
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Failed to insert Wi-Fi hardware mode for policy '{wireless_wifi_policy}'. Error: {str(e)}")

    '''
                                ROUTER-CONFIGURATION

                            ROUTER-CONFIGURATION-INTERFACE
    '''

    def select_interfaces(self) -> list[Result]:
        """
        Select a list of interface names based on the specified interface type.

        Args:
            interface_type (InterfaceType): The type of interface to filter by.

        Returns:
            list[Result]: A list of Result objects containing the interface names.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT Interfaces.ID, Interfaces.InterfaceName
                FROM Interfaces
                ''')

            result_list = []
            rows = cursor.fetchall()

            for row in rows:
                result_list.append(
                    Result(status=STATUS_OK, row_id=row[0], result={'InterfaceName': row[1]}))

            return result_list

        except sqlite3.Error as e:
            error_message = f"Error selecting interface names by interface type: {e}"
            self.log.error(error_message)
            return [Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)]

    def select_interfaces_by_interface_type(self, interface_type: InterfaceType) -> list[Result]:
        """
        Select a list of interface names based on the specified interface type.

        Args:
            interface_type (InterfaceType): The type of interface to filter by.

        Returns:
            list[Result]: A list of Result objects containing the interface names.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT Interfaces.ID, Interfaces.InterfaceName
                FROM Interfaces
                WHERE Interfaces.InterfaceType = ?;
                ''', (interface_type.value,))

            result_list = []
            rows = cursor.fetchall()

            for row in rows:
                result_list.append(
                    Result(status=STATUS_OK, row_id=row[0], result={'InterfaceName': row[1]}))

            return result_list

        except sqlite3.Error as e:
            error_message = f"Error selecting interface names by interface type: {e}"
            self.log.error(error_message)
            return [Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)]

    def select_interface_configuration(self, interface_name: InterfaceName) -> Result:
        """
        Select information about a specific interface.

        Args:
            interface_name (str): The name of the interface to select.

        Returns:
            Result: A Result object containing information about the selected interface.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(f'''
                SELECT DISTINCT
                    'interface ' || Interfaces.InterfaceName AS Interface,
                    'description ' || Interfaces.Description AS Description,
                    'mac address ' || InterfaceSubOptions.MacAddress AS MacAddress,
                    'duplex ' || InterfaceSubOptions.Duplex AS Duplex,
                    'speed ' || CASE 
                                WHEN InterfaceSubOptions.Speed = 1 THEN 'auto' 
                                ELSE InterfaceSubOptions.Speed 
                                END AS Speed,
                    CASE 
                        WHEN InterfaceSubOptions.ProxyArp THEN 'ip proxy-arp' 
                        ELSE 'no ip proxy-arp' 
                    END AS ProxyArp,
                    CASE 
                        WHEN InterfaceSubOptions.DropGratuitousArp THEN 'ip drop-gratuitous-arp' 
                        ELSE 'no ip drop-gratuitous-arp' 
                    END AS DropGratuitousArp,
                    'bridge group ' || Bridges.BridgeName AS BridgeGroup,
                    'ip nat ' || NatDirections.Direction || ' pool ' || Nats.NatPoolName AS NatInterfaceDirection,
                    CASE 
                        WHEN Interfaces.ShutdownStatus THEN 'shutdown' 
                        ELSE 'no shutdown' 
                    END AS Shutdown
                FROM
                    Interfaces
                LEFT JOIN
                    InterfaceAlias ON Interfaces.ID = InterfaceAlias.Interfaces_FK
                LEFT JOIN
                    InterfaceSubOptions ON Interfaces.ID = InterfaceSubOptions.Interfaces_FK
                LEFT JOIN
                    BridgeGroups ON Interfaces.ID = BridgeGroups.Interfaces_FK
                LEFT JOIN
                    Bridges ON Bridges.ID = BridgeGroups.Bridges_FK
                LEFT JOIN
                    NatDirections ON Interfaces.ID = NatDirections.Interfaces_FK
                LEFT JOIN
                    Nats ON Nats.ID = NatDirections.NAT_FK
                WHERE
                    Interfaces.InterfaceName = ?
                    
                AND Interfaces.InterfaceType != '{InterfaceType.BRIDGE.value}';

                ''', (interface_name,))

            result = cursor.fetchone()

            if result is not None:
                i = 0
                sql_result_dict = {
                    'Interface': result[0],
                    'Description': result[1],
                    'MacAddress': result[2],
                    'Duplex': result[3],
                    'Speed': 'auto' if result[4] == 1 else result[4],
                    'ProxyArp': result[5],
                    'DropGratuitousArp': result[6],
                    'BridgeGroup': result[7],
                    'NatInterafaceDirection': result[8],
                    'Shutdown': result[9],
                }
                return Result(status=STATUS_OK, row_id=None, result=sql_result_dict)
            else:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"Interface {interface_name} not found.")

        except sqlite3.Error as e:
            error_message = f"Error selecting interface information: {e}"
            self.log.error(error_message)
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)

    def select_interface_ip_dhcp_server_policies(self, interface_name: InterfaceName) -> list[Result]:
        """
        Retrieve DHCP server pool information associated with a specific interface.

        Parameters:
            interface_name (str): The name of the interface for which to retrieve DHCP server pool information.

        Returns:
            list[Result]: A list of Result objects representing the outcomes of the operation.
                Each Result object contains either the DHCP server pool information or an error message.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT DISTINCT
                    'ip dhcp-server pool-name ' || DHCPServer.DhcpPoolname as DhcpServerPool

                FROM Interfaces
                
                LEFT JOIN DHCPServer ON Interfaces.ID = DHCPServer.Interfaces_FK
                
                WHERE Interfaces.InterfaceName = ?;
                ''', (interface_name,))

            sql_results = cursor.fetchall()

            results = []

            for result in sql_results:
                results.append(Result(status=STATUS_OK, row_id=id,
                               result={'DhcpServerPool': result[0]}))

            return results

        except sqlite3.Error as e:
            error_message = f"Error selecting interface information: {e}"
            self.log.error(error_message)
            return [Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)]

    def select_interface_switchport_access_vlan_id(self, interface_name: InterfaceName) -> list[Result]:
        """
        Retrieve DHCP server pool information associated with a specific interface.

        Parameters:
            interface_name (str): The name of the interface for which to retrieve DHCP server pool information.

        Returns:
            list[Result]: A list of Result objects representing the outcomes of the operation.
                Each Result object contains either the DHCP server pool information or an error message.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT DISTINCT
                    'ip switchport access-vlan-id ' || VlanInterfaces.VlanID as SwitchportAccessVlanID

                FROM Interfaces
                
                LEFT JOIN VlanInterfaces ON Interfaces.ID = VlanInterfaces.Interfaces_FK
                
                WHERE Interfaces.InterfaceName = ?;
                ''', (interface_name,))

            sql_results = cursor.fetchall()

            results = []

            for result in sql_results:
                results.append(Result(status=STATUS_OK, 
                                      row_id=id,
                                      result={'SwitchportAccessVlanID': result[0]}))

            return results

        except sqlite3.Error as e:
            error_message = f"Error selecting interface information: {e}"
            self.log.error(error_message)
            return [Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)]

    def select_interface_dhcp_client_configuration(self, interface_name: InterfaceName) -> list[Result]:
        """
        Retrieve DHCP client configuration information associated with a specific interface.

        Parameters:
            interface_name (str): The name of the interface for which to retrieve DHCP client configuration information.

        Returns:
            list[Result]: A list of Result objects representing the outcomes of the operation.
                Each Result object contains either the DHCP client configuration information or an error message.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(f'''
                SELECT DISTINCT
                    CASE
                        WHEN DHCPClient.DHCPVersion = '{DHCPVersion.DHCP_V4.value}' THEN 'ip dhcp-client'
                        WHEN DHCPClient.DHCPVersion = '{DHCPVersion.DHCP_V6.value}' THEN 'ipv6 dhcp-client'
                        ELSE NULL  -- Handle other cases as needed
                    END AS DhcpClientVersion
                
                FROM Interfaces
                
                LEFT JOIN DHCPClient ON Interfaces.ID = DHCPClient.Interfaces_FK
                
                WHERE Interfaces.InterfaceName = ?;
                ''', (interface_name,))

            sql_results = cursor.fetchall()

            results = []

            for result in sql_results:
                results.append(Result(status=STATUS_OK, row_id=id, result={
                               'DhcpClientVersion': result[0]}))

            return results

        except sqlite3.Error as e:
            error_message = f"Error selecting interface information: {e}"
            self.log.error(error_message)
            return [Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)]

    def select_interface_ip_address_configuration(self, interface_name: InterfaceName) -> list[Result]:
        """
        Select distinct IP addresses for a specific interface.

        Args:
            interface_name (str): The name of the interface.

        Returns:
            list[Result]: A list of Result objects containing the IP addresses for the interface.
        """
        try:
            cursor = self.connection.cursor()

            cursor.execute('''
                SELECT DISTINCT
                    CASE
                        WHEN InterfaceIpAddress.IpAddress LIKE '%:%' THEN 'ipv6 address '
                        ELSE 'ip address '
                    END || InterfaceIpAddress.IpAddress || CASE WHEN InterfaceIpAddress.SecondaryIp THEN ' secondary' ELSE '' END AS IpAddress
                FROM
                    Interfaces
                LEFT JOIN InterfaceIpAddress ON Interfaces.ID = InterfaceIpAddress.Interfaces_FK
                WHERE Interfaces.InterfaceName = ?;
                ''', (interface_name,))

            result_list = []
            rows = cursor.fetchall()

            for row in rows:
                result_list.append(
                    Result(status=STATUS_OK, row_id=None, result={'IpAddress': row[0]}))

            return result_list

        except sqlite3.Error as e:
            error_message = f"Error selecting interface IP addresses: {e}"
            self.log.error(error_message)
            return [Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)]

    def select_interface_ip_static_arp_configuration(self, interface_name: InterfaceName) -> list[Result]:
        """
        Select distinct static ARP entries for a specific interface.

        Args:
            interface_name (str): The name of the interface.

        Returns:
            list[Result]: A list of Result objects containing the static ARP entries for the interface.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT DISTINCT
                    CASE WHEN InterfaceStaticArp.IpAddress THEN 'ip static-arp '    || InterfaceStaticArp.IpAddress  || ' ' 
                                                                                    || InterfaceStaticArp.MacAddress || ' ' 
                                                                                    || InterfaceStaticArp.Encapsulation END AS StaticArp
                FROM
                    Interfaces
                    
                LEFT JOIN InterfaceStaticArp ON Interfaces.ID = InterfaceStaticArp.Interfaces_FK
                
                WHERE Interfaces.InterfaceName = ?;
                ''', (interface_name,))

            result_list = []
            rows = cursor.fetchall()

            for row in rows:
                result_list.append(
                    Result(status=STATUS_OK, row_id=None, result={'StaticArp': row[0]}))

            return result_list

        except sqlite3.Error as e:
            error_message = f"Error selecting interface static ARP entries: {e}"
            self.log.error(error_message)
            return [Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)]

    def select_interface_wifi_configuration(self, interface_name: InterfaceName) -> list[Result]:
        """
        Select distinct wireless wifi policy entries for a given interface.

        Args:
            interface_name (str): The name of the interface.

        Returns:
            list[Result]: A list of Result objects containing the wireless wifi policy names.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT DISTINCT
                    'wireless wifi policy ' || WirelessWifiPolicy.WifiPolicyName AS WifiPolicyName
                FROM
                    Interfaces
                JOIN
                    WirelessWifiPolicyInterface ON Interfaces.ID = WirelessWifiPolicyInterface.Interfaces_FK
                JOIN
                    WirelessWifiPolicy ON WirelessWifiPolicyInterface.WirelessWifiPolicy_FK = WirelessWifiPolicy.ID
                WHERE
                    Interfaces.InterfaceName = ?;
                ''', (interface_name,))

            result_list = []
            rows = cursor.fetchall()

            for row in rows:
                result_list.append(
                    Result(status=STATUS_OK, row_id=None, result={'WifiPolicyName': row[0]}))

            return result_list

        except sqlite3.Error as e:
            error_message = f"Error selecting interface wifi-policy entries: {e}"
            self.log.error(error_message)
            return [Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)]

    '''
                            ROUTER-CONFIGURATION-GLOBAL
    '''

    def select_global_interface_rename_configuration(self) -> list[Result]:
        """
        Retrieve data from the 'RenameInterface' table and format it into a list of Result objects.

        Returns:
            list[Result]: A list of Result objects containing data from the 'RenameInterface' table.
        """
        query = '''
            SELECT DISTINCT
                'rename if ' || RenameInterface.InitialInterface || ' if-alias ' || RenameInterface.AliasInterface AS RenameInterfaceConfig
            FROM
                RenameInterface
        '''

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)

            rows = cursor.fetchall()

            result_list = [Result(status=STATUS_OK, row_id=None, result={
                                  'RenameInterfaceConfig': row[0]}) for row in rows]

            return result_list

        except sqlite3.Error as e:
            error_message = f"Error retrieving data from 'RenameInterface': {e}"
            self.log.error(error_message)

            return [Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)]

    def select_global_bridge_configuration(self) -> list[Result]:
        """
        Retrieve bridge configuration data from the 'Bridges' table.

        Returns:
            list[Result]: A list of Result objects containing bridge configuration data.
        """
        query = '''
            SELECT DISTINCT
                'bridge '           || Bridges.BridgeName AS BridgeName,
                'description '      || Interfaces.Description AS Description,
                'inet management '  || InterfaceIpAddress.IpAddress AS InetMgt,
                'protocol '         || Bridges.Protocol AS Protocol,    
                CASE WHEN Bridges.StpStatus = 1 THEN 'stp enable' ELSE 'stp disable' END AS StpStatus,
                CASE WHEN Interfaces.ShutdownStatus THEN 'shutdown' ELSE 'no shutdown' END AS Shutdown
            FROM
                Bridges
            LEFT JOIN
                Interfaces ON Bridges.Interfaces_FK = Interfaces.ID
            LEFT JOIN
                InterfaceIpAddress ON Interfaces.ID = InterfaceIpAddress.Interfaces_FK;
        '''

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)

            # Fetch all rows from the result set
            rows = cursor.fetchall()

            result_list = [
                Result(status=STATUS_OK, row_id=None,
                       result={
                           'BridgeName': row[0],
                           'Description': row[1],
                           'InetMgt': row[2],
                           'Protocol': row[3],
                           'StpStatus': row[4],
                           'Shutdown': row[5]
                       }
                       ) for row in rows
            ]

            return result_list

        except sqlite3.Error as e:
            error_message = f"Error retrieving data from 'Bridges': {e}"
            self.log.error(error_message)

            return [Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)]

    def select_global_vlan_configuration(self) -> list[Result]:
        """
        Retrieve VLAN configuration data from the 'Vlans' table.

        Returns:
            list[Result]: A list of Result objects containing VLAN configuration data.
        """
        query = '''
            SELECT DISTINCT
                'vlan '         || Vlans.VlanID AS VlanID,
                'description '  || Vlans.VlanDescription AS VlanDescription,
                'name '         || Vlans.VlanName AS VlanName
            FROM
                Vlans;
        '''

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)

            rows = cursor.fetchall()

            result_list = [
                Result(status=STATUS_OK, row_id=None,
                       result={
                           'VlanID': row[0],
                           'VlanDescription': row[1],
                           'VlanName': row[2],
                       }
                       ) for row in rows
            ]

            return result_list

        except sqlite3.Error as e:
            error_message = f"Error retrieving data from 'Vlans': {e}"
            self.log.error(error_message)

            return [Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)]

    def select_global_nat_configuration(self) -> list[Result]:
        """
        Select distinct NAT pool names from the 'Nats' table.

        Returns:
        list[Result]: A list of Result objects with the selected NAT pool names.
        """
        self.log.debug("select_global_nat_configuration()")

        try:
            cursor = self.connection.cursor()

            cursor.execute(
                "SELECT DISTINCT 'ip nat ' || NatPoolName AS IpNatPoolName FROM Nats")

            rows = cursor.fetchall()

            result_list = [Result(status=STATUS_OK, row_id=None, result={
                                  'IpNatPoolName': row[0]}) for row in rows]

            self.log.debug(
                f"Selected global NAT configurations: {result_list}")

            return result_list

        except sqlite3.Error as e:
            error_message = f"Error selecting global NAT configurations: {e}"
            self.log.error(error_message)
            return [Result(STATUS_NOK, reason=error_message)]

    def select_global_dhcp_server_configuration(self) -> list[Result]:
        """
        Retrieve a list of global DHCP server configurations.

        Returns:
            list[Result]: A list of Result objects, each representing a row from the DHCPServer and DHCPSubnet tables.

        Note:
        - This method assumes that the necessary tables (DHCPServer, DHCPSubnet) exist with the specified schema.
        """
        try:

            query = """
                SELECT DISTINCT
                    'dhcp pool-name '   || DHCPServer.DhcpPoolname AS DhcpServerPollName,
                    'subnet '           || DHCPSubnet.InetSubnet AS DHCPSubnetSubnet
                FROM DHCPServer
                LEFT JOIN DHCPSubnet ON DHCPServer.ID = DHCPSubnet.DHCPServer_FK;
            """
            cursor = self.connection.cursor()
            cursor.execute(query)

            rows = cursor.fetchall()

            results = [
                Result(
                    status=STATUS_OK,
                    row_id=0,
                    reason=f"Retrieved global DHCP server configuration for pool '{row[0]}' and subnet '{row[1]}' successfully",
                    result={
                        "DhcpServerPoolName": row[0],
                        "DHCPSubnetSubnet": row[1],
                    },
                )
                for row in rows
            ]

            return results

        except sqlite3.Error as e:
            error_message = f"Failed to retrieve global DHCP server configurations. Error: {str(e)}"
            self.log.error(error_message)
            return [Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)]

    def select_global_dhcp_server_pool(self, dhcp_pool_name: DhcpPoolName) -> list[Result]:
        """
        Retrieve a list of global DHCP server pool IP address configurations.

        Args:
            dhcp_pool_name (str): The name of the DHCP server pool.

        Returns:
            list[Result]: A list of Result objects, each representing a row from the DHCPSubnetPools table.

        Note:
        - This method assumes that the necessary tables (DHCPServer, DHCPSubnet, DHCPSubnetPools) exist with the specified schema.
        """
        try:

            query = """
                SELECT DISTINCT
                    'pool ' || DHCPSubnetPools.InetAddressStart || ' ' || DHCPSubnetPools.InetAddressEnd || ' ' || DHCPSubnetPools.InetSubnet AS DhcpServerIpAddrPool
                
                FROM DHCPServer
                
                LEFT JOIN DHCPSubnet ON DHCPServer.ID = DHCPSubnet.DHCPServer_FK
                LEFT JOIN DHCPSubnetPools ON DHCPSubnet.ID = DHCPSubnetPools.DHCPSubnet_FK
                
                WHERE DHCPServer.DhcpPoolname = ?;
            """
            cursor = self.connection.cursor()
            cursor.execute(query, (dhcp_pool_name,))

            rows = cursor.fetchall()

            results = [
                Result(
                    status=STATUS_OK,
                    row_id=0,
                    reason=f"Retrieved global DHCP server pool IP address configuration for pool '{dhcp_pool_name}' successfully",
                    result={"DhcpServerIpAddrPool": row[0]},
                )
                for row in rows
            ]

            return results

        except sqlite3.Error as e:
            error_message = f"Failed to retrieve global DHCP server pool IP address configurations. Error: {str(e)}"
            self.log.error(error_message)
            return [Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)]

    def select_global_dhcp_server_reservation_pool(self, dhcp_pool_name: DhcpPoolName) -> list[Result]:
        """
        Retrieve a list of global DHCP server reservation pool configurations.

        Args:
            dhcp_pool_name (str): The name of the DHCP server pool.

        Returns:
            list[Result]: A list of Result objects, each representing a row from the DHCPSubnetReservations table.

        Note:
        - This method assumes that the necessary tables (DHCPServer, DHCPSubnet, DHCPSubnetReservations) exist with the specified schema.
        """
        try:
            query = """
                SELECT DISTINCT
                    'reservations ' || 'hw-address ' || DHCPSubnetReservations.MacAddress || ' ip-address ' || DHCPSubnetReservations.InetAddress AS DhcpServerReservationPool
                
                FROM DHCPServer
                
                LEFT JOIN DHCPSubnet ON DHCPServer.ID = DHCPSubnet.DHCPServer_FK
                LEFT JOIN DHCPSubnetReservations ON DHCPSubnet.ID = DHCPSubnetReservations.DHCPSubnet_FK
                
                WHERE DHCPServer.DhcpPoolname = ?;
            """
            cursor = self.connection.cursor()
            cursor.execute(query, (dhcp_pool_name,))

            rows = cursor.fetchall()

            results = [
                Result(
                    status=STATUS_OK,
                    row_id=0,
                    reason=f"Retrieved global DHCP server reservation pool configuration for pool '{dhcp_pool_name}' successfully",
                    result={"DhcpServerReservationPool": row[0]},
                )
                for row in rows
            ]

            return results

        except sqlite3.Error as e:
            error_message = f"Failed to retrieve global DHCP server reservation pool configurations. Error: {str(e)}"
            self.log.error(error_message)
            return [Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)]

    def select_global_dhcp_server_subnet_option_pool(self, dhcp_pool_name: DhcpPoolName) -> list[Result]:
        """
        Retrieve a list of global DHCP server subnet option pool configurations.

        Args:
            dhcp_pool_name (str): The name of the DHCP server pool.

        Returns:
            list[Result]: A list of Result objects, each representing a row from the DHCPOptions table.

        Note:
        - This method assumes that the necessary tables (DHCPServer, DHCPSubnet, DHCPSubnetPools, DHCPOptions) exist with the specified schema.
        """
        try:
            query = """
                SELECT DISTINCT
                    'option ' || DHCPOptions.DhcpOption || ' ' || DHCPOptions.DhcpValue AS DhcpServerOptionPool
                
                FROM DHCPServer
                
                LEFT JOIN DHCPSubnet ON DHCPServer.ID = DHCPSubnet.DHCPServer_FK
                LEFT JOIN DHCPSubnetPools ON DHCPServer.ID = DHCPSubnetPools.DHCPSubnet_FK
                LEFT JOIN DHCPOptions ON DHCPSubnetPools.ID = DHCPOptions.DHCPSubnetPools_FK
                
                WHERE DHCPServer.DhcpPoolname = ?;
            """
            cursor = self.connection.cursor()
            cursor.execute(query, (dhcp_pool_name,))

            rows = cursor.fetchall()

            results = [
                Result(
                    status=STATUS_OK,
                    row_id=0,
                    reason=f"Retrieved global DHCP server subnet option pool configuration for pool '{dhcp_pool_name}' successfully",
                    result={"DhcpServerOptionPool": row[0]},
                )
                for row in rows
            ]

            return results

        except sqlite3.Error as e:
            error_message = f"Failed to retrieve global DHCP server subnet option pool configurations. Error: {str(e)}"
            self.log.error(error_message)
            return [Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)]

    def select_global_dhcpv6_server_options(self, dhcp_pool_name: DhcpPoolName) -> list[Result]:
        """
        Retrieve DHCP Server Options for a specified DHCP pool name.

        Parameters:
            dhcp_pool_name (str): The name of the DHCP pool for which to retrieve options.

        Returns:
            list[Result]: A list of Result objects representing the outcomes of the operation.
        """
        try:
            query = """
                SELECT DISTINCT
                    'mode ' || DHCPv6ServerOption.Mode AS Mode,
                    'constructor ' || DHCPv6ServerOption.Constructor AS Constructor
                    
                FROM DHCPServer
                
                LEFT JOIN DHCPSubnet ON DHCPServer.ID = DHCPSubnet.DHCPServer_FK
                LEFT JOIN DHCPVersionServerOptions ON DHCPSubnet.ID = DHCPVersionServerOptions.DHCPSubnet_FK
                LEFT JOIN DHCPv6ServerOption ON DHCPVersionServerOptions.ID = DHCPv6ServerOption.DHCPVersionServerOptions_FK
                
                WHERE DHCPServer.DhcpPoolname = ?;
            """
            cursor = self.connection.cursor()
            cursor.execute(query, (dhcp_pool_name,))

            rows = cursor.fetchall()

            results = [
                Result(
                    status=STATUS_OK,
                    row_id=0,
                    reason=f"Retrieved global DHCPv6 server subnet option pool configuration for pool '{dhcp_pool_name}' successfully",
                    result={'Mode': row[0],
                            'Constructor': row[1],
                            },
                )
                for row in rows
            ]

            return results

        except sqlite3.Error as e:
            error_message = f"Failed to retrieve global DHCPv6 server subnet option pool configurations. Error: {str(e)}"
            self.log.error(error_message)
            return [Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)]

    def select_global_wireless_wifi_policy(self, wifi_policy_name: WifiPolicyName) -> Result:
        """
        Selects global wireless WiFi policy based on the provided WifiPolicyName.

        Parameters:
        - wifi_policy_name (str): The WifiPolicyName to search for.

        Returns:
        - Result: A dictionary containing the selected wireless WiFi policy information.

        Example:
        ```
        result = db_instance.select_global_wireless_wifi_policy("example_policy")

        if result.status:
            print(f"Successfully retrieved WiFi policy: {result.result}")
        else:
            print(f"Failed to retrieve WiFi policy. Reason: {result.reason}")
        ```

        Note:
        - 'status' attribute should be set to True for successful operations (STATUS_OK) and False for failed ones (STATUS_NOK).
        - 'row_id' represents the unique identifier of the affected row. Set to None for STATUS_OK or 0 for STATUS_NOK.
        - 'reason' provides additional information about the operation, which is particularly useful for error messages.
        - 'result' is a dictionary containing the selected wireless WiFi policy information.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT DISTINCT
                    'wireless wifi '    || WirelessWifiPolicy.WifiPolicyName AS WifiPolicyName,
                    'channel '          || WirelessWifiPolicy.Channel AS Channel,
                    'mode '             || WirelessWifiPolicy.HardwareMode AS HardwareMode
                FROM WirelessWifiPolicy
                                
                WHERE WirelessWifiPolicy.WifiPolicyName = ?;
                ''', (wifi_policy_name,))

            result = cursor.fetchone()

            if result is not None:
                sql_result_dict = {
                    'WifiPolicyName': result[0],
                    'Channel': result[1],
                    'HardwareMode': result[2],
                }
                return Result(status=STATUS_OK, row_id=None, result=sql_result_dict)
            else:
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"WifiPolicyName {wifi_policy_name} not found.")

        except sqlite3.Error as e:
            error_message = f"Error selecting WifiPolicyName information: {e}"
            self.log.error(error_message)
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)

    def select_global_wireless_wifi_security_policy(self, wifi_policy_name: WifiPolicyName) -> list[Result]:
        """
        Selects global wireless WiFi security policy based on the provided WifiPolicyName.

        Parameters:
        - wifi_policy_name (str): The WifiPolicyName to search for.

        Returns:
        - list[Result]: A list of dictionaries containing selected wireless WiFi security policy information.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT DISTINCT
                    'ssid '         || wws.Ssid AS Ssid,
                    'pass-phrase '  || wws.WpaPassPhrase AS WpaPassPhrase,
                    'wpa-mode '     || wws.WpaVersion AS WpaVersion
                
                FROM WirelessWifiPolicy wwp
                
                LEFT JOIN WirelessWifiSecurityPolicy wws ON wwp.ID = wws.WirelessWifiPolicy_FK
                
                WHERE wwp.WifiPolicyName = ?;
                ''', (wifi_policy_name,))

            results = cursor.fetchall()

            if results:
                # Create a list of dictionaries for each result
                result_list: list[Result] = [
                    {
                        'Ssid': result[0],
                        'WpaPassPhrase': result[1],
                        'WpaVersion': result[2],
                    }
                    for result in results
                ]
                return result_list
            else:
                return [Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=f"WifiPolicyName {wifi_policy_name} not found.")]

        except sqlite3.Error as e:
            error_message = f"Error selecting WifiPolicyName information: {e}"
            self.log.error(error_message)
            return [Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=error_message)]

    def select_global_telnet_server(self) -> Result:
        """
        Select the status and port of the Telnet server from the TelnetServer table,
        linked through the SystemConfiguration table.

        Returns:
            Result: A Result object indicating the operation's success or failure, 
                    the Telnet server status, and port.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT ts.Enable, ts.Port
                FROM TelnetServer ts
                JOIN SystemConfiguration sc ON sc.TelnetServer_FK = ts.ID
                WHERE sc.ID = 1
            """)
            result = cursor.fetchone()

            if not result:
                return Result(status=STATUS_NOK,
                              row_id=self.ROW_ID_NOT_FOUND,
                              reason="No entry found in 'TelnetServer' or 'SystemConfiguration' tables.")

            enable, port = result

            return Result(status=STATUS_OK, row_id=1, result={'Enable': enable, 'Port': port})

        except sqlite3.Error as e:
            self.log.error(
                "Error selecting Telnet server status and port: %s", e)
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=str(e), result=None)

    def update_global_telnet_server(self, enable: bool, port: int) -> Result:
        """
        Update the existing Telnet server configuration in the TelnetServer table
        and ensure the SystemConfiguration table's foreign key reference is maintained.

        Args:
            enable (bool): The status of the Telnet server.
            port (int): The port of the Telnet server.

        Returns:
            Result: A Result object indicating the operation's success or failure,
                    including the updated values of the Telnet server configuration.
        """
        self.log.debug(
            f'update_global_telnet_server() -> Enable: {enable} -> Port: {port}')
        try:
            cursor = self.connection.cursor()

            # Check if TelnetServer entry exists
            cursor.execute(
                "SELECT TelnetServer_FK FROM SystemConfiguration WHERE ID = 1")
            result = cursor.fetchone()

            if not result:
                self.log.error(
                    'update_global_telnet_server() -> TelnetServer_FK: No FK Key found')
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason="No entry found in 'SystemConfiguration' table for ID 1.")

            telnet_server_id = result[0]

            if telnet_server_id is None:
                self.log.error(
                    'update_global_telnet_server() -> No TelnetServer linked in SystemConfiguration table.')
                return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason="No TelnetServer linked in 'SystemConfiguration' table.")

            # Update the Telnet server configuration
            cursor.execute("""
                UPDATE TelnetServer SET Enable = ?, Port = ? WHERE ID = ?
            """, (enable, port, telnet_server_id))

            self.connection.commit()

            return Result(status=STATUS_OK, row_id=telnet_server_id, result={'Enable': enable, 'Port': port})

        except sqlite3.Error as e:
            self.connection.rollback()
            self.log.error("Error updating Telnet server configuration: %s", e)
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=str(e), result=None)

    def insert_global_telnet_server(self, telnet_status: bool) -> Result:
        """
        Insert or update the Telnet server status in the SystemConfiguration table.

        Args:
            telnet_status (bool): The status of the Telnet server to insert or update.

        Returns:
            Result: A Result object indicating the operation's success or failure.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                    INSERT INTO SystemConfiguration (ID, TelnetServer)
                    VALUES (1, ?)
                    ON CONFLICT(ID) DO UPDATE SET TelnetServer=excluded.TelnetServer;
                """, (telnet_status,))
            self.connection.commit()
            cursor.close()

            return Result(status=STATUS_OK, row_id=1, result={'TelnetServerStatus': telnet_status})

        except sqlite3.Error as e:
            self.log.error("Error inserting Telnet server status: %s", e)
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=str(e), result=None)

    def select_global_ssh_server(self) -> Result:
        """
        Select the status and port of the Secure Shell (SSH) server from the SshServer table,
        linked through the SystemConfiguration table.

        Returns:
            Result: A Result object indicating the operation's success or failure, 
                    the SSH server status, and port.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT ssh.Enable, ssh.Port
                FROM SshServer ssh
                JOIN SystemConfiguration sc ON sc.SshServer_FK = ssh.ID
                WHERE sc.ID = 1
            """)
            result = cursor.fetchone()

            if not result:
                return Result(status=STATUS_NOK,
                              row_id=self.ROW_ID_NOT_FOUND,
                              reason="No entry found in 'SshServer' or 'SystemConfiguration' tables.")

            enable, port = result

            return Result(status=STATUS_OK, row_id=1, result={'Enable': enable, 'Port': port})

        except sqlite3.Error as e:
            self.log.error("Error selecting SSH server status and port: %s", e)
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=str(e), result=None)

    def insert_global_Ssh_server(self, ssh_status: bool) -> Result:
        """
        Insert or update the SSH server status in the SystemConfiguration table.

        Args:
            ssh_status (bool): The status of the SSH server to insert or update.

        Returns:
            Result: A Result object indicating the operation's success or failure.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                    INSERT INTO SystemConfiguration (ID, SshServer)
                    VALUES (1, ?)
                    ON CONFLICT(ID) DO UPDATE SET SshServer=excluded.SshServer;
                """, (ssh_status,))
            self.connection.commit()
            cursor.close()

            return Result(status=STATUS_OK, row_id=1, result={'SshServerStatus': ssh_status})

        except sqlite3.Error as e:
            self.log.error("Error inserting SSH server status: %s", e)
            return Result(status=STATUS_NOK, row_id=self.ROW_ID_NOT_FOUND, reason=str(e), result=None)

# FILE: src/routershell/lib/db/system_db.py
import logging

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK, Status
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import HostnameText
from routershell.lib.db.sqlite_db.router_shell_db import RouterShellDB as DB


class SystemDatabase:

    rsdb = DB()
    
    def __init__(cls):
        cls.log = logging.getLogger(cls.__class__.__name__)
        cls.log.setLevel(RSLS().SYSTEM_DB)
        
        if not cls.rsdb:
            cls.log.debug("Connecting RouterShell Database")
            cls.rsdb = DB()
    
    def set_hostname_db(cls, host_name: HostnameText) -> bool:
        """
        Sets the hostname in the system database.

        Updates the hostname in the database with the provided hostname.

        Args:
            host_name (str): The new hostname to set.

        Returns:
            bool: STATUS_OK if the hostname is successfully updated, STATUS_NOK otherwise.
        """
        return cls.rsdb.update_hostname(host_name).status
    
    def get_hostname_db(cls) -> str:
        """
        Retrieves the hostname from the system database.

        Fetches the current hostname from the database.

        Returns:
            str: The current hostname, else None.
        """
        result = cls.rsdb.select_hostname()
        if result.status == STATUS_OK and result.result:
            return result.result.get('Hostname')
        return None

    def set_banner_motd(cls, motd_banner:str) -> bool:
        """
        Set the banner Message of the Day (Motd) in the RouterShell configuration.

        Args:
            cls: The RouterShellDB class.
            motd_banner (str): The new banner text.

        Returns:
            bool: STATUS_OK if the banner is successfully set, STATUS_NOK otherwise.
        """        
        return cls.rsdb.update_banner_motd(motd_banner).status
    
    def get_banner_motd(cls) -> tuple[bool, str]:
        """
        Retrieve the banner Message of the Day (Motd) from the RouterShell configuration.

        Args:
            cls: The RouterShellDB class

        Returns:
            tuple[bool, str]: A tuple containing the status (STATUS_OK | STATUS_NOK) of the operation and the formatted banner text with lines
        """
        result = cls.rsdb.select_banner_motd()

        return result.status, result.result.get('BannerMotd')

    def get_telnet_server_status(cls) -> tuple[bool, dict]:
        """
        Retrieve the Telnet server status and port from the database.

        Returns:
            tuple[bool, dict]: A tuple containing a boolean indicating the success of the operation and a dictionary.
                            The dictionary contains the Telnet server status ('Enable') and port ('Port') if the 
                            operation is successful. If the operation fails, the boolean is STATUS_NOK and the dictionary is empty.
        """
        try:
            result = cls.rsdb.select_global_telnet_server()
            if result.status:
                cls.log.error(f"Failed to retrieve Telnet server status: {result.reason}")
                return STATUS_NOK, {}
            
            return STATUS_OK, result.result
        
        except Exception as e:
            cls.log.error(f"Unexpected error while retrieving Telnet server status: {e}")
            return STATUS_NOK, {}

    def set_telnet_server_status(cls, telnet_server_status: bool, port: int) -> bool:
        """
        Sets the status of the Telnet server and updates the port configuration.

        Parameters:
        telnet_server_status (bool): The desired status of the Telnet server (True to enable, False to disable).
        port (int): The port number for the Telnet server.

        Returns:
        bool: The status indicating whether the update was successful.
        """
        result = cls.rsdb.update_global_telnet_server(telnet_server_status, port)
        return result.status

    def get_ssh_server_status(cls) -> tuple[bool, dict]:
        """
        Retrieve the SSH server status and port from the database.

        Returns:
            tuple[bool, dict]: A tuple containing a boolean indicating the success of the operation 
                               and a dictionary. The dictionary contains the SSH server status ('Enable') 
                               and port ('Port') if the operation is successful. If the operation fails, 
                               the boolean is STATUS_NOK and the dictionary is empty.
        """
        try:
            result = cls.rsdb.select_global_ssh_server()
            if result.status:
                cls.log.error(f"Failed to retrieve SSH server status: {result.reason}")
                return STATUS_NOK, {}
            
            return STATUS_OK, result.result
        
        except Exception as e:
            cls.log.error(f"Unexpected error while retrieving SSH server status: {e}")
            return STATUS_NOK, {}

    def set_ssh_server_status(cls, ssh_server_status: Status) -> bool:
        """
        Set the status of the SSH server.

        Args:
            ssh_server_status (Status): The desired status of the SSH server (ENABLE or DISABLE).

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        tss = ssh_server_status == Status.ENABLE
        return cls.rsdb.insert_global_ssh_server(tss).status
              

# FILE: src/routershell/lib/db/vlan_db.py
import logging

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import InterfaceName, VlanName
from routershell.lib.db.sqlite_db.router_shell_db import Result
from routershell.lib.db.sqlite_db.router_shell_db import RouterShellDB as DB
from routershell.lib.network_manager.common.interface import InterfaceType


class VlanDatabase:
    
    rsdb = DB()
    
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().VLAN_DB)   
    
    def add_vlan_id(self, vlan_id: int) -> bool:
        """
        Add a VLAN ID to the database using the rsdb method.

        Args:
            vlan_id (int): The VLAN ID to be added.

        Returns:
            bool: STATUS_OK if the VLAN ID was successfully added or already exists,
                  STATUS_NOK if there was an error adding the VLAN ID.
        """
        
        if not self.rsdb.vlan_id_exists(vlan_id).status:
            self.log.debug(f'VlanID: {vlan_id}, does not exists, adding Vlan to DB')
            return self.rsdb.insert_vlan_id(vlan_id).status
        
        self.log.debug(f'VlanID: {vlan_id} already exisit, no need to add')
        
        return STATUS_OK

    def add_vlan(self, vlan_id: int, vlan_name: VlanName, description: str = None) -> Result:
        """
        Add a new VLAN to the database.

        Args:
            vlan_id (int): The unique ID of the VLAN.
            vlan_name (str): The name of the VLAN.
            description (str, optional): A description of the VLAN.

        Returns:
            Result: A Result object representing the outcome of the operation.
                - If the operation is successful, the Result object will have 'status' set to STATUS_OK
                  and 'row_id' containing the unique identifier of the inserted VLAN.
                - If there is an error or if the VLAN already exists, the Result object will have 'status' set to STATUS_NOK,
                  'row_id' set to None, and 'reason' providing additional information.
        """
        return self.rsdb.insert_vlan(vlan_id, vlan_name, description)

    def update_vlan_description(self, vlan_id: int, vlan_description: str) -> bool:
        """
        Update the description of a VLAN by its ID.

        Args:
            vlan_id (int): The unique ID of the VLAN.
            vlan_description (str): The new description for the VLAN.

        Returns:
            bool: True if the update is successful, False otherwise.

        Example:
        You can use the update_vlan_description class method to update the description of a VLAN.
        For example:
        ```
        success = YourClass.update_vlan_description(10, 'New VLAN Description')
        
        if success:
            print("VLAN description updated successfully.")
        else:
            print("Failed to update VLAN description.")
        ```
        """
        return self.rsdb.update_vlan_description_by_vlan_id(vlan_id, vlan_description).status

    def vlan_exists(self, vlan_id: int) -> bool:
        """
        Check if a VLAN with the given ID exists in the database.

        Args:
            self: The class reference.
            vlan_id (int): The unique ID of the VLAN to check.

        Returns:
            bool: True if a VLAN with the given ID exists, False otherwise.
        """
        return self.rsdb.vlan_id_exists(vlan_id).status

    def get_vlan_name_by_vlan_id(self, vlan_id: int) -> Result:
        """
        Get the name of a VLAN by its ID.

        Args:
            vlan_id (int): The unique ID of the VLAN.

        Returns:
            Result: A Result object representing the outcome of the operation.
            - If the operation is successful, the Result object will have 'status' set to STATUS_OK,
                  'row_id' set to the unique identifier of the VLAN, and 'result' containing the VLAN name.
            - If there is an error or if the VLAN with the provided ID does not exist, the Result object will have
                  'status' set to STATUS_NOK, 'row_id' set to None, and 'reason' providing additional information.

        """
        return self.rsdb.select_vlan_name_by_vlan_id(vlan_id)

    def update_vlan_name_via_vlanID(self, vlan_id: int, vlan_name: VlanName) -> Result:
        """
        Update the name of a VLAN by its ID.

        Args:
            self: The class reference.
            vlan_id (int): The unique ID of the VLAN to update.
          self  vlan_name (str): The new name for the VLAN.

        Returns:
            bool: (STATUS_OK) if the update is successful, (STATUS_NOK) if it fails.
        """        
        return self.rsdb.update_vlan_name_by_vlan_id(vlan_id, vlan_name)

    def delete_interface_from_vlan(self, vlan_id: int, port_to_delete: int):
        # Delete an interface (port) from a VLAN
        vlan_interface_id = self.get_vlan_interface_id(vlan_id)
        if vlan_interface_id:
            self.delete_vlan_interface_mapping(vlan_interface_id, port_to_delete)

    def add_interface_to_vlan(self, vlan_id: int, interface_name: InterfaceName) -> bool:
        """
        Add a VLAN to a specific interface type in the database.

        Args:
            vlan_id (int): The unique identifier of the VLAN.
            interface_name (str): The name of the interface or bridge group.

        Returns:
            bool: STATUS_OK if the VLAN was successfully added to the specified interface type, STATUS_NOK otherwise.
        """
        
        interface_type = self.rsdb.select_interface_type(interface_name)
        
        self.log.debug(f"add_vlan_to_interface_type({vlan_id} -> {interface_name}) -> Interface-Type: {interface_type}")
        
        try:
            if interface_type == InterfaceType.BRIDGE:
                result = self.rsdb.insert_vlan_interface(vlan_id, bridge_group_name=interface_name)
            
            else:
                result = self.rsdb.insert_vlan_interface(vlan_id, interface_name=interface_name)

            return result.status

        except Exception as e:
            self.log.error("add_vlan_to_interface_type() -> Error adding VLAN to interface type: %s", e)
            return STATUS_NOK

    def get_vlan_id_from_vlan_name(self, vlan_name: VlanName) -> int:
        """
        Retrieves the VLAN ID associated with a given VLAN name.

        Args:
            vlan_name (str): The name of the VLAN.

        Returns:
            int: The VLAN ID if found, otherwise returns Vlan.INVALID_VLAN_ID.

        """
        from routershell.lib.network_manager.network_operations.vlan import Vlan
        result = self.rsdb.select_vlan_id_by_vlan_name(vlan_name)

        if result.status == STATUS_OK and result.result:
            return result.result.get('VlanID', Vlan.INVALID_VLAN_ID)
        else:
            self.log.debug(f"Unable to retrieve VLAN ID for VLAN name: {vlan_name}")
            return Vlan.INVALID_VLAN_ID

    def get_interfaces_from_vlan_id(self, vlan_id: int) -> list[str]:
        """
        Retrieves a list of interfaces associated with a given VLAN ID.
        """
        return []

# FILE: src/routershell/lib/db/wifi_db.py
import logging

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import InterfaceName, SsidText, WifiPassphraseText, WifiPolicyName
from routershell.lib.db.sqlite_db.router_shell_db import Result
from routershell.lib.db.sqlite_db.router_shell_db import RouterShellDB as DB


class WifiPolicyNotFoundError(Exception):
    """
    Exception raised when a Wi-Fi policy is not found.
    """

    def __init__(self, message="Wi-Fi policy not found."):
        self.message = message
        super().__init__(self.message)


class WifiDB:
    
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().WIFI_DB)
            
    def wifi_policy_exist(self, wifi_policy_name: WifiPolicyName) -> bool:
        """
        Check if a wireless Wi-Fi policy with the given name exists in the database.

        Args:
        wifi_policy_name (str): The name of the wireless Wi-Fi policy to check for existence.

        Returns:
        bool: True if the policy exists, False if it doesn't.

        Note:
        - This method checks the database for the existence of a wireless Wi-Fi policy with the provided name.
        - It returns True if the policy exists, and False if it doesn't.

        """
        return DB().wifi_policy_exist(wifi_policy_name).status

    def add_wifi_policy(self, wifi_policy_name: WifiPolicyName) -> bool:
        """
        Insert a new wireless Wi-Fi policy into the database.

        Args:
        wifi_policy_name (str): The name of the wireless Wi-Fi policy to insert.

        Returns:
        bool: True if the insertion is successful, False if it fails.

        Note:
        - This method inserts a new wireless Wi-Fi policy with the provided name into the database.
        - It returns STATUS_Ok if the insertion is successful, and STATUS_NOK if it fails.

        """
        
        sql_result = DB().insert_wifi_policy(wifi_policy_name)
        
        if sql_result.status:
            self.log.error(f"Unable to add wifi-policy: {wifi_policy_name} -> Reason: {sql_result.reason}")
            return STATUS_NOK
                
        return STATUS_OK 

    def add_wifi_security_access_group(self, wifi_policy_name: WifiPolicyName, ssid: SsidText, pass_phrase: WifiPassphraseText, mode: str) -> bool:
        """
        Insert a new Wi-Fi security group into the database associated with a wireless Wi-Fi policy.

        Args:
        wifi_policy_name (str): The name of the wireless Wi-Fi policy to associate the security group with.
        ssid (str): The SSID (Service Set Identifier) for the security group.
        pass_phrase (str): The security passphrase or key for the security group.
        mode (str): The security mode for the security group (e.g., WPA2, WPA3).

        Returns:
        bool: True if the security group is successfully inserted, False if the insertion fails.

        Note:
        - This method inserts a new Wi-Fi security group associated with the specified wireless Wi-Fi policy.
        - It returns True if the insertion is successful, and False if there is an error or the insertion fails.

        """
        self.log.debug(f"{wifi_policy_name}, {ssid}, {pass_phrase}, {mode}")
        return DB().insert_wifi_access_security_group(wifi_policy_name, ssid, pass_phrase, mode).status

    def add_wifi_security_access_group_default(self, wifi_policy_name: WifiPolicyName) -> bool:
        """
        Add a default Wi-Fi security access group to the specified wireless Wi-Fi policy.

        Args:
            wifi_policy_name (str): The name of the wireless Wi-Fi policy to add the default security access group to.

        Returns:
            bool: True if the default Wi-Fi security access group is added successfully, False otherwise.

        Note:
        - This method adds a default Wi-Fi security access group to the specified wireless Wi-Fi policy.
        - The default Wi-Fi security access group typically includes pre-defined settings for SSID, WPA passphrase, and security mode.
        - Returns True if the default Wi-Fi security access group is added successfully, and False otherwise.
        """
        self.log.debug(f"Adding default Wi-Fi security access group to policy '{wifi_policy_name}'")
        return DB().insert_wifi_access_security_group_default(wifi_policy_name).status
  
    def add_wifi_key_management(self, wifi_policy_name:WifiPolicyName, key_management:str) -> bool:
        return STATUS_OK

    def add_wifi_hardware_mode(self, wifi_policy_name:WifiPolicyName, hardware_mode: str) -> bool:
        """
        Add/update a hardware mode to a wireless Wi-Fi policy.

        Args:
            - wifi_policy_name (str): The name of the wireless Wi-Fi policy.
            - hardware_mode (str): The hardware mode to add.

        Returns:
            bool: True if the addition is successful, False if it fails.

        Raises:
            - Wi-FiPolicyNotFoundError: If the specified Wi-Fi policy is not found.
            - InvalidHardwareModeError: If the provided hardware mode is not valid.

        Note:
            - This method associates a hardware mode with the specified wireless Wi-Fi policy.
            - When a Wifi-policy name is create, a hardware-mode default of any is set
            - The hardware mode should be a valid mode from the HardwareMode enum.
            - If the Wi-Fi policy or hardware mode is not found, respective errors will be raised.
        """
        sql_result = DB().update_wifi_hardware_mode(wifi_policy_name, hardware_mode)
        if sql_result.status:
            self.log.error(f"Unable update wifi-hardware-mode: {hardware_mode} -> Reason: {sql_result.reason}")
            return STATUS_NOK
        
        return STATUS_OK

    def add_wifi_policy_to_wifi_interface(self, wifi_policy_name: WifiPolicyName, wifi_interface_name: InterfaceName) -> bool:
        """
        Add a wireless Wi-Fi policy to a Wi-Fi interface.

        Args:
            wifi_policy_name (str): The name of the wireless Wi-Fi policy to associate with the Wi-Fi interface.
            wifi_interface_name (str): The name of the Wi-Fi interface to which the policy should be added.

        Returns:
            bool: STATUS_OK if the association is successful, STATUS_NOK if it fails.

        Note:
            - If the Wi-Fi policy or Wi-Fi interface is not found, respective errors will be logged.
        """
        # Check if the Wi-Fi policy exists
        if not self.wifi_policy_exist(wifi_policy_name):
            self.log.error(f"Wi-Fi policy '{wifi_policy_name}' not found.")
            return STATUS_NOK

        # Check if the Wi-Fi interface exists
        if not DB().interface_exists(wifi_interface_name):
            self.log.error(f"Wi-Fi interface '{wifi_interface_name}' not found.")
            return STATUS_NOK

        # Associate the Wi-Fi policy with the Wi-Fi interface
        sql_result = DB().insert_wifi_policy_to_wifi_interface(wifi_policy_name, wifi_interface_name)

        if sql_result.status:
            self.log.error(f"Unable to associate wifi-policy '{wifi_policy_name}' with wifi-interface '{wifi_interface_name}' -> Reason: {sql_result.reason}")
            return STATUS_NOK

        return STATUS_OK

    def add_wifi_channel(self, wifi_policy_name: WifiPolicyName, channel: str) -> bool:
        """
        Add a Wi-Fi channel to a wireless Wi-Fi policy.

        Args:
        - wifi_policy_name (str): The name of the wireless Wi-Fi policy.
        - channel (str): The Wi-Fi channel to add.

        Returns:
        bool: STATUS_OK if the addition is successful, STATUS_NOK if it fails.

        Note:
        - This method associates a Wi-Fi channel with the specified wireless Wi-Fi policy.
        """
        return DB().insert_wifi_channel(wifi_policy_name, channel).status

    def get_wifi_security_policy(self, wifi_policy_name: WifiPolicyName) -> list[dict]:
        """
        Get a list of security policies associated with a specific Wi-Fi policy.

        Args:
            wifi_policy_name (str): The name of the Wi-Fi policy.

        Returns:
            list[dict]: A list of dictionaries containing security policy information.
        """
        return Result.sql_result_to_value_list(DB().select_wifi_security_policy(wifi_policy_name))

    def del_wifi_security_access_group(self, wifi_policy_name: WifiPolicyName, ssid: SsidText) -> bool:
        """
        Delete a Wi-Fi security access group with the specified SSID from the wireless Wi-Fi policy.

        Args:
            wifi_policy_name (str): The name of the wireless Wi-Fi policy from which to delete the security access group.
            ssid (str): The SSID (Service Set Identifier) of the Wi-Fi security access group to delete.

        Returns:
            bool: STATUS_OK if the Wi-Fi security access group is deleted successfully, STATUS_NOK otherwise.

        Note:
        - This method deletes a Wi-Fi security access group with the specified SSID from the wireless Wi-Fi policy.
        - Returns True if the deletion is successful, and False otherwise.
        """
        return DB().delete_wifi_ssid(wifi_policy_name, ssid).status


# FILE: src/routershell/lib/network_manager/common/inet.py
import ipaddress
import json
import logging
from enum import Enum

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import InetAddressText, InetCidrText, InterfaceName
from routershell.lib.network_manager.common.mac import MacServiceLayer
from routershell.lib.network_manager.common.run_commands import RunResult


class InetVersion(Enum):
    IPv4 = 4
    IPv6 = 6
    UNKNOWN = 0

class InetServiceLayer(MacServiceLayer):
    """
    A class for configuring network settings using iproute2.
    """
    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().INET)
                    
    def is_valid_ipv4(self, inet_address: InetAddressText) -> bool:
        """
        Check if an IPv4 address is valid.

        Args:
            inet_address (str): The IPv4 address as a string.

        Returns:
            bool: True if the address is valid, False otherwise.
        """
        
        self.log.debug(f"is_valid_ipv4() -> Inet Address: ({inet_address})")
        
        try:
            ipaddress.IPv4Address(inet_address)
            self.log.debug(f"is_valid_ipv4() -> Inet Address: ({inet_address}) is Good")
            return True
        except ipaddress.AddressValueError:
            self.log.error(f"is_valid_ipv4() -> Inet Address: ({inet_address}) is Bad")
            return False

    def is_secondary_address(self, interface, address):
        """
        Check if an IP address is a secondary address on the given interface.

        Args:
            interface (dict): The interface information in JSON format.
            address (str): The IP address to check.

        Returns:
            bool: True if the address is a secondary address, False otherwise.
        """
        for addr_info in interface["addr_info"]:
            if addr_info["family"] in ["inet", "inet6"] and addr_info["local"] == address:
                if "label" in addr_info and "secondary" in addr_info["label"]:
                    return True
        return False

    def get_ip_addr_info(self, interface_name: InterfaceName | None = None) -> list:
        """
        Get IP address information for network interfaces.

        Args:
            interface_name (str, optional): If provided, fetch IP information for the specified network interface.

        Returns:
            list: A list of dictionaries containing IP address information for network interfaces.
        """
        cmd = ["ip", "--json", "addr", "show"]
        if interface_name:
            cmd.extend(['dev', interface_name])

        ip_addr_raw_json = self.run(cmd)
        
        if ip_addr_raw_json.exit_code:
            self.log.error(f"Error getting ip address info: cmd -> {cmd} error: {ip_addr_raw_json.stderr}")
            return []
        
        try:
            ip_addr_json_obj = json.loads(ip_addr_raw_json.stdout)
            return ip_addr_json_obj
        
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
 
    def is_valid_ipv6(self, inet6_address: InetAddressText, include_prefix=True) -> bool:
        """
        Check if an IPv6 address is valid.

        Args:
            inet6_address (str): The IPv6 address as a string.

        Returns:
            bool: True if the address is valid, False otherwise.
        """
        try:
            parts = inet6_address.split('/')
            self.log.debug(f"is_valid_ipv6() -> inet6: ({parts}) -> include-prefix({include_prefix})")
            if len(parts) != 2:
                return False

            address, prefix_length = parts[0], int(parts[1])
            ipaddress.IPv6Network(address)
            return True
        except (ipaddress.AddressValueError, ValueError):
            return False

    def is_ip_assigned_to_interface(self, ip_address, interface) -> bool:
        """
        Check if an IP address is assigned to a specific network interface on a Linux system.

        Args:
            ip_address (str): The IP address to check.
            interface (str): The network interface to check.

        Returns:
            bool: True if the IP address is assigned to the interface, False otherwise.
        """
        command = ['ip', 'addr', 'show', interface]
        result = self.run(command)

        lines = result.stdout.split('\n')
        for line in lines:
            if ip_address in line:
                return True
        return False

    def is_valid_inet_address(self, ip_address: InetAddressText) -> bool:
        """
        Check if a string is a valid IP address.

        Args:
            ip_address (str): The IP address to validate.

        Returns:
            bool: True if the input is a valid IP address, False otherwise.
        """
        try:
            ip = ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False

    def set_ipv4_default_gateway(self, interface: InterfaceName, inet_address: InetAddressText) -> RunResult:
        """
        Set the default IPv4 gateway on an interface.

        Args:
            interface (str): The network interface.
            inet_address (str): The IPv4 gateway address as a string.

        Returns:
            str: Status code, either STATUS_OK or STATUS_NOK.
        """
        if not self.is_valid_ipv4(inet_address):
            logging.error(f"Invalid IPv4 gateway address: {inet_address}")
            return STATUS_NOK
        
        cmd = ["ip", "route", "add", "default", "via", inet_address, "dev", interface]
        return self.run(cmd)
     
    def set_ipv6_default_gateway(self, interface: InterfaceName, inet6_address: InetAddressText) -> RunResult:
        """
        Set the default IPv6 gateway on an interface.

        Args:
            interface (str): The network interface.
            inet6_address (str): The IPv6 gateway address as a string.

        Returns:
            str: Status code, either STATUS_OK or STATUS_NOK.
        """
        if not self.is_valid_ipv6(inet6_address):
            logging.error(f"Invalid IPv6 gateway address: {inet6_address}")
            return STATUS_NOK
        
        cmd = ["ip", "-6", "route", "add", "default", "via", inet6_address, "dev", interface]
        return self.run(cmd)

    def is_valid_network_interface(self, interface: InterfaceName) -> bool:
        """
        Check if a string is a valid network interface name.

        Args:
            interface (str): The network interface name.

        Returns:
            bool: True if the input is a valid network interface name, False otherwise.
        """
        # Add your network interface validation logic here
        return True  # Replace with actual validation logic

    def get_interface_ip_addresses(self, interface_name, ip_version=None) -> list:
        """
        Get IP addresses of a network interface using iproute2 --json option.

        Args:
            interface_name (str): The name of the network interface.
            ip_version (str, optional): IP version to filter (None for both IPv4 and IPv6,
                                        'ipv4' for IPv4 only, 'ipv6' for IPv6 only).

        Returns:
            list: list of IP addresses associated with the interface.
        """
        # Run the ip command with --json option
        output = self.run(['ip', '--json', 'addr', 'show', interface_name])
        
        if output.exit_code:
            self.log.error(f"Unable to obtain ip addresses from interface: {interface_name}")
            return []

        # Parse the JSON output
        ip_info = json.loads(output.stdout)

        # Extract IP addresses based on the specified IP version
        addresses = []
        for addr_info in ip_info[0]['addr_info']:
            ip_addr = addr_info['local']
            if ip_version is None or (ip_version == 'ipv4' and ':' not in ip_addr) or (ip_version == 'ipv6' and ':' in ip_addr):
                addresses.append(ip_addr)

        return addresses
    
    def set_inet_address_loopback(self, loopback_name: InterfaceName, inet_address_cidr: InetCidrText) -> bool:
        """
        Set an internet address (IPv4 or IPv6) on a loopback interface. 
        Appending to the local loopback (lo) interface 

        Args:
            loopback_name (str): The name of the loopback interface.
            inet_address_cidr (str): The CIDR notation of the IP address to assign.

        Returns:
            bool: STATUS_OK if the address was successfully set, STATUS_NOK otherwise.
        """
        self.log.debug(f"set_inet_address_loopback() - Loopback: {loopback_name} -> inet: {inet_address_cidr}")

        if not loopback_name:
            self.log.error("set_inet_address_loopback() -> Loopback not defined")
            return STATUS_NOK

        try:
            ip_interface = ipaddress.ip_interface(inet_address_cidr)
            ip_version = ip_interface.version
            
        except ValueError:
            self.log.error(f"set_inet_address_loopback() -> Invalid IP address: {inet_address_cidr}")
            return STATUS_NOK

        lo_name = f'lo:{loopback_name}'
        cmd = ['ip', 'addr', 'add', inet_address_cidr, 'label', lo_name, 'dev', 'lo']

        if ip_version == 6:
            cmd.insert(1, '-6')
            
        self.log.debug(f'set_inet_address_loopback() -> {cmd}')
        out = self.run(cmd)

        if out.exit_code:
            self.log.error(f"set_inet_address_loopback() -> Unable to set inet address: "
                           f"{inet_address_cidr} on loopback: {loopback_name}, Reason: {out.stderr}")
            return STATUS_NOK

        return STATUS_OK

    def del_inet_address_loopback(self, loopback_name: InterfaceName, inet_address_cidr: InetCidrText) -> bool:
        """
        Delete an internet address (IPv4 or IPv6) from a loopback interface.

        Args:
            loopback_name (str): The name of the loopback interface.
            inet_address_cidr (str): The CIDR notation of the IP address to remove.

        Returns:
            bool: STATUS_OK if the address was successfully removed, STATUS_NOK otherwise.
        """
        self.log.debug(f"del_inet_address_loopback() - Loopback: {loopback_name} -> inet: {inet_address_cidr}")

        if not loopback_name:
            self.log.error("del_inet_address_loopback() -> Loopback not defined")
            return STATUS_NOK

        try:
            ip_interface = ipaddress.ip_interface(inet_address_cidr)
            ip_version = ip_interface.version
            
        except ValueError:
            self.log.error(f"del_inet_address_loopback() -> Invalid IP address: {inet_address_cidr}")
            return STATUS_NOK

        lo_name = f'lo:{loopback_name}'
        cmd = ['ip', 'addr', 'del', inet_address_cidr, 'label', lo_name, 'dev', 'lo']

        if ip_version == 6:
            cmd.insert(1, '-6')

        self.log.info(f'del_inet_address_loopback() -> {cmd}')
        out = self.run(cmd)

        if out.exit_code:
            self.log.error(f"del_inet_address_loopback() -> Unable to delete inet address: "
                        f"{inet_address_cidr} from loopback: {loopback_name}, Reason: {out.stderr}")
            return STATUS_NOK

        return STATUS_OK
    
    def update_inet_address_loopback(self, loopback_name: InterfaceName, old_inet_address_cidr: InetCidrText, new_inet_address_cidr: InetCidrText) -> bool:
        """
        # TODO Need to test, not sure if this works
        
        Update (overwrite) an internet address (IPv4 or IPv6) on a loopback interface.

        Args:
            loopback_name (str): The name of the loopback interface.
            old_inet_address_cidr (str): The CIDR notation of the current IP address to be replaced.
            new_inet_address_cidr (str): The CIDR notation of the new IP address to assign.

        Returns:
            bool: STATUS_OK if the address was successfully updated, STATUS_NOK otherwise.
        """
        self.log.debug(f"update_inet_address_loopback() - Loopback: {loopback_name} -> "
                    f"Old Inet: {old_inet_address_cidr}, New Inet: {new_inet_address_cidr}")

        if not loopback_name:
            self.log.error("update_inet_address_loopback() -> Loopback not defined")
            return STATUS_NOK

        try:
            old_ip_interface = ipaddress.ip_interface(old_inet_address_cidr)
            new_ip_interface = ipaddress.ip_interface(new_inet_address_cidr)
            old_ip_version = old_ip_interface.version
            new_ip_version = new_ip_interface.version

        except ValueError as e:
            self.log.error(f"update_inet_address_loopback() -> Invalid IP address: {e}")
            return STATUS_NOK

        # Delete old IP address
        lo_name = f'lo:{loopback_name}'
        del_cmd = ['ip', 'addr', 'del', old_inet_address_cidr, 'label', lo_name, 'dev', 'lo']
        if old_ip_version == 6:
            del_cmd.insert(1, '-6')
        
        self.log.info(f'update_inet_address_loopback() - Deleting old address -> {del_cmd}')
        out = self.run(del_cmd)
        
        if out.exit_code:
            self.log.error(f"update_inet_address_loopback() -> Unable to delete old inet address: "
                        f"{old_inet_address_cidr} from loopback: {loopback_name}, Reason: {out.stderr}")
            return STATUS_NOK

        # Add new IP address
        add_cmd = ['ip', 'addr', 'add', new_inet_address_cidr, 'label', lo_name, 'dev', 'lo']
        if new_ip_version == 6:
            add_cmd.insert(1, '-6')

        self.log.info(f'update_inet_address_loopback() - Adding new address -> {add_cmd}')
        out = self.run(add_cmd)

        if out.exit_code:
            self.log.error(f"update_inet_address_loopback() -> Unable to set new inet address: "
                        f"{new_inet_address_cidr} on loopback: {loopback_name}, Reason: {out.stderr}")
            return STATUS_NOK

        return STATUS_OK

        
    def set_inet_address(self, interface_name: InterfaceName, inet_address_cidr: InetCidrText, secondary: bool = False) -> bool:
        """
        Set an IP address on an interface via OS.

        Args:
            interface_name (str): The network interface.
            inet_address_cidr (str): The IP address to set as a string in CIDR notation, including the label.
            secondary (bool, optional): Set as a secondary address. Defaults to False.

        Returns:
            bool: STATUS_OK for success, STATUS_NOK for failure.
        """
        self.log.debug(f"set_inet_address() - Interface: {interface_name} -> inet: {inet_address_cidr} -> secondary: {secondary}")

        if not interface_name:
            self.log.error("set_inet_address() -> Interface not defined")
            return STATUS_NOK

        try:
            ip = ipaddress.ip_interface(inet_address_cidr)
            
            if ip.ip == ip.network.network_address or ip.ip == ip.network.broadcast_address:
                self.log.error(f"Invalid IP address: {inet_address_cidr}, it's a network or broadcast address")
                return STATUS_NOK
            
        except ValueError as e:
            self.log.error(f"Invalid IP address: {inet_address_cidr}, Error: {e}")
            return STATUS_NOK

        if self.is_ip_assigned_to_interface(inet_address_cidr, interface_name):
            self.log.debug(f"Skipping...Inet: {inet_address_cidr} already assigned to Interface: {interface_name}")
        else:
            cmd = ["ip", "addr", "add", f"{inet_address_cidr}", "dev", interface_name]
            
            # TODO: ip route has a 15 character length label limit, need to add check
            if secondary:
                cmd += ["label", f"{interface_name}:sec"]
            
            self.log.debug(f"set_inet_address() -> cmd: {cmd}")
                    
            result = self.run(cmd)
            if result.exit_code:
                self.log.error(f"Unable to add inet: {inet_address_cidr} to interface: {interface_name} -> status: {result.stderr}")
                return STATUS_NOK
        
        return STATUS_OK 

    def del_inet_address(self, interface: InterfaceName, ip_address: InetAddressText) -> bool:
        """
        Remove an IP address from a network interface.

        Args:
            interface (str): The name of the network interface.
            ip_address (str): The IP address to remove.

        Returns:
            bool: STATUS_OK for success, STATUS_NOK for failure.
        """
        if not self.is_valid_network_interface(interface):
            self.log.debug(f"Invalid network interface: {interface}")
            return STATUS_NOK

        if not self.is_valid_inet_address(ip_address):
            self.log.debug(f"Invalid IP address: {ip_address}")
            return STATUS_NOK

        self.log.debug(f"Removing IP address {ip_address} from interface {interface}")

        result = self.run(["sudo", "ip", "addr", "del", ip_address, "dev", interface])

        if result.exit_code:
            self.log.debug(f"Unable to remove IP address {ip_address} from Interface {interface}")
            return STATUS_NOK

        self.log.debug(f"Removed IP address {ip_address} from interface {interface}")
        return STATUS_OK

    def is_ip_in_range(self, ip_and_subnet: InetCidrText, ip_address_start: InetAddressText, ip_address_end: InetAddressText, subnet_of_ip_start_ip_end: InetCidrText) -> bool:
        """
        Check if an IP address is within a specified range considering a given subnet.

        Args:
            ip_and_subnet (str): The IP address and subnet in CIDR notation (e.g., "192.168.1.10/24" or "2001:0db8::1/64").
            ip_address_start (str): The start IP address of the range.
            ip_address_end (str): The end IP address of the range.
            subnet_of_ip_start_ip_end (str): The subnet for the start and end IP addresses.

        Returns:
            bool: True if the IP address is in the specified range, False otherwise.
        """
        try:
            ip_and_subnet = ipaddress.ip_network(ip_and_subnet, strict=False)
            start_ip = ipaddress.ip_network(ip_address_start + "/" + subnet_of_ip_start_ip_end, strict=False)
            end_ip = ipaddress.ip_network(ip_address_end + "/" + subnet_of_ip_start_ip_end, strict=False)
            return start_ip <= ip_and_subnet <= end_ip
        except (ipaddress.AddressValueError, ValueError):
            return False

    def is_ip_range_within_subnet(self, subnet_cidr: InetCidrText, ip_range_start: InetAddressText, ip_range_end: InetAddressText, ip_range_subnet: InetCidrText) -> bool:
        """
        Check if an IP range is within a given subnet.

        Args:
            subnet_cidr (str): The subnet in CIDR notation (e.g., "192.168.1.0/24" or "2001:db8::/64").
            ip_range_start (str): The start IP address of the range.
            ip_range_end (str): The end IP address of the range.
            ip_range_subnet (str): The subnet mask for the IP range.

        Returns:
            bool: True if the IP range is within the subnet, False otherwise.
        """
        
        try:
            network = ipaddress.ip_network(subnet_cidr, strict=False)
            ip_start = ipaddress.ip_address(ip_range_start)
            ip_end = ipaddress.ip_address(ip_range_end)
            subnet_mask = ipaddress.ip_network(ip_range_subnet, strict=False).netmask

            return network.network_address <= ip_start and network.broadcast_address >= ip_end and subnet_mask == network.netmask

        except (ipaddress.AddressValueError, ValueError):
            return False

    def convert_ip_mask_to_cidr(ip_address:InetAddressText, prefix_length:IndentationError) -> str:
        """
        Convert an IP address and prefix length into a formatted IP address with CIDR notation.

        Args:
            ip_address (str): The IP address, either IPv4 or IPv6.
            prefix_length (int): The prefix length (subnet mask) for the IP address.

        Returns:
            str: A formatted IP address in CIDR notation (e.g., "192.168.1.0/24" or "2001:0db8::/64").
            Returns None if the input is not a valid IP address or prefix length.
        """
        try:
            # Check if the input IP address is IPv4 or IPv6
            if ':' in ip_address:
                # IPv6 address
                ip_network = ipaddress.IPv6Network(f"{ip_address}/{prefix_length}", strict=False)
                formatted_ip = str(ip_network.network_address)
                formatted_prefix = ip_network.prefixlen
            else:
                # IPv4 address
                ip_network = ipaddress.IPv4Network(f"{ip_address}/{prefix_length}", strict=False)
                formatted_ip = str(ip_network.network_address)
                formatted_prefix = ip_network.prefixlen

            return f"{formatted_ip}/{formatted_prefix}"
        except (ipaddress.AddressValueError, ValueError):
            return None

    def is_valid_inet_subnet(self, inet_subnet_cidr: InetCidrText) -> bool:
        """
        Check if the given string is a valid IPv4 or IPv6 subnet in CIDR notation.

        Args:
            inet_subnet_cidr (str): The CIDR notation to check for validity.

        Returns:
            bool: True if the CIDR notation is a valid IPv4 or IPv6 subnet, False otherwise.

        Note:
        This function uses the `ipaddress` module to verify the validity of the CIDR notation.
        If the notation is valid and corresponds to either an IPv4 or IPv6 network, it returns True.
        If the notation is invalid or not recognized as IPv4 or IPv6, it returns False.
        """
        try:
            network = ipaddress.ip_network(inet_subnet_cidr, strict=False)
            return network.version in {4, 6}
        except (ipaddress.AddressValueError, ValueError):
            return False


    def get_inet_subnet_inet_version(self, inet_subnet_cidr: InetCidrText) -> InetVersion:
        """
        Determine the IP version (IPv4 or IPv6) based on the CIDR notation of an IP subnet.

        Args:
            inet_subnet_cidr (str): The CIDR notation for the IP subnet (e.g., "192.168.0.0/24" for IPv4 or "2001:db8::/32" for IPv6).

        Returns:
            InetVersion: An InetVersion enum representing the IP version (IPv4, IPv6, or UNKNOWN).

        Raises:
            ValueError: If the input is not a valid CIDR notation.

        """
        try:
            network = ipaddress.IPv4Network(inet_subnet_cidr, strict=False)
            return InetVersion.IPv4

        except ValueError:
            try:
                network = ipaddress.IPv6Network(inet_subnet_cidr, strict=False)
                return InetVersion.IPv6
            except ValueError:
                return InetVersion.UNKNOWN

    @staticmethod
    def validate_subnet_format(subnet: InetCidrText) -> tuple[bool, str | None]:
        """
        Validate the format of an IPv4 or IPv6 subnet.

        Args:
            subnet (str): The subnet in CIDR notation.

        Returns:
            tuple: (bool, str | None) where the first element is True if valid, otherwise False.
                The second element is an error message or None if valid.

        Example:
            subnet = "172.16.0.0/24"
            subnet = "fd00:1::/64"
        """
        try:
            ipaddress.ip_network(subnet)
            return True, None
        except ValueError as e:
            return False, str(e)

    @staticmethod
    def validate_inet_ranges(subnet_cidr: InetCidrText, pool_start: InetAddressText, pool_end: InetAddressText) -> bool:
        """
        Validate if the specified IP address range in the DHCP pool falls within both the subnet and the pool subnet.

        This method checks if the IP address range specified in the DHCP pool falls within the given subnet and considers
        the pool subnet as well. It iterates over subnets within the pool range subnet using 
        `ipaddress.summarize_address_range` and checks if any part of the pool range overlaps with the specified subnet.

        Args:
            subnet_cidr (str): The subnet CIDR of the DHCP pool.
            pool_start (str): The starting IP address of the DHCP pool.
            pool_end (str): The ending IP address of the DHCP pool.

        Returns:
            bool: True if the DHCP pool range is valid within both the subnet and the pool subnet, False otherwise.
        """
        try:
            subnet = ipaddress.ip_network(subnet_cidr)
            pool_start_address = ipaddress.ip_address(pool_start)
            pool_end_address = ipaddress.ip_address(pool_end)

            for subnet_segment in ipaddress.summarize_address_range(pool_start_address, pool_end_address):
                if not subnet.overlaps(subnet_segment):
                    return False

            return True
        
        except ValueError:
            return False

    @staticmethod
    def validate_inet_range(subnet_cidr: InetCidrText, inet: InetAddressText) -> bool:
        """
        Validate if the specified IP address falls within the given subnet.

        This method checks if the provided IP address falls within the specified subnet. It uses the `ipaddress` module
        to validate the IP address format and then checks if the IP address is within the given subnet.

        Args:
            subnet_cidr (str): The subnet CIDR to validate against.
            inet (str): The IP address to be validated.

        Returns:
            bool: True if the provided IP address is within the specified subnet, False otherwise.
        """
        try:
            subnet = ipaddress.ip_network(subnet_cidr)
            inet_address = ipaddress.ip_address(inet)

            # Check if the IP address is within the subnet
            return inet_address in subnet
            
        except ValueError:
            # Log or handle the specific error message
            return False


# FILE: src/routershell/lib/network_manager/common/interface.py
import logging
import re
from enum import Enum

from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import InterfaceName
from routershell.lib.network_manager.common.phy import PhyServiceLayer


class InterfaceLayerFoundError(Exception):

    def __init__(self, message="Interface Layer error"):
        self.message = message
        super().__init__(self.message)

class InterfaceType(Enum):
    """
    Enumeration representing different types of network interfaces.

    Each member of the enumeration corresponds to a specific type of network interface.
    The values are used to identify and categorize network interfaces based on their characteristics.

    Enum Members:
        DEFAULT (str): Default type.
        PHYSICAL (str): Physical interface type.
        ETHERNET (str): Ethernet interface type.
        VLAN (str): Virtual LAN interface type.
        LOOPBACK (str): Loopback interface type.
        VIRTUAL (str): Virtual interface type.
        BRIDGE (str): Bridge interface type.
        WIRELESS_WIFI (str): Wireless Wi-Fi interface type.
        WIRELESS_CELL (str): Wireless cellular interface type.
        UNKNOWN (str): Unknown or undefined interface type.
    """
    DEFAULT = 'if' 
    PHYSICAL = 'phy'
    ETHERNET = 'eth'
    VLAN = 'vlan'
    LOOPBACK = 'loopback'
    VIRTUAL = 'vir'
    BRIDGE = 'br'
    WIRELESS_WIFI = 'wifi'
    WIRELESS_CELL = 'cell'
    UNKNOWN = 'UNKNOWN'

class InterfaceLayer(PhyServiceLayer):

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().INTERFACE)
        
    def get_os_interface_type(self, interface_name: InterfaceName) -> InterfaceType:
        """
        Determines the type of a network interface using information from the 'nmcli dev show' command.

        Args:
            interface_name (str): The name of the network interface.

        Returns:
            InterfaceType: An enumeration representing the type of the network interface.
            Returns InterfaceType.UNKNOWN if an error occurs or if the interface type is unknown.

        Raises:
            InterfaceLayerFoundError: If an error occurs during the execution of 'nmcli dev show'.
        """
        try:
            output = self.run(["nmcli", "dev", "show", interface_name])

            if output.exit_code:
                self.log.error(f"Error executing 'nmcli': {output.stderr}")
                return InterfaceType.UNKNOWN

            if re.search(r"\bGENERAL\.TYPE:\s*wifi\b", output.stdout):
                return InterfaceType.WIRELESS_WIFI

            elif re.search(r"\bGENERAL\.TYPE:\s*gsm\b", output.stdout):
                return InterfaceType.WIRELESS_CELL

            elif re.search(r"\bGENERAL\.TYPE:\s*ethernet\b", output.stdout):
                return InterfaceType.ETHERNET

            elif re.search(r"\bGENERAL\.TYPE:\s*vlan\b", output.stdout):
                return InterfaceType.VLAN

            elif re.search(r"\bGENERAL\.TYPE:\s*bridge\b", output.stdout):
                return InterfaceType.BRIDGE

            elif re.search(r"\bGENERAL\.TYPE:\s*tun\b", output.stdout):
                return InterfaceType.VIRTUAL

            elif re.search(r"\bGENERAL\.TYPE:\s*loopback\b", output.stdout):
                return InterfaceType.LOOPBACK

            else:
                return InterfaceType.UNKNOWN

        except InterfaceLayerFoundError as e:
            self.log.error(f"An error occurred: {e}")
            return InterfaceType.UNKNOWN


            

        

# FILE: src/routershell/lib/network_manager/common/mac.py
import logging
import random
import re

from tabulate import tabulate

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import InterfaceName, MacAddressText
from routershell.lib.network_manager.common.interface import InterfaceLayer


class MacServiceLayerFoundError(Exception):
    """
    Exception raised when a network interface is not found.
    """

    def __init__(self, message="Mac Service error"):
        self.message = message
        super().__init__(self.message)

class MacServiceLayer(InterfaceLayer):
    """
    A class for configuring network settings using iproute2.
    """
    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().MAC)
        
    def set_interface_mac(self, interface_name: InterfaceName, mac_address: MacAddressText) -> bool:
        """
        Set the MAC address of a network interface via os.

        Args:
            interface_name (str): The name of the network interface to update.
            mac_address (str): The new MAC address to set for the network interface.
            
        Returns:
            bool: STATUS_OK if the MAC address was successfully updated, STATUS_NOK otherwise.

        Note:
            - This method requires administrative privileges to update the MAC address.
            - The 'ifName' parameter is optional, and if not provided, the method will not perform any actions.
            - It checks if the MAC address is in a valid format and returns STATUS_NOK if not.
        """
        
        if not interface_name:
            self.log.error(f"update_if_mac_address() No Interface Defined -> mac {mac_address} -> ifName: {interface_name}")
            MacServiceLayerFoundError("No Interface Defined")
            return STATUS_NOK
            
        self.log.debug(f"update_if_mac_address() -> mac {mac_address} -> ifName: {interface_name}")
        
        if not self.is_valid_mac_address(mac_address):
            self.log.debug(f"update_if_mac_address() -> Error -> mac {mac_address} -> ifName: {interface_name}")
            MacServiceLayerFoundError(f"Mac Address is not valid: {mac_address}")
            return STATUS_NOK
            
        self.log.debug(f"update_if_mac_address() -> ifName: {interface_name} -> mac: {mac_address}")
        try:
            self.run(["ip", "link", "set", "dev", interface_name, "down"])
            self.run(["ip", "link", "set", "dev", interface_name, "address", mac_address])
            self.run(["ip", "link", "set", "dev", interface_name, "up"])

            self.log.debug(f"Changed MAC address of {interface_name} to {mac_address}")
            return STATUS_OK
        
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return STATUS_NOK

    def is_valid_mac_address(self, mac: MacAddressText) -> bool:
        """
        Check if a given MAC address is valid.

        Args:
            mac (str): The MAC address to be validated.

        Supported MAC address formats:
        - xxxxxxxxxxxx: Twelve characters with no delimiters.
        - xx:xx:xx:xx:xx:xx: Six pairs of two characters separated by colons.
        - xx-xx-xx-xx-xx-xx: Six pairs of two characters separated by hyphens.
        - xxxx.xxxx.xxxx: Three groups of four characters separated by dots.

        Returns:
            bool: True if the MAC address is valid, False otherwise.
        """
        # Define regular expression patterns for supported MAC address formats
        patterns = [
            r'^[0-9A-Fa-f]{12}$',
            r'^[0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}$',
            r'^[0-9A-Fa-f]{2}-[0-9A-Fa-f]{2}-[0-9A-Fa-f]{2}-[0-9A-Fa-f]{2}-[0-9A-Fa-f]{2}-[0-9A-Fa-f]{2}$',
            r'^[0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4}$'
        ]

        # Check if the MAC address matches any of the patterns
        for pattern in patterns:
            if re.match(pattern, mac):
                return True

        return False

    def format_mac_address(self, mac_address: MacAddressText) -> tuple[bool, str]:
        """
        Normalize and format a MAC address into the standard format (xx:xx:xx:xx:xx:xx).

        Args:
            mac_address (str): The MAC address in various formats.

        Supported MAC address formats:
        - xxxxxxxxxxxx: Twelve alphanumeric characters with no delimiters.
        - xxxx.xxxx.xxxx: Twelve alphanumeric characters separated by dots.
        - xx:xx:xx:xx:xx:xx: Six pairs of two alphanumeric characters separated by colons or hyphens.
        - xx-xx-xx-xx-xx-xx: Six pairs of two alphanumeric characters separated by hyphens.

        Returns:
        tuple: A tuple containing:
            - bool: True if the MAC address was successfully formatted, False otherwise.
            - str: The formatted MAC address in the standard format (xx:xx:xx:xx:xx:xx) if successful,
                or None if the input MAC address is not recognized.

        """
        # Remove any non-alphanumeric characters from the input
        mac_address = re.sub(r'[^0-9a-fA-F]', '', mac_address)

        # Check if the MAC address is already in the standard format
        if len(mac_address) == 12:
            formatted_mac = ':'.join([mac_address[i:i+2] for i in range(0, 12, 2)])
            return True, formatted_mac

        # Check if the MAC address is in the xxxx.xxxx.xxxx format
        if len(mac_address) == 14:
            formatted_mac = ':'.join([mac_address[i:i+4] for i in range(0, 14, 4)])
            return True, formatted_mac

        # Check if the MAC address is in the xx:xx:xx:xx:xx:xx format
        if len(mac_address) == 17 and (mac_address.count(':') == 5 or mac_address.count('-') == 5):
            formatted_mac = ':'.join(mac_address.split(':'))
            return True, formatted_mac

        # Check if the MAC address is in the xx-xx-xx-xx-xx-xx format
        if len(mac_address) == 17 and mac_address.count('-') == 5:
            formatted_mac = ':'.join(mac_address.split('-'))
            return True, formatted_mac

        # If none of the recognized formats, return None
        return False, None

    def generate_random_mac(self, address_type='UA') -> str:
        """
        Generate a random MAC address with the specified address type.

        Args:
            address_type (str): The type of MAC address to generate. Possible values:
            - 'UA' for Universally Administered (default).
            - 'LA' for Locally Administered.
            - 'MC' for Multicast.
            - 'SA' for Universally Administered but with the second least significant bit set (Stallion MAC).

        Returns:
            str: A randomly generated MAC address in the specified address type range, formatted as 'xx:xx:xx:xx:xx:xx'.
        """
        if address_type == 'UA':
            # UA MAC address: The first byte should start with '02' to indicate UA MAC address
            mac = [0x02] + [random.randint(0x00, 0xFF) for _ in range(5)]
        elif address_type == 'LA':
            # LA MAC address: The first byte should start with '02' to indicate LA MAC address
            mac = [0x02] + [random.randint(0x00, 0xFF) for _ in range(5)]
            # Set the second least significant bit to indicate LA
            mac[0] |= 0x02
        elif address_type == 'MC':
            # Multicast MAC address: The first byte should start with '01' to indicate multicast MAC address
            mac = [0x01] + [random.randint(0x00, 0xFF) for _ in range(5)]
        elif address_type == 'SA':
            # Stallion MAC address: The first byte should start with '02' to indicate UA MAC address
            mac = [0x02] + [random.randint(0x00, 0xFF) for _ in range(5)]
            # Set the second least significant bit to indicate SA
            mac[0] |= 0x02
        else:
            raise ValueError("Invalid address_type. Use 'UA', 'LA', 'MC', or 'SA'.")

        return ':'.join(map(lambda x: format(x, '02x'), mac))
    
    def get_arp(self, args=None):
        try:
            
            self.log.debug("get_arp()")
            
            # Run the 'ip neighbor show' command and capture the output
            output = self.run(['ip', 'neighbor', 'show'])

            self.log.debug(f"get_arp() stderr: ({output.stderr}) -> exit_code: ({output.exit_code }) -> stdout: \n{output.stdout}")
            
            if output.exit_code == 0:
                
                arp_lines = output.stdout.strip().split('\n')

                arp_table = [line.split() for line in arp_lines]

                headers = ["IP Address", "Device", "Interface", "Type", "MAC Address", "State"]
                
                table = tabulate(arp_table, headers=headers, tablefmt='plain', colalign=("left", "left", "left", "left", "left"))

                print(table)
            else:
                print(f"Error executing 'ip neighbor show' command: {output.stderr}")
        except Exception as e:
            print(f"Error: {e}")

    def is_valid_duid_ll(self, duid):
        """
        Validate if the provided string is a valid DUID-LL (Link-layer address) in DHCPv6.

        Args:
            duid (str): The DHCP Unique Identifier to be validated.

        Returns:
            bool: True if the provided string is a valid DUID-LL, False otherwise.
        """
        duid_ll_pattern = re.compile(r'^00:01:[0-9a-fA-F:]+$')
        return bool(duid_ll_pattern.match(duid))

# FILE: src/routershell/lib/network_manager/common/phy.py
import logging
from enum import Enum

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import InterfaceName
from routershell.lib.network_manager.common.run_commands import RunCommand


class State(Enum):
    UP = 'up'
    DOWN = 'down'
    UNKNOWN = 'unknown'
    
class Duplex(Enum):
    
    AUTO = "auto"
    """
    Auto-negotiation (Auto): In auto-negotiation mode, the device negotiates with 
    its link partner to determine the best duplex mode to use. Auto-negotiation is recommended 
    for most modern networks as it allows devices to automatically adapt to the highest common denominator.
    """

    HALF = "half"
    """
    Half Duplex (Half): In half-duplex mode, a network interface can either transmit or receive data at a time, but not both simultaneously. 
    This mode is typically used for older networks or when compatibility with legacy equipment is required.
    """

    FULL = "full"
    """
    Full Duplex (Full): In full-duplex mode, a network interface can transmit and receive data simultaneously. 
    This mode is typically used for high-speed connections where there is a dedicated channel 
    for both sending and receiving data. It minimizes collisions and improves network performance.
    """
    
    NONE = None
    """
    NONE: Interface that does not support a specific duplex
    Example: (wireless, loopback, vlan, bridges, only ethernet interfaces)
    """       

class Speed(Enum):
    MBPS_10 = 10
    """
    10 MBPS: Configures the interface to operate at a fixed speed of 10 megabits per second (Mbps).
    """

    MBPS_100 = 100
    """
    100 MBPS: Configures the interface to operate at a fixed speed of 100 megabits per second (Mbps).
    """

    MBPS_1000 = 1000
    """
    1000 MBPS: Configures the interface to operate at a fixed speed of 1 gigabit per second (Gbps).
    """

    MBPS_2500 = 2500
    """
    2500 MBPS: Configures the interface to operate at a fixed speed of 2.5 gigabit per second (Gbps).
    """
        
    MBPS_10000 = 10000
    """
    1000 MBPS: Configures the interface to operate at a fixed speed of 10 gigabits per second (Gbps).
    """

    AUTO_NEGOTIATE = True
    """
    AUTO-NEGOTIATE: In auto-negotiation mode, the device negotiates with its link partner to determine the 
    best speed and duplex mode to use within the limits supported by both devices.
    """
    
    NONE = None
    """
    NONE: Interface that does not support a specific speed
    Example (wireless, loopback, vlan, bridges, only ethernet interfaces)
    """   
        
class PhyServiceLayer(RunCommand):
    """
    A class for configuring network settings using iproute2.
    """
    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().PHY)
            
    def set_duplex(self, interface_name: InterfaceName, duplex: Duplex):
        """
        Set the duplex mode of a network interface.

        Args:
            interface_name (str): The name of the network interface.
            duplex (Duplex): The desired duplex mode to set for the interface (e.g., Duplex.DUPLEX_AUTO).

        Returns:
            bool: STATUS_OK if the duplex mode is successfully set, STATUS_NOK otherwise.
        """
        if duplex is Duplex.AUTO:
            self.log.debug("do_duplex() - duplex set to auto")
            cmd = ['ethtool', '-s', interface_name, 'autoneg' , 'on']
        else:
            cmd = ['ethtool', '-s', interface_name, 'duplex', duplex.value]

        status = self.run(cmd).exit_code

        if status == STATUS_OK:
            self.log.debug(f"Set duplex mode of {interface_name} to {duplex.name}")
            return STATUS_OK
        else:
            self.log.error(f"Failed to set duplex mode of {interface_name} to {duplex.name}")
            return STATUS_NOK

    def set_speed(self, interface_name: InterfaceName, ifSpeed: Speed, auto: bool = False) -> bool:
        """
        Set the speed of a network interface and optionally enable or disable auto-negotiation.

        Args:
            interface_name (str): The name of the network interface.
            ifSpeed (Speed): The desired speed to set for the interface.
            autoneg (bool, optional): Whether to enable (True) or disable (False) auto-negotiation. Defaults to False.

        Returns:
            bool: STATUS_OK if the speed is successfully set, STATUS_NOK otherwise.
        """
        try:
            cmd_auto = ['ethtool', '-s', interface_name, 'autoneg', 'on' if auto else 'off']
            status_auto = self.run(cmd_auto).exit_code

            if not auto:
                cmd_speed = ["ethtool", "-s", interface_name, "speed", str(ifSpeed.value)]
                status_speed = self.run(cmd_speed).exit_code

                if status_speed == STATUS_OK:
                    self.log.debug(f"Set speed of {interface_name} to {ifSpeed.name}")
                else:
                    self.log.error(f"Failed to set speed of {interface_name} to {ifSpeed.name}")
            else:
                status_speed = STATUS_OK

            if status_auto == STATUS_OK:
                if auto:
                    self.log.debug(f"Enabled auto-negotiation on {interface_name}")
                else:
                    self.log.debug(f"Disabled auto-negotiation on {interface_name}")
            else:
                self.log.error(f"Failed to set auto-negotiation on {interface_name} to {'on' if auto else 'off'}")

            return status_speed == STATUS_OK and status_auto == STATUS_OK

        except Exception as e:
            self.log.error(f"An error occurred while setting interface speed: {e}")
            return STATUS_NOK

    def set_interface_shutdown(self, interface_name: InterfaceName, state: State) -> bool:
        """
        Set the state of a network interface (up or down).

        Args:
            interface_name (str): The name of the network interface to configure.
            state (State): The state to set. Valid values are State.UP (to bring the interface up)
                        or State.DOWN (to shut the interface down).

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        
        self.log.debug(f"set_interface_state() -> interface_name: {interface_name} -> state: {state}")
        
        if state not in (State.UP, State.DOWN):
            self.log.error("Invalid state. Use State.UP or State.DOWN.")
            return STATUS_NOK

        cmd = ['ip', 'link', 'set', 'dev', interface_name, state.value]

        status = self.run(cmd).exit_code

        if not status:
            self.log.debug(f"Changed state of {interface_name} to {state.value}")
        else:
            self.log.error(f"Failed to change state of {interface_name} to {state.value}")

        return status == STATUS_OK

    def set_mtu(self, interface_name: InterfaceName, mtu_size: int) -> bool:
        """
        Set the Maximum Transmission Unit (MTU) size for a network interface using iproute2.

        Args:
            interface_name (str): The name of the network interface to configure.
            mtu_size (int): The MTU size to set for the interface.

        Returns:
            bool: True if the MTU size was unsuccessfully set, False otherwise.

        """
        # Run the iproute2 command to set the MTU size
        if self.run(['ip', 'link', 'set', interface_name, 'mtu', str(mtu_size)]).exit_code:
            return STATUS_NOK
        else:
            return STATUS_OK
    
    def get_duplex(self, interface_name: InterfaceName) -> Duplex:
        """
        Get the current duplex mode of a network interface.

        Args:
            interface_name (str): The name of the network interface.

        Returns:
            Duplex: The current duplex mode of the interface.
        """
        # Run the ethtool command to get duplex mode
        result = self.run(['ethtool', '-s', interface_name], capture_output=True, text=True, check=True)
        output = result.stdout

        if "Duplex: Full" in output:
            return Duplex.FULL
        elif "Duplex: Half" in output:
            return Duplex.HALF
        else:
            return Duplex.AUTO

    def get_speed(self, interface_name: InterfaceName) -> Speed:
        """
        Get the current speed setting of a network interface.

        Args:
            interface_name (str): The name of the network interface.

        Returns:
            Speed: The current speed setting of the interface.
        """
        # Run the ethtool command to get speed
        result = self.run(['ethtool', interface_name], capture_output=True, text=True, check=True)
        output = result.stdout

        if "Speed: 1000Mb/s" in output:
            return Speed.MBPS_1000
        elif "Speed: 100Mb/s" in output:
            return Speed.MBPS_100
        elif "Speed: 10Mb/s" in output:
            return Speed.MBPS_10
        else:
            return Speed.AUTO_NEGOTIATE

    def get_mtu(self, interface_name: InterfaceName) -> int:
        """
        Get the current Maximum Transmission Unit (MTU) size of a network interface.

        Args:
            interface_name (str): The name of the network interface.

        Returns:
            int: The current MTU size of the interface.
        """
        # Run the ip command to get MTU size
        result = self.run(['ip', 'link', 'show', 'dev', interface_name], capture_output=True, text=True, check=True)
        output = result.stdout

        # Parse the MTU value from the output
        for line in output.splitlines():
            if 'mtu' in line:
                mtu = int(line.split('mtu')[1].split(' ')[0])
                return mtu

        return -1  # Return a default value if MTU is not found

        

# FILE: src/routershell/lib/network_manager/network_interfaces/bridge/bridge_factory.py
import logging

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import BridgeName
from routershell.lib.network_manager.common.phy import State
from routershell.lib.network_manager.network_interfaces.bridge.bridge_interface import BridgeInterface


class BridgeInterfaceFactory:
    """
    Factory class for creating and managing bridge interface commands.

    Attributes:
        _bridge_config_command_list (list['BridgeInterface']): A list that holds the bridge configuration commands 
        for different bridges. This list is used to store and manage the configuration commands for bridges 
        created by the factory.
        
    Methods:
        __init__(bridge_name: BridgeName):
            Initializes the BridgeConfigFactory with the given bridge name and sets up logging.
        
        get_bridge_interface() -> 'BridgeInterface':
            Creates a new BridgeInterface object for the current bridge and adds it to the list of commands.
            Returns the newly created BridgeInterface object.
    """
    
    _bridge_interface_list: list[BridgeInterface] = []
    
    def __init__(self, bridge_name: BridgeName):
        """
        Initializes the BridgeConfigFactory with the given bridge name and sets up logging.

        Args:
            bridge_name (str): The name of the bridge for which configuration commands will be created.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().BRIDGE_INTERFACE_FACTORY)        
        self._bridge_name = bridge_name
    
    def destroy_bridge(self) -> bool:
        """
        Destroy the bridge associated with the current object.

        This method iterates through the list of bridge configuration commands and 
        destroys the bridge if it matches the current bridge name.

        Returns:
            bool: STATUS_OK if the bridge was successfully destroyed, STATUS_NOK otherwise.
        """
        if BridgeInterfaceFactory._bridge_interface_list:
            for bcc in BridgeInterfaceFactory._bridge_interface_list:
                if self._bridge_name == bcc.get_bridge_name():
                    if bcc.destroy_bridge():
                        self.log.debug(f'Failed to destroy bridge {bcc.get_bridge_name()}')
                        return STATUS_NOK
                    else:
                        self.log.debug(f'Destroyed bridge {bcc.get_bridge_name()}')
                        return STATUS_OK
        return STATUS_NOK

    def get_bridge_interface(self) -> 'BridgeInterface':
        """
        Creates a new BridgeInterface object for the current bridge and adds it to the list of commands.

        This method initializes a new BridgeInterface object with the bridge name and appends it to 
        the class-level list of bridge configuration commands.

        Returns:
            BridgeInterface: The newly created BridgeInterface object.
        """
        bcc = BridgeInterface(self._bridge_name)
        BridgeInterfaceFactory._bridge_interface_list.append(bcc)

        if not bcc.does_bridge_exist() and not bcc.create_bridge():
            self.log.debug(f"Bridge {self._bridge_name} created successfully.")
            
        return bcc
    
    def set_shutdown_status_all_bridges(self, shutdown_state: State) -> bool:
        """
        Sets the shutdown status for all bridges managed by the system using the BridgeInterface class.

        This method performs the following actions:
        1. Iterates over each bridge configuration command in the singleton list.
        2. Applies the specified shutdown status to each bridge.
        3. Logs the result of the operation.

        Args:
            shutdown_state (State): The desired shutdown status to set for all bridges. 
                This should be an instance of the `State` enum, such as `State.UP` or `State.DOWN`.

        Returns:
            bool: STATUS_OK if the shutdown status was successfully set for all bridges, STATUS_NOK otherwise.
        """
        if not BridgeInterfaceFactory._bridge_interface_list:
            self.log.error("No BridgeInterface Found")
            return STATUS_NOK
        
        success = STATUS_OK

        for bcc in BridgeInterfaceFactory._bridge_interface_list:
            if not bcc.set_shutdown_status(shutdown_state):
                self.log.error(f"Failed to set bridge {bcc._bridge_name} to {shutdown_state}")
                success = STATUS_NOK

        return success

# FILE: src/routershell/lib/network_manager/network_interfaces/bridge/bridge_group_interface_abc.py
import logging
from abc import ABC

from routershell.lib.common.types import BridgeName, InterfaceName
from routershell.lib.network_manager.network_operations.bridge import Bridge


class BridgeGroup(ABC):
    """
    Abstract base class representing a bridge group for network interfaces.
    
    This class provides methods to set and delete bridge groups for a specified network interface.
    """

    def __init__(self, interface_name: InterfaceName):
        """
        Initializes the BridgeGroup with a network interface name.

        Args:
            interface_name (str): The name of the network interface.
        """
        self._interface_name = interface_name
        self.log = logging.getLogger(self.__class__.__name__)
    
    def set_bridge_group(self, bridge_group: BridgeName) -> bool:
        """
        Adds the network interface to the specified bridge group.

        Args:
            bridge_group (str): The name of the bridge group to add the interface to.

        Returns:
            bool: STATUS_OK if the interface was successfully added to the bridge group,
                  STATUS_NOK otherwise.
        """
        return Bridge().add_interface_to_bridge_group(self._interface_name, bridge_group)
    
    def del_bridge_group(self, bridge_group: BridgeName) -> bool:
        """
        Removes the network interface from the specified bridge group.

        Args:
            bridge_group (str): The name of the bridge group to remove the interface from.

        Returns:
            bool: STATUS_OK if the interface was successfully removed from the bridge group,
                  STATUS_NOK otherwise.
        """
        return Bridge().del_interface_to_bridge_group(self._interface_name, bridge_group)

# FILE: src/routershell/lib/network_manager/network_interfaces/bridge/bridge_interface.py
import logging

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import BridgeName, InetAddressText
from routershell.lib.network_manager.common.phy import State
from routershell.lib.network_manager.network_interfaces.bridge.bridge_protocols import STP_STATE, BridgeProtocol
from routershell.lib.network_manager.network_operations.bridge import Bridge


class BridgeInterface:
    def __init__(self, bridge_name: BridgeName, defaults_at_create:bool=True):
        """
        Initialize the BridgeInterface instance.

        Args:
            bridge_name (str): The name of the bridge to configure.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().BRIDGE_INTERFACE)
        self._bridge_name = bridge_name
        self._defaults_at_create = defaults_at_create
    
    def get_bridge_name(self):
        """
        Retrieve the name of the current bridge.

        This method returns the bridge name stored in the instance's _bridge_name attribute.

        Returns:
            str: The name of the bridge.
        """
        return self._bridge_name

    def does_bridge_exist(self) -> bool:
        """
        Check if the specified bridge exists.

        Returns:
            bool: True if the bridge exists, False otherwise.
        """
        if not Bridge().does_bridge_exist(self._bridge_name):
            self.log.debug(f'does_bridge_exist() -> {self._bridge_name} does not exist')
            return False         
        return True
    
    def create_bridge(self) -> bool:
        """
        Create a bridge interface if it does not already exist.

        Returns:
            bool: STATUS_OK if the bridge was successfully created or already exists, STATUS_NOK otherwise.
        """        
        if self.does_bridge_exist():
            self.log.error(f'Can not create bridge: {self._bridge_name}, already exists')
            return STATUS_NOK
            
        if Bridge().add_bridge(self.get_bridge_name()):
            self.log.error(f'create_bridge(return {STATUS_NOK}) -> Failed to create Bridge {self.get_bridge_name()}')
            return STATUS_NOK
        
        if self._defaults_at_create:
            if Bridge().update_bridge(self._bridge_name, 
                                        BridgeProtocol.IEEE_802_1S,
                                        STP_STATE.STP_ENABLE, 
                                        shutdown_status=State.DOWN):
                self.log.error(f'create_bridge(return {STATUS_NOK}) -> Failed to configure Bridge {self._bridge_name} with IEEE 802.1S and STP enabled')
                return STATUS_NOK
        
        self.log.debug(f'create_bridge(return {STATUS_NOK}) -> successfully created bridge {self.get_bridge_name()}')
        return STATUS_OK
    
    def destroy_bridge(self):
        """
        Destroy the current bridge by calling the del_bridge method of the Bridge class.

        This method retrieves the bridge name of the current instance and 
        deletes the bridge using the del_bridge method from the Bridge class.
        """
        return Bridge().del_bridge(self.get_bridge_name())

    def set_inet_management(self, inet: InetAddressText) -> bool:
        """
        Set the IPv4 or IPv6 address for the bridge.

        Args:
            inet (str): The IP address to set.

        Returns:
            bool: STATUS_OK if the IP address was successfully set, STATUS_NOK otherwise.
        """
        if not self.does_bridge_exist():
            self.log.error(f'Unable to set management inet {inet} to bridge: {self._bridge_name} does not exists')
            return STATUS_NOK
        
        if Bridge().update_bridge(bridge_name=self._bridge_name, management_inet=inet):
            self.log.debug(f'set_inet_management() -> Failed to set inet address {inet} to bridge {self._bridge_name}')
            return STATUS_NOK

        self.log.debug(f'set_inet_management() -> Inet address {inet} is set to bridge {self._bridge_name}')
        return STATUS_OK
    
    def set_shutdown_status(self, state: State) -> bool:
        """
        Set the shutdown status for a specified bridge.

        This method checks if the bridge exists. If it does, it compares the current shutdown status 
        with the desired new status. If they differ, it updates the bridge's shutdown status. 

        Parameters:
            state (State): The desired shutdown status to set for the bridge. 
                        It can be State.UP, State.DOWN, or State.UNKNOWN.

        Returns:
            bool: STATUS_OK (True) if the shutdown status was successfully set or if it was already set to the desired status.
                STATUS_NOK (False) if there was an error setting the shutdown status.
        """
        if not self.does_bridge_exist():
            self.log.error(f'Unable to set {state} to bridge: {self._bridge_name} does not exists')
            return STATUS_NOK
        
        if Bridge().update_bridge(bridge_name=self._bridge_name, shutdown_status=state):
            self.log.debug(f'set_shutdown_status() -> Failed shutdown status {state} set for bridge {self._bridge_name}')
            return STATUS_NOK

        self.log.debug(f'set_shutdown_status() -> Shutdown status {state} is set to bridge {self._bridge_name}')
        return STATUS_OK

    def set_stp(self, stp: STP_STATE) -> bool:
        """
        Set the Spanning Tree Protocol (STP) state for the bridge.

        Args:
            stp (STP_STATE): The STP state to set.

        Returns:
            bool: STATUS_OK if the STP state was successfully set, STATUS_NOK otherwise.
        """
        if not self.does_bridge_exist():
            self.log.error(f'Unable to set stp {stp} to bridge: {self._bridge_name} does not exists')
            return STATUS_NOK
           
        if Bridge().update_bridge(bridge_name=self._bridge_name, stp_status=stp):
            self.log.debug(f'set_stp() -> Failed to set STP status {stp} to bridge {self._bridge_name}')
            return STATUS_NOK
        
        self.log.debug(f'set_stp() -> STP status {stp} is set for bridge {self._bridge_name}')
        
        return STATUS_OK
    
    def set_bridge_protocol(self, protocol: BridgeProtocol) -> bool:
        """
        Set the bridge protocol for the bridge.

        Args:
            protocol (BridgeProtocol): The bridge protocol to set.

        Returns:
            bool: STATUS_OK if the bridge protocol was successfully set, STATUS_NOK otherwise.
        """
        if not self.does_bridge_exist():
            self.log.error(f'Unable to set protocol {protocol} to bridge: {self._bridge_name} does not exists')
            return STATUS_NOK

        if Bridge().update_bridge(bridge_name=self._bridge_name, protocol=protocol):
            self.log.error(f'set_bridge_protocol() -> Failed to set description "{protocol}" to bridge {self._bridge_name}')
            return STATUS_NOK
            
        self.log.debug(f'set_bridge_protocol() -> Bridge protocol {protocol} is already set for bridge {self._bridge_name}')
        return STATUS_OK
    
    def set_description(self, description: str | None) -> bool:
        """
        Set a description for the bridge.

        Args:
            description (str | None): The description to set. If None, the description will be cleared.

        Returns:
            bool: STATUS_OK if the description was successfully set, STATUS_NOK otherwise.
        """
        if not self.does_bridge_exist():
            self.log.error(f'Unable to set description {description} to bridge: {self._bridge_name} does not exists')
            return STATUS_NOK

        if Bridge().update_bridge(bridge_name=self._bridge_name, description=description):
            self.log.error(f'set_description() -> Failed to set description "{description}" to bridge {self._bridge_name}')
            return STATUS_NOK
            
        self.log.debug(f'set_description() -> Description "{description}" set to bridge {self._bridge_name}')
        
        return STATUS_OK

# FILE: src/routershell/lib/network_manager/network_interfaces/create_loopback_net_interface.py
import logging

from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import InterfaceName
from routershell.lib.network_manager.common.interface import InterfaceType
from routershell.lib.network_manager.network_interfaces.loopback_interface import LoopbackInterface
from routershell.lib.network_manager.network_interfaces.network_interface_factory import NetInterfaceFactory
from routershell.lib.network_manager.network_operations.interface import Interface


class CreateLoopBackNetInterfaceError(Exception):
    def __init__(self, message):
        super().__init__(message)

class CreateLoopBackNetInterface:
    
    # Singleton {'interface_name': LoopbackInterface}
    _loopback_net_interface_obj_dict: dict[str, LoopbackInterface] = {}

    def __init__(self, loopback_name: InterfaceName):
        """
        Initialize a CreateLoopBackNetInterface instance to create a loopback network interface.

        Args:
            loopback_name (str): The name of the loopback network interface.

        Raises:
            InvalidNetInterface: If the loopback interface already exists or if creation fails.
        """
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS.CREATE_LB_INTERFACE)
        self.loopback_name = loopback_name
        self.interface = Interface()
        self.log.debug(f'Loopback-Name: {loopback_name}')
        
        if Interface().does_os_interface_exist(loopback_name):
            
            if Interface().does_db_interface_exist(loopback_name):
                
                #If both exists, that mean we added it either at start-up or run-time
                if self.loopback_name not in CreateLoopBackNetInterface._loopback_net_interface_obj_dict:
                    self.log.error(f'Interface: {self.loopback_name} not found in NetInterface dict Object')
                
        else:
            self.log.debug(f'Adding Loopback: {loopback_name} to OS')
            ni = NetInterfaceFactory(self.loopback_name, InterfaceType.LOOPBACK).getNetInterface(self.loopback_name)            
            
            if ni.auto_inet_127_loopback():
                self.log.error(f'Unable to auto-assign 127 subnet to looopback: {self.loopback_name}')
            
            ni.set_description('Auto Assign loopback')
            CreateLoopBackNetInterface._loopback_net_interface_obj_dict[self.loopback_name] = ni
    
    def getLoopbackInterface(self, loopback_name:InterfaceName) -> LoopbackInterface:
        """
        Get a NetInterfaceFactory instance for the created loopback network interface.

        Returns:
            NetInterface: A NetInterface object associated with the created loopback interface.
        """
        self.log.debug(f'getLoopbackInterface() -> Interface: {loopback_name}')
        return CreateLoopBackNetInterface._loopback_net_interface_obj_dict[loopback_name]

# FILE: src/routershell/lib/network_manager/network_interfaces/ethernet/ethernet_interface.py
import logging

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import InetAddressText, InterfaceName, MacAddressText, NatPoolName
from routershell.lib.network_manager.common.interface import InterfaceType
from routershell.lib.network_manager.common.phy import Duplex, Speed, State
from routershell.lib.network_manager.network_interfaces.bridge.bridge_group_interface_abc import BridgeGroup
from routershell.lib.network_manager.network_interfaces.vlan.vlan_switchport_interface_abc import VlanSwitchport
from routershell.lib.network_manager.network_operations.arp import Encapsulate
from routershell.lib.network_manager.network_operations.dhcp.client.dhcp_clinet_interface_abc import DHCPInterfaceClient
from routershell.lib.network_manager.network_operations.interface import Interface
from routershell.lib.network_manager.network_operations.nat import NATDirection


class EthernetInterfaceError(Exception):
    def __init__(self, message):
        super().__init__(message)

class EthernetInterface(BridgeGroup, DHCPInterfaceClient, VlanSwitchport):

    def __init__(self, ethernet_name: InterfaceName):
        BridgeGroup.__init__(self, ethernet_name)
        DHCPInterfaceClient.__init__(self, ethernet_name)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().ETHERNET_INTERFACE)        
        self._interface_name = ethernet_name
    
    def get_interface_name(self) -> str:
        return self._interface_name
            
    def flush_interface(self) -> bool:
        """
        Flush network interface, removing any configurations.

        Returns:
            bool: STATUS_OK if the flush process is successful, STATUS_NOK otherwise.
        """
        return Interface().flush_interface(self._interface_name)

    def get_interface_shutdown_state(self) -> State:
        """
        Get the shutdown state of the network interface.

        Returns:
            State: The current shutdown state of the interface.
        """
        state = Interface().get_os_interface_hardware_info(self._interface_name).get('state')
        return State[state.upper()] if state else None

    def set_interface_shutdown_state(self, state: State) -> bool:
        """
        Set the shutdown state of the network interface.

        Args:
            state (State): The desired shutdown state (UP or DOWN).

        Returns:
            bool: STATUS_OK if the state change is successful, STATUS_NOK otherwise.
        """
        return Interface().update_shutdown(self._interface_name, state)

    def get_interface_speed(self) -> Speed:
        """
        Get the speed of the network interface.

        Returns:
            Speed: The current speed of the interface.
        """
        speed = Interface().get_os_interface_hardware_info(self._interface_name).get('speed')
        return Speed[speed.upper()] if speed else Speed.NONE

    def set_interface_speed(self, speed: Speed) -> bool:
        """
        Set the speed of the network interface.

        Args:
            speed (Speed): The desired speed of the interface.

        Returns:
            bool: STATUS_OK if the speed change is successful, STATUS_NOK otherwise.
        """
        return Interface().update_interface_speed(self._interface_name, speed)
    
    def set_proxy_arp(self, negate: bool = False) -> bool:
        """
        Enable or disable Proxy ARP on the network interface.

        This method allows you to enable or disable Proxy ARP on the specified network interface.

        Args:
            negate (bool): If True, Proxy ARP will be disabled. If False, Proxy ARP will be enabled.

        Returns:
            bool: STATUS_OK if the Proxy ARP configuration was successfully updated, STATUS_NOK otherwise.
        """
        return Interface().update_interface_proxy_arp(self._interface_name, negate)
    
    def set_drop_gratuitous_arp(self, negate: bool = False) -> bool:
        """
        Sets the drop gratuitous ARP configuration for the interface.

        Args:
            negate (bool, optional): If True, disables dropping gratuitous ARP packets (default: False).

        Returns:
            bool: True if the drop gratuitous ARP configuration was successfully set,
                False otherwise.
        """
        if Interface().update_interface_drop_gratuitous_arp(self._interface_name, (not negate)):
            self.log.error(f'Failed to update drop gratuitous ARP setting for interface: {self._interface_name}')
            return STATUS_NOK
        
        return STATUS_OK

    def set_mac_address(self, mac_addr: MacAddressText | None = None) -> bool:
        """
        Set the MAC address of the network interface.

        If `mac_addr` is None, the interface is set to auto, which typically resets the MAC address to the default hardware address.

        Args:
            mac_addr (str, optional): The new MAC address to assign to the network interface. If None, the MAC address is reset to the default.

        Returns:
            bool: STATUS_OK if the MAC address is successfully updated, STATUS_NOK otherwise.
        """
        return Interface().update_interface_mac(self._interface_name, mac_addr)
    
    def set_duplex(self, duplex: Duplex) -> bool:
        """
        Sets the duplex mode for the interface and updates the database entry.

        Args:
            duplex (Duplex): The duplex mode to set for the interface.

        Returns:
            bool: True if the duplex mode was successfully set and updated in the database,
                False otherwise.
        """
        return Interface().update_interface_duplex(self._interface_name, duplex)
    
    def add_inet_address(self, inet_address, secondary_address:bool=False, negate:bool=False) -> bool:
        """
        Add or modify an IP address on the network interface.

        Args:
            inet_address (str): The IP address to add or modify.
            secondary_address (bool, optional): Whether the IP address is a secondary address. Defaults to False.
            negate (bool, optional): Whether to remove the IP address if it exists. Defaults to False.

        Returns:
            bool: True if the IP address is successfully added or modified, False otherwise.
        """
        return Interface().update_interface_inet(self._interface_name, inet_address, secondary_address, negate)
    
    def add_static_arp(self, inet_address: InetAddressText, mac_addr: MacAddressText, negate: bool = False) -> bool:
        """
        Adds or removes a static ARP entry for the interface.

        Args:
            inet_address (str): The IP address for the ARP entry.
            mac_addr (str): The MAC address associated with the IP address.
            negate (bool, optional): If True, removes the static ARP entry (default: False).

        Returns:
            bool: True if the static ARP entry was successfully added or removed,
                False otherwise.
        """
        return Interface().update_interface_static_arp(self._interface_name, inet_address, mac_addr, Encapsulate.ARPA, negate)
    
    def get_ifType(self) -> InterfaceType:
        return InterfaceType.ETHERNET
        
    
    def set_nat_domain_direction(self, nat_pool_name: NatPoolName, nat_direction: NATDirection, negate: bool = False) -> bool:
        """
        Set the NAT domain direction on the specified NAT pool.

        Args:
            nat_pool_name (str): The name of the NAT pool.
            nat_direction (NATDirection): The direction of NAT (inside or outside).
            negate (bool): If True, remove the NAT direction; otherwise, set the NAT direction.

        Returns:
            bool: STATUS_OK if the NAT direction was successfully set, STATUS_NOK otherwise.
        """
        if Interface.set_nat_domain_status(self, self._interface_name, nat_pool_name, nat_direction, negate):
            self.log.error(f'Unable to add NAT-{nat_direction.name} to pool-name: {nat_pool_name} Negate: {negate}')
            return STATUS_NOK
        return STATUS_OK


# FILE: src/routershell/lib/network_manager/network_interfaces/loopback_interface.py
import logging

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import InetCidrText, InterfaceName
from routershell.lib.network_manager.network_interfaces.network_interface import NetworkInterface
from routershell.lib.network_manager.network_operations.interface import Interface


class LoopbackInterfaceError(Exception):
    def __init__(self, message):
        super().__init__(message)

class LoopbackInterface(NetworkInterface):
    """
    Class for managing loopback interfaces.

    Attributes:
        interface_name (str): The name of the loopback interface.
        log (Logger): Logger instance for the class.
    """

    def __init__(self, loopback_name: InterfaceName) -> None:
        """
        Initializes a LoopbackInterface instance.

        Args:
            interface_name (str): The name of the loopback interface.
        """
        super().__init__(interface_name=loopback_name)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS.LOOPBACK_INTERFACE)
        self._127_inet_address = None
        
        if not Interface().does_os_interface_exist(loopback_name):
            self.log.info(f'Adding loopback: {loopback_name} to system')

            if Interface().update_interface_loopback_inet(loopback_name, inet_address_cidr=None):
                self.log.info(f"Loopback: {loopback_name} created successfully.")
            
            if self.set_description(f'Auto Assigned Loopback Address: {self._127_inet_address}'):
                self.log.error(f'Failed to set description for Loopback: {loopback_name}')
            
        else:
            self.log.debug(f'Loopback: {loopback_name} already exists')
        

    def destroy(self) -> bool:
        """
        Destroys the loopback interface by removing its database entry and 
        deleting the OS-level dummy interface.

        Returns:
            bool: STATUS_OK if the loopback interface was successfully destroyed,
                  STATUS_NOK otherwise.
        """
        if Interface().del_db_interface(self.interface_name):
            self.log.error(f'Failed to delete interface {self.interface_name} from database')
            return STATUS_NOK
        
        if Interface().destroy_os_dummy_interface(self.interface_name):
            self.log.error(f'Failed to delete interface {self.interface_name} from OS')
            return STATUS_NOK
        
        return STATUS_OK

    def auto_inet_127_loopback(self) -> bool:
        """
        Automatically assign the next available 127.x.x.x address to the loopback interface.

        If the loopback interface does not have an assigned 127.x.x.x address,
        this method will find the next available address in the 127.x.x.x range
        and assign it to the loopback interface.

        Returns:
            bool: STATUS_OK if the address was successfully assigned, STATUS_NOK otherwise.
        """
        if not self._127_inet_address:
            next_available_127 = Interface().get_next_loopback_address()

            if not next_available_127:
                self.log.error('Unable to determine the next available 127.x.x.x address.')
                return STATUS_NOK

            if Interface().set_inet_address_loopback(self.interface_name, next_available_127):
                self.log.error(f'Unable to auto-assign: {next_available_127} to loopback: {self.get_interface_name()}')
                return STATUS_NOK

            self.log.debug(f'Auto Assign: {next_available_127} to loopback: {self.get_interface_name()} to OS')
            self._127_inet_address = next_available_127

        return STATUS_OK

    
    def add_inet_address(self, inet_address_cidr:InetCidrText, secondary_address:bool=False, negate:bool=False) -> bool:
        return STATUS_OK

# FILE: src/routershell/lib/network_manager/network_interfaces/network_interface.py

import logging

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import InterfaceName, MacAddressText
from routershell.lib.network_manager.common.interface import InterfaceType
from routershell.lib.network_manager.common.phy import State
from routershell.lib.network_manager.network_operations.interface import Interface


class NetworkInterface:
    """
    Base class for all network interfaces.

    This class serves as a parent class for specific types of network interfaces like loopback, Ethernet, and wireless interfaces.
    It provides a common interface name attribute and a logger for logging operations.

    Attributes:
        interface_name (str): The name of the network interface.
        log (logging.Logger): Logger for logging operations.
    """

    def __init__(self, interface_name: InterfaceName) -> None:
        """
        Initializes the NetworkInterface with the given interface name.

        Args:
            interface_name (str): The name of the network interface.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS.NETWORK_INTERFACE)
        self.interface_name = interface_name
        pass

    def set_description(self, description:str=None) -> bool:
        """
        Set the description for the network interface.

        Args:
            description (str, optional): The description to set for the network interface. Defaults to None.

        Returns:
            bool: True if the description is successfully updated, False otherwise (STATUS_NOK).
        """
        if Interface().update_db_description(self.interface_name, description):
            return STATUS_NOK
        
        return STATUS_OK

    def get_ifType(self) -> InterfaceType:
        """
        Retrieve the type of the network interface.

        Returns:
            InterfaceType: The type of the network interface.
        """
        return Interface().get_os_interface_type_extened(self.interface_name)

    def get_interface_name(self) -> str:
        """
        Retrieve the name of the network interface.

        Returns:
            str: The name of the network interface.
        """
        return self.interface_name

    def interface_exist_os(self) -> bool:
        """
        Check if the network interface exists in the operating system.

        This method verifies the existence of the network interface specified by `interface_name` in the operating system.

        Returns:
            bool: True if the interface exists, False otherwise.
        """
        return Interface().does_os_interface_exist(self.interface_name)

    def interface_exist_db(self) -> bool:
        """
        Check if the network interface exists in the database.

        Returns:
            bool: True if the interface exists in the database, False otherwise.
        """
        if self.interface_name in Interface().get_db_interface_names():
            return True
        return False

    def get_interface_shutdown_state(self) -> State:
        """
        Get the shutdown state of the network interface.

        Returns:
            State: The current shutdown state of the interface.
        """
        pass

    def set_interface_shutdown_state(self, state: State) -> bool:
        """
        Set the shutdown state of the network interface.

        Args:
            state (State): The desired shutdown state (UP or DOWN).

        Returns:
            bool: STATUS_OK if the state change is successful, STATUS_NOK otherwise.
        """
        pass
    
    def set_mac_address(self, mac_addr: MacAddressText | None = None) -> bool:
        """
        Set the MAC address of the network interface.

        If `mac_addr` is None, the interface is set to auto, which typically resets the MAC address to the default hardware address.

        Args:
            mac_addr (str, optional): The new MAC address to assign to the network interface. If None, the MAC address is reset to the default.

        Returns:
            bool: STATUS_OK if the MAC address is successfully updated, STATUS_NOK otherwise.
        """
        pass
    
    def add_inet_address(self, inet_address, secondary_address:bool=False, negate:bool=False) -> bool:
        """
        Add or modify an IP address on the network interface.

        Args:
            inet_address (str): The IP address to add or modify.
            secondary_address (bool, optional): Whether the IP address is a secondary address. Defaults to False.
            negate (bool, optional): Whether to remove the IP address if it exists. Defaults to False.

        Returns:
            bool: True if the IP address is successfully added or modified, False otherwise.
        """
        pass

# FILE: src/routershell/lib/network_manager/network_interfaces/network_interface_factory.py
import logging

from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import InterfaceName
from routershell.lib.network_manager.common.interface import InterfaceType
from routershell.lib.network_manager.network_interfaces.ethernet.ethernet_interface import EthernetInterface
from routershell.lib.network_manager.network_interfaces.loopback_interface import LoopbackInterface
from routershell.lib.network_manager.network_interfaces.wireless_wifi_interface import WirelessWifiInterface


class NetInterfaceFactoryError(Exception):
    def __init__(self, message):
        super().__init__(message)

class NetInterfaceFactory:
    """
    Factory class for creating and managing network interfaces.

    This class provides a factory mechanism for creating instances of different types of network interfaces such as
    loopback, Ethernet, and wireless interfaces. It ensures that only one instance of a particular interface is created
    and reused if requested again.

    Attributes:
        interface_name (str): The name of the network interface.
        log (logging.Logger): Logger for logging operations.

    Raises:
        NetInterfaceFactoryError: If required arguments are missing or invalid, or if the interface type is unsupported.
    """

    # Singleton {'interface_name': NetworkInterface}
    _net_interface_lookup_interface_name: dict[str, LoopbackInterface | EthernetInterface | WirelessWifiInterface] = {}

    def __init__(self, interface_name: InterfaceName, interface_type: InterfaceType):
        """
        Initializes the NetInterfaceFactory with the given interface name and type.

        Args:
            interface_name (str): The name of the network interface.
            interface_type (InterfaceType): The type of the network interface (e.g., LOOPBACK, ETHERNET, WIRELESS_WIFI).

        Raises:
            NetInterfaceFactoryError: If required arguments are missing or invalid, or if the interface type is unsupported.
        """
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS.NET_INTERFACE_FACTORY)
        self.interface_name = interface_name
        
        if not interface_name or not interface_type:
            raise NetInterfaceFactoryError('Arguments missing')
        
        if self.interface_name in NetInterfaceFactory._net_interface_lookup_interface_name:
            self.log.debug(f'Already created NetInterface Object for interface: {self.interface_name}')
        
        else:
            
            if interface_type == InterfaceType.LOOPBACK:
                network_interface_obj = LoopbackInterface(self.interface_name)
                
            elif interface_type == InterfaceType.ETHERNET:
                network_interface_obj = EthernetInterface(self.interface_name)
            
            elif interface_type == InterfaceType.WIRELESS_WIFI:
                network_interface_obj = WirelessWifiInterface(self.interface_name)
            
            else:
                raise NetInterfaceFactoryError(f"Unsupported interface type: {interface_type}")

            NetInterfaceFactory._net_interface_lookup_interface_name[self.interface_name] = network_interface_obj
            
    def getNetInterface(self) -> LoopbackInterface | EthernetInterface | WirelessWifiInterface:
        """
        Retrieve the NetworkInterface object associated with the specified interface name.

        Returns:
            LoopbackInterface | EthernetInterface | WirelessWifiInterface: The NetworkInterface object for the specified interface.
        """
        return NetInterfaceFactory._net_interface_lookup_interface_name[self.interface_name]
    
    @staticmethod
    def getNetInterface(interface_name: InterfaceName) -> LoopbackInterface | EthernetInterface | WirelessWifiInterface:
        """
        Retrieve the NetInterface object associated with the specified interface name.

        Args:
            interface_name (str): The name of the network interface.

        Returns:
            NetworkInterface (Base Object Class): The NetworkInterface object for the specified interface name.
        """
        return NetInterfaceFactory._net_interface_lookup_interface_name.get(interface_name)

# FILE: src/routershell/lib/network_manager/network_interfaces/vlan/vlan_mangement.py
import logging

from routershell.lib.common.constants import STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import VlanName
from routershell.lib.network_manager.network_operations.vlan import Vlan


class VlanMangementException(Exception):
    def __init__(self, message):
        super().__init__(message)

class VlanMangement:

    def __init__(self, vlan_id: int):
        """
        Initialize the VlanMangement with a VLAN ID.

        Args:
            vlan_id (int): The VLAN ID to be managed.

        Raises:
            VlanMangementException: If unable to add the VLAN ID to the database.
        """
        self._vlan_id = vlan_id
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().VLAN_CONFIG_CMD)

        if Vlan().add_vlan_id(vlan_id):
            self.log.error(f'Unable to insert/select VlanID: {vlan_id} to DB')
            raise VlanMangementException(f"Unable to add VlanID: {vlan_id} to DB")
        
        if Vlan().update_vlan_name(vlan_id, f'Vlan{vlan_id}'):
            self.log.error(f'Unable to update VlanID: {vlan_id} -> name: Vlan{vlan_id} to DB')
        
        self.log.debug(f'VlanMangement() Started - VlanID: {vlan_id}')
    
    def get_vlan_id(self) -> int:
        """
        Get the VLAN ID managed by the factory.

        Returns:
            int: The VLAN ID.
        """
        return self._vlan_id
    
    def set_name(self, vlan_name: VlanName) -> bool:
        """
        Set the name for the VLAN.

        Args:
            vlan_name (str): The name to be set for the VLAN.

        Returns:
            bool: True if the VLAN name was successfully updated, False otherwise.

        Raises:
            ValueError: If the vlan_name is None.
        """
        if vlan_name is None:
            raise ValueError("VLAN name cannot be None")
        
        return Vlan().update_vlan_name(self._vlan_id, vlan_name)

    def set_description(self, description: list[str] | None = None) -> bool:
        """
        Set the description for the VLAN.

        Args:
            description (list[str] | None): The description to be set for the VLAN. If None, it will be set as an empty string.
                                            If a list is provided, it will be joined into a single string with spaces.

        Returns:
            bool: True if the VLAN description was successfully updated, False otherwise.
        """
        if description is None:
            description_str = ""
        else:
            description_str = " ".join(description)

        return Vlan().update_vlan_description(self._vlan_id, description_str)

    def destroy_vlan(self) -> bool:
        return STATUS_OK


# FILE: src/routershell/lib/network_manager/network_interfaces/vlan/vlan_switchport_interface_abc.py
import logging
from abc import ABC

from routershell.lib.common.constants import STATUS_OK
from routershell.lib.common.types import InterfaceName
from routershell.lib.network_manager.network_operations.vlan import Vlan


class VlanSwitchport(ABC):
    """
    Abstract base class for managing VLAN switchport operations.
    
    Attributes:
        _interface_name (str): Name of the network interface.
        log (logging.Logger): Logger for the class.
    """
    
    def __init__(self, interface_name: InterfaceName):
        """
        Initializes the VlanSwitchport with a given interface name.
        
        Args:
            interface_name (str): The name of the network interface.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self._interface_name = interface_name
        
    def set_interface_to_vlan(self, vlan_id: int) -> bool:
        """
        Assigns the interface to a specified VLAN.
        
        Args:
            vlan_id (int): The VlanID.
        
        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """        
        return Vlan().add_interface_by_vlan_id(self._interface_name, vlan_id)
    
    def del_interface_from_vlan(self, vlan_if: int) -> bool:
        """
        Removes the interface from a specified VLAN.
        
        Args:
            vlan_name (str): The name of the VLAN.
        
        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        print('Not Implemented yet')
        return STATUS_OK

# FILE: src/routershell/lib/network_manager/network_interfaces/wireless_wifi_interface.py
import logging

from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import InterfaceName
from routershell.lib.network_manager.network_interfaces.network_interface import NetworkInterface


class WirelessWifiInterfaceError(Exception):
    def __init__(self, message):
        super().__init__(message)

class WirelessWifiInterface(NetworkInterface):

    def __init__(self, ethernet_name: InterfaceName):
        super().__init__(interface_name=ethernet_name)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().WIRELESS_WIFI_INTERFACE)        
            

# FILE: src/routershell/lib/network_manager/network_operations/arp.py
import json
import logging
from enum import Enum

from tabulate import tabulate

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import InetAddressText, InterfaceName, MacAddressText
from routershell.lib.network_manager.common.inet import InetServiceLayer
from routershell.lib.network_manager.common.sysctl import SysCtl
from routershell.lib.network_manager.network_operations.network_mgr import NetworkManager


class Encapsulate(Enum):
    """Enumeration of encapsulation types."""
    
    ARPA = 'arpa'
    """arpa Enables encapsulation for an Ethernet 802.3 network."""
    
    FRAME_RELAY = 'frame-relay'
    """frame-relay Enables encapsulation for a Frame Relay network."""
    
    SNAP = 'snap'
    """snap Enables encapsulation for FDDI and Token Ring networks."""

class ArpException(Exception):
    """Exception raised for ARP (Address Resolution Protocol) related errors."""

    def __init__(self, message="ARP error occurred"):
        self.message = message
        super().__init__(self.message)

class Arp(NetworkManager):
    """
    Class for managing ARP (Address Resolution Protocol) settings.

    Inherits from NetworkManager.
    """
    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().ARP)

    def is_arp_entry_exists(self, ip_address: InetAddressText, interface: InterfaceName | None = None) -> bool:
        """
        Check if an ARP entry already exists for a specific IP address on a given interface.

        Parameters:
            ip_address (str): The IP address to check.
            interface (str): The network interface to check. If None, checks all interfaces.

        Returns:
            bool: True if the ARP entry exists, False otherwise.
        """
        try:
            output = self.run(['ip', 'neighbor', 'show'])

            if output.exit_code == 0:
                arp_lines = output.stdout.strip().split('\n')

                for line in arp_lines:
                    words = line.split()

                    if ip_address in words:
                        if interface and interface in words or not interface:
                            return True
                return False
            else:
                self.log.error(f"Error executing 'ip neighbor show' command: {output.stderr}")
                return False
            
        except ArpException as e:
            self.log.error(f"Error: {e}")
            return False

    def arp_clear(self, ifName: InterfaceName = 'all') -> str:
        """
        Clears the ARP cache for a specific network interface or all interfaces.

        This method constructs and runs the appropriate command to flush the ARP cache 
        for a specified network interface if provided. If 'all' is specified, it will 
        flush the ARP cache for all interfaces.

        Args:
            ifName (str): The name of the network interface for which to flush 
                        the ARP cache. Default is 'all', which flushes the ARP cache 
                        for all interfaces.

        Returns:
            str: A status string indicating the result of the operation. STATUS_OK if the 
                command was successful, STATUS_NOK otherwise.
        """
        cmd = ['ip', 'neigh', 'flush']

        if ifName == 'all':
            cmd.append('all')
        else:
            cmd.extend(['dev', ifName])

        self.log.debug(f"CMD: {cmd}")

        result = self.run(cmd)

        return STATUS_OK if result.exit_code else STATUS_NOK

    def set_os_timeout(self, arp_time_out: int = 300) -> bool:
        """
        Sets the ARP cache timeout in the operating system.

        This method writes the given ARP cache timeout value to the system configuration
        using the `sysctl` interface. It sets the timeout value for the ARP cache entries.

        Args:
            arp_time_out (int): The desired timeout value for ARP cache entries in seconds.
                                Default is 300 seconds.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        sysctl_param = "net.ipv4.neigh.default.gc_stale_time"
        
        if SysCtl().write_sysctl(sysctl_param, str(arp_time_out)):
            print(f"Unable to set ARP cache timeout to {arp_time_out} seconds.")
            return STATUS_NOK
        else:
            print(f"Set ARP cache timeout to {arp_time_out} seconds.")
        
        return STATUS_OK

    def set_os_arp_accept(self, ifName: InterfaceName = "all", enable: bool = True) -> bool:
        """
        Sets the ARP accept mode for a specific network interface or all interfaces.

        This method writes the given ARP accept mode value to the system configuration
        file corresponding to the specified network interface. Enabling ARP accept mode
        allows the system to respond to ARP requests that match the host.

        Args:
            ifName (str): The name of the network interface for which to set ARP accept mode.
                        Default is "all", which applies the setting to all interfaces.
            enable (bool): If True, enables ARP accept mode. If False, disables ARP accept mode.
                        Default is True.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        arp_accept_file = f"/proc/sys/net/ipv4/conf/{ifName}/arp_accept"
        value = "1" if enable else "0"
        
        return SysCtl().write_sysctl(arp_accept_file, value)

        def set_os_arp_announce(self, ifName:InterfaceName, value:int) -> bool:
            """
            Set the ARP announce value for a specific network interface.

            :param ifName: The name of the network interface.
            :param value: The ARP announce value (0, 1, or 2).
            :return: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
            """
            arp_announce_file = f"/proc/sys/net/ipv4/conf/{ifName}/arp_announce"
            return SysCtl().write_sysctl(arp_announce_file, str(value))

    def set_os_arp_evict_nocarrier(self, ifName: InterfaceName = "all", enable: bool = True) -> bool:
        """
        Sets the ARP eviction behavior on carrier loss for a specific network interface or all interfaces.

        This method writes the given value to the system configuration file corresponding 
        to the specified network interface. Enabling ARP eviction on carrier loss causes 
        ARP entries to be removed when the carrier is lost.

        Args:
            ifName (str): The name of the network interface for which to set ARP eviction behavior.
                        Default is "all", which applies the setting to all interfaces.
            enable (bool): If True, enables ARP eviction on carrier loss. If False, disables it.
                        Default is True.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        arp_evict_file = f"/proc/sys/net/ipv4/conf/{ifName}/arp_evict_nocarrier"
        value = "1" if enable else "0"
        return SysCtl().write_sysctl(arp_evict_file, value)

    def set_os_arp_filter(self, ifName: InterfaceName = "all", enable: bool = True) -> bool:
        """
        Sets the ARP filtering behavior for a specific network interface or all interfaces.

        This method writes the given value to the system configuration file corresponding 
        to the specified network interface. Enabling ARP filtering allows the system to use 
        more stringent rules when selecting ARP responses.

        Args:
            ifName (str): The name of the network interface for which to set ARP filtering behavior.
                        Default is "all", which applies the setting to all interfaces.
            enable (bool): If True, enables ARP filtering. If False, disables it.
                        Default is True.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        arp_filter_file = f"/proc/sys/net/ipv4/conf/{ifName}/arp_filter"
        value = "1" if enable else "0"
        return SysCtl.write_sysctl(arp_filter_file, value)

    def set_os_arp_ignore(self, ifName: InterfaceName="all", enable: bool=True) -> bool:
        """
        Set the ARP ignore value for a specific network interface.

        :param ifName: The name of the network interface. Default is 'all' to apply to all interfaces.
        :param value: The ARP ignore value (0, 1, or 2).
        :return: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        arp_ignore_file = f"/proc/sys/net/ipv4/conf/{ifName}/arp_ignore"
        value = "1" if enable else "0"
        return SysCtl().write_sysctl(arp_ignore_file, str(value))

    def set_os_arp_notify(self, ifName: InterfaceName = "all", enable: bool = True) -> bool:
        """
        Enable or disable ARP notifications for a specific network interface.

        Args:
            ifName (str): The name of the network interface. Default is 'all' to apply to all interfaces.
            enable (bool): True to enable ARP notifications, False to disable them.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise. Most of the time, it will be one of these values.
        """
        arp_notify_file = f"/proc/sys/net/ipv4/conf/{ifName}/arp_notify"
        value = "1" if enable else "0"
        
        return SysCtl().write_sysctl(arp_notify_file, value)

    def set_os_drop_gratuitous_arp(self, if_name: InterfaceName = "all", enable: bool = True) -> bool:
        """
        Enable or disable the dropping of gratuitous ARP packets for a specific network interface.

        Args:
            ifName (str): The name of the network interface. Default is 'all' to apply to all interfaces.
            enable (bool): True to enable dropping of gratuitous ARP packets, False to disable it.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise. Most of the time, it will be one of these values.
        """

        value = "1" if enable else "0"
        arp_file = f"/proc/sys/net/ipv4/conf/{if_name}/drop_gratuitous_arp"
        
        command = ["sh", "-c", f"echo {value} > {arp_file}"]
        
        results = self.run(command)
        
        self.log.debug(f"set_drop_gratuitous_arp(ifname: {if_name} -> enable: {enable}) -> Cmd: {command}")
        
        if results.exit_code:
            self.log.error(f"Failed to set gratuitous ARP to {value} due to {results.stderr}")
            return STATUS_NOK
        else:
            self.log.debug(f"Set gratuitous ARP to {value}")
            return STATUS_OK

    def set_os_proxy_arp(self, if_name: InterfaceName = 'all', enable: bool = True) -> bool:
        """
        Enable or disable proxy ARP for a specific network interface.

        Args:
            ifName (str): The name of the network interface. Default is 'all' to apply to all interfaces.
            enable (bool): True to enable proxy ARP, False to disable it.

        Returns:
            bool: STATUS_OK for success, STATUS_NOK for failure.
        """       
        value = "1" if enable else "0"
        
        arp_file = f"/proc/sys/net/ipv4/conf/{if_name}/proxy_arp"
        
        command = ["sh", "-c", f"echo {value} > {arp_file}"]

        results = self.run(command)
        
        self.log.debug(f"set_proxy_arp(ifname: {if_name} -> enable: {enable}) -> Cmd: {command}")
        
        if results.exit_code:
            self.log.error(f"Failed to set proxy ARP to {value} due to {results.stderr}")
            return STATUS_NOK
        else:
            self.log.debug(f"Set proxy ARP to {value}")
            return STATUS_OK
            
    def set_os_proxy_arp_pvlan(self, ifName: InterfaceName, enable: bool) -> bool:
        """
        Enable or disable proxy ARP for Private VLAN (PVLAN) on a specific network interface.

        Args:
            ifName (str): The name of the network interface.
            enable (bool): True to enable proxy ARP for PVLAN, False to disable it.

        Returns:
            bool: STATUS_OK for success, STATUS_NOK for failure.
        """

        proxy_arp_pvlan_file = f"/proc/sys/net/ipv4/conf/{ifName}/proxy_arp_pvlan"
        value = "1" if enable else "0"
        
        self.log.debug(f"set_proxy_arp(ifname: {ifName}) -> File: {proxy_arp_pvlan_file} -> enable: {enable}")
                
        return SysCtl().write_sysctl(proxy_arp_pvlan_file, value)

    def set_os_static_arp(self, interface_name:InterfaceName, inet:InetAddressText, mac_address:MacAddressText, encap:Encapsulate=Encapsulate.ARPA, add_arp_entry:bool=True) -> bool:
        """
        Configure or remove a static ARP entry using iproute2.

        Args:
            interface_name (str): The name of the network interface.
            inet (str): The IPv4 address for the static ARP entry.
            mac_address (str): The MAC address for the static ARP entry.
            encap (Encapsulate, optional): The ARP encapsulation type (default is ARPA).
            add_arp_entry (bool, optional): True to configure the entry (default), False to remove it.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.

        Note:
            - To configure a static ARP entry, set `enable` to True.
            - To remove a static ARP entry, set `enable` to False.
        """
        self.log.debug(f"set_os_static_arp() interface: {interface_name} -> inet: {inet} -> mac: {mac_address} -> encap: {encap} -> add-arp: {add_arp_entry}")
        arp_entry_action='add'
        
        if not InetServiceLayer().is_valid_ipv4(inet):
            self.log.error(f"Invalid Inet Address -> ({inet})")
            return STATUS_NOK
            
        status, mac_address = self.format_mac_address(mac_address)
        
        if not status:
            self.log.error(f"Invalid Mac Address -> ({mac_address})")
            return STATUS_NOK
        
        if not add_arp_entry:
           arp_entry_action='del' 
        
        command = ['ip', 'neigh', arp_entry_action, inet, 'lladdr', mac_address, 'dev', interface_name]
        
        self.log.debug(f"Static ARP CMD: {command}")
        
        results = self.run(command, suppress_error=True)
        
        if results.exit_code:
            self.log.error(f"Unable to set static arp entry {inet} -> {mac_address} : {results.stderr}")
            return STATUS_NOK
        
        self.log.debug(f"set_static_arp(ifName: {interface_name}) -> inet: {inet} -> mac: {mac_address}")
        return STATUS_OK
            
    def get_arp(self, args: list[str] | None = None) -> None:
        """
        Retrieves the ARP table and prints it in a formatted table.

        This method runs the 'ip -json neighbor show' command to fetch the ARP table
        and processes the JSON output to display it in a readable format using the
        'tabulate' library.

        Args:
            args (list[str] | None): Additional arguments to pass to the 'ip' command.
                                        Default is None.

        Raises:
            ArpException: If an error occurs while executing the command.
        """
        try:
            self.log.debug("get_arp()")

            # Run the 'ip -json neighbor show' command and capture the output
            cmd = ['ip', '-json', 'neighbor', 'show']
            if args:
                cmd.extend(args)

            output = self.run(cmd, suppress_error=True)

            self.log.debug(f"get_arp() stderr: ({output.stderr}) -> exit_code: ({output.exit_code}) -> stdout: \n{output.stdout}")

            if output.exit_code == 0:
                # Parse the JSON output
                arp_entries: list[dict[str, object]] = json.loads(output.stdout)

                self.log.debug(f"get_arp() JSON Arp Entries: {arp_entries}")

                # Define headers for the ARP table
                headers = ["IP Address", "Device", "MAC Address", "State"]

                if not arp_entries:
                    # Print an empty table with headers
                    print(tabulate([], headers=headers, tablefmt='simple', colalign=("left", "left", "left", "left")))
                    print("ARP table is empty.")
                    return None

                # Transform the JSON data into a list of lists (rows) for tabulate
                arp_table = [
                    [entry.get("dst", ""), entry.get("dev", ""), entry.get("lladdr", ""), entry.get("state", "")]
                    for entry in arp_entries
                ]

                # Pretty-print the ARP table using the 'tabulate' library
                table = tabulate(arp_table, headers=headers, tablefmt='simple', colalign=("left", "left", "left", "left"))

                # Print the formatted ARP table
                print(table)
            else:
                print(f"Error executing 'ip -json neighbor show' command: {output.stderr}")
        except Exception as e:
            raise ArpException(f"Error: {e}")

# FILE: src/routershell/lib/network_manager/network_operations/bridge.py
import json
import logging

from routershell.lib.common.common import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import BridgeName, InterfaceName
from routershell.lib.db.bridge_db import BridgeDatabase
from routershell.lib.network_manager.common.phy import State
from routershell.lib.network_manager.common.run_commands import RunCommand
from routershell.lib.network_manager.network_interfaces.bridge.bridge_protocols import STP_STATE, BridgeProtocol


class Bridge(RunCommand, BridgeDatabase):

    def __init__(self):
        super().__init__()
        BridgeDatabase().__init__()
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().BRIDGE)
        
    def get_bridge_list_os(self) -> list[str]:
        """
        Get a list of bridge names from OS

        Returns:
            list[str]: A list of bridge names.
        """
        result = self.run(['ip', '-j', 'link', 'show', 'type', 'bridge'])

        if result.exit_code:
            self.log.error("Unable to get bridge list")
            return []

        try:
            bridge_links = json.loads(result.stdout)
            bridge_names = [link['ifname'] for link in bridge_links]
            return bridge_names
        
        except json.JSONDecodeError as e:
            self.log.debug(f"Failed to parse JSON: {e}")
            return []
        
        except KeyError as e:
            self.log.debug(f"Unexpected data format: {e}")
            return []

    def add_bridge(self, bridge_name: BridgeName, fix_os_db_inconsistency: bool = False) -> bool:
        """
        Adds a bridge to both the operating system (OS) and the database (DB).

        If the bridge already exists in either the OS or the DB, it checks for inconsistencies 
        and can optionally fix them based on the `fix_os_db_inconsistency` flag.

        Args:
            bridge_name (str): The name of the bridge to add.
            fix_os_db_inconsistency (bool): Flag to indicate if inconsistencies between 
                                            the OS and DB should be fixed.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        if self._does_bridge_exist_os(bridge_name):
            return self._handle_bridge_os_db_inconsistencies(bridge_name, fix_os_db_inconsistency, os_exists=True)
        
        elif self.does_bridge_exists_db(bridge_name):
            return self._handle_bridge_os_db_inconsistencies(bridge_name, fix_os_db_inconsistency, os_exists=False)
        
        else:
            self.log.debug(f"Adding bridge {bridge_name} to both OS and DB")
            if self._add_bridge_os(bridge_name):
                self.log.error(f'Unable to add bridge {bridge_name} to OS')
                return STATUS_NOK
            
            if self.add_bridge_db(bridge_name):
                self.log.error(f'Unable to add bridge {bridge_name} to DB')
                return STATUS_NOK                
        
        return STATUS_OK

    def update_bridge(self, bridge_name: BridgeName, 
                        protocol: BridgeProtocol | None = None, 
                        stp_status: STP_STATE | None = None,
                        management_inet: str | None = None,
                        description: str | None = None,
                        shutdown_status: State | None = None) -> bool:
        """
        Update the bridge configuration both on the operating system and in the database.

        This method performs the following actions:
        1. Updates the bridge on the operating system.
        2. Updates the bridge in the database with the new configuration.

        Args:
            bridge_name (str): The name of the bridge to update.
            protocol (BridgeProtocol | None): The new protocol for the bridge. Defaults to None.
            stp_status (STP_STATE | None): The new STP status for the bridge. Defaults to None.
            management_inet (str | None): The management IP address for the bridge. Defaults to None.
            description (str | None): The new description for the bridge. Defaults to None.
            shutdown_status (State | None): The new shutdown status for the bridge. Defaults to None.

        Returns:
            bool: STATUS_OK if both OS and DB updates were successful, STATUS_NOK otherwise.
        """
        # Update the bridge on the operating system
        if self._update_bridge_via_os(bridge_name, protocol, stp_status, management_inet, shutdown_status):
            self.log.error(f"Failed to update bridge {bridge_name} on OS")
            return STATUS_NOK

        # Update the bridge in the database
        update_result = self.update_bridge_db(
            bridge_name=bridge_name,
            protocol=protocol,
            stp_status=stp_status,
            management_inet=management_inet,
            description=description,
            shutdown_status=shutdown_status
        )
        
        if update_result:
            self.log.error(
                f"Failed to update bridge {bridge_name} in DB with parameters: "
                f"protocol={protocol}, stp_status={stp_status}, "
                f"management_inet={management_inet}, description={description}, "
                f"shutdown_status={shutdown_status}"
            )
            return STATUS_NOK

        self.log.debug(f"Bridge {bridge_name} successfully updated in both OS and DB")
        return STATUS_OK

    def get_shutdown_status_os(self, bridge_name: BridgeName) -> State:
        """
        Retrieve the shutdown status of a bridge from the operating system.

        Args:
            bridge_name (str): The name of the bridge to query.

        Returns:
            State: The shutdown status of the bridge (UP, DOWN, UNKNOWN).
        """
        # Execute the command and capture the output
        result = self.run(['ip', '-j', 'link', 'show', bridge_name])
        
        if result.exit_code != 0:
            self.log.error(f"Failed to get status for bridge {bridge_name}: {result.stderr}")
            return State.UNKNOWN

        # Parse the JSON output
        try:
            bridges = json.loads(result.stdout)
            for bridge in bridges:
                if bridge.get('ifname') == bridge_name:
                    # Check the 'operstate' field for status
                    operstate = bridge.get('operstate')
                    if operstate == 'down':
                        return State.DOWN
                    elif operstate == 'up':
                        return State.UP
                    else:
                        return State.UNKNOWN
        except json.JSONDecodeError as e:
            self.log.error(f"Failed to parse JSON output for bridge {bridge_name}: {e}")
            return State.UNKNOWN

        return State.UNKNOWN

    def get_bridge_stp_status_os(self, bridge_name: BridgeName) -> STP_STATE:
        """
        Retrieve the STP status of a bridge from the operating system.

        Args:
            bridge_name (str): The name of the bridge to query.

        Returns:
            STP_STATE: The STP status of the bridge (STP_DISABLE or STP_ENABLE).
        """
        # Execute the command and capture the output
        result = self.run(['bridge', 'stp', 'show', bridge_name, '-json'])

        if result.exit_code != 0:
            self.log.error(f"Failed to get STP status for bridge {bridge_name}: {result.stderr}")
            return STP_STATE.STP_DISABLE  # Default to STP_DISABLE if there's an error

        # Parse the output to determine the STP status
        output = result.stdout
        try:
            # Assuming output is a JSON string and we need to parse it
            import json
            status_info = json.loads(output)

            # Check if 'stp_state' field is present and determine the status
            stp_state = status_info.get('stp_state', None)
            if stp_state == 'enabled':
                return STP_STATE.STP_ENABLE
            elif stp_state == 'disabled':
                return STP_STATE.STP_DISABLE
            else:
                return STP_STATE.STP_DISABLE  # Default to STP_DISABLE if state is unknown
        except (json.JSONDecodeError, KeyError) as e:
            self.log.error(f"Error parsing STP status for bridge {bridge_name}: {e}")
            return STP_STATE.STP_DISABLE

    def del_bridge(self, bridge_name: BridgeName) -> bool:
        """
        Delete a bridge from the operating system and the database.

        This method performs the following actions:
        1. Attempts to delete the bridge from the operating system using `_del_bridge_via_os`.
        2. If successful, proceeds to delete the bridge from the database using `del_bridge_db`.
        3. Returns `STATUS_OK` if both operations are successful, or `STATUS_NOK` if any operation fails.

        Args:
            bridge_name (str): The name of the bridge to delete.

        Returns:
            bool: `STATUS_OK` if the bridge was successfully deleted from both the OS and the DB,
                `STATUS_NOK` otherwise.
        """
        if self._del_bridge_via_os(bridge_name):
            self.log.error(f'Failed to delete bridge {bridge_name} from OS')
            return STATUS_NOK
        
        if self.del_bridge_db(bridge_name):
            self.log.error(f"Failed to delete bridge {bridge_name} from DB")
            return STATUS_NOK
        
        return STATUS_OK
    
    def does_bridge_exist(self, bridge_name: BridgeName) -> bool:
        """
        Check if a bridge exists both on the operating system and in the database.

        This method performs the following checks:
        1. Verifies if the bridge exists on the operating system.
        2. Checks if the bridge also exists in the database.

        Args:
            bridge_name (str): The name of the bridge to check.

        Returns:
            bool: True if the bridge exists on the operating system and does not exist in the database, 
                indicating that it needs to be added to the database. False otherwise.
        """
        if not self._does_bridge_exist_os(bridge_name):
            self.log.debug(f'Bridge {bridge_name} does not exist on OS')
            
            if self.does_bridge_exists_db(bridge_name):
                self.log.warn(f'Bridge {bridge_name} does exists in DB, but not in OS')            
            
            return False
        
        if not self.does_bridge_exists_db(bridge_name):
            self.log.debug(f'Bridge {bridge_name} does not exists in DB, but does in OS')
            return False

        self.log.debug(f'Bridge {bridge_name} does exists in both OS and DB')
        
        return True

    def add_interface_to_bridge_group(self, interface_name: InterfaceName, bridge_group: BridgeName) -> bool:
        """
        Adds a specified network interface to a bridge group both in the OS and the database.

        This method first attempts to add the interface to the bridge group using OS commands.
        If successful, it then updates the bridge group information in the database.
        Logs an error message if either operation fails and returns a status indicating success
        or failure.

        Args:
            interface_name (str): The name of the network interface to add to the bridge group.
            bridge_group (str): The name of the bridge group to which the interface should be added.

        Returns:
            bool: STATUS_OK if the interface was successfully added to the bridge group in both 
                the OS and the database, STATUS_NOK otherwise.
        """
        if self._add_interface_to_bridge_group_os(interface_name, bridge_group):
            self.log.error(f'Failed to add interface {interface_name} to bridge group {bridge_group} to OS')
            return STATUS_NOK
        
        if self.update_interface_bridge_group_db(interface_name, bridge_group, remove=False):
            self.log.error(f"Failed to update interface {interface_name} bridge group {bridge_group} to DB")
            return STATUS_OK
        
        return STATUS_OK

    def del_interface_to_bridge_group(self, interface_name: InterfaceName, bridge_group: BridgeName) -> bool:
        """
        Deletes a specified network interface from a bridge group.

        This method removes the given interface from the specified bridge group using OS commands.
        It then updates the database to reflect this change. If any step fails, it logs an error message
        and returns a status indicating the failure.

        Args:
            interface_name (str): The name of the network interface to remove from the bridge group.
            bridge_group (str): The name of the bridge group from which the interface should be removed.

        Returns:
            bool: STATUS_OK if the interface was successfully removed from the bridge group,
                STATUS_NOK otherwise.
        """

        if not self._del_interface_from_bridge_group_os(interface_name, bridge_group):
            self.log.error(f'Failed to remove interface {interface_name} from bridge group {bridge_group} in the OS')
            return STATUS_NOK

        if not self.update_interface_bridge_group_db(interface_name, bridge_group, remove=True):
            self.log.error(f"Failed to update interface {interface_name} bridge group {bridge_group} in the DB")
            return STATUS_NOK

        return STATUS_OK

    def _add_interface_to_bridge_group_os(self, interface_name: InterfaceName, bridge_group: BridgeName) -> bool:
        """
        Adds a specified network interface to a bridge group using OS commands.

        This private method constructs and executes an `ip` command to set the given
        interface as a member of the specified bridge group. It first checks if the 
        interface is already attached to any bridge group and verifies if it needs to 
        be removed before adding it to the new bridge group. It logs appropriate messages 
        and returns a status indicating success or failure.

        Args:
            interface_name (str): The name of the network interface to add to the bridge group.
            bridge_group (str): The name of the bridge group to which the interface should be added.

        Returns:
            bool: STATUS_OK if the interface was successfully added to the bridge group, 
                STATUS_NOK otherwise.
        """
        if self._is_interface_attached_to_any_bridge_group_os(interface_name):
            self.log.debug(f'Interface {interface_name} is already attached to a bridge group.')

            if self._is_interface_attached_to_bridge_group_os(interface_name, bridge_group):
                self.log.debug(f'Interface {interface_name} is already attached to bridge group {bridge_group}')
                return STATUS_OK
            else:
                self.log.debug(f'Interface {interface_name} is attached to a different bridge group. Must remove it before adding to {bridge_group}')
                return STATUS_NOK

        result = self.run(['ip', 'link', 'set', 'dev', interface_name, 'master', bridge_group])
        if result.exit_code:
            self.log.error(f'Failed to add interface {interface_name} to bridge group {bridge_group}, error: {result.stderr}')
            return STATUS_NOK
        return STATUS_OK

    def _is_interface_attached_to_bridge_group_os(self, interface_name: InterfaceName, bridge_group: BridgeName) -> bool:
        """
        Checks if a specified network interface is attached to a specific bridge group using OS commands with JSON output.

        This private method constructs and executes an `ip` command with the `-json` option to verify if the given
        interface is a member of the specified bridge group. It returns a boolean indicating whether the interface 
        is attached to the specified bridge group.

        Args:
            interface_name (str): The name of the network interface to check.
            bridge_group (str): The name of the bridge group to check against.

        Returns:
            bool: True if the interface is attached to the specified bridge group, False otherwise.
        """
        command = ['ip', '-j', 'link', 'show', interface_name]
        result = self.run(command)
        if result.exit_code:
            self.log.error(f'Failed to retrieve information for interface {interface_name}, error: {result.stderr}')
            return False

        try:
            import json
            interface_info = json.loads(result.stdout)
            
            # Check if the interface has a 'master' key and if the master bridge group matches
            if interface_info and 'master' in interface_info[0] and interface_info[0]['master'] == bridge_group:
                return True
        except json.JSONDecodeError:
            self.log.error(f'Failed to parse JSON output for interface {interface_name}')
            return False

        return False

    def _is_interface_attached_to_any_bridge_group_os(self, interface_name: InterfaceName) -> bool:
        """
        Checks if a specified network interface is attached to any bridge group using OS commands with JSON output.

        This private method constructs and executes an `ip` command with the `-json` option to verify if the given
        interface is a member of any bridge group. It returns a boolean indicating whether the interface is attached
        to any bridge group.

        Args:
            interface_name (str): The name of the network interface to check.

        Returns:
            bool: True if the interface is attached to any bridge group, False otherwise.
        """
        command = ['ip', '-j', 'link', 'show', interface_name]
        result = self.run(command)
        if result.exit_code:
            self.log.error(f'Failed to retrieve information for interface {interface_name}, error: {result.stderr}')
            return False

        try:
            import json
            interface_info = json.loads(result.stdout)
            
            # Check if the interface has a 'master' key indicating it is part of a bridge group
            if 'master' in interface_info[0] and interface_info[0]['master']:
                return True
        except json.JSONDecodeError:
            self.log.error(f'Failed to parse JSON output for interface {interface_name}')
            return False

        return False

    def _del_interface_from_bridge_group_os(self, interface_name: InterfaceName, bridge_group: BridgeName) -> bool:
        """
        Removes a specified network interface from a bridge group using OS commands.

        This private method constructs and executes an `ip` command to remove the given
        interface from the specified bridge group. It logs an error message if the 
        command fails and returns a status indicating success or failure.

        Args:
            interface_name (str): The name of the network interface to remove from the bridge group.
            bridge_group (str): The name of the bridge group from which the interface should be removed.

        Returns:
            bool: STATUS_OK if the interface was successfully removed from the bridge group, 
                STATUS_NOK otherwise.
        """
        command = ['ip', 'link', 'set', 'dev', interface_name, 'nomaster']
        result = self.run(command)
        if result.exit_code:
            self.log.error(f'Failed to remove interface {interface_name} from bridge group {bridge_group}. error: {result.stderr}')
            return STATUS_NOK
        return STATUS_OK

    def _does_bridge_exist_os(self, bridge_name:BridgeName, suppress_error=False) -> bool:
        """
        Check if a bridge with the given name exists via iproute.
        Will also remove bridge name in db if the interface is not available

        Args:
            bridge_name (str): The name of the bridge to check.

        Returns:
            bool: True if the bridge exists, False otherwise.
        """
        self.log.debug(f"_does_bridge_exist_os() -> Checking bridge name exists: {bridge_name}")
        
        output = self.run(['ip', 'link', 'show', 'dev', bridge_name], suppress_error=True)
        
        if output.exit_code:
            self.log.debug(f"_does_bridge_exist_os(return:{False}) -> Bridge does NOT exist: {bridge_name} - iproute: exit-code: {output.exit_code}")
            return False
            
        self.log.debug(f"_does_bridge_exist_os(exit-code({output.exit_code})) -> Bridge does exist: {bridge_name}")
        return True

    def _del_bridge_via_os(self, bridge_name: BridgeName) -> bool:
        """
        Delete a bridge from the operating system. If there are any interfaces linked to the bridge,
        they will be unlinked before the bridge is deleted.

        This method first checks if the bridge exists on the OS. If it does, it will also ensure that
        all interfaces linked to the bridge are unlinked before attempting to delete the bridge itself.

        Args:
            bridge_name (str): The name of the bridge to delete.

        Returns:
            bool: STATUS_OK if the bridge was successfully deleted from the OS, STATUS_NOK otherwise.
        """
        if not self._does_bridge_exist_os(bridge_name):
            self.log.debug(f"Bridge {bridge_name} does not exist on OS. No deletion performed.")
            return STATUS_NOK

        linked_interfaces = self._get_linked_interfaces(bridge_name)
        
        if linked_interfaces:
            self.log.debug(f"Unlinking interfaces {linked_interfaces} from bridge {bridge_name}")
            for iface in linked_interfaces:
                result = self.run(['ip', 'link', 'set', iface, 'nomaster'], suppress_error=True)
                if result.exit_code:
                    self.log.error(f"Failed to unlink interface {iface} from bridge {bridge_name}")
                    return STATUS_NOK
        
        result = self.run(['ip', 'link', 'delete', bridge_name, 'type', 'bridge'], suppress_error=True)
        
        if result.exit_code:
            self.log.error(f"Failed to delete bridge {bridge_name} from OS")
            return STATUS_NOK            
        
        self.log.debug(f"Bridge {bridge_name} successfully deleted from OS")
        return STATUS_OK
        
    def _get_linked_interfaces(self, bridge_name: BridgeName) -> list[str]:
        """
        Retrieve a list of interfaces linked to the given bridge using JSON output for parsing.

        Args:
            bridge_name (str): The name of the bridge to check.

        Returns:
            list[str]: A list of interface names that are linked to the bridge.
        """
        result = self.run(['ip','-json','show', 'master', bridge_name], suppress_error=True)
        
        if result.exit_code:
            self.log.debug(f"Failed to retrieve linked interfaces for bridge {bridge_name}")
            return []

        try:
            data = json.loads(result.stdout)
            interfaces = [entry['ifname'] for entry in data if 'ifname' in entry]
            
        except json.JSONDecodeError as e:
            self.log.error(f"Failed to parse JSON for bridge {bridge_name}: {e}")
            return []

        return interfaces

    def _update_bridge_via_os(self, bridge_name: BridgeName, 
                            protocol: BridgeProtocol | None = None, 
                            stp_status: STP_STATE | None = None,
                            management_inet: str | None = None,
                            shutdown_status: State | None = None) -> bool:
        """
        Update a bridge on the operating system with the specified parameters.

        This method updates the bridge's protocol, STP status, management IP address, 
        and shutdown status on the operating system.

        Args:
            bridge_name (str): The name of the bridge to update.
            protocol (BridgeProtocol | None): The new protocol for the bridge. Defaults to None.
            stp_status (STP_STATE | None): The new STP status for the bridge. Defaults to None.
            management_inet (str | None): The management IP address for the bridge. Defaults to None.
            shutdown_status (State | None): The new shutdown status for the bridge. Defaults to None.

        Returns:
            bool: True if the bridge was successfully updated, False otherwise.
        """
        if not self._does_bridge_exist_os(bridge_name):
            self.log.debug(f"Bridge {bridge_name} does not exist on OS. No update performed.")
            return STATUS_NOK

        if protocol is None and stp_status is None and management_inet is None and shutdown_status is None:
            self.log.debug('_update_bridge_via_os() - All Arguments None - no action needed')
            return STATUS_OK
        
        cmd = []

        if protocol:
            self.log.debug('Bridge Protocol is not supported with iproute')
            
        if stp_status:
            stp_command = '1' if stp_status == STP_STATE.STP_ENABLE else '0'
            cmd.append(['ip', 'link', 'set', 'dev', bridge_name, 'type','bridge', 'stp_state', stp_command])

        if management_inet:
            cmd.append(['ip', 'addr', 'add', management_inet, 'dev', bridge_name])
        
        if shutdown_status:
            shutdown_command = 'down' if shutdown_status == State.DOWN else 'up'
            cmd.append(['ip', 'link', 'set', 'dev', bridge_name, shutdown_command])

        for command in cmd:
            self.log.debug(f'_update_bridge_via_os() -> cmd: {" ".join(command)}')
            result = self.run(command)
            
            if result.exit_code != 0:            
                self.log.error(f"Failed to update bridge {bridge_name} on OS: {result.stderr.strip()}")
                return STATUS_NOK

        self.log.debug(f"Bridge {bridge_name} successfully updated on OS")
        return STATUS_OK
  
    def _handle_bridge_os_db_inconsistencies(self, bridge_name: BridgeName, fix_os_db_inconsistency: bool, os_exists: bool) -> bool:
        """
        Handles inconsistencies between the operating system (OS) and the database (DB) for a bridge.

        Args:
            bridge_name (str): The name of the bridge.
            fix_os_db_inconsistency (bool): Flag to indicate if inconsistencies should be fixed.
            os_exists (bool): Flag indicating if the bridge exists in the OS.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        if os_exists:
            self.log.debug(f"Bridge {bridge_name} already exists in the OS")
            if not self.does_bridge_exists_db(bridge_name):
                self.log.debug(f"Bridge {bridge_name} does not exist in the database")
                self.log.critical(f'Inconsistency between the OS and DB: bridge {bridge_name} not found in the DB but found in the OS')

                if fix_os_db_inconsistency:
                    self.log.debug("Fixing the DB to match the OS")
                    if self.add_bridge_db(bridge_name):
                        return STATUS_OK
                    return STATUS_NOK
                return STATUS_NOK
        else:
            self.log.debug(f"Bridge {bridge_name} does not exist in the OS but exists in the database")

            if fix_os_db_inconsistency:
                self.log.debug("Fixing the OS to match the DB")
                if self.del_bridge_db(bridge_name):
                    if self._add_bridge_os(bridge_name):
                        self.add_bridge_db(bridge_name)
                        return STATUS_OK
                return STATUS_NOK
            return STATUS_NOK

    def _add_bridge_os(self, bridge_name: BridgeName) -> bool:
        """
        Create a bridge with Spanning Tree Protocol (STP) enabled.

        Args:
            bridge_name (str): The name of the bridge to create.

        Returns:
            bool: STATUS_OK if the bridge is created with STP enabled successfully, STATUS_NOK if creation fails.
        """
        self.log.debug(f"_add_bridge_os() -> Adding bridge: {bridge_name} to OS")
        
        result = self.run(['ip', 'link', 'add', 'name', bridge_name, 'type', 'bridge'])
        
        if result.exit_code:
            self.log.warning(f"Bridge {bridge_name} cannot be created - exit-code: {result.exit_code}")
            return STATUS_NOK

        self.log.debug(f"_add_bridge_os() -> Added bridge: {bridge_name} to OS")
        return STATUS_OK
                       

# FILE: src/routershell/lib/network_manager/network_operations/dhcp/client/dhcp_client.py
import logging
import re

from routershell.lib.common.constants import STATUS_NOK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import InterfaceName
from routershell.lib.db.dhcp_client_db import DHCPClientDatabase
from routershell.lib.network_manager.network_operations.dhcp.client.supported_dhcp_clients import (
    DHCPClientFactory,
    DHCPClientOperations,
)
from routershell.lib.network_manager.network_operations.dhcp.common.dhcp_common import DHCPStackVersion, DHCPStatus
from routershell.lib.system.init_system import InitSystemChecker, SysV


class DHCPClientException(Exception):
    """
    Custom exception for DHCP client operations.

    Attributes:
        message (str): Error message for the exception.
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"DHCPClientException: {self.message}"

class DHCPClient(DHCPClientDatabase):
    """
    A class for managing DHCP client operations on a network interface.

    This class provides methods to start, stop, and restart DHCP clients for IPv4,
    IPv6, or dual stack configurations on a specific network interface. It also retrieves
    DHCP client flow logs.

    Attributes:
        _interface_name (str): The name of the network interface.
        _dhcp_stack_version (DHCPStackVersion): The DHCP stack version to use.
        _dhcp_client (DHCPClientOperations): The specific DHCP client instance for the network interface.
        _last_status (DHCPClientStatus): The last status of the DHCP client.

    Methods:
        start(): Start the DHCP client with the configured stack version.
        stop(): Stop the DHCP client.
        restart(): Restart the DHCP client service.
        get_flow_log(): Retrieve DHCP client flow logs from the system journal.
        get_last_status(): Get the last status of the DHCP client.
    """
    def __init__(self, interface_name: InterfaceName, dhcp_stack_version: DHCPStackVersion):
        """
        Initialize the DHCPClient with the network interface name and DHCP stack version.

        Args:
            interface_name (str): The name of the network interface.
            dhcp_stack_version (DHCPStackVersion): The DHCP stack version to use.
        """
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DHCP_CLIENT)
        
        self._interface_name = interface_name
        self._dhcp_stack_version = dhcp_stack_version
        
        self._dhcp_client : DHCPClientOperations = DHCPClientFactory().get_supported_dhcp_client(interface_name, dhcp_stack_version)
    
    def get_last_status(self) -> DHCPStatus:
        """
        Get the last status of the DHCP client.

        Returns:
            DHCPClientStatus: The last status of the DHCP client.
        """
        return self._dhcp_client.get_last_status()
                
    def start(self) -> bool:
        """
        Start the DHCP client with the configured stack version.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        self.log.debug(f'Start DHCP client on interface {self._dhcp_client.get_interface()}')
        if self._dhcp_client.start():
            return STATUS_NOK
        
        return self.update_db_dhcp_client(self._dhcp_client.get_interface(), self._dhcp_stack_version)
        
    def stop(self) -> bool:
        """
        Stop the DHCP client.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        self.log.debug(f'Stop DHCP client on interface {self._dhcp_client.get_interface()}')
        if self._dhcp_client.stop():
            return STATUS_NOK
        
        return self.remove_db_dhcp_client(self._dhcp_client.get_interface(), self._dhcp_stack_version.value)
    
    def restart(self) -> bool:
        """
        Restart the DHCP client service.

        Returns:
            bool: STATUS_OK if the DHCP client service restart was successful, STATUS_NOK otherwise.
        """        
        return self._dhcp_client.restart()

    @staticmethod
    def get_flow_log() -> list[dict]:
        """
        Retrieve DHCP client flow logs (DORA/SAAR) from the system journal.

        Returns:
            list[dict]: A list of DHCP client flow log entries.
        """
        isc = InitSystemChecker()
        
        if isc.is_sysv():
            dhcp_msgs = SysV().get_messages("DHCP")
            return [DHCPClientLogParser.parse_log_line(line) for line in dhcp_msgs if line.strip()]
                    
        elif isc.is_systemd():
            return []
            
        return []

class DHCPClientLogParser:
    
    @staticmethod
    def parse_log_line(line: str) -> dict:
        """
        Parses a single log line into its components.

        Args:
            line (str): The log line to parse.

        Returns:
            dict: A dictionary with the parsed components.
        """
        # Example log line:
        # Jul 26 14:48:41 Router daemon.info dnsmasq-dhcp[573]: DHCPDISCOVER(eth4) 192.168.100.90 94:c6:91:15:14:3e
        regex = (r"(?P<timestamp>\w+\s+\d+\s+\d+:\d+:\d+)\s+"
                 r"(?P<host>\w+).*"
                 r"(?P<dhcp>DHCPDISCOVER|DHCPOFFER|DHCPREQUEST|DHCPACK)"
                 r"\((?P<interface>\w+)\)\s+"
                 r"(?P<ip_address>\d+\.\d+\.\d+\.\d+)?\s*"
                 r"(?P<mac_address>[0-9a-f:]{17})")
                
        match = re.match(regex, line)
        
        if match:
            return match.groupdict()
        
        return {}

# FILE: src/routershell/lib/network_manager/network_operations/dhcp/client/dhcp_clinet_interface_abc.py

import logging
from abc import ABC

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import InterfaceName
from routershell.lib.network_manager.common.phy import State
from routershell.lib.network_manager.network_operations.dhcp.client.dhcp_client import DHCPClient
from routershell.lib.network_manager.network_operations.dhcp.common.dhcp_common import DHCPStackVersion


class DHCPInterfaceClient(ABC):
    def __init__(self, interface_name:InterfaceName):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DHCP_INTERFACE_CLIENT)
        self._interface_name = interface_name

    def update_interface_dhcp_client(self, dhcp_stack_ver: DHCPStackVersion, dhcp_client_state: State) -> bool:
        """
        Update the DHCP configuration for a network interface via OS.
        Update the DHCP configuration for a network interface via DB.
        
        Args:
            interface_name (str): The name of the network interface.
            dhcp_stack_ver (DHCPStackVersion): The DHCP version (DHCP_V4 or DHCP_V6).
            dhcp_client_state (State): If DOWN, disable DHCP; if UP, enable DHCP.

        Returns:
            bool: STATUS_OK for success, STATUS_NOK for failure.

        """
        try:
            dhcp_client = DHCPClient(self._interface_name, dhcp_stack_ver)
            self.log.debug(f"Updated DHCP client configuration for interface: {self._interface_name} via OS")
        
        except Exception as e:
            self.log.critical(f"Failed to update DHCP client configuration for interface: {self._interface_name} via OS: {e}")
            return STATUS_NOK
        
        if dhcp_client_state == State.DOWN:
            if dhcp_client.stop():
                self.log.error(f"Failed to stop client on interface: {self._interface_name} OS update error.")
                return STATUS_NOK
        
        else:                                            
            if dhcp_client.start():
                self.log.error(f"Failed to start {dhcp_stack_ver.value} client on interface: {self._interface_name} OS update error.")
                return STATUS_NOK

        return STATUS_OK

         

# FILE: src/routershell/lib/network_manager/network_operations/dhcp/client/supported_dhcp_clients.py
import ipaddress
import logging
import shutil
from abc import ABC, abstractmethod
from enum import Enum
from ipaddress import ip_address

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import InterfaceName
from routershell.lib.network_manager.common.inet import InetServiceLayer
from routershell.lib.network_manager.common.run_commands import RunCommand, RunResult
from routershell.lib.network_manager.network_operations.dhcp.common.dhcp_common import DHCPStackVersion, DHCPStatus
from routershell.lib.system.os.os import OSChecker, SupportedOS


class SupportedDhcpClients(Enum):
    """
    Enumeration of supported DHCP clients.

    Attributes:
        UDHCPC (str): The DHCP (IPv4) client provided by BusyBox, commonly used in lightweight and embedded Linux systems.
        UDHCPC6 (str): The DHCP (IPv6) client provided by BusyBox, commonly used in lightweight and embedded Linux systems.
        DHCPCD (str): The ISC DHCP client with dual stack support (IPv4 and IPv6), suitable for a variety of systems and scenarios.
        DHCLIENT (str): The ISC DHCP client with dual stack support, which was deprecated in 2022. This client is still available but not recommended for new deployments.
    """
    # BusyBox (Need both to Support Dual-Stack)
    UDHCPC = 'udhcpc'
    UDHCPC6 = 'udhcpc6'
    
    # ISC (Dual-Stack Support)
    DHCPCD = 'dhcpcd'
    
    # ISC Deprecated 2022 (Dual-Stack Support)
    DHCLIENT = 'dhclient'

class SupportedDhcpClientsDHCPVersion(Enum):
    """
    Enumeration of supported DHCP clients with specific versions for IPv4 and IPv6.

    Attributes:
        UDHCPC_V4 (str): The BusyBox DHCP client for IPv4, commonly used in lightweight and embedded Linux systems.
        UDHCPC_V6 (str): The BusyBox DHCP client for IPv6.
        DHCPCD_V4 (str): The ISC DHCP client (dhcpcd) with dual stack support for IPv4, suitable for a variety of systems and scenarios.
        DHCPCD_V6 (str): The ISC DHCP client (dhcpcd) with dual stack support for IPv6.
        DHCLIENT_V4 (str): The ISC DHCP client (dhclient) with dual stack support for IPv4, which was deprecated in 2022. 
                           This client is still available but not recommended for new deployments.
        DHCLIENT_V6 (str): The ISC DHCP client (dhclient) with dual stack support for IPv6, which was deprecated in 2022. 
                           This client is still available but not recommended for new deployments.
    """
    # BusyBox
    UDHCPC_V4 = 'udhcpc'
    UDHCPC_V6 = 'udhcpc6'
    
    # ISC (Dual Stack Support)
    DHCPCD_V4 = 'dhcpcd'
    DHCPCD_V6 = 'dhcpcd'
    
    # ISC Deprecated 2022 (Dual Stack Support)
    DHCLIENT_V4 = 'dhclient'
    DHCLIENT_V6 = 'dhclient'

class DHCPClientFactory:
    """
    A factory class to get the supported DHCP client based on the interface name and optional override.
    """
    
    _DHCPClientOperationsList:list['DHCPClientOperations'] = []
    
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DHCP_CLIENT_FACTORY)      
          
    def get_supported_dhcp_client(
        self, interface_name: InterfaceName, dhcp_stack_version: DHCPStackVersion, auto_sdc_override=None
    ) -> 'DHCPClientOperations':
        """
        Determines and returns the appropriate DHCP client operations object based on 
        the specified interface name, DHCP stack version, and optional override.

        Args:
            interface_name (str): The name of the network interface.
            dhcp_stack_version (DHCPStackVersion): The version of the DHCP stack to use.
            auto_sdc_override (SupportedDhcpClients | None): optional override for 
                selecting the DHCP client. If provided, it determines which DHCP client 
                will be used regardless of the current OS. If not provided, the selection 
                is based on the current OS.

        Returns:
            DHCPClientOperations: An instance of the appropriate DHCP client operations 
                class based on the provided arguments and conditions.
        """
        # Track DHCPClientOperations
        dco: DHCPClientOperations = None
        
        if auto_sdc_override:

            self.log.debug(f'Selecting DHCP Client: {auto_sdc_override.name}')
            if auto_sdc_override == SupportedDhcpClients.UDHCPC:
                dco = DHCPClientOperations_udhcpc(interface_name, dhcp_stack_version)

            elif auto_sdc_override == SupportedDhcpClients.DHCPCD:
                dco = DHCPClientOperations_dhcpcd(interface_name, dhcp_stack_version)

            elif auto_sdc_override == SupportedDhcpClients.DHCLIENT:
                dco = DHCPClientOperations_dhclient(interface_name, dhcp_stack_version)

        else:
            current_os = OSChecker().get_current_os()
            self.log.debug(f'Auto Selecting DHCP Client on {current_os.name} OS')
            
            if current_os == SupportedOS.BUSY_BOX:
                dco = DHCPClientOperations_udhcpc(interface_name, dhcp_stack_version)

            elif current_os == SupportedOS.UBUNTU:
                auto_sdc = self._auto_find_dhcp_client()

                if auto_sdc == SupportedDhcpClients.DHCPCD:
                    dco = DHCPClientOperations_dhcpcd(interface_name, dhcp_stack_version)

                elif auto_sdc == SupportedDhcpClients.DHCLIENT:
                    dco = DHCPClientOperations_dhclient(interface_name, dhcp_stack_version)

            else:
                raise NotImplementedError(f'Unsupported OS: {current_os.name}')
            
        if not dco:
            raise Exception(f'Failed to determine DHCP Client Operations object for {interface_name}')
        
        DHCPClientFactory._DHCPClientOperationsList.append(dco)
        return dco

    def _auto_find_dhcp_client(self) -> SupportedDhcpClients:
        """
        Automatically find a supported DHCP client.

        Returns:
            SupportedDhcpClients: The DHCP client found.
        """
        # Maintain this order BusyBox -> General Linux Distro
        if self._check_command_exists("udhcpc"):
            return SupportedDhcpClients.UDHCPC
        
        elif self._check_command_exists("dhcpcd"):
            return SupportedDhcpClients.DHCPCD
        
        elif self._check_command_exists("dhclient"):
            return SupportedDhcpClients.DHCLIENT
        
        else:
            raise DHCPClientException("No supported DHCP client found.")
    
    def _check_command_exists(self, command: str) -> bool:
        """
        Check if a command exists in the system.

        Args:
            command (str): The command to check.

        Returns:
            bool: True if the command exists, False otherwise.
        """
        return shutil.which(command) is not None
            
class DHCPClientException(Exception):
    """
    Custom exception class for DHCP client operations.

    Attributes:
        message (str): The error message.
        command (str): The command that caused the exception (if applicable).
    """

    def __init__(self, message: str, command: str = None):
        self.message = message
        self.command = command
        super().__init__(self.message)

    def __str__(self):
        if self.command:
            return f"{self.message} | Command: {self.command}"
        return self.message                    

class DHCPClientOperations(ABC, RunCommand):
    """
    Abstract base class for DHCP client operations on a network interface.


    This class provides a template for implementing various DHCP client operations
    such as checking client availability, configuring network settings, and managing
    the DHCP client lifecycle.

    Attributes:
        _interface_name (str): The name of the network interface.

    Methods:
        Implemented Methods:
            get_interface(): Get the name of the network interface.
            set_dual_stack(): Configure the interface with both IPv4 and IPv6 settings.
            get_inet(): Retrieve the current IP address assigned to the interface.
            is_client_available(): Check if the DHCP client is available.
            get_dhcp_client(): Retrieve the supported DHCP client.
            start(): Start the DHCP client.
            restart(): Restart the DHCP client.
            set_auto(): Start the DHCP client based

        Abstract Methods:
            remove_interface(): Remove the network interface configuration.
            set_inet4(): Configure the interface with IPv4 settings.
            set_inet6(): Configure the interface with IPv6 settings.
            stop(): Stop the DHCP client.
            release_inet(): Release the current IP address.
            renew_inet(): Renew the IP address for the interface.
    """

    def __init__(self, interface_name: InterfaceName, dhcp_stack_version: DHCPStackVersion, sdc: SupportedDhcpClients):
        super().__init__()
        RunCommand().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DHCP_SUPPORTED_CLIENTS_ABC)
        self._interface_name = interface_name
        self._dsv = dhcp_stack_version
        self._sdc = sdc
        self._last_dhcp_client_status = DHCPStatus.STOP
        
        if not self.is_client_available():
            raise DHCPClientException("DHCP client is not available.", self._sdc.value)
    
    def get_dhcp_stack_version(self) -> DHCPStackVersion:
        """
        Get the DHCP stack version being used.

        Returns:
            DHCPStackVersion: The DHCP stack version.
        """
        return self._dsv

    def get_dhcp_client(self) -> SupportedDhcpClients:
        """
        Retrieve the supported DHCP client.

        Returns:
            SupportedDhcpClients: The supported DHCP client.
        """
        return self._sdc    

    def is_client_available(self) -> bool:
        """
        Check if the udhcpc DHCP client is available on the system.

        Returns:
            bool: True if udhcpc is available, False otherwise.
        """
        return shutil.which(self._sdc.value) is not None

    def get_interface(self) -> str:
        """
        Get the name of the network interface.

        Returns:
            str: The name of the network interface.
        """
        return self._interface_name

    @abstractmethod
    def remove_interface(self) -> bool:
        """
        Remove the network interface configuration.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return STATUS_OK

    @abstractmethod
    def set_inet4(self) -> bool:
        """
        Configure the interface with IPv4 settings.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return STATUS_OK

    @abstractmethod
    def set_inet6(self) -> bool:
        """
        Configure the interface with IPv6 settings.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return STATUS_OK

    def set_dual_stack(self) -> bool:
        """
        Configure the interface with both IPv4 and IPv6 settings.
        
        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        inet4_status = self.set_inet4()
        inet6_status = self.set_inet6()
        
        if inet4_status == STATUS_OK and inet6_status == STATUS_OK:
            return STATUS_OK
        else:
            self.log.error(f'Unable to set dual stack on interface: {self.get_interface()}')
            return STATUS_NOK
        
    def set_auto(self) -> bool:
        """
        Automatically configure the interface with the appropriate DHCP settings based on the stack version.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        if self.get_dhcp_stack_version() == DHCPStackVersion.DHCP_V4:
            return self.set_inet4()
        elif self.get_dhcp_stack_version() == DHCPStackVersion.DHCP_V6:
            return self.set_inet6()
        elif self.get_dhcp_stack_version() == DHCPStackVersion.DHCP_DUAL_STACK:
            return self.set_dual_stack()
        else:
            self.log.error(f'Unable to set auto on interface: {self.get_interface()}')
            return STATUS_NOK

    def start(self) -> bool:
        """
        Start the DHCP client.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        self._last_dhcp_client_status = DHCPStatus.START
        return self.set_auto()

    @abstractmethod
    def stop(self) -> bool:
        """
        Stop the DHCP client.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        self._last_dhcp_client_status = DHCPStatus.STOP
        return STATUS_OK

    def restart(self) -> bool:
        """
        Restart the DHCP client (udhcpc6) on the interface.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        stop_status = self.stop()
        start_status = self.start()
        self._last_dhcp_client_status = DHCPStatus.RESTART
        return STATUS_OK if stop_status == STATUS_OK and start_status == STATUS_OK else STATUS_NOK

    def get_inet(self) -> list[ip_address]:
        """
        Retrieve all IP addresses assigned to the interface, including both IPv4 and IPv6 addresses.

        Returns:
            list[ipaddress.ip_address]: A list of IP addresses assigned to the interface. This list can include both IPv4 and IPv6 addresses.
            
        """
        return InetServiceLayer().get_interface_ip_addresses(self.get_interface())

    @abstractmethod
    def release_inet(self) -> bool:
        """
        Release the current IP address.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return STATUS_OK

    @abstractmethod
    def renew_inet(self) -> ipaddress:
        """
        Renew the IP address for the interface.

        Returns:
            ipaddress.ip_address: The new IP address assigned to the interface.
        """
        pass
    
    def get_last_status(self) -> DHCPStatus:
        """
        Get the last status of the DHCP client.
        """
        return self._last_dhcp_client_status

    def _execute_command(self, command: list[str]) -> bool:
        """
        Executes a shell command and logs the result.

        Args:
            command (list[str]): The command to be executed as a list of strings.

        Returns:
            bool: STATUS_OK if the command executed successfully, STATUS_NOK otherwise.
        """
        self.log.debug(f"Executing command: {command}")
        result : RunResult = self.run(command)
        
        if result.exit_code:
            self.log.error(f"Command failed with error: {result.stderr}")
            return STATUS_NOK
        
        self.log.debug(f"Command executed successfully: {result.stdout}")
        return STATUS_OK

class DHCPClientOperations_udhcpc(DHCPClientOperations):
    def __init__(self, interface_name: InterfaceName, dhcp_stack_version: DHCPStackVersion):
        """
        Initialize the DHCPClient_udhcpc with a network interface name.
        
        Args:
            interface_name (str): The name of the network interface.
        """
        super().__init__(interface_name, dhcp_stack_version, SupportedDhcpClients.UDHCPC)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DHCP_CLIENT_UDHCPC)

        self._dco_udhcpc6 = DHCPClientOperations_udhcpc6(interface_name, DHCPStackVersion.DHCP_V6)
        
    def remove_interface(self) -> bool:
        """
        Remove the network interface configuration by stopping udhcpc.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        #Busy Box pkill implementation
        return self._execute_command(['pkill', f'udhcpc -i {self._interface_name}'])
        
    def set_inet4(self) -> bool:
        """
        Configure the interface with IPv4 settings using udhcpc.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self._execute_command(['udhcpc', '-i', self._interface_name])
    
    def set_inet6(self) -> bool:
        """
        Configure the interface with IPv6 settings. Note: udhcpc does not support IPv6 natively.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self._dco_udhcpc6.set_inet6()

    def stop(self) -> bool:
        """
        Stop the DHCP client (udhcpc) on the interface.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        self._get_last_status = DHCPStatus.STOP
        return self.remove_interface()

    def release_inet(self) -> bool:
        """
        Release the current IP address by stopping udhcpc.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self.stop()

    def renew_inet(self) -> ipaddress.ip_address:
        """
        Renew the IP address for the interface by restarting udhcpc.

        Returns:
            ipaddress.ip_address: The new IP address assigned to the interface.
        """
        if self.restart() == STATUS_OK:
            return self.get_inet()
        return None

class DHCPClientOperations_udhcpc6(DHCPClientOperations):
    def __init__(self, interface_name: InterfaceName, dhcp_stack_version: DHCPStackVersion):
        """
        Initialize the DHCPClient_udhcpc6 with a network interface name.
        
        Args:
            interface_name (str): The name of the network interface.
        """
        super().__init__(interface_name, dhcp_stack_version, SupportedDhcpClients.UDHCPC)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DHCP_CLIENT_UDHCPC6)

    def remove_interface(self) -> bool:
        """
        Remove the network interface configuration by stopping udhcpc6.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self._execute_command(['pkill', f'udhcpc6 -i {self._interface_name}'])
    
    def set_inet4(self) -> bool:
        """
        Configure the interface with IPv4 settings. Note: udhcpc6 does not support IPv4.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        self.log.error('udhcpc6 does not support IPv4.')
        return STATUS_NOK

    def set_inet6(self) -> bool:
        """
        Configure the interface with IPv6 settings using udhcpc6.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self._execute_command(['udhcpc6', '-i', self._interface_name])
    
    def start(self) -> bool:
        """
        Start the DHCP client (udhcpc6) on the interface.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self.set_inet6()

    def stop(self) -> bool:
        """
        Stop the DHCP client (udhcpc6) on the interface.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        self._last_dhcp_client_status = DHCPStatus.STOP
        return self.remove_interface()

    def release_inet(self) -> bool:
        """
        Release the current IP address by stopping udhcpc6.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self.stop()

    def renew_inet(self) -> ipaddress.ip_address:
        """
        Renew the IP address for the interface by restarting udhcpc6.

        Returns:
            ipaddress.ip_address: The new IP address assigned to the interface.
        """
        if self.restart() == STATUS_OK:
            return self.get_inet()
        return None

class DHCPClientOperations_dhcpcd(DHCPClientOperations):
    def __init__(self, interface_name: InterfaceName, dhcp_stack_version: DHCPStackVersion):
        """
        Initialize the DHCPClient_dhcpcd with a network interface name.
        
        Args:
            interface_name (str): The name of the network interface.
        """
        super().__init__(interface_name, dhcp_stack_version, SupportedDhcpClients.DHCPCD)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DHCP_CLIENT_DHCPCD)

    def remove_interface(self) -> bool:
        """
        Remove the network interface configuration by stopping dhcpcd.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self._execute_command(['dhcpcd', '--release', self._interface_name])
    
    def set_inet4(self) -> bool:
        """
        Configure the interface with IPv4 settings using dhcpcd.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self._execute_command(['dhcpcd', '-4', self._interface_name])
    
    def set_inet6(self) -> bool:
        """
        Configure the interface with IPv6 settings using dhcpcd.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self._execute_command(['dhcpcd', '-6', self._interface_name])
    
    def stop(self) -> bool:
        """
        Stop the DHCP client (dhcpcd) on the interface.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        self._last_dhcp_client_status = DHCPStatus.STOP
        return self._execute_command(['dhcpcd', '--release', self._interface_name])
        
    def release_inet(self) -> bool:
        """
        Release the current IP address by stopping dhcpcd.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self.stop()

    def renew_inet(self) -> ip_address:
        """
        Renew the IP address for the interface by restarting dhcpcd.

        Returns:
            ipaddress.ip_address: The new IP address assigned to the interface.
        """
        if self.restart() == STATUS_OK:
            return self.get_inet()
        return None

class DHCPClientOperations_dhclient(DHCPClientOperations):
    def __init__(self, interface_name: InterfaceName, dhcp_stack_version: DHCPStackVersion):
        """
        Initialize the DHCPClient_dhclient with a network interface name.

        Args:
            interface_name (str): The name of the network interface.
        """
        super().__init__(interface_name, dhcp_stack_version, SupportedDhcpClients.DHCLIENT)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DHCP_CLIENT_DHCLIENT)

    def remove_interface(self) -> bool:
        """
        Remove the network interface configuration by stopping dhclient.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self._execute_command(['dhclient', '-r', self._interface_name])
        
    def set_inet4(self) -> bool:
        """
        Configure the interface with IPv4 settings using dhclient.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self._execute_command(['dhclient', '-4', self._interface_name])
        
    def set_inet6(self) -> bool:
        """
        Configure the interface with IPv6 settings using dhclient.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self._execute_command(['dhclient', '-6', self._interface_name])
        
    def stop(self) -> bool:
        """
        Stop the DHCP client (dhclient) on the interface.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        self._last_dhcp_client_status = DHCPStatus.STOP
        return self._execute_command(['dhclient', '-r', self._interface_name])
        
    def release_inet(self) -> bool:
        """
        Release the current IP address by stopping dhclient.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        return self.stop()

    def renew_inet(self) -> ip_address:
        """
        Renew the IP address for the interface by restarting dhclient.

        Returns:
            ipaddress.ip_address: The new IP address assigned to the interface.
        """
        if self.restart() == STATUS_OK:
            return self.get_inet()
        return None

    

# FILE: src/routershell/lib/network_manager/network_operations/dhcp/server/dhcp_server.py
import logging
import os

from routershell.lib.common.common import STATUS_NOK, STATUS_OK
from routershell.lib.common.constants import DNSMASQ_LEASE_FILE_PATH
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import DhcpPoolName, InetAddressText, InetCidrText, InterfaceName, MacAddressText
from routershell.lib.db.dhcp_server_db import DHCPServerDatabase as DSD
from routershell.lib.network_manager.common.inet import InetServiceLayer, InetVersion
from routershell.lib.network_manager.common.mac import MacServiceLayer
from routershell.lib.network_manager.common.run_commands import RunCommand
from routershell.lib.network_manager.network_operations.network_mgr import NetworkManager
from routershell.lib.network_services.dhcp.common.dhcp_common import DHCPVersion
from routershell.lib.network_services.dhcp.dnsmasq.dnsmasq import DNSMasqDeploy, DNSMasqInterfaceService
from routershell.lib.network_services.dhcp.dnsmasq.dnsmasq_config_gen import DHCPv6Modes
from routershell.lib.system.system_service_control.system_service_control import SysServCntrlAction


class InvalidDhcpServer(Exception):
    def __init__(self, message):
        super().__init__(message)
    
class DHCPServer(NetworkManager):

    def __init__(self):
        """
        Initialize the DHCPServer instance.
        """
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DHCP_SERVER)
    
    def dhcp_pool_name_exists(self, dhcp_pool_name: DhcpPoolName) -> bool:
        """
        Check if a DHCP pool with the given name exists.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool to check.

        Returns:
            bool: True if the pool exists, False otherwise.
        """
        return DSD().dhcp_pool_name_exists_db(dhcp_pool_name)

    def get_dhcp_pool_name_list(self) -> list[str]:
        """
        Retrieve a list of DHCP pool names from the DSD class.

        This method calls the dhcp_pool_name_list method from an instance
        of the DSD class to get the list of DHCP pool names.

        Returns:
            list[str]: A list of DHCP pool names.
        """
        return DSD().dhcp_pool_name_list()
    
    def dhcp_pool_subnet_exists(self, dhcp_pool_subnet_cidr: InetCidrText) -> bool:
        """
        Check if a DHCP subnet within a DHCP pool exists.

        Args:
            dhcp_pool_subnet_cidr (str): The subnet CIDR to check.

        Returns:
            bool: True if the subnet exists, False otherwise.
        """
        return DSD().dhcp_pool_subnet_exist_db(dhcp_pool_subnet_cidr)
    
    def get_dhcp_pool_subnet(self, dhcp_pool_name:DhcpPoolName) -> str:
        """
        Retrieve the DHCP pool subnet from the RouterShell database using the provided DHCP pool name.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool.

        Returns:
            str: The DHCP pool subnet name retrieved from the RouterShell database.
            
        """        
        return DSD().get_dhcp_pool_subnet_name_db(dhcp_pool_name)
    
    def add_dhcp_pool_name(self, dhcp_pool_name: DhcpPoolName) -> bool:
        """
        Add a DHCP pool name to the DHCP server if it does not already exist.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool to add.

        Returns:
            bool: STATUS_OK if the pool name was added successfully or already exists, STATUS_NOK otherwise.
        """
        if self.dhcp_pool_name_exists(dhcp_pool_name):
            self.log.debug(f"DHCP pool-name: {dhcp_pool_name}, already exists")
            return STATUS_OK

        return DSD().add_dhcp_pool_name_db(dhcp_pool_name)
    
    def del_dhcp_pool_name(self, dhcp_pool_name: DhcpPoolName) -> bool:
        """
        Delete a DHCP pool by its name.
        
        Args:
            dhcp_pool_name (str): The name of the DHCP pool to be deleted.
        
        Returns:
            bool: STATUS_NOK if the DHCP pool does not exist, otherwise the status of the delete operation.
        """
        if not self.dhcp_pool_name_exists(dhcp_pool_name):
            self.log.debug(f"DHCP pool-name: {dhcp_pool_name} does not exist")
            return STATUS_NOK
        return DSD().del_dhcp_pool_name(dhcp_pool_name)

    def add_dhcp_pool_subnet(self, dhcp_pool_name: DhcpPoolName, dhcp_pool_subnet_cidr: InetCidrText) -> bool:
        """
        Add a DHCP subnet to the DHCP server for the specified DHCP pool if it does not already exist.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool to add the subnet to.
            dhcp_pool_subnet_cidr (str): The subnet CIDR to add.

        Returns:
            bool: STATUS_OK if the subnet was added successfully or already exists, STATUS_NOK otherwise.
        """
        if not self.dhcp_pool_name_exists(dhcp_pool_name):
            self.log.critical(f"Unable to add DHCP subnet to the DHCP server, dhcp-pool-name : {dhcp_pool_name} , does not exists")
            return STATUS_NOK
        
        if not self.is_valid_inet_subnet(dhcp_pool_subnet_cidr):
            self.log.error(f"Unable to add DHCP subnet to the DHCP server, subnet : {dhcp_pool_subnet_cidr} , is invalid subnet/CIDR")
            return STATUS_NOK
                    
        return DSD().add_dhcp_pool_subnet_db(dhcp_pool_name, dhcp_pool_subnet_cidr)
 
    def add_dhcp_pool_subnet_inet_range(self, dhcp_pool_name:DhcpPoolName, 
                                        dhcp_pool_subnet_cidr: InetCidrText, 
                                        inet_pool_start: InetAddressText, 
                                        inet_pool_end: InetAddressText, 
                                        inet_pool_subnet_cidr: InetCidrText) -> bool:
        """
        Add an IP address range to a DHCP subnet within a DHCP pool.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool.
            inet_dhcp_pool_subnet_cidr (str): The DHCP pool subnet CIDR.
            inet_pool_start (str): The starting IP address of the range.
            inet_pool_end (str): The ending IP address of the range.
            inet_pool_subnet_cidr (str): The subnet CIDR of the range.

        Returns:
            bool: STATUS_OK if the range was added successfully, STATUS_NOK otherwise
        """
        if not self.dhcp_pool_name_exists(dhcp_pool_name):
            self.log.critical(f"Unable to add subnet pool inet range, dhcp-pool-name : {dhcp_pool_name} , does not exist")
            return STATUS_NOK

        if self.is_ip_range_within_subnet(dhcp_pool_subnet_cidr, inet_pool_start, inet_pool_end, inet_pool_subnet_cidr):
            self.log.error(f"inet pool range: ({inet_pool_start} - {inet_pool_end}) mask: {inet_pool_subnet_cidr} - "\
                           f"not within DHCP subnet-pool: {dhcp_pool_subnet_cidr}")
            return STATUS_NOK

        return DSD().add_dhcp_subnet_inet_address_range_db(dhcp_pool_subnet_cidr, 
                                                           inet_pool_start, 
                                                           inet_pool_end, 
                                                           inet_pool_subnet_cidr)
    
    def add_dhcp_pool_reservation(self, dhcp_pool_name: DhcpPoolName, 
                                  inet_subnet_cidr: InetCidrText, 
                                  hw_address: MacAddressText, inet_address: InetAddressText) -> bool:
        """
        Add a reservation to a DHCP pool.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool.
            inet_subnet_cidr (str): The subnet CIDR of the reservation.
            hw_address (str): The MAC address for the reservation.
            inet_address (str): The reserved IP address.

        Returns:
            bool: STATUS_OK if the reservation was added successfully, STATUS_NOK otherwise
        """
        if not self.dhcp_pool_name_exists(dhcp_pool_name):
            self.log.critical(f"Unable to add a reservation to a DHCP pool, dhcp-pool-name : {dhcp_pool_name} , does not exist")
            return STATUS_NOK
        
        return DSD().add_dhcp_subnet_reservation_db(inet_subnet_cidr, hw_address, inet_address)
    
    def add_dhcp_pool_option(self, dhcp_pool_name: DhcpPoolName, inet_subnet_cidr: InetCidrText, dhcp_option: str, value: str) -> bool:
        """
        Add a DHCP option to a DHCP pool.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool.
            inet_subnet_cidr (str): The subnet CIDR where the option is added.
            dhcp_option (str): The DHCP option to add.
            value (str): The value of the DHCP option.

        Returns:
            bool: STATUS_OK if the option was added successfully, STATUS_NOK otherwise
        """
        if not self.dhcp_pool_name_exists(dhcp_pool_name):
            self.log.critical(f"Unable to add DHCP option to a DHCP pool, dhcp-pool-name : {dhcp_pool_name} , does not exist")
            return STATUS_NOK

        return DSD().add_dhcp_subnet_option_db(inet_subnet_cidr, dhcp_option, value)

    def add_dhcp_pool_to_interface(self, dhcp_pool_name: DhcpPoolName, interface_name: InterfaceName, negate:bool=False) -> bool:
        """
        Adds a DHCP pool to an interface.

        This method updates the DHCP pool name associated with a given interface.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool to add to the interface.
            interface_name (str): The name of the interface to associate with the DHCP pool.

        Returns:
            bool: STATUS_OK if the DHCP pool was successfully added to the interface, STATUS_NOK otherwise.

        """
        
        # TODO Check interface IP address(es) are within the DHCP-pool-subnet range

        # Get inet-subnet-cidr from dhcp-pool-name == interface-inet-address -> subnet-range
        dhcp_pool_subnet = DSD().get_dhcp_pool_subnet_name_db(dhcp_pool_name)
        
        self.log.debug(f"add_dhcp_pool_to_interface() {dhcp_pool_name} -> {dhcp_pool_subnet}")
        
        DSD().update_dhcp_pool_name_interface(dhcp_pool_name, interface_name, negate)

        DMIS = DNSMasqInterfaceService(dhcp_pool_name, dhcp_pool_subnet)
        
        if negate:
            if DMIS.clear_configurations():
                self.log.error(f"Unable to remove DHCP Policy: {dhcp_pool_name} from router")
                return STATUS_NOK
            
            return STATUS_OK
        
        if DMIS.build_interface_configuration():
            self.log.error("Unable to build DNSMasq Configuration")
            return STATUS_NOK
        
        if DMIS.deploy_configuration(DNSMasqDeploy.INTERFACE):
            self.log.error("Unable to set DNSMasq interface configuration")
            return STATUS_NOK
        
        if DMIS.control_service(SysServCntrlAction.RESTART):
            self.log.error("Unable to restart DNSMasq")
            return STATUS_NOK    
        
        return STATUS_OK

    def update_dhcp_pool_mode(self, dhcp_pool_name: DhcpPoolName, mode: DHCPv6Modes) -> bool:
        """
        Update the DHCP version mode for a specific DHCP pool.

        Parameters:
            dhcp_pool_name (str): The name of the DHCP pool.
            mode (DHCPv6Modes): The DHCP version mode to set.

        Returns:
            bool: STATUS_OK if the update is successful, STATUS_NOK otherwise.

        This method checks if the specified DHCP pool exists. If the pool exists, it proceeds to update
        the DHCP version mode for that pool using the provided mode. If the update is successful,
        the method returns True; otherwise, it returns False.

        Note:
        - The DHCP pool's existence is verified using the `dhcp_pool_name_exists` method.
        - The actual update is performed by calling the `add_dhcp_subnet_option_db` method from the `DSD` class.

        """
        if not self.dhcp_pool_name_exists(dhcp_pool_name):
            self.log.critical(f"Unable to update DHCP pool mode. DHCP pool name '{dhcp_pool_name}' does not exist.")
            return STATUS_NOK

        return DSD().update_dhcp_pool_mode_db(dhcp_pool_name, mode)

class DhcpPoolFactory:

    def __init__(self, dhcp_pool_name: DhcpPoolName):
        """
        Initialize the DhcpPoolFactory instance.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool.

        Raises:
            ValueError: If the provided subnet CIDR is invalid.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DHCP_POOL_FACTORY)
        self.log.debug(f"Create DhcpPoolFactory({dhcp_pool_name}) ")
        
        self.factory_status = True
        
        self.dhcp_pool_name = None
        self.dhcp_pool_inet_subnet_cidr = None
                
        self.dhcp_srv_obj = DHCPServer()

        if not self.dhcp_srv_obj.dhcp_pool_name_exists(dhcp_pool_name):
            self.log.debug(f"Adding dhcp-pool-name: {dhcp_pool_name} to DB")
            self.dhcp_srv_obj.add_dhcp_pool_name(dhcp_pool_name)

        self.dhcp_pool_name = dhcp_pool_name
        self.dhcp_pool_inet_subnet_cidr = self.dhcp_srv_obj.get_dhcp_pool_subnet(dhcp_pool_name)
        self.log.debug(f"Create DhcpPoolFactory({dhcp_pool_name} , {self.dhcp_pool_inet_subnet_cidr}) ")

    def delete_pool_name(self) -> bool:
        """
        Delete a DHCP pool by its name.
                
        Returns:
            bool: The status of the delete operation.
        """
        return self.dhcp_srv_obj.del_dhcp_pool_name(self.dhcp_pool_name)

    def status(self) -> bool:
        """
        Get the status of the DhcpPoolFactory.

        Returns:
            bool: True if the factory status is OK, False otherwise.
        """
        return self.factory_status
    
    def add_pool_subnet(self, inet_subnet_cidr: InetCidrText) -> bool:
        """
        Add a subnet to the DHCP pool.

        Args:
            inet_subnet_cidr (str): The subnet CIDR to add.

        Returns:
            bool: STATUS_OK if the subnet was added successfully, STATUS_NOK otherwise.
        """     

        is_valid, error_msg = InetServiceLayer.validate_subnet_format(inet_subnet_cidr)
        
        if not is_valid:
            self.log.error(f'Invalid subnet: {inet_subnet_cidr}. Error: {error_msg}')
            self._update_status(False)
            return STATUS_NOK

        if not self.status():
            self.log.error("Unable to add DHCP Pool subnet - ERROR: DhcpPoolFactory()")
            return STATUS_NOK        

        self.dhcp_pool_inet_subnet_cidr = inet_subnet_cidr

        if self.dhcp_srv_obj.add_dhcp_pool_subnet(self.dhcp_pool_name, inet_subnet_cidr):
            self.log.error(f"Failed to add subnet {inet_subnet_cidr} to the DHCP pool")
            return STATUS_NOK

        return STATUS_OK

    def add_inet_pool_range(self, inet_start: str, inet_end: str, inet_subnet_cidr: InetCidrText) -> bool:
        """
        Add an IP address range to the DHCP pool.

        Args:
            inet_start (str): The starting IP address of the range.
            inet_end (str): The ending IP address of the range.
            inet_subnet_cidr (str): The subnet CIDR of the range.

        Returns:
            bool: STATUS_OK if the range was added successfully, STATUS_NOK otherwise.
        """
        if not self.status():
            self.log.error("Unable to add DHCP pool - ERROR: DhcpPoolFactory()")
            return STATUS_NOK

        if not InetServiceLayer.validate_inet_ranges(self.dhcp_pool_inet_subnet_cidr, inet_start, inet_end):
            self.log.error(f'Invalid IP Range [{self.dhcp_pool_inet_subnet_cidr} ->{inet_start} - {inet_end}]')
            return STATUS_NOK

        return self.dhcp_srv_obj.add_dhcp_pool_subnet_inet_range(
            self.dhcp_pool_name,
            self.dhcp_pool_inet_subnet_cidr,
            inet_start, inet_end, inet_subnet_cidr
        )

    def add_reservation(self, hw_address: MacAddressText, inet_address: InetAddressText) -> bool:
        """
        Add a reservation to the DHCP pool.

        Args:
            hw_address (str): The MAC address for the reservation.
            inet_address (str): The reserved IP address.

        Returns:
            bool: STATUS_OK if the reservation was added successfully, STATUS_NOK otherwise.
        """
        if not self.status():
            self.log.error("Unable to add DHCP reservation - ERROR: DhcpPoolFactory()")
            return STATUS_NOK

        if not MacServiceLayer().is_valid_mac_address(hw_address) and not MacServiceLayer().is_valid_duid_ll(hw_address):
            self.log.error(f'Invalid hw-address: {hw_address}')    
            return STATUS_NOK
        
        if not InetServiceLayer.validate_inet_range(self.dhcp_pool_inet_subnet_cidr, inet_address):
            self.log.error(f'IP address not part of pool subnet [{self.dhcp_pool_inet_subnet_cidr} -> {inet_address}]')
            return STATUS_NOK

        return self.dhcp_srv_obj.add_dhcp_pool_reservation(self.dhcp_pool_name,
                                                           self.dhcp_pool_inet_subnet_cidr,
                                                           hw_address, inet_address)
    
    def add_option(self, dhcp_option: str, value: str) -> bool:
        """
        Add a DHCP option to the DHCP pool.

        Args:
            dhcp_option (str): The DHCP option to add.
            value (str): The value of the DHCP option.

        Returns:
            bool: STATUS_OK if the option was added successfully, STATUS_NOK otherwise.
        """
        if not self.status():
            self.log.error("Unable to add DHCP options - ERROR: DhcpPoolFactory()")
            return STATUS_NOK

        return self.dhcp_srv_obj.add_dhcp_pool_option(self.dhcp_pool_name,
                                                      self.dhcp_pool_inet_subnet_cidr,
                                                      dhcp_option, value)

    def get_subnet_inet_version(self) -> DHCPVersion:
        """
        Determine the DHCP version (DHCPv4 or DHCPv6) based on the subnet's CIDR notation.

        Returns:
            DHCPVersion: An enum representing the DHCP version (DHCPv4, DHCPv6, or UNKNOWN).

        """
        if not self.dhcp_pool_inet_subnet_cidr:
            return DHCPVersion.UNKNOWN

        inet_version = InetServiceLayer().get_inet_subnet_inet_version(self.dhcp_pool_inet_subnet_cidr)

        if inet_version == InetVersion.IPv4:
            return DHCPVersion.DHCP_V4
        else:
            return DHCPVersion.DHCP_V6

    def add_dhcp_mode(self, mode: DHCPv6Modes) -> bool:
        """
        Update the DHCP mode for DHCPv6 subnets.

        This method allows updating the DHCP mode for DHCPv6 subnets. It checks the current status of the DHCP server,
        ensures it is in a valid state using `self.status()`, and then validates the DHCP version. If the DHCP version is 
        DHCPv4, it logs a debug message indicating that DHCP mode is reserved for DHCPv6 subnets and returns STATUS_NOK.

        Args:
            mode (DHCPv6Modes): The desired DHCP mode for DHCPv6 subnets.

        Returns:
            bool: STATUS_OK if the DHCP mode was updated successfully, STATUS_NOK otherwise.
        """
        if not self.status():
            self.log.error("Unable to update DHCP Mode - ERROR: DhcpPoolFactory()")
            return STATUS_NOK

        if self.get_subnet_inet_version() == DHCPVersion.DHCP_V4:
            self.log.debug('DHCP Mode is reserved for DHCPv6 subnet')
            return STATUS_NOK
        
        return self.dhcp_srv_obj.update_dhcp_pool_mode(self.dhcp_pool_name, mode)
        
    def _update_status(self, status: bool):
        """
        Update the status of the DhcpPoolFactory.

        This method is used to update the status of the DhcpPoolFactory. It takes a boolean parameter 'status' indicating
        whether the factory is in a valid state.

        Args:
            status (bool): The new status of the DhcpPoolFactory. True if the factory is in a valid state, False otherwise.

        Returns:
            None
        """
        self.factory_status = status


class DhcpServerManager(RunCommand):

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DHCP_SERVER_MANAGER)

    def get_leases(self) -> list[dict[str, str]]:
        """
        Retrieve a list of DHCP leases from the dnsmasq leases file.

        Returns:
            list[dict[str, str]]: A list of dictionaries containing lease information.
                Each dictionary has the following keys:
                - 'ip_address': The leased IP address.
                - 'mac_address': The MAC address of the device.
                - 'hostname': The hostname associated with the lease.
                - 'expires': The expiration timestamp of the lease.
        """        
        try:
            leases_path = DNSMASQ_LEASE_FILE_PATH

            if os.path.exists(leases_path):
                with open(leases_path) as leases_file:
                    leases_raw = leases_file.readlines()

                leases = []

                for lease_raw in leases_raw:
                    lease_info = lease_raw.split()
                    if len(lease_info) >= 5:
                        if "duid" not in lease_raw.lower():
                            lease_dict = {
                                "ip_address": lease_info[2],
                                "mac_address": lease_info[1],
                                "hostname": lease_info[3],
                                "expires": lease_info[0],
                            }
                            leases.append(lease_dict)
                            self.log.debug(f"Processed lease entry: {lease_dict}")
                    else:
                        lease_dict = {
                            "malformed_entry": lease_raw.strip(),
                        }
                        leases.append(lease_dict)
                        self.log.error(f"Processed malformed lease entry: {lease_dict}")

                return leases

            else:
                self.log.debug(f"Leases file '{leases_path}' not found.")
                return []

        except Exception as e:
            self.log.error(f"Error retrieving DHCP leases: {e}")
            return []
        
    def status(self) -> bool:
        """
        Get the status of dnsmasq.

        Returns:
            bool: STATUS_OK is active, otherwise STATUS_NOK

        """

        result = self.run(["systemctl", "is-active", "dnsmasq"])

        if result.exit_code:
            self.log.error(f"Error: Unable to get dnsmasq status. Exit code: {result.stderr}")
            return STATUS_NOK

        if result.stdout.strip() != 'active':
            self.log.debug(result.stdout)
            return STATUS_NOK

        return STATUS_OK

    def test_dhcp_server(self) -> bool:
        """
        Test the syntax of dnsmasq configuration files.

        Returns:
            bool: STATUS_OK if the syntax test is successful, STATUS_NOK otherwise.
        """

        result = self.run(["dnsmasq", "--test"])
        
        if result.exit_code:
            return STATUS_NOK
        
        self.log.debug(f"dnsmasq syntax test passed: {result.stdout}")
        return STATUS_OK

    def lease_log(self) -> list[str]:
        """
        Get the DHCP-related log entries from the system journal.

        Returns:
            list[str]: A list of DHCP-related log entries.
        """
        result = self.run(['journalctl | grep dnsmasq-dhcp'], shell=True, sudo=False)
        
        if result.exit_code:
            return []
        
        log_entries = result.stdout.split('\n')
        return log_entries

    def server_log(self) -> list[str]:
        """
        Get the DHCP-related log entries from the system journal.

        Returns:
            list[str]: A list of DHCP-related log entries.
        """
        command = 'journalctl | grep dnsmasq\\['

        result = self.run(["journalctl | grep 'dnsmasq\\['"], shell=True, sudo=False)
        
        if result.exit_code:
            return []
        
        log_entries = result.stdout.split('\n')
        return log_entries

 

# FILE: src/routershell/lib/network_manager/network_operations/hostapd_mgr.py
import os
from enum import Enum

from routershell.lib.common.constants import HOSTAPD_CONF_DIR, STATUS_NOK, STATUS_OK
from routershell.lib.common.types import BridgeName, FilePath, InterfaceName, SsidText
from routershell.lib.network_manager.common.run_commands import RunCommand


class HostapdIEEE802Config(Enum):
    IEEE80211AC = "ieee80211ac"
    IEEE80211AX = "ieee80211ax"
    IEEE80211BE = "ieee80211be"
    IEEE80211D = "ieee80211d"
    IEEE80211H = "ieee80211h"
    IEEE80211N = "ieee80211n"
    IEEE8021X = "ieee8021x"
    IEEE80211W = "ieee80211w"

class HostapdConfigGenerator:
    def __init__(self):
        """
        Initialize the HostapdConfigGenerator.

        The constructor sets up an empty list to store the Hostapd configuration lines.
        """
        self.config = []

    def generate_config(self):
        """
        Generate the Hostapd configuration.

        Returns:
            list[str]: A list of configuration lines for the Hostapd configuration.
        """
        return self.config

    def add_wmm(self, value: int):
        """
        Set the Wireless Multimedia (WMM) support.

        Args:
            value (int): The value to set for WMM (1 for enabled, 0 for disabled).
        """
        if value in [0, 1]:
            self.config.append(f'wmm_enabled={value}')
        else:
            print("Invalid WMM value. Use 1 for enabled or 0 for disabled.")

    def add_ieee802(self, option: HostapdIEEE802Config, value: int):
        """
        Set the IEEE802 configuration option to the specified value.

        Args:
            option (HostapdIEEE802Config): The IEEE802 configuration option to set.
            value (int): The value to set for the option (0 or 1).
        """
        if option.value in ["ieee80211d","ieee80211d", "ieee80211h", "ieee80211ac", "ieee80211ax", "ieee80211be", "ieee8021x", "ieee80211w"]:
            self.config.append(f'{option.value}={value}')
        else:
            print(f"Invalid IEEE802 option: {option.value}")
            
    def add_bss(self, bss_name: SsidText):
        """
        Add a BSS (Basic Service Set) configuration to the Hostapd config.

        Args:
            bss_name (str): The name of the BSS.
        """
        self.config.append(f'\n# BSS configuration for {bss_name}')
        self.config.append(f'bss={bss_name}')

    def add_interface(self, interface_name: InterfaceName):
        """
        Add interface configuration to the BSS.

        Args:
            interface_name (str): The name of the interface.
        """
        self.config.append(f'interface={interface_name}')

    def add_bridge(self, bridge_name: BridgeName):
        """
        Add bridge configuration to the BSS.

        Args:
            bridge_name (str): The name of the bridge.
        """
        self.config.append(f'bridge={bridge_name}')

    def add_ssid(self, ssid: SsidText):
        """
        Add SSID (Service Set Identifier) configuration to the BSS.

        Args:
            ssid (str): The SSID to set.
        """
        self.config.append(f'ssid={ssid}')

    def add_channel(self, channel: int):
        """
        Add channel configuration to the Hostapd configuration.

        Args:
            channel (int): The channel number to set.
        """
        self.config.append(f'channel={channel}')

    def add_hw_mode(self, mode: str):
        """
        Add operation mode configuration to the Hostapd configuration.

        Args:
            mode (str): The operation mode to set (e.g., 'a', 'b', 'g', 'ad').
        """
        valid_modes = ['a', 'b', 'g', 'ad']

        if mode in valid_modes:
            self.config.append(f'hw_mode={mode}')
        else:
            print(f"Invalid operation mode: {mode}. Use one of {valid_modes}")

    def add_auth_algs(self, value: int):
        """
        Set the allowed authentication algorithms in the Hostapd configuration.

        Args:
            value (int): Bit-field of allowed authentication algorithms.
                         Bit 0 = Open System Authentication
                         Bit 1 = Shared Key Authentication (requires WEP)
        """
        if 0 <= value <= 3:
            self.config.append(f'auth_algs={value}')
        else:
            print("Invalid value for auth_algs. Use a bit-field value between 0 and 3.")

    def add_wpa(self, wpa_version: int):
        """
        Add WPA version configuration to the BSS.

        Args:
            wpa_version (int): Set to 2 for WPA2, 3 for WPA3.
        """
        self.config.append(f'wpa={wpa_version}')

    def add_wpa_psk(self, psk: str):
        """
        Add WPA PSK (Pre-Shared Key) configuration to the BSS.

        Args:
            psk (str): The WPA PSK to set.
        """
        self.config.append(f'wpa_psk={psk}')

    def add_wpa_passphrase(self, passphrase: str):
        """
        Add WPA passphrase configuration to the BSS.

        Args:
            passphrase (str): The WPA passphrase to set.
        """
        self.config.append(f'wpa_passphrase={passphrase}')

    def add_wpa_psk_file(self, psk_file: FilePath):
        """
        Add WPA PSK file configuration to the BSS.

        Args:
            psk_file (str): The path to the WPA PSK file.
        """
        self.config.append(f'wpa_psk_file={psk_file}')

    def add_wpa_psk_radius(self, psk_radius: str):
        """
        Add WPA PSK radius configuration to the BSS.

        Args:
            psk_radius (str): The WPA PSK radius setting.
        """
        self.config.append(f'wpa_psk_radius={psk_radius}')

    def add_wpa_key_mgmt(self, key_mgmt: str):
        """
        Add WPA key management configuration to the BSS.

        Args:
            key_mgmt (str): The WPA key management options.
        """
        self.config.append(f'wpa_key_mgmt={key_mgmt}')

    def add_wpa_pairwise(self, pairwise: str):
        """
        Add WPA pairwise configuration to the BSS.

        Args:
            pairwise (str): The WPA pairwise options.
        """
        self.config.append(f'wpa_pairwise={pairwise}')

    def add_wpa_group_rekey(self, rekey_interval: int):
        """
        Add WPA group rekey configuration to the BSS.

        Args:
            rekey_interval (int): The rekey interval in seconds.
        """
        self.config.append(f'wpa_group_rekey={rekey_interval}')

    def add_wpa_strict_rekey(self, strict_rekey: int):
        """
        Add WPA strict rekey configuration to the BSS.

        Args:
            strict_rekey (int): Set to 1 to enable strict rekeying, 0 to disable.
        """
        self.config.append(f'wpa_strict_rekey={strict_rekey}')

    def add_ap_max_inactivity(self, max_inactivity: int):
        """
        Add maximum inactivity timeout for stations.

        Args:
            max_inactivity (int): Maximum inactivity timeout in seconds.
        """
        self.config.append(f'ap_max_inactivity={max_inactivity}')

    def add_ap_isolate(self, enable_isolate: int):
        """
        Add AP isolation configuration.

        Args:
            enable_isolate (int): Set to 1 to enable AP isolation, 0 to disable.
        """
        self.config.append(f'ap_isolate={enable_isolate}')

    def add_eap_message(self, eap_message: str):
        """
        Add EAP message configuration.

        Args:
            eap_message (str): EAP message to include in the configuration.
        """
        self.config.append(f'eap_message={eap_message}')

    def add_eap_reauth_period(self, reauth_period: int):
        """
        Add EAP reauthentication period.

        Args:
            reauth_period (int): EAP reauthentication period in seconds.
        """
        self.config.append(f'eap_reauth_period={reauth_period}')

    def add_eap_user_file(self, user_file: FilePath):
        """
        Add EAP user file configuration.

        Args:
            user_file (str): Path to the EAP user file.
        """
        self.config.append(f'eap_user_file={user_file}')

    def add_eap_sim_db(self, sim_db: str):
        """
        Add EAP-SIM database configuration.

        Args:
            sim_db (str): EAP-SIM database configuration.
        """
        self.config.append(f'eap_sim_db={sim_db}')

    def add_eap_sim_db_timeout(self, timeout: int):
        """
        Add EAP-SIM database timeout configuration.

        Args:
            timeout (int): EAP-SIM database timeout in seconds.
        """
        self.config.append(f'eap_sim_db_timeout={timeout}')

    def add_eap_fast_a_id(self, a_id: str):
        """
        Add EAP-FAST A-ID configuration.

        Args:
            a_id (str): EAP-FAST A-ID.
        """
        self.config.append(f'eap_fast_a_id={a_id}')

    def add_eap_fast_a_id_info(self, a_id_info: str):
        """
        Add EAP-FAST A-ID-Info configuration.

        Args:
            a_id_info (str): EAP-FAST A-ID-Info.
        """
        self.config.append(f'eap_fast_a_id_info={a_id_info}')

    def add_eap_fast_prov(self, prov: int):
        """
        Add EAP-FAST provisioning configuration.

        Args:
            prov (int): EAP-FAST provisioning option.
        """
        self.config.append(f'eap_fast_prov={prov}')

    def add_eap_teap_auth(self, enable_teap_auth: int):
        """
        Add EAP-TEAP authentication configuration.

        Args:
            enable_teap_auth (int): Set to 1 to enable EAP-TEAP, 0 to disable.
        """
        self.config.append(f'eap_teap_auth={enable_teap_auth}')

    def add_eap_teap_pac_no_inner(self, enable_pac_no_inner: int):
        """
        Add EAP-TEAP PAC without inner method configuration.

        Args:
            enable_pac_no_inner (int): Set to 1 to enable PAC without inner method, 0 to disable.
        """
        self.config.append(f'eap_teap_pac_no_inner={enable_pac_no_inner}')

    def add_eap_teap_separate_result(self, enable_separate_result: int):
        """
        Add EAP-TEAP separate result configuration.

        Args:
            enable_separate_result (int): Set to 1 to enable separate result, 0 to disable.
        """
        self.config.append(f'eap_teap_separate_result={enable_separate_result}')

    def add_eap_teap_id(self, teap_id: int):
        """
        Add EAP-TEAP ID configuration.

        Args:
            teap_id (int): EAP-TEAP ID.
        """
        self.config.append(f'eap_teap_id={teap_id}')

    def add_eap_sim_aka_result_ind(self, result_ind: int):
        """
        Add EAP-SIM-AKA result indication configuration.

        Args:
            result_ind (int): Set to 1 to enable result indication, 0 to disable.
        """
        self.config.append(f'eap_sim_aka_result_ind={result_ind}')

    def add_eap_sim_id(self, sim_id: int):
        """
        Add EAP-SIM ID configuration.

        Args:
            sim_id (int): EAP-SIM ID.
        """
        self.config.append(f'eap_sim_id={sim_id}')

    def add_eap_sim_aka_fast_reauth_limit(self, limit: int):
        """
        Add EAP-SIM-AKA fast reauthentication limit configuration.

        Args:
            limit (int): EAP-SIM-AKA fast reauthentication limit.
        """
        self.config.append(f'eap_sim_aka_fast_reauth_limit={limit}')

    def add_eap_server_erp(self, enable_erp: int):
        """
        Add EAP server ERP configuration.

        Args:
            enable_erp (int): Set to 1 to enable EAP server ERP, 0 to disable.
        """
        self.config.append(f'eap_server_erp={enable_erp}')

    def add_ap_table_max_size(self, max_size: int):
        """
        Add maximum AP table size configuration.

        Args:
            max_size (int): Maximum AP table size.
        """
        self.config.append(f'ap_table_max_size={max_size}')

    def add_ap_table_expiration_time(self, expiration_time: int):
        """
        Add AP table expiration time configuration.

        Args:
            expiration_time (int): AP table expiration time in seconds.
        """
        self.config.append(f'ap_table_expiration_time={expiration_time}')

    def add_ap_setup_locked(self, setup_locked: int):
        """
        Add AP setup locked configuration.

        Args:
            setup_locked (int): Set to 1 to lock AP setup, 0 to unlock.
        """
        self.config.append(f'ap_setup_locked={setup_locked}')

    def add_ap_pin(self, pin: str):
        """
        Add AP PIN configuration.

        Args:
            pin (str): AP PIN.
        """
        self.config.append(f'ap_pin={pin}')

    def add_ap_settings(self, ap_settings: str):
        """
        Add AP settings configuration.

        Args:
            ap_settings (str): AP settings.
        """
        self.config.append(f'ap_settings={ap_settings}')

    def add_multi_ap_backhaul_ssid(self, backhaul_ssid: SsidText):
        """
        Add Multi-AP backhaul SSID configuration.

        Args:
            backhaul_ssid (str): Multi-AP backhaul SSID.
        """
        self.config.append(f'multi_ap_backhaul_ssid={backhaul_ssid}')

    def add_multi_ap_backhaul_wpa_psk(self, backhaul_wpa_psk: str):
        """
        Add Multi-AP backhaul WPA PSK configuration.

        Args:
            backhaul_wpa_psk (str): Multi-AP backhaul WPA PSK.
        """
        self.config.append(f'multi_ap_backhaul_wpa_psk={backhaul_wpa_psk}')

    def add_multi_ap_backhaul_wpa_passphrase(self, backhaul_passphrase: str):
        """
        Add Multi-AP backhaul WPA passphrase configuration.

        Args:
            backhaul_passphrase (str): Multi-AP backhaul WPA passphrase.
        """
        self.config.append(f'multi_ap_backhaul_wpa_passphrase={backhaul_passphrase}')

    def add_qos_map_set(self, qos_map_set: str):
        """
        Add QoS map set configuration.

        Args:
            qos_map_set (str): QoS map set configuration.
        """
        self.config.append(f'qos_map_set={qos_map_set}')

    def add_dynamic_vlan(self, dynamic_vlan: int):
        """
        Add dynamic VLAN configuration to the BSS.

        Args:
            dynamic_vlan (int): Set to 1 to enable dynamic VLAN support, 0 to disable.
        """
        self.config.append(f'dynamic_vlan={dynamic_vlan}')

    def add_vlan_file(self, vlan_file: FilePath):
        """
        Add the VLAN configuration file path to the BSS.

        Args:
            vlan_file (str): Path to the VLAN configuration file.
        """
        self.config.append(f'vlan_file={vlan_file}')

    def add_vlan_tagged_interface(self, tagged_interface: InterfaceName):
        """
        Add the tagged interface for VLANs to the BSS.

        Args:
            tagged_interface (str): Name of the tagged interface (e.g., "eth0").
        """
        self.config.append(f'vlan_tagged_interface={tagged_interface}')

    def add_vlan_bridge(self, vlan_bridge: str):
        """
        Add the VLAN bridge to the BSS.

        Args:
            vlan_bridge (str): Name of the VLAN bridge (e.g., "brvlan").
        """
        self.config.append(f'vlan_bridge={vlan_bridge}')

class HostapdManager(RunCommand, HostapdConfigGenerator):
    """
    HostapdManager class for managing hostapd service and configuration.

    This class inherits from RunCommand and HostapdConfigGenerator.

    Attributes:
        HOSTAPD_CONF_DIR (str): Directory for hostapd configuration files.

    """

    def __init__(self, hostapd_filename:FilePath):
        """
        Initializes the HostapdManager.

        Inherits from RunCommand and HostapdConfigGenerator.
        """
        super().__init__()
        
        self.hostapd_filename = f'{hostapd_filename}'

    def start(self) -> bool:
        """
        Start the hostapd service.

        Returns:
            bool: True if the service starts successfully, False otherwise.
        """
        try:
            result = self.run_command(["service", "hostapd", "start"])
            return STATUS_OK if result.exit_code == STATUS_OK else STATUS_NOK

        except Exception as e:
            self.log.exception(f"Failed to start hostapd service: {e}")
            return STATUS_NOK
    
    def enable_hostapd_cli(self, enable=True) -> bool:
        '''
        ctrl_interface=/var/run/hostapd
        ctrl_interface_group=0
        '''
        return STATUS_OK

    def restart(self) -> bool:
        """
        Restart the hostapd service.

        Returns:
            bool: True if the service restarts successfully, False otherwise.
        """
        try:
            result = self.run_command(["service", "hostapd", "restart"])
            return STATUS_OK if result.exit_code == STATUS_OK else STATUS_NOK

        except Exception as e:
            self.log.exception(f"Failed to restart hostapd service: {e}")
            return STATUS_NOK

    def stop(self) -> bool:
        """
        Stop the hostapd service.

        Returns:
            bool: True if the service stops successfully, False otherwise.
        """
        try:
            result = self.run_command(["service", "hostapd", "stop"])
            return STATUS_OK if result.exit_code == STATUS_OK else STATUS_NOK

        except Exception as e:
            self.log.exception(f"Failed to stop hostapd service: {e}")
            return STATUS_NOK

    def write_hostapd_config(self) -> bool:
        """
        Write the Hostapd configuration to a file.

        Returns:
            bool: True if the configuration is written successfully, False otherwise.
        """
        try:
            config_lines = self.generate_config()

            with open(f'{HOSTAPD_CONF_DIR}/{self.hostapd_filename}', "w") as file:
                file.write("\n".join(config_lines))

            return STATUS_OK

        except Exception as e:
            self.log.exception(f"Failed to write Hostapd configuration: {e}")
            return STATUS_NOK

    def delete_hostapd_config(self) -> bool:
        """
        Remove the Hostapd configuration file.

        Returns:
        - bool: STATUS_OK if the file is deleted successfully, STATUS_NOK otherwise.
        """
        try:

            if os.path.exists(f'{HOSTAPD_CONF_DIR}/{self.hostapd_file_name}'):
                os.remove(f'{HOSTAPD_CONF_DIR}/{self.hostapd_file_name}')
                self.log.debug(f"Hostapd configuration file '{self.hostapd_file_name}' deleted successfully.")
                return STATUS_OK
            else:
                self.log.warning(f"Hostapd configuration file '{self.hostapd_file_name}' not found.")
                return STATUS_NOK

        except Exception as e:
            self.log.error(f"Failed to delete Hostapd configuration file: {e}")
            return STATUS_NOK
  
    def restart_with_new_config(self, hostapd_config_fn: str) -> bool:
        """
        Restart the hostapd service with a new configuration.

        Args:
            hostapd_config_fn (str): Filename for the hostapd configuration.

        Returns:
            bool: True if the service restarts successfully, False otherwise.
        """
        try:
            restart_result = self.restart()

            if restart_result != STATUS_OK:
                self.log.error("Failed to restart hostapd service after configuration update.")
                return STATUS_NOK

            return STATUS_OK

        except Exception as e:
            self.log.exception(f"Failed to restart hostapd service: {e}")
            return STATUS_NOK

    def load(self, hostapd_config_fn: str) -> bool:
        """
        Load the Hostapd configuration.

        Args:
            hostapd_config_fn (str): Filename for the hostapd configuration.

        Returns:
            bool: True if the configuration is loaded successfully, False otherwise.
        """
        cmd = ['hostapd', '-B', f'{HOSTAPD_CONF_DIR}/{hostapd_config_fn}']
        result = self.run(cmd, suppress_error=True)

        if result.exit_code:
            self.log.error(f'Unable to load hostapd config: {hostapd_config_fn}')
            return STATUS_NOK

        return STATUS_OK

      

# FILE: src/routershell/lib/network_manager/network_operations/interface.py
import ipaddress
import json
import logging

from routershell.lib.common.common import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import InetAddressText, InetCidrText, InterfaceName, MacAddressText, NatPoolName
from routershell.lib.db.interface_db import InterfaceDatabase
from routershell.lib.network_manager.common.interface import InterfaceType
from routershell.lib.network_manager.common.phy import Duplex, Speed, State
from routershell.lib.network_manager.network_operations.arp import Arp, Encapsulate
from routershell.lib.network_manager.network_operations.nat import Nat, NATDirection
from routershell.lib.network_manager.network_operations.network_mgr import NetworkManager


class InvalidInterface(Exception):
    def __init__(self, message):
        super().__init__(message)

class Interface(NetworkManager, InterfaceDatabase):

    def __init__(self, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().INTERFACE)
        self.arg = arg

    def clear_interface_arp(self, interface_name: InterfaceName | None=None) -> bool:
        """
        Clear the ARP cache for a specific network interface using iproute2.

        This method clears the ARP cache for the specified network interface using the iproute2 tool.

        Args:
            interface_name (str, optional): The name of the network interface to clear the ARP cache for.
                If not provided, the ARP cache for all interfaces will be cleared. Defaults to None.

        Returns:
            bool: STATUS_OK if the ARP cache was successfully cleared, STATUS_NOK otherwise.
        """

        if interface_name:
            # Clear the ARP cache for a specific interface
            self.run(['sudo', 'ip', 'neigh', 'flush', 'dev', interface_name], suppress_error=True)
        else:
            # Clear the ARP cache for all interfaces
            self.run(['sudo', 'ip', 'neigh', 'flush', 'all'], suppress_error=True)
        return STATUS_OK
    
    def get_os_network_interfaces(self, interface_type: InterfaceType | None = None) -> list[str]:
        """
        Retrieve network interface names based on their type. If no type is specified, retrieves all interfaces.

        Args:
            interface_type (InterfaceType | None): The type of network interface to retrieve.
                - InterfaceType.LOOPBACK: Retrieve loopback interfaces.
                - InterfaceType.ETHERNET: Retrieve Ethernet interfaces.
                - InterfaceType.WIRELESS: Retrieve wireless interfaces.

        Returns:
            list[str]: A list of network interface names of the specified type, or all if no type is specified.
        """
        command = ['lshw', '-class', 'network', '-short']
        output = self.run(command, suppress_error=True)
        
        if not output.stdout:
            return []

        interfaces = []
        for line in output.stdout.split('\n')[2:]:
            if not line.strip():
                continue
            
            parts = line.split()
            description = ' '.join(parts[1:-1])
            iface_name = parts[1] if len(parts) > 1 else ""

            if interface_type is None:
                interfaces.append(iface_name)
            elif interface_type == InterfaceType.LOOPBACK:
                if 'loopback' in iface_name.lower():
                    interfaces.append(iface_name)
            elif interface_type == InterfaceType.ETHERNET:
                if 'Ethernet' in description:
                    interfaces.append(iface_name)
            elif interface_type == InterfaceType.WIRELESS_WIFI:
                if 'Wireless' in description:
                    interfaces.append(iface_name)

        return interfaces
    
    def does_os_interface_exist(self, interface_name: InterfaceName, include_loopbacks: bool=True) -> bool:
        """
        Determine if a network interface with the specified name exists on the current system.

        This method utilizes the 'ip -json address show' command to retrieve a list of all network interfaces
        present on the system and subsequently verifies if the provided interface name is included in the
        command's output. It also checks for labeled sub-interfaces of loopback.

        Args:
            interface_name (str): The name of the network interface to be checked.
            include_loopbacks (bool): Whether to include loopback interfaces in the check.

        Returns:
            bool: A boolean value indicating the existence of the specified interface.
            - True: The interface exists.
            - False: otherwise
        """
        try:
            result = self.run(['ip', '-json', 'address', 'show'], suppress_error=True)
            
            if result.exit_code:
                self.log.debug(f"does_os_interface_exist() returned a non-zero exit code: {result.exit_code}")
                return False
            
            interfaces = json.loads(result.stdout)
            
            for interface in interfaces:
                ifname = interface.get("ifname", "")
                
                # Check for the main interface
                if ifname == interface_name:
                    if "loopback" in interface.get("link_type", "") and not include_loopbacks:
                        continue
                    return True
                
                # Check for labeled sub-interfaces under loopback (lo)
                if ifname == "lo" and include_loopbacks:
                    for addr_info in interface.get("addr_info", []):
                        label = addr_info.get("label", "")
                        if label == interface_name:
                            return True

            self.log.debug(f"does_os_interface_exist() '{interface_name}' does not exist")
            return False
                
        except Exception as e:
            self.log.error(f"Exception in does_os_interface_exist: {e}")
            return False

    def get_os_interface_type(self, interface_name: InterfaceName, include_loopback_labels: bool=True) -> InterfaceType:
        """
        Get the type of a network interface (physical, virtual, or VLAN) based on its name.

        Args:
            interface_name (str): The name of the network interface to query.

        Returns:
            InterfaceType: The type of the interface, which can be 'ETHERNET', 'VIRTUAL', 'VLAN', 'BRIDGE', 'LOOPBACK', or 'UNKNOWN'.
        """
        
        if include_loopback_labels:
            if interface_name in Interface().get_os_lo_labels():
                self.log.debug(f'interface" {interface_name} is a type {InterfaceType.LOOPBACK.value}')
                return InterfaceType.LOOPBACK
        
        result = self.run(['ip', '-json', 'link', 'show', interface_name], suppress_error=True)
        self.log.debug(f"get_os_interface_type() -> stdout: {result.stdout}")

        if result.exit_code:
            self.log.debug(f"get_os_interface_type() -> Interface Not Found: {interface_name}")
            return InterfaceType.UNKNOWN

        try:
            interfaces = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            self.log.error(f"Failed to decode JSON: {e}")
            return InterfaceType.UNKNOWN

        if not interfaces:
            self.log.debug(f"get_os_interface_type() -> No interfaces found for: {interface_name}")
            return InterfaceType.UNKNOWN

        interface = interfaces[0]
        self.log.debug(f"Parsed interface JSON: {interface}")

        link_type = interface.get('link_type', '')
        self.log.debug(f"Detected link type: {link_type}")

        if link_type == 'ether':
            return InterfaceType.ETHERNET
        elif link_type in ['tun', 'tap']:
            return InterfaceType.VIRTUAL
        elif link_type == 'vlan':
            return InterfaceType.VLAN
        elif link_type == 'bridge':
            return InterfaceType.BRIDGE
        elif link_type == 'loopback':
            return InterfaceType.LOOPBACK

        return InterfaceType.UNKNOWN

    def get_os_interface_type_extened(self, interface_name: InterfaceName) -> InterfaceType:
        """
        Get the type of a network interface using lshw.

        This method retrieves information about the network interface using lshw and determines its type based on the
        capabilities and configuration.

        Args:
            interface_name (str): The name of the network interface.

        Returns:
            InterfaceType: An enumeration representing the type of the network interface.
        """
        interface_info = self.get_os_interface_hardware_info(interface_name)
        
        if not interface_info:
            if_type =  self.get_os_interface_type(interface_name)
            return if_type
        
        elif interface_info.get('capabilities', {}).get('wireless'):
            return InterfaceType.WIRELESS_WIFI
        
        elif interface_info.get('capabilities', {}).get('tp') or interface_info.get('configuration', {}).get('duplex'):
            return InterfaceType.ETHERNET
        
        return self.get_os_interface_type(interface_name)

    def get_db_interface_type(self, interface_name) -> InterfaceType:
        """
        Get the interface type for a specified interface name from the database.

        Args:
            interface_name (str): The name of the interface.

        Returns:
            InterfaceType: The type of the interface.
        """
        interface_details = self.get_interface_details()

        for if_dict in interface_details:
            if if_dict['Interfaces']['InterfaceName'] == interface_name:                
                interface_type_str = if_dict['Interfaces']['Properties']['InterfaceType']
                for interface_enum in InterfaceType:
                    if interface_type_str == interface_enum.value:
                        return interface_enum

        return InterfaceType.UNKNOWN

    def does_db_interface_exist(self, interface_name: InterfaceName) -> bool:
        """
        Determine if a network interface with the specified name exists on the DB.
        Args:
            interface_name (str): The name of the network interface to be checked.

        Returns:
            bool: A boolean value indicating the existence of the specified interface in the DB.
            - True: The interface exists.
            - False: otherwise
        """        
        return self.db_lookup_interface_exists(interface_name).status

    def add_db_interface_entry(self, interface_name: InterfaceName, ifType: InterfaceType) -> bool:
        """
        Add an interface entry to the database.

        Args:
            interface_name (str): The name of the interface to be added.
            ifType (InterfaceType): The type of the interface.

        Returns:
            bool: STATUS_OK if the interface entry is added successfully, STATUS_NOK if there is an error.

        """
        if self.add_db_interface(interface_name, ifType):
            self.log.debug(f"Unable to add interface: {interface_name} to DB")
            return STATUS_NOK
        
        if ifType != InterfaceType.ETHERNET:
            self.update_db_ifSpeed(interface_name, None)
            self.update_db_duplex(interface_name, None)
        
        return STATUS_OK
        
    def update_interface_mac(self, interface_name: InterfaceName, mac: MacAddressText | None = None) -> bool:
        """
        Update the MAC address of a network interface.
        Update the MAC address to the DB 

        This method either generates a random MAC address or uses the provided MAC address
        (if valid) and assigns it to the specified network interface.

        Args:
        
        interface_name (str): The name of the network interface to which the MAC address will be assigned.
        
        mac (str, optional): Supported MAC address formats:
        - xx:xx:xx:xx:xx:xx
        - xx-xx-xx-xx-xx-xx
        - xxxx.xxxx.xxxx
        - xxxxxxxxxxxx

        Returns:
            bool: STATUS_OK if the MAC address was successfully added, STATUS_NOK otherwise.
        """
        self.log.debug(f"update_interface_mac() -> interface_name: {interface_name} -> mac: {mac}")

        if not mac:
            new_mac = self.generate_random_mac()
            self.log.debug(f"update_interface_mac() mac-auto: {new_mac}")

        elif self.is_valid_mac_address(mac):
            stat, format_mac = self.format_mac_address(mac)
            self.log.debug(f"update_interface_mac() -> mac: {mac} -> format_mac: {format_mac}")

            if not stat:
                self.log.error(f"Unable to format MAC address: {mac}")
                return STATUS_NOK

        else:
            self.log.error(f"Invalid MAC address: {mac}")
            return STATUS_NOK

        if self.set_interface_mac(interface_name, new_mac if not mac else format_mac):
            self.log.error(f"Unable to set MAC address to interface: {interface_name} via OS")
            return STATUS_NOK

        if self.update_db_mac_address(interface_name, new_mac if not mac else format_mac):
            self.log.error(f"Unable to set MAC address to interface: {interface_name} via DB")
            return STATUS_NOK

        return STATUS_OK

    def update_interface_inet(self, interface_name: InterfaceName, inet_address: InetAddressText, secondary: bool = False, negate: bool = False) -> bool:
        """
        Add or remove an inet address from a network interface.
        Update interface inet DB
        
        This method either adds or removes an inet address from the specified network interface.

        Args:
            interface_name (str): The name of the network interface.
            inet_address (str): The IP address in CIDR notation (e.g., "192.168.1.1/24" for IPv4 or "2001:db8::1/64" for IPv6).
            secondary (bool, optional): If True, the method will configure the address as secondary. If False, it will configure it as the primary address (default is False).
            negate (bool): If True, the method will remove the specified IP address from the interface. If False, it will add the address.

        Returns:
            bool: STATUS_OK if the IP address was successfully updated, STATUS_NOK otherwise.
        """
        self.log.debug(f"update_interface_inet() -> interface: {interface_name} -> inet: {inet_address} -> secondary: {secondary} -> negate: {negate}")

        if negate:
            if self.del_inet_address(interface_name, inet_address):
                self.log.error(f"Unable to remove inet Address: {inet_address} from interface: {interface_name} via OS")
                return STATUS_NOK
            
        else:
            if self.set_inet_address(interface_name, inet_address, secondary):
                self.log.error(f"Unable to set inet Address: {inet_address} to interface: {interface_name} via OS")
                return STATUS_NOK
        
        if self.update_db_inet_address(interface_name, inet_address, secondary, negate):
            self.log.error(f"Unable to update inet Address: {inet_address} to interface: {interface_name} via DB")
            return STATUS_NOK
        
        return STATUS_OK

    def update_interface_duplex(self, interface_name: InterfaceName, duplex: Duplex) -> bool:
        """
        Add or set the duplex mode for a network interface.

        This method allows adding or setting the duplex mode to 'auto', 'half', or 'full' for the specified interface.

        Args:
            interface_name (str): The name of the network interface to configure.
            duplex (Duplex): The duplex mode to set. Valid values are Duplex.AUTO, Duplex.HALF, or Duplex.FULL.

        Returns:
            bool: STATUS_OK if successful, STATUS_NOK otherwise.
        """
        
        if duplex == Duplex.NONE:
            
            if self.update_db_duplex(interface_name, duplex.value):
                self.log.error(f"Unable to update interface: {interface_name} to duplex: {duplex.value}")
                return STATUS_NOK
            
            return STATUS_OK            
        
        if self.set_duplex(interface_name, duplex):
            print(f"Invalid duplex mode ({duplex.value}). Use 'auto', 'half', or 'full'.")
            return STATUS_NOK
        
        if self.update_db_duplex(interface_name, duplex.value):
            self.log.error(f"Unable to update interface: {interface_name} to duplex: {duplex.value}")
            return STATUS_NOK
            
        self.log.debug(f"Updated interface: {interface_name} to duplex: {duplex.value}")
        
        return STATUS_OK
    
    def update_interface_speed(self, interface_name: InterfaceName, speed: Speed) -> bool:
        """
        Set the network interface speed and update it in the database.

        Args:
            interface_name (str): The name of the network interface to configure.
            speed (Speed): The desired speed setting.

        Returns:
            bool: STATUS_OK if the speed configuration was successful, STATUS_NOK otherwise.
        """

        self.log.debug(f"update_interface_speed() -> interface: {interface_name} Speed: {speed}")
        
        if speed == Speed.NONE:
            if self.update_db_ifSpeed(interface_name, speed.value):
                self.log.error(f'Unable to update database speed: {speed.value} on interface: {interface_name}')
                return STATUS_NOK
            return STATUS_OK
        
        if speed == Speed.AUTO_NEGOTIATE:
            self.set_speed(interface_name, Speed.AUTO_NEGOTIATE, Speed.AUTO_NEGOTIATE)
            self.update_db_ifSpeed(interface_name, Speed.AUTO_NEGOTIATE.value)
            
        elif speed in {Speed.MBPS_10, Speed.MBPS_100, Speed.MBPS_1000, Speed.MBPS_10000}:
            self.set_speed(interface_name, speed)
            self.update_db_ifSpeed(interface_name, str(speed.value))
        
        else:
            print(f"Invalid speed value: {speed.value}")
            return STATUS_NOK
        
        return STATUS_OK
            
    def update_shutdown(self, interface_name: InterfaceName, state: State) -> bool:
        """
        Set the shutdown status of a network interface.

        This method allows setting the shutdown status of the specified network interface to 'up' or 'down'.

        Args:
            interface_name (str): The name of the network interface to configure.
            state (State): The status to set. Valid values are State.UP (to bring the interface up)
                        or State.DOWN (to shut the interface down).

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        shutdown = state != State.UP
        
        if self.update_db_shutdown_status(interface_name, shutdown):
            self.log.error(f"Unable to set interface: {interface_name} to {state.value} via db")
            return STATUS_NOK
        
        self.log.debug(f"update_shutdown() -> interface_name: {interface_name} -> State: {state} via os")
        return self.set_interface_shutdown(interface_name, state)
     
    def create_os_dummy_interface(self, interface_name:InterfaceName) -> bool:
        """
        Create a dummy interface with the specified name to OS.

        Args:
            interface_name (str): The name for the dummy interface.

        Returns:
            bool: STATUS_OK if the dummy interface was created successfully, STATUS_NOK otherwise.
        """
        result = self.run(['ip', 'link', 'add', 'name', interface_name , 'type', 'dummy'], suppress_error=True)
        
        if result.exit_code:
            self.log.error(f'Error creating dummy -> {interface_name}, Reason: {result.stderr}')
            return STATUS_NOK
        
        self.log.debug(f'Created {interface_name} Dummy')
        
        return STATUS_OK

    def destroy_os_dummy_interface(self, interface_name: InterfaceName) -> bool:
        """
        Destroy a dummy interface with the specified name on the OS.

        Args:
            interface_name (str): The name of the dummy interface to destroy.

        Returns:
            bool: STATUS_OK if the dummy interface was destroyed successfully, STATUS_NOK otherwise.
        """
        result = self.run(['ip', 'link', 'delete', interface_name, 'type', 'dummy'], suppress_error=True)

        if result.exit_code:
            self.log.error(f'Error destroying dummy -> {interface_name}, Reason: {result.stderr}')
            return STATUS_NOK

        self.log.debug(f'Destroyed {interface_name} dummy')
        return STATUS_OK
        
    def rename_interface(self, initial_interface_name: InterfaceName, 
                        alias_interface_name: InterfaceName, 
                        suppress_error: bool=True) -> bool:
        """
        Rename a network interface to a specified alias name.
        
        This method renames a network interface from `initial_interface_name` to `alias_interface_name`. If the initial 
        interface does not exist, or if the renaming process fails, it logs an error unless `suppress_error` is set to `True`.
        
        Args:
            initial_interface_name (str): The current name of the network interface to be renamed.
            alias_interface_name (str): The new alias name for the network interface.
            suppress_error (bool, optional): If True, suppresses error logging when renaming fails. Defaults to True.
        
        Returns:
            bool: STATUS_OK if the interface was renamed successfully, STATUS_NOK otherwise.
        """
        self.log.debug(f"rename_interface() -> if: {initial_interface_name} -> alias-if: {alias_interface_name}")
        
        # Check if the initial interface exists
        if not self.does_os_interface_exist(initial_interface_name):
            if not suppress_error:
                self.log.error(f"Interface: {initial_interface_name} does not exist")
            return STATUS_NOK        

        # Get the hardware bus info for the initial interface
        bus_info = self.get_os_interface_hardware_info(initial_interface_name)['businfo']
        
        # Attempt to rename the interface using the `ip` command
        result = self.run(['ip', 'link', 'set', initial_interface_name, 'name', alias_interface_name], suppress_error=True)
        
        # Check if the alias interface already exists in the database
        if self.db_lookup_interface_alias_exist(initial_interface_name, alias_interface_name):
            self.log.debug(f"Alias-Interface already exists: {alias_interface_name} assigned to initial-interface: {initial_interface_name}")
            return STATUS_OK
        
        # If the `ip` command failed, handle the error
        if result.exit_code:
            if not suppress_error:
                self.log.error(f"Unable to rename interface {initial_interface_name} to {alias_interface_name} in the OS")
            return STATUS_NOK
        
        # Update the database with the new alias name
        if self.update_db_rename_alias(bus_info, initial_interface_name, alias_interface_name):
            if not suppress_error:
                self.log.error(f"Unable to add initial-interface: {initial_interface_name} to alias-interface: {alias_interface_name} in the DB")
            return STATUS_NOK
        
        return STATUS_OK
       
    def set_os_rename_interface(self, reverse=False, suppress_error: bool=True) -> bool:
        """
        Rename network interfaces based on database aliases.
        
        This method renames network interfaces as specified in the database. It can also reverse the renaming process
        if the `reverse` parameter is set to `True`. If an error occurs during the renaming process, it logs an error 
        message unless `suppress_error` is set to `True`.
        
        Args:
            reverse (bool, optional): If True, reverses the renaming process by swapping original and alias names. 
                                    Defaults to False.
            suppress_error (bool, optional): If True, suppresses error logging when renaming fails. Defaults to True.
        
        Returns:
            bool: STATUS_OK if all interfaces were renamed successfully, STATUS_NOK otherwise.
        """
        for alias in self.get_db_interface_aliases():
            original_name = alias['InterfaceName']
            alias_name = alias['AliasInterface']

            self.log.debug(f'orig-interface: {original_name} -> new-interface: {alias_name}')

            if reverse:
                original_name, alias_name = alias_name, original_name

            if self._rename_os_interface(original_name, alias_name):
                if not suppress_error:
                    self.log.error(f"Failed to update and rename interface: {original_name} to {alias_name}")
                return STATUS_NOK

            self.log.debug(f"Interface {original_name} successfully updated and renamed to {alias_name}")

        return STATUS_OK

    def update_interface_proxy_arp(self, interface_name: InterfaceName, negate: bool = False) -> bool:
        """
        Enable or disable Proxy ARP on a network interface and update the Proxy ARP configuration in the database.

        This method allows you to enable or disable Proxy ARP on the specified network interface and update the Proxy ARP
        configuration in the database.

        Args:
            interface_name (str): The name of the network interface.
            negate (bool): If True, Proxy ARP will be disabled on the interface. If False, Proxy ARP will be enabled.

        Returns:
            bool: STATUS_OK if the Proxy ARP configuration was successfully updated, STATUS_NOK otherwise.
        """
        if Arp().set_os_proxy_arp(interface_name, negate):
            self.log.error(f"Unable to update proxy-arp: {not negate} on interface: {interface_name} via OS")
            return STATUS_NOK

        if self.update_db_proxy_arp(interface_name, (not negate)):
            self.log.error(f"Unable to update proxy-arp: {not negate} on interface: {interface_name} via DB")
            return STATUS_NOK

        return STATUS_OK

    def update_interface_drop_gratuitous_arp(self, interface_name: InterfaceName, negate: bool = False) -> bool:
        """
        Enable or disable the dropping of gratuitous ARP packets on a network interface and update the configuration in the database.

        This method allows you to enable or disable the dropping of gratuitous ARP packets on the specified network interface
        and update the configuration in the database.

        Args:
            interface_name (str): The name of the network interface.
            negate (bool): If True, gratuitous ARP dropping will be disabled on the interface. If False, it will be enabled.

        Returns:
            bool: STATUS_OK if the gratuitous ARP configuration was successfully updated, STATUS_NOK otherwise.
        """
        if Arp().set_os_drop_gratuitous_arp(interface_name, negate):
            self.log.error(f"Unable to update drop-gratuitous-arp: {not negate} on interface: {interface_name} via OS")
            return STATUS_NOK

        if self.update_db_drop_gratuitous_arp(interface_name, (not negate)):
            self.log.error(f"Unable to update drop-gratuitous-arp: {not negate} on interface: {interface_name} via DB")
            return STATUS_NOK

        return STATUS_OK

    def update_interface_static_arp(self, interface_name: InterfaceName, inet: InetAddressText, mac_address: MacAddressText, encap: Encapsulate, negate: bool = False) -> bool:
        """
        Enable or disable a static ARP entry for a network interface and update the static ARP configuration in the database.

        This method allows you to enable or disable a static ARP entry on the specified network interface and update the
        static ARP configuration in the database.

        Args:
            interface_name (str): The name of the network interface.
            inet (str): The IP address associated with the ARP entry.
            mac_address (str): The MAC address associated with the ARP entry.
            encap (Encapsulate): The type of encapsulation used for the ARP entry.
            negate (bool): If True, the static ARP entry will be disabled. If False, the static ARP entry will be enabled.

        Returns:
            bool: STATUS_OK if the static ARP configuration was successfully updated, STATUS_NOK otherwise.
        """
        status, mac_address = self.format_mac_address(mac_address)
        
        if not status:
            self.log.error(f"Invalid ARP entry mac address: {mac_address}")
            return STATUS_NOK
        
        if not Arp().is_arp_entry_exists(inet):
            self.log.debug(f"ARP entry for {inet} already exists")
            
            if Arp().set_os_static_arp(interface_name, inet, mac_address, encap.value, not negate):
                self.log.error(f"Unable to update static ARP: {not negate} on interface: {interface_name} via OS")
                return STATUS_NOK
        
        if self.update_db_static_arp(interface_name, inet, mac_address, encap.value, negate):
            self.log.error(f"Unable to update static ARP: {not negate} on interface: {interface_name} via DB")
            return STATUS_NOK

        return STATUS_OK

    def set_nat_domain_status_1(self, interface_name:InterfaceName, nat_in_out:NATDirection, negate=False):
        
        if nat_in_out is NATDirection.INSIDE:
            if Nat().create_inside_nat(interface_name):
                self.log.error(f"Unable to add INSIDE NAT to interface: {interface_name}")
                return STATUS_NOK
        else:
            if Nat().create_outside_nat(interface_name):
                self.log.error(f"Unable to add INSIDE NAT to interface: {interface_name}")
                return STATUS_NOK
            
        return STATUS_OK        

    def set_nat_domain_status_2(self, interface_name:InterfaceName, nat_pool_name:NatPoolName, nat_in_out:NATDirection, negate=False):
        if nat_in_out == NATDirection.INSIDE.value:
            self.log.debug("Configuring NAT for the inside interface")
            
            if Nat().create_inside_nat(nat_pool_name, self.ifName, negate):
                self.log.error(f"Unable to set INSIDE NAT to interface: {self.ifName} to NAT-pool {nat_pool_name}")
                return STATUS_NOK

            if self.update_db_nat_direction(self.ifName, nat_pool_name, NATDirection.INSIDE, negate):
                self.log.debug(f"Unable to update NAT Direction: {nat_in_out}")
                return STATUS_NOK
        
        elif nat_in_out == NATDirection.OUTSIDE.value:
            self.log.debug("Configuring NAT for the outside interface")
            
            if Nat().create_outside_nat(nat_pool_name, self.ifName, negate):
                self.log.error(f"Unable to set OUTSIDE NAT to interface: {self.ifName} to NAT-pool {nat_pool_name}")
                return STATUS_NOK
            
            if self.update_db_nat_direction(self.ifName, nat_pool_name, NATDirection.OUTSIDE, negate):
                self.log.debug(f"Unable to update NAT Direction: {nat_in_out}")
                return STATUS_NOK
        return STATUS_OK

    def set_nat_domain_status(self, interface_name: InterfaceName, nat_pool_name: NatPoolName, nat_in_out: NATDirection, negate=False) -> bool:
        """
        Configure NAT domain status for an interface.

        Args:
            interface_name (str): The name of the interface.
            nat_pool_name (str): The name of the NAT pool.
            nat_in_out (NATDirection): The direction of NAT (INSIDE or OUTSIDE).
            negate (bool, optional): Whether to negate the NAT configuration. Default is False.

        Returns:
            bool: STATUS_OK if NAT configuration is successful, STATUS_NOK if there is an error.

        """
        if nat_in_out == NATDirection.INSIDE:
            self.log.debug("Configuring NAT for the inside interface")

            if Nat().create_inside_nat(nat_pool_name, interface_name, negate):
                self.log.error(f"Unable to set INSIDE NAT to interface: {interface_name} to NAT-pool {nat_pool_name} via OS")
                return STATUS_NOK
            
        elif nat_in_out == NATDirection.OUTSIDE:
            self.log.debug("Configuring NAT for the outside interface")

            if Nat().create_outside_nat(nat_pool_name, interface_name, negate):
                self.log.error(f"Unable to set OUTSIDE NAT to interface: {interface_name} to NAT-pool {nat_pool_name} via OS")
                return STATUS_NOK

        return STATUS_OK

    def get_os_interface_hardware_info(self, interface_name: InterfaceName) -> dict:
        """
        Retrieve information about hardware network interfaces.

        Args:
            interface_name (str): The name of the network interface to retrieve information for.

        Returns:
            dict or None: A dictionary containing information about the network interface if successful,
                          None otherwise.
        """
        try:
            result = self.run(['lshw', '-c', 'network', '-json'], suppress_error=True)

            if result.exit_code == 0:
                output_json = json.loads(result.stdout)

                for interface in output_json:
                    if interface.get('logicalname') == interface_name:
                        return interface

                self.log.debug(f"No information found for interface: {interface_name}")
                return None
            
            else:
                self.log.debug(f"Error running lshw command. Exit code: {result.exit_code}")
                return None

        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Error decoding JSON: {e}")
            return None

    def update_interface_description(self, interface_name: InterfaceName, description: str) -> bool:
        """
        Update the description of a network interface in the database.

        This method allows you to update the user-defined description of a specific network interface in the database.

        Args:
            interface_name (str): The name of the network interface.
            description (str): The new description to assign to the network interface.

        Returns:
            bool: STATUS_OK if the description is successfully updated, STATUS_NOK otherwise.
        """
        return self.update_db_description(interface_name, description)

    def update_interface_db_from_os(self, interface_name: InterfaceName | None = None) -> bool:
        """
        Update the database with information about network interfaces found by the operating system.

        This method iterates through all network interfaces discovered by the operating system,
        checks the database to ensure that each interface is not already defined. If not defined,
        it creates an entry with basic configuration. Otherwise, it skips the interface.

        Args:
            interface_name (str, optional): The name of a specific network interface to update.

        Returns:
            bool: STATUS_OK if the update process is successful, STATUS_NOK otherwise.
        """
        for if_name in self.get_os_network_interfaces():
            
            if interface_name is not None and if_name != interface_name or not self.db_lookup_interface_exists(if_name):
                self.log.debug(f"Unknown interface: {if_name}")
                continue
            
            if_type = self.get_os_interface_type_extened(if_name)
                       
            if if_type != InterfaceType.UNKNOWN:
                self.log.debug(f"Adding Interface: {if_name} -> if-type: {if_type.name} to DB")
                self.add_db_interface_entry(if_name, if_type)
                self.update_interface_description(if_name,f'Interface Type: {if_type.name}')
                self.update_shutdown(if_name, State.UP)

        return STATUS_OK

    def _rename_os_interface(self, initial_interface_name: InterfaceName, alias_interface_name: InterfaceName) -> bool:
        """
        Rename the operating system network interface.

        This method uses the 'ip' command to rename the specified network interface.
        
        Args:
            initial_interface_name (str): The current name of the network interface.
            alias_interface_name (str): The new name to assign to the network interface.

        Returns:
            bool: STATUS_OK if the renaming process is successful, STATUS_NOK otherwise.
        """
        result = self.run(['ip', 'link', 'set', initial_interface_name, 'name', alias_interface_name], suppress_error=True)

        if result.exit_code:
            self.log.debug(f"Error renaming interface: {initial_interface_name} to {alias_interface_name}")
            return STATUS_NOK

        self.log.debug(f"Interface {initial_interface_name} successfully renamed to {alias_interface_name}")
        
        return STATUS_OK

    def fetch_db_interface_names(self) -> list[str]:
        """
        Get a list of all interface names from DB.

        Returns:
            list[str]: A list containing the names of all interfaces.
        """
        return self.get_db_interface_names()
    
    def flush_interfaces(self, interface_name: InterfaceName | None = None) -> bool:
        """
        Flush network interfaces, removing any configurations.

        This method iterates through the list of network interfaces and uses the 'flush_interface' method
        to remove configurations. If a specific interface name is provided, only that interface is flushed.

        Args:
            interface_name (str, optional): The name of the specific network interface to flush.

        Returns:
            bool: STATUS_OK if the flush process is successful, STATUS_NOK otherwise.
        """
        if interface_name:
            self.flush_interface(interface_name)
        else:
            for if_name in self.get_db_interface_names():
                self.flush_interface(if_name)

        return STATUS_OK

    # LoopBack Operations

    def get_os_lo_labels(self) -> list[str]:
        """
        Extract labels from the loopback interface labels

        Args:
            ip_lo_json (dict): The JSON data structure for the loopback interface.

        Returns:
            list[str]: A list of labels found in the loopback interface's address information.
        """
        labels = []
        
        try:
            result = self.run(['ip', '-json', 'address', 'show', 'dev', 'lo'], suppress_error=True)
            
            if result.exit_code:
                self.log.debug(f"does_os_interface_exist() returned a non-zero exit code: {result.exit_code}")
                return []
                            
        except Exception as e:
            self.log.error(f"Exception in does_os_interface_exist: {e}")
            return []

        interfaces = json.loads(result.stdout)
        
        for interface in interfaces:
            ifname = interface.get("ifname", "")
                            
            if ifname == "lo":
                for addr_info in interface.get("addr_info", []):
                    label = addr_info.get("label", "lo")
                    labels.append(label.split(":")[-1])

        return labels

    def create_os_loopback(self, loopback_name: InterfaceName, inet_address: InetAddressText) -> bool:
        """
        Creates a loopback interface with the specified name (label) and IP address on the 'lo' device.

        Args:
            loopback_name (str): The name (label) for the new loopback interface.
            inet_address (str): The IP address to assign to the loopback interface.

        Returns:
            bool: STATUS_OK if the loopback interface was created successfully, otherwise STATUS_NOK.
        """
        
        if loopback_name in self.get_os_lo_labels():
            self.log.debug(f"Loopback interface {loopback_name} already exists.")
            return STATUS_NOK
        
        try:
            ip = ipaddress.ip_address(inet_address)
            if ip.version == 4:
                ip_ver_opt = 'addr'
                cidr = '/32'
            elif ip.version == 6:
                ip_ver_opt = '-6 addr'
                cidr = '/128'
            else:
                self.log.error(f'inet address is invalid: {inet_address}')
                return STATUS_NOK
            
        except ValueError:
            self.log.error(f'inet address is invalid: {inet_address}')
            return STATUS_NOK

        inet_address += cidr

        command = ['ip', ip_ver_opt, 'add', inet_address, 'label', f'lo:{loopback_name}', 'dev', 'lo']
        
        rtn = self.run(command, suppress_error=True)
        
        if rtn.exit_code != 0:
            self.log.error(f"Failed to create loopback interface {loopback_name} with address {inet_address}: {rtn.stderr}")
            return STATUS_NOK
        
        return STATUS_OK
    
    def set_db_loopback(self, loopback_name: InterfaceName, inet_address_cidr: InetCidrText) -> bool:
        """
        Sets a loopback interface in the database with the specified name and IP address in CIDR notation.

        Args:
            loopback_name (str): The name (label) for the loopback interface.
            inet_address_cidr (str): The IP address with CIDR notation to assign to the loopback interface.

        Returns:
            bool: STATUS_OK if the loopback interface was set successfully, otherwise STATUS_NOK.
        """
        
        # Attempt to add the loopback interface entry to the database
        if not self.add_db_interface_entry(interface_name=loopback_name, ifType=InterfaceType.LOOPBACK):
            self.log.error(f'Unable to add Loopback interface: {loopback_name}')
            return STATUS_NOK
        
        # Attempt to update the IP address for the loopback interface in the database
        if not self.update_db_inet_address(interface_name=loopback_name, inet_address_cidr=inet_address_cidr):
            self.log.error(f'Unable to update inet address for Loopback interface: {loopback_name} with address: {inet_address_cidr}')
            # Remove the interface entry since the IP address update failed
            self.del_db_loopback(loopback_name)
            return STATUS_NOK
        
        return STATUS_OK
    
    def destroy_os_loopback(self, loopback_name: InterfaceName, inet_address: InetAddressText) -> bool:
        """
        Destroys a loopback interface with the specified name (label) and IP address from the 'lo' device.

        Args:
            loopback_name (str): The name (label) for the loopback interface to be removed.
            inet_address (str): The IP address assigned to the loopback interface.

        Returns:
            bool: STATUS_OK if the loopback interface was removed successfully, otherwise STATUS_NOK.
        """
        
        if loopback_name not in self.get_os_lo_labels():
            self.log.debug(f"Loopback interface {loopback_name} does not exist.")
            return STATUS_NOK
        
        try:
            ip = ipaddress.ip_address(inet_address)
            if ip.version == 4:
                ip_ver_opt = 'addr'
                cidr = '/32'
            elif ip.version == 6:
                ip_ver_opt = '-6 addr'
                cidr = '/128'
            else:
                self.log.error(f'inet address is invalid: {inet_address}')
                return STATUS_NOK
            
        except ValueError:
            self.log.error(f'inet address is invalid: {inet_address}')
            return STATUS_NOK

        inet_address += cidr

        command = ['ip', ip_ver_opt, 'del', inet_address, 'label', f'lo:{loopback_name}', 'dev', 'lo']
        
        rtn = self.run(command, suppress_error=True)
        
        if rtn.exit_code != 0:
            self.log.error(f"Failed to destroy loopback interface {loopback_name} with address {inet_address}: {rtn.stderr}")
            return STATUS_NOK
        
        return STATUS_OK
    
    def del_db_loopback(self, loopback_name: InterfaceName) -> bool:
        """
        Deletes a loopback interface from the database with the specified name.

        Args:
            loopback_name (str): The name (label) of the loopback interface to be deleted.

        Returns:
            bool: STATUS_OK if the loopback interface was deleted successfully, otherwise STATUS_NOK.
        """
        
        if not self.del_db_interface(loopback_name):
            self.log.error(f'Unable to delete Loopback interface: {loopback_name}')
            return STATUS_NOK
        
        return STATUS_OK
    
    def get_next_loopback_address(self) -> str:
        """
        Search the lo interface, retrieve a list of IPv4 addresses in the 127.x.x.x range,
        and find the next available address in that range.

        Returns:
            str: The next available 127.x.x.x address in CIDR notation.
        """
        try:
            # Get the list of addresses on the loopback interface in JSON format
            result = self.run(['ip', '-j', 'addr', 'show', 'dev', 'lo'], suppress_error=True)

            if result.exit_code != 0:
                self.log.error(f"Error retrieving IP addresses: {result.stderr}")
                return None

            data = json.loads(result.stdout)

            # Collect all 127.x.x.x addresses
            addresses = [
                ipaddress.ip_interface(f"{addr_info['local']}/{addr_info['prefixlen']}").ip
                for iface in data if iface['ifname'] == 'lo'
                for addr_info in iface.get('addr_info', [])
                if addr_info['family'] == 'inet' and ipaddress.ip_interface(f"{addr_info['local']}/{addr_info['prefixlen']}").ip.is_loopback
            ]

            # Sort addresses and find the highest one
            addresses.sort()
            last_address = addresses[-1] if addresses else ipaddress.IPv4Address('127.0.0.0')

            # Calculate the next available address
            next_address = last_address + 1
            if next_address.is_loopback:
                next_address_cidr = f"{next_address}/8"
                return next_address_cidr
            else:
                self.log.error("No more available 127.x.x.x addresses")
                return None

        except Exception as e:
            self.log.error(f"An error occurred: {e}")
            return None

    def update_interface_loopback_inet(self, loopback_name: InterfaceName, inet_address_cidr: InetCidrText | None = None, negate: bool = False) -> bool:
        """
        Update or delete the inet address of a loopback interface.

        This function updates the inet address of a specified loopback interface. If the negate parameter is set to True,
        it attempts to delete the specified inet address from the loopback interface. Otherwise, it sets the specified
        inet address. If no address is provided, it attempts to auto-assign the next available inet address.

        Parameters:
        loopback_name (str): The name of the loopback interface to update.
        inet_address_cidr (str, optional): The inet address in CIDR notation to set or delete. If None, the next available
                                        address is auto-assigned. Defaults to None.
        negate (bool): If True, the inet address is deleted from the loopback interface. If False, the address is set.
                    Defaults to False.

        Returns:
        bool: STATUS_OK if the operation was successful, otherwise STATUS_NOK.
        """
        self.log.debug(f"update_interface_loopback_inet() - Loopback: {loopback_name}, "
                    f"Inet: {inet_address_cidr}, Negate: {negate}")

        if negate:
            if not self.del_inet_address_loopback(loopback_name, inet_address_cidr):
                self.log.error(f"Unable to delete loopback: {loopback_name} address: {inet_address_cidr} from OS")
                return STATUS_NOK

            if not self.del_db_interface(loopback_name):
                self.log.error(f"Unable to delete loopback: {loopback_name} address: {inet_address_cidr} from DB")
                return STATUS_NOK

        else:
            if not inet_address_cidr:
                inet_address_cidr = self.get_next_loopback_address()
                if not inet_address_cidr:
                    self.log.error("Unable to get next available loopback address")
                    return STATUS_NOK

                self.log.debug(f'Auto-Assign Loopback: {loopback_name} - inet: {inet_address_cidr}')

            if self.set_inet_address_loopback(loopback_name, inet_address_cidr):
                self.log.error(f"Unable to update loopback: {loopback_name} address: {inet_address_cidr} to OS")
                return STATUS_NOK

            if self.add_db_interface(loopback_name, InterfaceType.LOOPBACK):
                self.log.error(f"Unable to update loopback: {loopback_name} to DB")
                return STATUS_NOK

        return STATUS_OK

# FILE: src/routershell/lib/network_manager/network_operations/nat.py
import ipaddress
import logging
from enum import Enum

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import InterfaceName, NatPoolName
from routershell.lib.db.nat_db import NatDB
from routershell.lib.network_manager.common.sysctl import SysCtl
from routershell.lib.network_manager.network_operations.network_mgr import NetworkManager


class NATDirection(Enum):
    """
    Enumeration representing NAT directions.

    - `INSIDE`: Indicates NAT is applied to the inside interface.
    - `OUTSIDE`: Indicates NAT is applied to the outside interface.
    """
    INSIDE = 'inside'
    OUTSIDE = 'outside'

class Nat(NetworkManager):

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().NAT)
        self.sysctl = SysCtl()

    def enable_ip_forwarding(self, negate: bool = False) -> bool:
        """
        Enable or disable IP forwarding in the system.

        Args:
            negate (bool): If True, disable IP forwarding; if False, enable IP forwarding. (default: False)

        Returns:
            bool: STATUS_OK if IP forwarding was successfully enabled or disabled, STATUS_NOK otherwise.
        """
        self.log.debug(f"enable_ip_forwarding() negate:{negate}")
        if self.sysctl.write_sysctl('net.ipv4.ip_forward', 1 if not negate else 0):
            self.log.error("Failed to set IP forwarding.")
            return STATUS_NOK

        return STATUS_OK

    def create_nat_pool(self, nat_pool_name: NatPoolName, negate: bool = False) -> bool:
        """
        Create or delete a NAT pool configuration in the NAT database.

        This method allows you to create or delete a NAT pool configuration in the NAT database.
        You can specify the `nat_pool_name` to create or delete, and set `negate` to True to delete
        the NAT pool.

        Args:
            - nat_pool_name (str): The name of the NAT pool to create or delete.
            - negate (bool, optional): If STATUS_OK, the method will delete the NAT pool; if False, it will create it (default: STATUS_NOK).

        Returns:
            - bool: STATUS_OK if the operation is successful, STATUS_NOK if there was an error during the operation.

        """
        self.log.debug(f"create_nat_pool() -> NAT Pool: {nat_pool_name} -> negate: {negate}")
        
        try:
            if NatDB().pool_name_exists(nat_pool_name):
                self.log.error(f"Can Not create NAT pool '{nat_pool_name}' does exist.")
                return STATUS_NOK

            if negate:
                result = NatDB().delete_global_nat_pool_name(nat_pool_name)
                self.log.debug(f"Deleting NAT pool: {nat_pool_name}")
            else:
                result = NatDB().insert_global_nat_pool_name(nat_pool_name)
                self.log.debug(f"Creating NAT pool: {nat_pool_name}")
            
            if result:
                self.log.debug(f"Did Not Update NAT pool: {nat_pool_name} -> negate: {negate}")
                return STATUS_NOK
            
            else:
                self.log.debug(f"Updated NAT pool: {nat_pool_name} -> negate: {negate}")
                return STATUS_OK

        except Exception as e:
            self.log.error(f"An error occurred while creating or deleting NAT pool: {e}")
            return STATUS_NOK

    def create_nat_ip_pool(self, nat_pool_name: NatPoolName,
                        nat_inside_ip_start: ipaddress.IPv4Address,
                        nat_inside_ip_end: ipaddress.IPv4Address,
                        nat_outside_ip_address: ipaddress.IPv4Address = None,
                        nat_outside_ifName: InterfaceName | None = None,
                        negate: bool = False) -> bool:
        """
        Create a NAT pool.

        Args:
            nat_pool_name (str): Name of the NAT pool.
            nat_inside_ip_start (ipaddress.IPv4Address): Start IP address of the NAT pool.
            nat_inside_ip_end (ipaddress.IPv4Address): End IP address of the NAT pool.
            nat_outside_ip_address (ipaddress.IPv4Address, optional): External IP address for NAT (mutually exclusive with nat_outside_ifName).
            nat_outside_ifName (str, optional): Name of the external interface (mutually exclusive with nat_outside_ip_address).

        Returns:
            bool: True if NAT pool creation is successful, False otherwise.
        """
        self.log.debug("create_nat_ip_pool()")
        try:
            if nat_outside_ip_address:
                outside_nat_arg = f"--to-source {nat_outside_ip_address}"
            elif nat_outside_ifName:
                outside_nat_arg = f"--to-source {nat_outside_ifName}"
            else:
                raise ValueError("Either nat_outside_ip_address or nat_outside_ifName must be provided")

            command = f'iptables -t nat -A POSTROUTING -s {nat_inside_ip_start}-{nat_inside_ip_end} -j SNAT {outside_nat_arg}'
            self.log.debug(f"Adding NAT CMD: {command}")

            result = self.run([command])
            if result.exit_code:
                self.log.error(f"Failed to create NAT pool: {result.stderr}")
                self.log.error(command)
                return STATUS_NOK
            return STATUS_OK
        except Exception as e:
            self.log.error(f"An error occurred while creating NAT pool: {e}")
            return STATUS_NOK
    
    def apply_nat_acl_to_pool(self, in_out: NATDirection, acl_id, nat_pool_name) -> bool:
        '''
        ip nat inside source list <acl-id> pool <nat-pool-name>
        '''
        
        direction = 'inside' if in_out == NATDirection.INSIDE else 'outside'
        command = f'ip nat {direction} source list {acl_id} pool {nat_pool_name}'
        
        result = self.run([command])
        if result.exit_code:
            self.log.error(f"Failed to apply NAT ACL to pool: {result.stderr}")
            return STATUS_NOK
        
        return STATUS_OK

    def create_outside_nat(self, nat_pool_name: NatPoolName, interface_name: InterfaceName, negate: bool = False) -> bool:
        """
        Create or destroy outside NAT (Source NAT) rule.

        Args:
            nat_pool_name (str): Name of the NAT pool.
            interface_name (str): Name of the external or outside facing interface.
            negate (bool, optional): True to destroy the NAT rule, False to create it. Defaults to False.

        Returns:
            bool: STATUS_OK if the NAT rule is created or destroyed successfully, STATUS_NOK otherwise.
        """
        self.log.debug(f"create_outside_nat() -> Pool: {nat_pool_name} -> Interface: {interface_name} -> negate: {negate}")
        
        nat_pool = NatDB().pool_name_exists(nat_pool_name)
        
        if not nat_pool:
            self.log.error(f"NAT pool {nat_pool_name} not found.")
            return STATUS_NOK

        if NatDB().is_interface_direction_in_nat_pool(interface_name, nat_pool_name, NATDirection.INSIDE.value).status:
            self.log.error(f"Cannot create outside NAT rule for NAT pool {nat_pool_name} "
                            "with active inside interfaces. Delete inside interfaces first.")
            return STATUS_NOK

        try:
            create_destroy = '-D' if negate else '-A'
            
            command = f'iptables -t nat {create_destroy} POSTROUTING -o {interface_name} -j MASQUERADE'
            result = self.run(command.split())
            if result.exit_code:
                self.log.error(f"Failed to {'destroy' if negate else 'create'} outside NAT rule: {result.stderr}")
                self.log.error(command)
                return STATUS_NOK

            if not negate:
                if NatDB().add_outside_interface(nat_pool_name, interface_name):
                    self.log.error(f"Unable to add outside interface: {interface_name} to NAT pool: {nat_pool_name} via DB")
                    return STATUS_NOK
            else:
                NatDB().delete_outside_interface(interface_name)

            return STATUS_OK
        except Exception as e:
            self.log.error(f"An error occurred while {'destroying' if negate else 'creating'} outside NAT rule: {e} via OS")
            return STATUS_NOK

    def create_inside_nat(self, nat_pool_name: NatPoolName, ifName_inside: InterfaceName, negate: bool = False) -> bool:
        """
        Create or destroy inside NAT (Source NAT) rule.

        Args:
            nat_pool_name (str): Name of the NAT pool.
            ifName_inside (str): Name of the internal interface.
            negate (bool, optional): True to destroy the NAT rule, False to create it. Defaults to False.

        Returns:
            bool: STATUS_OK if the NAT rule is created or destroyed successfully, STATUS_NOK otherwise.
        """
 
        nat_pool = NatDB().pool_name_exists(nat_pool_name)
        if not nat_pool:
            self.log.error(f"NAT pool {nat_pool_name} not found.")
            return STATUS_NOK

        if NatDB().is_interface_direction_in_nat_pool(ifName_inside, 
                                                      nat_pool_name,
                                                      NATDirection.INSIDE.value).status:
            '''Not an error, just a check in case we are re-applying'''
            self.log.debug(f"Interface {ifName_inside} is part of {NATDirection.INSIDE.value} NAT pool {nat_pool_name}")
            return STATUS_NOK
        
        outside_nat_interfaces = NatDB().get_interface_direction_in_nat_pool_list(nat_pool_name, NATDirection.OUTSIDE.value)
        
        if len(outside_nat_interfaces) > 1:
            self.log.error(f"More than 1 interfaces are defined in: {nat_pool}.  DataBase ERROR")
            return STATUS_NOK

        outside_nat_interface = outside_nat_interfaces[0]
        
        if outside_nat_interface.status:
            self.log.error(f'Unable to retrieve outside NAT interface: {outside_nat_interface.reason}')
            return STATUS_NOK
            
        outside_nat_interface = outside_nat_interface.result
        
        outside_nat_if_ip_addr = self.get_interface_ip_addresses(outside_nat_interface['InterfaceName'], 'ipv4')
        
        self.log.debug(f"NAT-Pool: {nat_pool_name} -> Out-NAT-ifName: {outside_nat_interface} -> Out-NAT-Inet: {outside_nat_if_ip_addr}")

        if not outside_nat_if_ip_addr:
            self.log.error(f"No IPv4 address assigned to outside NAT interface: {outside_nat_interface}")
            return STATUS_NOK
        
        try:
            create_destroy = '-D' if negate else '-A'
            
            command = f'iptables -t nat {create_destroy} PREROUTING -i {ifName_inside} -j DNAT --to-destination {outside_nat_if_ip_addr[0]}'
            self.log.debug(f"create_inside_nat() -> cmd: {command}")
            
            result = self.run(command.split())
            
            if result.exit_code:
                self.log.error(f"Failed to {'destroy' if negate else 'create'} inside NAT rule: {result.stderr}")
                return STATUS_NOK

            if negate:
                if NatDB().delete_inside_interface(nat_pool_name, ifName_inside):
                    self.log.error(f"Unable to destroy NAT pool: {nat_pool_name} from interface: {ifName_inside} inside interface to DB")
                    return STATUS_NOK

            else:
                if NatDB().add_inside_interface(nat_pool_name, ifName_inside):
                    self.log.error(f"Unable to add NAT pool: {nat_pool_name} to interface: {ifName_inside} inside interface to DB")
                    return STATUS_NOK

            return STATUS_OK
        
        except Exception as e:
            self.log.error(f"An error occurred while {'destroying' if negate else 'creating'} inside NAT rule: {e}")
            return STATUS_NOK
    
    def create_fw_nat_rule(self, in_ifName: InterfaceName, out_ifName: InterfaceName) -> bool:
        '''
        sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
        sudo iptables -A INPUT -i Gig0 -j ACCEPT
        sudo iptables -A FORWARD -i Gig0 -o Gig1 -j ACCEPT
        '''

        # INPUT chain rules
        input_rules = [
             'iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT',
            f'iptables -A INPUT -i {in_ifName} -j ACCEPT'
        ]

        # FORWARD chain rules
        forward_rules = [
            f'iptables -A FORWARD -i {in_ifName} -o {out_ifName} -j ACCEPT'
        ]

        for rule in input_rules + forward_rules:
            
            result = self.run([rule])
            
            if result.exit_code:
                self.log.error(f"Unable to apply fire-wall NAT rule: {result.stderr}")    
                return STATUS_NOK

        return STATUS_OK

    def flush_nat_configuration(self) -> None:
        """
        Flush NAT configurations and reset the NAT pool Data Base.

        This method performs the following actions:
        1. Flush the NAT rules in the nat table.
        2. Flush the NAT rules in the mangle table (if used for NAT).
        3. Delete any user-defined chains in the nat table (optional).
        4. Delete any user-defined chains in the mangle table (optional).
        5. Flush the NAT rules in the nat table for IPv6.
        6. Delete any user-defined chains in the nat table for IPv6 (optional).
        7. Reset NatPool Database.

        Note:
        - This method uses the 'sudo' command to execute iptables and ip6tables commands.
        - Ensure that your NatPoolDB class has a proper method or logic to destroy NatPoolDB.

        Returns:
        None
        """
        # Flush the NAT rules in the nat table
        self.run(['sudo', 'iptables', '-t', 'nat', '-F'], suppress_error=True)

        # Flush the NAT rules in the mangle table (if used for NAT)
        self.run(['sudo', 'iptables', '-t', 'mangle', '-F'], suppress_error=True)

        # Delete any user-defined chains in the nat table (optional)
        self.run(['sudo', 'iptables', '-t', 'nat', '-X'], suppress_error=True)

        # Delete any user-defined chains in the mangle table (optional)
        self.run(['sudo', 'iptables', '-t', 'mangle', '-X'], suppress_error=True)

        # Flush the NAT rules in the nat table for IPv6
        self.run(['sudo', 'ip6tables', '-t', 'nat', '-F'], suppress_error=True)

        # Delete any user-defined chains in the nat table for IPv6 (optional)
        self.run(['sudo', 'ip6tables', '-t', 'nat', '-X'], suppress_error=True)

        NatDB().reset_db()
        
    def getNatIpTable(self) -> str:
        command = "iptables -t nat -L"
        out = self.run(command.split())
        return out.stdout

# FILE: src/routershell/lib/network_manager/network_operations/network_mgr.py
import ipaddress
import json
import logging
import subprocess

from tabulate import tabulate

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import InterfaceName
from routershell.lib.network_manager.common.inet import InetServiceLayer


class InterfaceNotFoundError(Exception):
    """
    Exception raised when a network interface is not found.
    """

    def __init__(self, message="Network interface not found"):
        self.message = message
        super().__init__(self.message)


class NetworkManager(InetServiceLayer):

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().NETWORK_MANAGER)
    
    def net_mgr_interface_exist(self, interface_name) -> bool:
        """
        Check if a network interface with the given name exists on the system.

        This method uses the 'ip link' command to list all network interfaces on
        the system and checks if the specified interface name exists in the output.

        Args:
            interface_name (str): The name of the network interface to check.

        Returns:
            bool: A status indicating whether the interface is valid or not.
            - 'True': If the interface exists.
            - 'False': If the interface does not exist or an error occurred.
        """
        command = ['ip', 'link', 'show', interface_name]

        try:
            # Run the 'ip link' command using self.run()
            result = self.run(command)

            # Check the exit code to determine the status
            if result.exit_code == 0:
                return True
            else:
                return False
        except Exception as e:
            # Handle any errors that occurred during the command execution
            print(f"Error: {e}")
            return 'STATUS_NOK'

    def flush_interface(self, interface_name: InterfaceName) -> bool:
        """
        Flush the configuration of a specific network interface.

        This method uses the 'ip addr flush' command to remove all configurations from the specified network interface.

        Args:
            interface_name (str): The name of the network interface to flush.

        Returns:
            bool: STATUS_OK if the flush process is successful, STATUS_NOK otherwise.
        """
        self.log.debug(f"flush_interface() -> interface_name: {interface_name}")

        if not self.net_mgr_interface_exist(interface_name):
            return STATUS_NOK

        if self.run(['ip', 'addr', 'flush', 'dev', f"{interface_name}"], suppress_error=True):
            self.log.debug(f'Unable to flush interface: {interface_name}')
            return STATUS_NOK

        return STATUS_OK

    def get_vlan_interfaces(self) -> list[str]:
        return []
    
    def get_interfaces(self, args=None):
        """
        Display information about network interfaces.

        This method uses the 'ip' command from the 'iproute2' tool to list and display information
        about network interfaces. It formats the output using the 'tabulate' library.

        Args:
            args (str, optional): Additional arguments (not used). Default is None.

        Returns:
            None
        """
        try:
            # Run the 'ip' command and capture the output
            output = self.run(['ip', 'addr', 'show'])

            # Split the output into interface sections
            interface_sections = output.stdout.strip().split('\n\n')

            # Initialize the data list for tabulation
            data = []

            for section in interface_sections:
                lines = section.strip().split('\n')
                interface_name = lines[0].split(':')[1].strip()

                inet_addresses = []
                inet6_addresses = []
                ether_address = ""
                state = ""

                for line in lines:
                    if 'inet ' in line:
                        inet_parts = line.strip().split()
                        subnet_cidr = str(ipaddress.IPv4Network(f'{inet_parts[1]}/{inet_parts[3]}', strict=False).prefixlen)
                        inet_addresses.append(inet_parts[1] + '/' + subnet_cidr)
                    elif 'inet6 ' in line:
                        inet6_parts = line.strip().split()
                        inet6_addresses.append(inet6_parts[1] + '/' + inet6_parts[3])
                    elif 'link/ether ' in line:
                        ether_parts = line.strip().split()
                        ether_address = ether_parts[1]

                flags = lines[1].strip()
                state = "UP" if "UP" in flags else "DOWN"

                inet_address = '\n'.join(inet_addresses)
                inet6_address = '\n'.join(inet6_addresses)

                data.append([interface_name, inet_address, inet6_address, ether_address, state])

            # Display the interface information as a table
            headers = ['Interface', 'inet', 'inet6', 'ether', 'State']
            print(tabulate(data, headers, tablefmt='simple'))

        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

        return True

    def show_interfaces(self, args=None):
        # Run the 'ip -json addr show' command and capture its output
        result = self.run(['ip', '-json', 'addr', 'show'])

        # Check if the command was successful
        if result.exit_code != 0:
            print("Error executing 'ip -json addr show'.")
            return

        # Parse the JSON output
        json_data = result.stdout

        # Parse the JSON data into a list of network interfaces
        interface_data = json.loads(json_data)

        # Prepare data for tabulation
        table_data = []

        if isinstance(interface_data, list):
            for info in interface_data:
                interface_name = info.get("ifname", "")
                inet = ""
                inet6 = ""
                ether = info.get("address", "")
                flags = info.get("flags", [])
                state = "UP" if 'UP' in flags else "DOWN"

                for addr_info in info.get("addr_info", []):
                    if addr_info["family"] == "inet":
                        inet = f"{addr_info['local']}/{addr_info['prefixlen']}"
                    elif addr_info["family"] == "inet6":
                        if inet6:
                            inet6 += "\n"
                        inet6 += f"{addr_info['local']}/{addr_info['prefixlen']}"

                table_data.append([interface_name, inet, inet6, ether, state])
        else:
            interface_name = interface_data.get("ifname", "")
            inet = ""
            inet6 = ""
            ether = interface_data.get("address", "")
            flags = interface_data.get("flags", [])
            state = "UP" if 'UP' in flags else "DOWN"

            for addr_info in interface_data.get("addr_info", []):
                if addr_info["family"] == "inet":
                    inet = f"{addr_info['local']}/{addr_info['prefixlen']}"
                elif addr_info["family"] == "inet6":
                    if inet6:
                        inet6 += "\n"
                    inet6 += f"{addr_info['local']}/{addr_info['prefixlen']}"

            table_data.append([interface_name, inet, inet6, ether, state])

        # Define headers
        headers = ["Interface", "inet", "inet6", "ether", "State"]

        # Display the table using tabulate
        table = tabulate(table_data, headers, tablefmt="simple")

        print(table)

    def detect_network_hardware(self, args=None):
        """
        Detect and display information about network hardware on the system.

        This function runs the 'lshw -c network' command using sudo to gather information about
        network hardware on the system. It extracts relevant information for each network interface,
        such as logical name, bus info, serial number, capacity, and type (Ethernet or Wireless).
        The gathered information is displayed in a tabular format.

        Note:
            - The function requires administrative privileges to execute the 'lshw' command.
            - The 'lshw' command should be available on the system.

        Returns:
            None
        """
        interface_info = []

        try:
            # Run the 'lshw -c network' command and capture the output
            network_info = self.run(['lshw', '-c', 'network'], text=True)

            # Split the output into sections for each network interface
            sections = network_info.stdout.split('*-network')

            for section in sections[1:]:
                lines = section.strip().split('\n')

                # Initialize a dictionary to store information for this interface
                interface_data = {
                    'Logical Name': "N/A",
                    'Bus Info': "N/A",
                    'Serial': "N/A",
                    'Capacity': "N/A",
                    'Type': 'Unknown'
                }

                # Parse the lines for relevant information
                for line in lines:
                    if "bus info:" in line:
                        interface_data['Bus Info'] = line.split("bus info:")[1].strip()
                    elif "logical name:" in line:
                        interface_data['Logical Name'] = line.split("logical name:")[1].strip()
                    elif "serial:" in line:
                        interface_data['Serial'] = line.split("serial:")[1].strip()
                    elif "configuration:" in line:
                        configuration = line.split("configuration:")[1].strip()
                        if "pci@" in interface_data['Bus Info'] and "wireless" in configuration.lower():
                            interface_data['Type'] = "Wireless"
                    elif "capacity:" in line:
                        interface_data['Capacity'] = line.split("capacity:")[1].strip()

                # Determine the interface type based on bus info
                if "usb@" in interface_data['Bus Info']:
                    interface_data['Type'] = "USB-Ethernet"
                elif "pci@" in interface_data['Bus Info'] and "Wireless" not in interface_data['Type']:
                    interface_data['Type'] = "PCI-Ethernet"

                # Append the interface information to the list
                interface_info.append(interface_data)

        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
    
        # Display the interface information in a tabular format
        headers = ['Logical Name', 'Bus Info', 'Serial', 'Capacity', 'Type']
        table_data = [[
            interface['Logical Name'],
            interface['Bus Info'],
            interface['Serial'],
            interface['Capacity'],
            interface['Type']
        ] for interface in interface_info]

        print(tabulate(table_data, headers, tablefmt='simple'))

# FILE: src/routershell/lib/network_manager/network_operations/vlan.py
import json
import logging

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import BridgeName, InterfaceName, VlanName
from routershell.lib.db.sqlite_db.router_shell_db import Result
from routershell.lib.db.vlan_db import VlanDatabase
from routershell.lib.network_manager.common.phy import State
from routershell.lib.network_manager.common.run_commands import RunCommand
from routershell.lib.network_manager.network_operations.bridge import Bridge


class Vlan(RunCommand):

    VLAN_PREFIX_ID = "Vlan"
    INVALID_VLAN_ID:int = 0
    VLAN_DEFAULT_START:int = 1
    VLAN_MAX_ID:int = 4096
    
    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().VLAN)

    @staticmethod
    def is_vlan_id_range_valid(vlan_id: int) -> bool:
        """
        Check if a given VLAN ID is within the valid range.

        Args:
            vlan_id (int): The VLAN ID to be checked.

        Returns:
            bool: True if the VLAN ID is within the valid range, False otherwise.
        """
        return vlan_id >= Vlan.VLAN_DEFAULT_START and vlan_id <= Vlan.VLAN_MAX_ID

    def add_vlan_id(self, vlan_id: int) -> bool:
        """
        Add a VLAN ID to the database using the VLANDatabase method.

        Args:
            vlan_id (int): The VLAN ID to be added.

        Returns:
            bool: STATUS_OK if the VLAN ID was successfully added, STATUS_NOK otherwise.
        """
        return VlanDatabase().add_vlan_id(vlan_id)

    def does_vlan_id_exist_db(self, vlan_id: int) -> bool:
        """
        Check if a given VLAN ID exists in the database.

        Args:
            vlan_id (int): The VLAN ID to be checked.

        Returns:
            bool: True if the VLAN ID exists in the database, False otherwise.
        """
        return VlanDatabase().vlan_exists(vlan_id)

    def does_vlan_name_exist(vlan_name: VlanName) -> bool:
        """
        Checks if a VLAN with the given name exists.

        Args:
            vlan_name (str): The name of the VLAN to check.

        Returns:
            bool: True if the vlan name exists, False otherwise.
        """
        if VlanDatabase().get_vlan_id_from_vlan_name(vlan_name) == Vlan.INVALID_VLAN_ID:
            return False
        return True

    def update_vlan_name(self, vlan_id: int, vlan_name: VlanName) -> bool:
        """
        Update the name of a VLAN in the database.

        Args:
            vlan_id (int): The unique ID of the VLAN to update.
            vlan_name (str): The new name for the VLAN.

        Note:
        - This method calls the `update_vlan_name` method of `VLANDatabase` to update the VLAN's name in the database.
        """
        self.log.debug(f"update_vlan_name() -> VlanID: {vlan_id} -> VlanName: {vlan_name}")
        
        return VlanDatabase().update_vlan_name_via_vlanID(vlan_id, vlan_name).status

    def update_vlan_description(self, vlan_id: int, vlan_description: str) -> bool:
        """
        Update the description of a VLAN in the database.

        Args:
            vlan_id (int): The unique ID of the VLAN to update.
            vlan_description (str): The new description for the VLAN.

        Note:
        - This method calls the `update_vlan_description_by_vlan_id` method of `VLANDatabase` to update the VLAN's description in the database.
        """
        return VlanDatabase().update_vlan_description(vlan_id, vlan_description)

    def add_vlan_to_interface_os(self, vlan_id: int, interface_name: InterfaceName) -> bool:

        result = self.run(["ip", "-j", "link", "show", "type", "vlan"])
        
        if result.exit_code:
            self.log.error("Failed to fetch existing VLAN interfaces.")
            return STATUS_NOK

        try:
            existing_vlans = json.loads(result.stdout)
            vlan_interface_name = f"{interface_name}.{vlan_id}"
            
            for vlan in existing_vlans:
                if vlan_interface_name in vlan['ifname']:
                    print(f"VLAN interface {vlan_interface_name} already exists.")
                    return STATUS_NOK

        except json.JSONDecodeError:
            self.log.error("Failed to parse JSON output for existing VLAN interfaces.")
            return STATUS_NOK

        result = self.run(["ip", "link", "add", "link", interface_name, "name", vlan_interface_name, "type", "vlan", "id", str(vlan_id)])
        
        if result.exit_code:
            self.log.error(f"Unable to create VLAN: {vlan_id}, error: {result.stderr}")
            return STATUS_NOK
        
        return STATUS_OK

    def add_bridge_by_vlan_id(self, bridge_name: BridgeName, vlan_id: int) -> str:
        """
        Add a bridge to a VLAN.

        Args:
            bridge_name (str): The name of the bridge to be added to the VLAN.
            vlan_id (int): The VLAN ID to which the bridge should be added.

        Returns:
            str: A status code indicating the outcome of the operation.
                - If the bridge does not exist, returns STATUS_NOK.
                - If the interface cannot be added to the VLAN, returns STATUS_NOK.
                - If the operation is successful, returns STATUS_OK.

        """
        if Bridge().does_bridge_exist(bridge_name):
            self.log.debug(f"Bridge does not exist: {bridge_name}")
            return STATUS_NOK
        
        if self.add_interface_by_vlan_id(bridge_name, vlan_id):
            self.log.debug(f"Unable to add bridge: {bridge_name} to VLAN: {vlan_id}")
            return STATUS_NOK
        
        return STATUS_OK

    def add_interface_by_vlan_id(self, interface_name: InterfaceName, vlan_id: int) -> bool:
        """
        Add an interface to a VLAN.

        Args:
            interface_name (str): The name of the network interface.
            vlan_id (int): The VLAN ID to assign to the VLAN.

        Returns:
            bool: A status indicating the result of the operation:
            - 'STATUS_OK' if the interface was successfully added to the VLAN.
            - 'STATUS_NOK' if the operation failed due to invalid parameters or other issues.
        """
        if not Vlan.is_vlan_id_range_valid(vlan_id):
            self.log.debug(f"add_interface_by_vlan_id({interface_name}) Error: Invalid VLAN ID: {vlan_id}")
            return STATUS_NOK

        if not self.does_vlan_id_exist_db(vlan_id):
            self.log.debug(f"add_interface_by_vlan_id({interface_name}) Error: VLAN ID {vlan_id} already exists.")
            return STATUS_NOK
        
        if self.add_interface_to_vlan_os(vlan_id, interface_name):
            self.log.error(f'Unable to add interface {interface_name} to vlan-id: {vlan_id} -> vlan-id: {vlan_id} to OS')
            return STATUS_NOK
        
        if VlanDatabase().add_interface_to_vlan(vlan_id, interface_name):
            self.log.error(f'Unable to add interface {interface_name} to vlan-id: {vlan_id} -> vlan-id: {vlan_id} to DB')
            return STATUS_NOK
        
        return STATUS_OK
    
    def add_interface_to_vlan_os(self, vlan_id: int, interface_name: InterfaceName) -> bool:
        """
        Add an interface to a VLAN on the operating system.

        Args:
            vlan_id (int): The VLAN ID to add the interface to.
            interface_name (str): The name of the interface to be added to the VLAN.

        Returns:
            bool: STATUS_OK if the interface was successfully added to the VLAN, otherwise STATUS_NOK.

        Logs:
            Logs a debug message if the interface could not be added to the VLAN via the OS.
        """
        if not isinstance(vlan_id, int):
            self.log.error(f"Invalid type for vlan_id: {type(vlan_id)}. Expected int.")
            return STATUS_NOK
        
        if not isinstance(interface_name, str):
            self.log.error(f"Invalid type for interface_name: {type(interface_name)}. Expected str.")
            return STATUS_NOK
        
        vlan_name = f'{interface_name}.{vlan_id}'
        
        result = self.run(['ip', 'link', 'add', 'link', interface_name, 'name', vlan_name, 'type', 'vlan', 'id', str(vlan_id)])

        if result.exit_code:
            self.log.error(f"Unable to add VlanID {vlan_id} to interface: {interface_name} via OS, error: {result.stderr}")
            return STATUS_NOK

        result = self.run(['ip', 'link', 'set', 'dev', vlan_name, 'up'])

        if result.exit_code:
            self.log.error(f"Unable to enable Vlan {vlan_name} via OS, error: {result.stderr}")
            return STATUS_NOK

        return STATUS_OK

    def delete_interface_from_vlan(self, interface_name: InterfaceName, vlan_id: int) -> bool:
        return STATUS_OK

    def get_vlan_name_from_vlan_id(self, vlan_id: int) -> str | None:
        """
        Retrieves the VLAN name corresponding to a given VLAN ID.
        
        Args:
            vlan_id (int): The ID of the VLAN.
        
        Returns:
            str | None: The name of the VLAN if found, Vlan.INVALID_VLAN_ID otherwise.
        """
        result: Result = VlanDatabase().get_vlan_name_by_vlan_id(vlan_id)
        
        if result.status:
            self.log.error(f"Unable to retrieve VLAN name from VLAN ID: {vlan_id}")
            return Vlan.INVALID_VLAN_ID
        
        return result.result.get('VlanName')
    
    def get_vlan_id_from_vlan_name(self, vlan_name:VlanName) -> int:
        """
        Retrieves the VLAN ID associated with a given VLAN name.

        Args:
            vlan_name (str): The name of the VLAN.

        Returns:
            int: The VLAN ID if found, otherwise returns Vlan.INVALID_VLAN_ID.
        """     
        return VlanDatabase().get_vlan_id_from_vlan_name(vlan_name)
    
    def set_vlan_state(self, vlan_id: int, state: State) -> bool:
        """
        Sets the state of all interfaces associated with a specific VLAN.
        """
        try:
            # Convert state to lowercase string ('up' or 'down')
            status = state.value.lower()

            # Retrieve the list of all network interfaces in JSON format
            result = self.run(['ip', '-json', 'link', 'show'])

            if result.exit_code != 0:
                self.log.error(f"Failed to retrieve interface information: {result.stderr}")
                return STATUS_NOK

            try:
                interfaces_data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                self.log.error(f"Error decoding JSON output: {str(e)}")
                return STATUS_NOK

            success = STATUS_OK

            # Loop through the interfaces and set the state for the ones matching the VLAN ID
            for interface in interfaces_data:
                if interface.get('ifname', '').endswith(f'.{vlan_id}'):
                    # Set the state (up or down) of the VLAN interface
                    set_result = self.run(['ip', 'link', 'set', 'dev', interface['ifname'], status])
                    if set_result.exit_code != 0:
                        self.log.error(f"Failed to set interface {interface['ifname']} to {status}: {set_result.stderr}")
                        success = STATUS_NOK

            return success

        except Exception as e:
            self.log.error(f"Unexpected error setting VLAN state: {str(e)}")
            return STATUS_NOK

        
            
    
            

# FILE: src/routershell/lib/network_manager/network_operations/wireless_wifi.py
import logging
from enum import Enum

import jc

from routershell.lib.common.constants import HOSTAPD_CONF_FILE, STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import InterfaceName, SsidText, WifiPassphraseText, WifiPolicyName
from routershell.lib.db.wifi_db import WifiDB
from routershell.lib.network_manager.common.run_commands import RunCommand
from routershell.lib.network_manager.network_operations.hostapd_mgr import HostapdIEEE802Config, HostapdManager
from routershell.lib.network_manager.network_operations.network_mgr import NetworkManager


class WPAVersion(Enum):
    """
    Enum representing different versions of WPA (Wi-Fi Protected Access).

    Attributes:
        WPA1 (int): WPA version 1.
        WPA2 (int): WPA version 2.
        WPA3 (int): WPA version 3.
        UNKNOWN (int): An unknown or undefined version of WPA.
    """
    WPA1 = 1
    WPA2 = 2
    WPA3 = 3
    UNKNOWN = -1

    @classmethod
    def display_list(cls, return_values=True):
        """
        Returns a list of known WPA versions.

        Args:
            return_values (bool): If True, returns version values; if False, returns version names.

        Returns:
            list: A list of known WPA versions.
        """
        if return_values:
            return [version.value for version in cls if version != cls.UNKNOWN]
        else:
            return [version.name for version in cls if version != cls.UNKNOWN]
    
class WPAkeyManagement(Enum):
    """
    Enum representing key management algorithms for Wi-Fi networks.

    Attributes:
        WPA_PSK (str): Wi-Fi Protected Access - Pre-Shared Key (WPA-PSK).
        WPA_EAP (str): Wi-Fi Protected Access - Extensible Authentication Protocol (WPA-EAP).
        WPA_EAP_SHA256 (str): WPA-EAP using SHA256-based encryption.
        WPA_EAP_TLS (str): WPA-EAP using Transport Layer Security (TLS).
    """
    WPA_PSK = 'WPA-PSK'
    WPA_EAP = 'WPA-EAP'
    WPA_EAP_SHA256 = 'WPA-EAP-SHA256'
    WPA_EAP_TLS = 'WPA-EAP-TLS'
    
    @classmethod
    def display_list(cls):
        """
        Returns a list of available key management algorithms.
        """
        return [algorithm.value for algorithm in cls]

class KeyManagementRule:
    '''
    Rules defined in hostapd.config as of 231105

    This section defines a set of accepted key management algorithms for wireless networks.
    The key management algorithms determine how encryption keys are negotiated and managed
    for securing Wi-Fi communication. The entries are separated by spaces.

    - WPA-PSK: WPA-Personal / WPA2-Personal
    - WPA-PSK-SHA256: WPA2-Personal using SHA256 for stronger security
    - WPA-EAP: WPA-Enterprise / WPA2-Enterprise
    - WPA-EAP-SHA256: WPA2-Enterprise using SHA256 for stronger security
    - SAE: Simultaneous Authentication of Equals (WPA3-Personal)
    - WPA-EAP-SUITE-B-192: WPA3-Enterprise with 192-bit security (CNSA suite)
    - FT-PSK: Fast Transition with passphrase/PSK
    - FT-EAP: Fast Transition with EAP
    - FT-EAP-SHA384: Fast Transition with EAP using SHA384 for stronger security
    - FT-SAE: Fast Transition with SAE
    - FILS-SHA256: Fast Initial Link Setup with SHA256
    - FILS-SHA384: Fast Initial Link Setup with SHA384
    - FT-FILS-SHA256: Fast Transition and Fast Initial Link Setup with SHA256
    - FT-FILS-SHA384: Fast Transition and Fast Initial Link Setup with SHA384
    - OWE: Opportunistic Wireless Encryption (a.k.a. Enhanced Open)
    - DPP: Device Provisioning Protocol
    - OSEN: Hotspot 2.0 online signup with encryption

    These rules define the key management algorithms that can be used to secure Wi-Fi networks.
    Please configure your network's key management algorithms based on your security requirements.

    (dot11RSNAConfigAuthenticationSuitesTable)
    '''

    def __init__(self):
        self.allowed_combinations = {
            ('WPA_PSK', 'WPA_EAP'): lambda wpa_key_mgmt: 'WPA-Personal' in wpa_key_mgmt and 'WPA-Enterprise' in wpa_key_mgmt,
            ('WPA_PSK', 'WPA_EAP_SHA256'): lambda wpa_key_mgmt: 'WPA-Personal' in wpa_key_mgmt and 'WPA-Enterprise-SHA256' in wpa_key_mgmt,
            ('WPA_EAP', 'WPA_EAP_SHA256'): lambda wpa_key_mgmt: 'WPA-Enterprise' in wpa_key_mgmt and 'WPA-Enterprise-SHA256' in wpa_key_mgmt,
        }

    def validate_key_management(self, wpa_key_mgmt):
        provided_algorithms = set(wpa_key_mgmt.split())

        for allowed_combination, validation_rule in self.allowed_combinations.items():
            if all(mode in provided_algorithms for mode in allowed_combination) and not validation_rule(wpa_key_mgmt):
                return False

        return True
    
class Pairwise(Enum):
    """
    Enum representing pairwise cipher suites for Wi-Fi security.

    Attributes:
        CCMP (str): Cipher-based encryption for enhanced security (e.g., WPA2).
        TKIP (str): Temporal Key Integrity Protocol, an older encryption method (e.g., WPA).
    """
    CCMP = 'CCMP'
    TKIP = 'TKIP'
    
    @classmethod
    def display_list(cls):
        """
        Returns a list of available pairwise cipher suites for Wi-Fi security.
        """
        return [cipher_suite.value for cipher_suite in cls]
    
class HardwareMode(Enum):
    """
    Enum representing hardware modes for Wi-Fi devices.

    Attributes:
        A (str): Wi-Fi mode 'a' (5 GHz band).
        B (str): Wi-Fi mode 'b' (2.4 GHz band).
        G (str): Wi-Fi mode 'g' (2.4 GHz band).
        AD (str): Wi-Fi mode 'ad' (60 GHz band).
        AX (str): Wi-Fi mode 'ax' (6 GHz band and beyond).
        ANY (str): Represents any hardware mode.
    """
    A = 'a'
    B = 'b'
    G = 'g'
    AD = 'ad'
    AX = 'ax'
    ANY = 'any'
    
    @classmethod
    def display_list(cls):
        """
        Returns a list of available hardware modes for Wi-Fi devices (values only).
        """
        return [mode.value for mode in cls]

class AuthAlgorithms(Enum):
    """
    Enum representing authentication algorithms for Wi-Fi networks.

    Attributes:
        OSA (str): Open System Authentication (OSA).
        SKA (str): Shared Key Authentication (SKA).
    """
    OSA = 'OSA'
    SKA = 'SKA'

    @classmethod
    def display_list(cls):
        """
        Returns a list of available authentication algorithms.
        """
        return [algorithm.value for algorithm in cls]

class WifiChannel(Enum):
    """
    Enum representing Wi-Fi channels.

    Attributes:
        CHANNEL_1 (int): Wi-Fi channel 1.
        CHANNEL_2 (int): Wi-Fi channel 2.
        CHANNEL_3 (int): Wi-Fi channel 3.
        CHANNEL_4 (int): Wi-Fi channel 4.
        CHANNEL_5 (int): Wi-Fi channel 5.
        CHANNEL_6 (int): Wi-Fi channel 6.
        CHANNEL_7 (int): Wi-Fi channel 7.
        CHANNEL_8 (int): Wi-Fi channel 8.
        CHANNEL_9 (int): Wi-Fi channel 9.
        CHANNEL_10 (int): Wi-Fi channel 10.
        CHANNEL_11 (int): Wi-Fi channel 11.
        CHANNEL_12 (int): Wi-Fi channel 12.
        CHANNEL_13 (int): Wi-Fi channel 13.
        CHANNEL_14 (int): Wi-Fi channel 14.
    """
    CHANNEL_1 = 1
    CHANNEL_2 = 2
    CHANNEL_3 = 3
    CHANNEL_4 = 4
    CHANNEL_5 = 5
    CHANNEL_6 = 6
    CHANNEL_7 = 7
    CHANNEL_8 = 8
    CHANNEL_9 = 9
    CHANNEL_10 = 10
    CHANNEL_11 = 11
    CHANNEL_12 = 12
    CHANNEL_13 = 13
    CHANNEL_14 = 14

    @classmethod
    def display_list(cls):
        """
        Returns a list of available Wi-Fi channels.
        """
        return [channel.value for channel in cls]

class WifiPolicy:
    """
    Represents a Wi-Fi policy for network management.

    This class allows you to define and manage Wi-Fi policies based on specific criteria.

    Args:
        wifi_policy_name (str): The name of the Wi-Fi policy.
        negate (bool): If True, the policy will be negated.

    Attributes:
        wifi_policy_name (str): The name of the Wi-Fi policy.
        negate (bool): Indicates whether the policy is negated.
        wifi_policy_status (bool): The status of the Wi-Fi policy (STATUS_OK or STATUS_NOK).

    """

    def __init__(self, wifi_policy_name: WifiPolicyName, negate=False):
        """
        Initializes a new Wi-Fi policy with the given parameters.

        Args:
            wifi_policy_name (str): The name of the Wi-Fi policy.
            negate (bool, optional): If True, the policy will be negated (default is False).

        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().WIFI_POLICY)
        self.log.debug(f"WifiPolicy() -> Wifi-Policy: {wifi_policy_name} -> Negate: {negate}")
        
        self.wifi_db = WifiDB()

        if not self.wifi_db.wifi_policy_exist(wifi_policy_name):
            self.log.debug(f"Wifi-Policy: {wifi_policy_name} does not exist.")
            if self.wifi_db.add_wifi_policy(wifi_policy_name):
                self.log.debug(f"Error Adding wifi-policy: {wifi_policy_name} to DB")
                self._set_status(STATUS_NOK)
            else:
                
                self._set_status(STATUS_OK)

        self.wifi_policy_name = wifi_policy_name
        self.negate = negate

    def add_security_access_group(self, ssid: SsidText, pass_phrase: WifiPassphraseText, mode: WPAVersion=WPAVersion.WPA2) -> bool:
        """
        Add a security access group with the specified SSID, passphrase, and security mode.

        Args:
        ssid (str): The SSID (Service Set Identifier) for the security access group.
        pass_phrase (str): The security passphrase or key for the security access group.
        mode (WPAVersion): The security mode for the security access group (e.g., WPA, WPA2, WPA3).

        Returns:
        bool: STATUS_OK if the security access group is added successfully, STATUS_NOK if the addition fails.

        Note:
        - This method adds a security access group with the provided SSID, passphrase, and security mode to the database.
        - It returns STATUS_OK if the addition is successful, and STATUS_NOK if there is an error or the addition fails.

        """
        return self.wifi_db.add_wifi_security_access_group(self.wifi_policy_name, ssid, pass_phrase, mode.value)

    def add_security_access_group_default(self, wifi_policy_name: WifiPolicyName) -> bool:
        """
        Add a default security access group to the specified wireless Wi-Fi policy.

        Args:
            wifi_policy_name (str): The name of the wireless Wi-Fi policy to add the default security access group to.

        Returns:
            bool: True if the default security access group is added successfully, False otherwise.

        Note:
        - This method adds a default security access group to the specified wireless Wi-Fi policy.
        - The default security access group typically includes pre-defined settings for SSID, WPA passphrase, and security mode.
        - Returns True if the default security access group is added successfully, and False otherwise.
        """
        return self.wifi_db.add_wifi_security_access_group_default(wifi_policy_name)

    def add_key_management(self, key_managment:WPAkeyManagement) -> bool:
        return STATUS_OK
    
    def add_hardware_mode(self, hardware_mode:HardwareMode) -> bool:
        """
        Add a hardware mode to a wireless Wi-Fi policy.

        Args:
            hardware_mode (HardwareMode): The hardware mode to add to the policy.

        Returns:
            bool: STATUS_OK if the hardware mode was successfully added, STATUS_NOK if it fails.

        Note:
        - This method associates a hardware mode with the specified wireless Wi-Fi policy.
        - It returns STATUS_OK if the association is successful, and STATUS_NOK if it fails.
        """
        return self.wifi_db.add_wifi_hardware_mode(self.wifi_policy_name, hardware_mode.value)
    
    def add_channel(self, wifi_channel: WifiChannel=WifiChannel.CHANNEL_6) -> bool:
        """
        Add a Wi-Fi channel to a wireless Wi-Fi policy.

        Args:
        - wifi_channel (WifiChannel): The Wi-Fi channel to add. Default is CHANNEL_6.

        Returns:
        bool: True if the addition is successful, False if it fails.

        Note:
        - This method associates a Wi-Fi channel with the specified wireless Wi-Fi policy.
        """        
        return self.wifi_db.add_wifi_channel(self.wifi_policy_name, str(wifi_channel.value))

    def del_ssid(self, ssid: SsidText) -> bool:
        """
        Delete a Wi-Fi security access group with the specified SSID from the associated wireless Wi-Fi policy.

        Args:
            ssid (str): The SSID (Service Set Identifier) of the Wi-Fi security access group to delete.

        Returns:
            bool: STATUS_OK if the Wi-Fi security access group is deleted successfully, STATUS_NOK otherwise.

        Note:
        - This method deletes a Wi-Fi security access group with the specified SSID from the associated wireless Wi-Fi policy.
        - Returns True if the deletion is successful, and False otherwise.
        """
        return self.wifi_db.del_wifi_security_access_group(self.wifi_policy_name, ssid)

    def security_access_group_entry_exist(self, wifi_policy_name: WifiPolicyName) -> bool:
        # Get the security policies associated with the Wi-Fi policy
        security_policies = self.wifi_db.get_wifi_security_policy(wifi_policy_name)

        # Check if there are any security policies
        if len(security_policies) > 0:
            self.log.debug(f"Security access group entry exists for Wi-Fi policy '{wifi_policy_name}'.")
            return True
        else:
            self.log.debug(f"No security access group entry found for Wi-Fi policy '{wifi_policy_name}'.")
            return False

    def get_ssid_list(self, wifi_policy_name: WifiPolicyName) -> list:  
        self.wifi_db.get_wifi_security_policy(wifi_policy_name)
             
    def status(self) -> bool:
        """
        Get the status of the Wi-Fi policy.

        Returns:
            bool: The status of the Wi-Fi policy (STATUS_OK or STATUS_NOK).

        """
        return self.wifi_policy_status

    def _set_status(self, status: bool) -> bool:
        """
        Set the status of the Wi-Fi policy.

        Args:
            status (bool): The status to set (STATUS_OK or STATUS_NOK).

        Returns:
            bool: STATUS_OK if the status is successfully set.

        """
        self.wifi_policy_status = status
        return STATUS_OK

class WifiInterface:
    '''
    Interface level wifi settings
    '''
    
    def __init__(self, wifi_interface_name: InterfaceName):
        """
        Initialize a WifiInterface instance.

        Parameters:
            interface_name (str): The name of the wireless interface.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().WIFI_INTERFACE)
        self.log.debug(f"WifiInterface() -> interface: {wifi_interface_name}")
        
        self.wifi_interface_name = wifi_interface_name
        self.cmd = RunCommand()
        self.wifi_db = WifiDB()
        
        self.is_wifi_interface = self._is_interface_wifi()

    def _is_interface_wifi(self) -> bool:
        """
        Check if the current wireless interface is associated with Wi-Fi.

        Returns:
            bool: True if the current interface is associated with Wi-Fi, False otherwise.
        """
        cmd = ['iw', 'dev', self.wifi_interface_name , 'info']
        
        result = self.cmd.run(cmd)
        
        if result.exit_code:
            self.log.error("Unable to get wireless interface list")
            return False

        output_lines = result.stdout.strip().split('\n')
        interface_names = [line.split()[1] for line in output_lines if line.startswith('Interface')]

        if not interface_names:
            self.log.error("No wireless interfaces found")
            return False

        if self.wifi_interface_name not in interface_names:
            return False

        return True

    def is_interface_wifi(self) -> bool:
        """
        Check if the current interface is associated with Wi-Fi.

        Returns:
            bool: True if the interface is associated with Wi-Fi, False otherwise.
        """
        return self.is_wifi_interface
    
    def scan(self):
        """
        Perform a Wi-Fi scan on the specified interface and return the parsed scan results.

        Returns:
            list[dict[str, str | int | float]]: Parsed Wi-Fi scan results as a list
            of dictionaries, where each dictionary represents information about a Wi-Fi network.
        """
        result = self.cmd.run(['iw', 'dev', self.wifi_interface_name, 'scan'])

        if result.exit_code:
            self.log.error(f"Unable to obtain scan from wifi-interface: {self.wifi_interface_name}")
            return []

        try:
            parsed_data = jc.parse('iw_scan', result.stdout)
            return parsed_data
        
        except Exception as e:
            self.log.error(f"Error parsing scan results: {e}")
            return []

    def update_policy_to_wifi_interface(self, wifi_policy_name: WifiPolicyName) -> bool:
        """
        Update the Wi-Fi policy for the wireless interface.

        Parameters:
            wifi_policy_name (str): The name of the Wi-Fi policy.

        Returns:
            bool: STATUS_OK if the update is successful, STATUS_NOK otherwise.
        """
        if not self.is_interface_wifi():
            self.log.error(f"Unable to apply wifi-policy: {wifi_policy_name} , due to interface: {self.wifi_interface_name} is not wifi")
            return STATUS_NOK
        
        if not self.wifi_db.wifi_policy_exist(wifi_policy_name):
            self.log.error(f"Unable to apply wifi-policy: {wifi_policy_name} , interface: {self.wifi_interface_name} does not exists")
            return STATUS_NOK
        
        return self.wifi_db.add_wifi_policy_to_wifi_interface(wifi_policy_name, self.wifi_interface_name)
    
    def set_hardware_mode(self, wifi_interface_name:InterfaceName, hw_mode: HardwareMode) -> bool:
        """
        Set the hardware mode for the wireless interface.

        Parameters:
            hw_mode (HardwareMode): The hardware mode to set.

        Returns:
            bool: STATUS_OK if the set operation is successful, STATUS_NOK otherwise.
        """

        if not self.is_interface_wifi():
            self.log.error(f"Unable to apply hardware-mode: {hw_mode.value} , due to interface: {self.wifi_interface_name} is not wifi")
            return STATUS_NOK
        
        return STATUS_OK
    
    def set_channel(self, wifi_interface_name:InterfaceName, channel: WifiChannel) -> bool:
        """
        Set the Wi-Fi channel for the wireless interface.

        Parameters:
            channel (WifiChannel): The Wi-Fi channel to set.

        Returns:
            bool: STATUS_OK if the set operation is successful, STATUS_NOK otherwise.
        """
        if not self.is_interface_wifi():
            self.log.error(f"Unable to apply channel: {channel.value} , due to interface: {self.wifi_interface_name} is not wifi")
            return STATUS_NOK   
        
        return STATUS_OK

class Wifi(NetworkManager):
    """Command set for managing wireless networks using the 'iw' command."""

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().WIFI)

    def wifi_policy_name_exist(self, wifi_policy_name:WifiPolicyName) -> bool:
        return True 

    def wifi_interface_exist(self, wifi_interface_name: InterfaceName) -> bool:
        """
        Check if a Wi-Fi interface exists.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface to check.

        Returns:
            bool: True if the Wi-Fi interface exists, False otherwise.
        """
        output = self.run(['iw', 'dev', wifi_interface_name , 'info'])
        
        if output.exit_code:
            self.log.debug(f"Unable to obtain wifi-interface: {wifi_interface_name} status")
            return False
        return True
            
    def set_ssid(self, wifi_interface_name: InterfaceName, ssid: SsidText) -> bool:
        """
        Set the SSID (Service Set Identifier) for a Wi-Fi interface.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface.
            ssid (str): The SSID to set.

        Returns:
            bool: STATUS_OK if the SSID was successfully set, STATUS_NOK otherwise.
        """
        output = self.run(['iw', 'dev', wifi_interface_name, 'set', 'ssid', ssid])
        
        if output.exit_code:
            self.log.error(f"Failed to set SSID for {wifi_interface_name}")
            return STATUS_NOK
        
        return STATUS_OK

    def set_wpa_passphrase(self, wifi_interface_name: InterfaceName, pass_phrase: WifiPassphraseText) -> bool:
        """
        Set the WPA passphrase for a Wi-Fi interface using the iw command.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface.
            pass_phrase (str): The WPA passphrase to set.

        Returns:
            bool: STATUS_OK if the WPA passphrase was successfully set, STATUS_NOK otherwise.
        """
        cmd = ['iw', 'dev', wifi_interface_name, 'set', 'wpa_passphrase', pass_phrase]
        output = self.run(cmd)

        if output.exit_code:
            self.log.error(f"Failed to set WPA passphrase for {wifi_interface_name}")
            return STATUS_NOK

        return STATUS_OK
    
    def set_wpa_key_mgmt(self, wifi_interface_name: InterfaceName, wpa_key_mgmt: WPAkeyManagement) -> bool:
        """
        Set the WPA key management method for a Wi-Fi interface using the iw command.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface.
            wpa_key_mgmt (WPAkeyManagement): The key management method to set.

        Returns:
            bool: STATUS_OK if the key management method was successfully set, STATUS_NOK otherwise.
        """
        cmd = ['iw', 'dev', wifi_interface_name, 'set', 'key_mgmt', wpa_key_mgmt.value]
        output = self.run(cmd)

        if output.exit_code:
            self.log.error(f"Failed to set key management method for {wifi_interface_name}")
            return STATUS_NOK

        return STATUS_OK

    def set_wpa_pairwise(self, wifi_interface_name: InterfaceName, wpa_pairwise: Pairwise) -> bool:
        """
        Set the WPA pairwise cipher for a Wi-Fi interface using the iw command.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface.
            wpa_pairwise (str): The WPA pairwise cipher to set (CCMP, TKIP, etc.).

        Returns:
            bool: STATUS_OK if the WPA pairwise cipher was successfully set, STATUS_NOK otherwise.
        """
        cmd = ['iw', 'dev', wifi_interface_name, 'set', 'wpa_pairwise', wpa_pairwise.value]
        output = self.run(cmd)

        if output.exit_code:
            self.log.error(f"Failed to set WPA pairwise cipher for {wifi_interface_name}")
            return STATUS_NOK

        return STATUS_OK

    def set_rsn_pairwise(self, wifi_interface_name: InterfaceName, rsn_pairwise: Pairwise) -> bool:
        """
        Set the RSN pairwise cipher for a Wi-Fi interface using the iw command.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface.
            rsn_pairwise (str): The RSN pairwise cipher to set (CCMP, TKIP, etc.).

        Returns:
            bool: STATUS_OK if the RSN pairwise cipher was successfully set, STATUS_NOK otherwise.
        """
        cmd = ['iw', 'dev', wifi_interface_name, 'set', 'rsn_pairwise', rsn_pairwise.value]
        output = self.run(cmd)

        if output.exit_code:
            self.log.error(f"Failed to set RSN pairwise cipher for {wifi_interface_name}")
            return STATUS_NOK

        return STATUS_OK
    
    def set_wifi_mode(self, wifi_interface_name: InterfaceName, mode: HardwareMode) -> bool:
        """
        Set the Wi-Fi mode for a Wi-Fi interface using the iw command.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface.
            mode (str): The Wi-Fi mode to set (a, b, g, ad, ax, any).

        Returns:
            bool: STATUS_OK if the Wi-Fi mode was successfully set, STATUS_NOK otherwise.
        """
        cmd = ['iw', 'dev', wifi_interface_name, 'set', 'mode', mode.value]
        output = self.run(cmd)

        if output.exit_code:
            self.log.error(f"Failed to set Wi-Fi mode for {wifi_interface_name}")
            return STATUS_NOK

        return STATUS_OK

    def set_wifi_channel(self, wifi_interface_name: InterfaceName, channel: int) -> bool:
        """
        Set the Wi-Fi channel for a Wi-Fi interface using the iw command.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface.
            channel (int): The Wi-Fi channel to set (1, 2, 3, 4, 5, 6, 8, 7, 8, 9, 10, 11).

        Returns:
            bool: STATUS_OK if the Wi-Fi channel was successfully set, STATUS_NOK otherwise.
        """
        if channel < 1 or channel > 11:
            self.log.error("Invalid Wi-Fi channel. The channel must be in the range 1 to 11.")
            return STATUS_NOK

        cmd = ['iw', 'dev', wifi_interface_name, 'set', 'channel', str(channel)]
        output = self.run(cmd)

        if output.exit_code:
            self.log.error(f"Failed to set Wi-Fi channel for {wifi_interface_name}")
            return STATUS_NOK

        return STATUS_OK

    def set_auth_algs(self, wifi_interface_name: InterfaceName, auth_alg: AuthAlgorithms) -> bool:
        """
        Set the authentication algorithms for a Wi-Fi interface using the iw command.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface.
            auth_alg (AuthAlgorithms): The authentication algorithm to set (AuthAlgorithms.OSA or AuthAlgorithms.SKA).

        Returns:
            bool: STATUS_OK if the authentication algorithm was successfully set, STATUS_NOK otherwise.
        """
        cmd = ['iw', 'dev', wifi_interface_name, 'set', 'auth-algs', auth_alg.value]
        output = self.run(cmd)

        if output.exit_code:
            self.log.error(f"Failed to set authentication algorithm for {wifi_interface_name}")
            return STATUS_NOK

        return STATUS_OK

    def set_ieee80211(self, ieee802_support:HostapdIEEE802Config, negate=False) -> bool:
        return STATUS_OK

class WifiAccessPoint(HostapdManager):
    def __init__(self, interface_name: InterfaceName, wifi_policy_name: WifiPolicyName):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().WIFI_ACCESS_POINT)
        
        self.interface_name = interface_name
        self.wifi_policy_name = wifi_policy_name

        self.hostapd_file_name = f'{interface_name}_{wifi_policy_name}_{HOSTAPD_CONF_FILE}'
        
        HostapdManager().__init__(self.hostapd_file_name)
        


    
        
        

# FILE: src/routershell/lib/network_manager/network_operations/wireless_wifi_iw.py
import logging
from enum import Enum

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import InterfaceName, SsidText, WifiPassphraseText, WifiPolicyName
from routershell.lib.network_manager.network_operations.hostapd_mgr import HostapdIEEE802Config
from routershell.lib.network_manager.network_operations.network_mgr import NetworkManager


class WPAVersion(Enum):
    WPA1 = 1
    WPA2 = 2
    WPA3 = 3
    UNKNOWN = -1
    
class WPAkeyManagement(Enum):
    WPA_PSK = 'WPA-PSK'
    WPA_EPA = 'WPA-EPA'
    WPA_EPA_SHA265 = 'WPA-EPA-SHA265'
    WPA_EPA_TLA = 'WPA-EPA-TLS'   
    
class Pairwise(Enum):
    CCMP = 'CCMP'
    TKIP = 'TKIP'

class HardwareMode(Enum):
    A = 'a'
    B = 'b'
    G = 'g'
    AD = 'ad'
    AX = 'ax'
    ANY = 'any'

class AuthAlgorithms(Enum):
    OSA = 'OSA'
    SKA = 'SKA'

class WifiPolicy:
    """
    Represents a Wi-Fi policy for network management.

    This class allows you to define and manage Wi-Fi policies based on specific criteria.

    Args:
        wifi_policy_name (str): The name of the Wi-Fi policy.
        negate (bool): If True, the policy will be negated.

    Attributes:
        wifi_policy_name (str): The name of the Wi-Fi policy.
        negate (bool): Indicates whether the policy is negated.
        wifi_policy_status (bool): The status of the Wi-Fi policy (STATUS_OK or STATUS_NOK).

    """

    def __init__(self, wifi_policy_name: WifiPolicyName, negate=False):
        """
        Initializes a new Wi-Fi policy with the given parameters.

        Args:
            wifi_policy_name (str): The name of the Wi-Fi policy.
            negate (bool, optional): If True, the policy will be negated (default is False).

        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().WIRELESS_WIFI_POLICY)
        self.log.debug(f"WifiPolicy() -> Wifi-Policy: {wifi_policy_name} -> Negate: {negate}")

        self.wifi = Wifi()

        if not self.wifi.wifi_policy_name_exist(wifi_policy_name):
            self.log.debug(f"Wifi-Policy: {wifi_policy_name} does not exist.")
            self.wifi_policy_status = STATUS_NOK
            return

        self.wifi_policy_name = wifi_policy_name
        self.negate = negate
        self.wifi_policy_status = STATUS_OK

    def status(self) -> bool:
        """
        Get the status of the Wi-Fi policy.

        Returns:
            bool: The status of the Wi-Fi policy (STATUS_OK or STATUS_NOK).

        """
        return self.wifi_policy_status

    def _set_status(self, status: bool) -> bool:
        """
        Set the status of the Wi-Fi policy.

        Args:
            status (bool): The status to set (STATUS_OK or STATUS_NOK).

        Returns:
            bool: STATUS_OK if the status is successfully set.

        """
        self.wifi_policy_status = status
        return STATUS_OK

           
class Wifi(NetworkManager):
    """Command set for managing wireless networks using the 'iw' command."""

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().WIFI)

    def wifi_policy_name_exist(self, wifi_policy_name:WifiPolicyName) -> bool:
        return True 

    def wifi_interface_exist(self, wifi_interface_name: InterfaceName) -> bool:
        """
        Check if a Wi-Fi interface exists.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface to check.

        Returns:
            bool: True if the Wi-Fi interface exists, False otherwise.
        """
        output = self.run(['iw', 'dev', wifi_interface_name , 'info'])
        
        if output.exit_code:
            self.log.debug(f"Unable to obtain wifi-interface: {wifi_interface_name} status")
            return False
        return True
            
    def set_ssid(self, wifi_interface_name: InterfaceName, ssid: SsidText) -> bool:
        """
        Set the SSID (Service Set Identifier) for a Wi-Fi interface.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface.
            ssid (str): The SSID to set.

        Returns:
            bool: STATUS_OK if the SSID was successfully set, STATUS_NOK otherwise.
        """
        output = self.run(['iw', 'dev', wifi_interface_name, 'set', 'ssid', ssid])
        
        if output.exit_code:
            self.log.error(f"Failed to set SSID for {wifi_interface_name}")
            return STATUS_NOK
        
        return STATUS_OK

    def set_wpa_passphrase(self, wifi_interface_name: InterfaceName, pass_phrase: WifiPassphraseText) -> bool:
        """
        Set the WPA passphrase for a Wi-Fi interface using the iw command.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface.
            pass_phrase (str): The WPA passphrase to set.

        Returns:
            bool: STATUS_OK if the WPA passphrase was successfully set, STATUS_NOK otherwise.
        """
        cmd = ['iw', 'dev', wifi_interface_name, 'set', 'wpa_passphrase', pass_phrase]
        output = self.run(cmd)

        if output.exit_code:
            self.log.error(f"Failed to set WPA passphrase for {wifi_interface_name}")
            return STATUS_NOK

        return STATUS_OK
    
    def set_wpa_key_mgmt(self, wifi_interface_name: InterfaceName, wpa_key_mgmt: WPAkeyManagement) -> bool:
        """
        Set the WPA key management method for a Wi-Fi interface using the iw command.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface.
            wpa_key_mgmt (WPAkeyManagement): The key management method to set.

        Returns:
            bool: STATUS_OK if the key management method was successfully set, STATUS_NOK otherwise.
        """
        cmd = ['iw', 'dev', wifi_interface_name, 'set', 'key_mgmt', wpa_key_mgmt.value]
        output = self.run(cmd)

        if output.exit_code:
            self.log.error(f"Failed to set key management method for {wifi_interface_name}")
            return STATUS_NOK

        return STATUS_OK

    def set_wpa_pairwise(self, wifi_interface_name: InterfaceName, wpa_pairwise: Pairwise) -> bool:
        """
        Set the WPA pairwise cipher for a Wi-Fi interface using the iw command.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface.
            wpa_pairwise (str): The WPA pairwise cipher to set (CCMP, TKIP, etc.).

        Returns:
            bool: STATUS_OK if the WPA pairwise cipher was successfully set, STATUS_NOK otherwise.
        """
        cmd = ['iw', 'dev', wifi_interface_name, 'set', 'wpa_pairwise', wpa_pairwise.value]
        output = self.run(cmd)

        if output.exit_code:
            self.log.error(f"Failed to set WPA pairwise cipher for {wifi_interface_name}")
            return STATUS_NOK

        return STATUS_OK

    def set_rsn_pairwise(self, wifi_interface_name: InterfaceName, rsn_pairwise: Pairwise) -> bool:
        """
        Set the RSN pairwise cipher for a Wi-Fi interface using the iw command.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface.
            rsn_pairwise (str): The RSN pairwise cipher to set (CCMP, TKIP, etc.).

        Returns:
            bool: STATUS_OK if the RSN pairwise cipher was successfully set, STATUS_NOK otherwise.
        """
        cmd = ['iw', 'dev', wifi_interface_name, 'set', 'rsn_pairwise', rsn_pairwise.value]
        output = self.run(cmd)

        if output.exit_code:
            self.log.error(f"Failed to set RSN pairwise cipher for {wifi_interface_name}")
            return STATUS_NOK

        return STATUS_OK
    
    def set_wifi_mode(self, wifi_interface_name: InterfaceName, mode: HardwareMode) -> bool:
        """
        Set the Wi-Fi mode for a Wi-Fi interface using the iw command.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface.
            mode (str): The Wi-Fi mode to set (a, b, g, ad, ax, any).

        Returns:
            bool: STATUS_OK if the Wi-Fi mode was successfully set, STATUS_NOK otherwise.
        """
        cmd = ['iw', 'dev', wifi_interface_name, 'set', 'mode', mode.value]
        output = self.run(cmd)

        if output.exit_code:
            self.log.error(f"Failed to set Wi-Fi mode for {wifi_interface_name}")
            return STATUS_NOK

        return STATUS_OK

    def set_wifi_channel(self, wifi_interface_name: InterfaceName, channel: int) -> bool:
        """
        Set the Wi-Fi channel for a Wi-Fi interface using the iw command.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface.
            channel (int): The Wi-Fi channel to set (1, 2, 3, 4, 5, 6, 8, 7, 8, 9, 10, 11).

        Returns:
            bool: STATUS_OK if the Wi-Fi channel was successfully set, STATUS_NOK otherwise.
        """
        if channel < 1 or channel > 11:
            self.log.error("Invalid Wi-Fi channel. The channel must be in the range 1 to 11.")
            return STATUS_NOK

        cmd = ['iw', 'dev', wifi_interface_name, 'set', 'channel', str(channel)]
        output = self.run(cmd)

        if output.exit_code:
            self.log.error(f"Failed to set Wi-Fi channel for {wifi_interface_name}")
            return STATUS_NOK

        return STATUS_OK

    def set_auth_algs(self, wifi_interface_name: InterfaceName, auth_alg: AuthAlgorithms) -> bool:
        """
        Set the authentication algorithms for a Wi-Fi interface using the iw command.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface.
            auth_alg (AuthAlgorithms): The authentication algorithm to set (AuthAlgorithms.OSA or AuthAlgorithms.SKA).

        Returns:
            bool: STATUS_OK if the authentication algorithm was successfully set, STATUS_NOK otherwise.
        """
        cmd = ['iw', 'dev', wifi_interface_name, 'set', 'auth-algs', auth_alg.value]
        output = self.run(cmd)

        if output.exit_code:
            self.log.error(f"Failed to set authentication algorithm for {wifi_interface_name}")
            return STATUS_NOK

        return STATUS_OK

    def set_ieee80211(self, ieee802_support:HostapdIEEE802Config, negate=False) -> bool:
        return STATUS_OK

# FILE: src/routershell/lib/network_services/dhcp/dnsmasq/dnsmasq.py
import logging
import os
from enum import Enum, auto

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.string_formats import StringFormats
from routershell.lib.common.types import DhcpPoolName, InetCidrText
from routershell.lib.db.dhcp_server_db import DHCPServerDatabase
from routershell.lib.network_manager.network_operations.network_mgr import NetworkManager
from routershell.lib.network_services.dhcp.common.dhcp_common import DHCPOptionLookup, DHCPVersion
from routershell.lib.network_services.dhcp.dnsmasq.dnsmasq_config_gen import DHCPv6Modes, DNSMasqConfigurator
from routershell.lib.system.system_service_control.system_service_control import (
    SysServCntrlAction,
    SystemServiceControl,
)


class DNSMasqExitCode(Enum):
    """
    Enum class representing DNSMasq exit codes.

    EXIT CODES:
    0 - Dnsmasq successfully forked into the background, or terminated normally if back-ground is not enabled.
    1 - A problem with configuration was detected.
    2 - A problem with network access occurred (address in use, attempt to use privileged ports without permission).
    3 - A problem occurred with a filesystem operation (missing file/directory, permissions).
    4 - Memory allocation failure.
    5 - Other miscellaneous problem.
    11 or greater - a non-zero return code was received from the lease-script process "init" call or a --conf-script file.
                    The exit code from dnsmasq is the script's exit code with 10 added.
    """

    SUCCESS = 0
    CONFIG_PROBLEM = 1
    NETWORK_ACCESS_PROBLEM = 2
    FILESYSTEM_OPERATION_PROBLEM = 3
    MEMORY_ALLOCATION_FAILURE = 4
    MISC_PROBLEM = 5

    @classmethod
    def from_script_exit_code(cls, script_exit_code):
        """
        Map a script exit code to a DNSMasq exit code.

        Args:
            script_exit_code (int): The script's exit code.

        Returns:
            DNSmasqExitCode: The corresponding DNSMasq exit code.
        """
        if script_exit_code >= 11:
            return cls(script_exit_code - 10)
        else:
            raise ValueError("Invalid DNSMasq exit code")

class DNSMasqDeploy(Enum):
    GLOBAL = auto()
    INTERFACE = auto()
    
class DNSMasqRunStatus(Enum):
    RUNNING = auto()
    STOPPED = auto()
    UNKNOWN = auto()

class DNSMasqService(NetworkManager):
    """
    Class for controlling the DNSMasq daemon service.
    """

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DNSMASQ_SERVICE)
        
    def control_service(self, service_action: SysServCntrlAction) -> bool:
        """
        Control the DNSMasq service with the specified action.

        Args:
            service_action (SysServCntrlAction): The action to perform on the service (start, restart, stop, status).

        Returns:
            bool: STATUS_OK if the command succeeds, STATUS_NOK otherwise.
        """
        result = SystemServiceControl().service_control('dnsmasq', service_action)
        if result == STATUS_OK:
            self.log.debug(f"DNSMasq service {service_action.value}ed successfully.")
        else:
            self.log.error(f"Failed to {service_action.value} DNSMasq service.")
        return result
        
    def start_dnsmasq(self) -> bool:
        """
        Start the DNSMasq service.

        Returns:
            bool: STATUS_OK if the command succeeds, STATUS_NOK otherwise.
        """
        return self.control_service(SysServCntrlAction.START)

    def restart_dnsmasq(self) -> bool:
        """
        Restart the DNSMasq service.

        Returns:
            bool: STATUS_OK if the command succeeds, STATUS_NOK otherwise.
        """
        return self.control_service(SysServCntrlAction.RESTART)

    def stop_dnsmasq(self) -> bool:
        """
        Stop the DNSMasq service.

        Returns:
            bool: STATUS_OK if the command succeeds, STATUS_NOK otherwise.
        """
        return self.control_service(SysServCntrlAction.STOP)

class DNSMasqInterfaceService(DNSMasqService):
    """
    Class for controlling the DNSMasq Interface Service.

    Args:
        dhcp_pool_name (str): Name of the DHCP pool.
        dhcp_pool_subnet (str): Subnet configuration for the DHCP pool.
        negate (bool): Whether to negate the configuration (default: False).

    Attributes:
        dhcp_pool_name (str): Name of the DHCP pool.
        dhcp_pool_subnet (str): Subnet configuration for the DHCP pool.
        negate (bool): Whether to negate the configuration.
    """

    DNSMASQ_FILENAME_SUFFIX = '_dnsmasq.conf'
    DNSMASQ_GLOBAL_FILENAME = 'dnsmasq.conf'
    DNSMASQ_CONFIG_DIR = '/etc/dnsmasq.d'
    DEFAULT_LEASE_TIME = 86400
    DEFAULT_DNS_LISTEN_PORT=5353 # '''Setting DNS to 5353 prevents conflict if there is already DNS running'''

    def __init__(self, dhcp_pool_name: DhcpPoolName, dhcp_pool_subnet: InetCidrText, negate=False):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DNSMASQ_INTERFACE_SERVICE)

        self.dhcp_pool_name = dhcp_pool_name
        self.dhcp_pool_subnet = dhcp_pool_subnet
        self.negate = negate
                
        self.d_masq_if_config = DNSMasqConfigurator()
        self.d_masq_global_config = DNSMasqConfigurator()
        self.dhcp_srv_db = DHCPServerDatabase()
        self._build_global_configuration()

    def _build_global_configuration(self) -> bool:
        self.d_masq_global_config.add_listen_port(self.DEFAULT_DNS_LISTEN_PORT)
        return STATUS_OK
    
    def build_interface_configuration(self) -> bool:
        """
        Build the interface configuration for DNSMasq.

        This method configures DNSMasq for the specified DHCP pool by setting the listen interfaces,
        DHCP pool ranges, and DHCP host reservations.

        Returns:
            bool: STATUS_OK if the configuration was successfully built, STATUS_NOK otherwise.
        """
        # Get the interface names for the DHCP pool
        interface_names = self.dhcp_srv_db.get_dhcp_pool_interfaces_db(self.dhcp_pool_name)
        self.log.debug(f"Number of interfaces: {len(interface_names)} -> {interface_names[0]}")

        # Get the DHCP pool ranges
        dhcp_pool_ranges = self.dhcp_srv_db.get_dhcp_pool_inet_range_db(self.dhcp_pool_name)
        self.log.debug(dhcp_pool_ranges)

        # Get the DHCP host reservations
        dhcp_hosts = self.dhcp_srv_db.get_dhcp_pool_reservation_db(self.dhcp_pool_name)
        self.log.debug(dhcp_hosts)

        # Set the listen interfaces in DNSMasq
        for interface_name in interface_names:
            self.d_masq_if_config.set_listen_interfaces(list(interface_name.values()))

        if self.dhcp_srv_db.dhcp_pool_name_dhcp_version_db(self.dhcp_pool_name) == DHCPVersion.DHCP_V4:
            for entry in dhcp_pool_ranges:
                range_start, range_end, netmask = entry['inet_start'], entry['inet_end'], entry['inet_subnet']
                self.d_masq_if_config.add_dhcp4_range_with_netmask(range_start, range_end, netmask, self.DEFAULT_LEASE_TIME)
        
        else:
            for entry in dhcp_pool_ranges:
                
                StringFormats.modify_dict_value(entry, 'inet_subnet', '/', '')
                
                range_start, range_end, netmask = entry['inet_start'], entry['inet_end'], entry['inet_subnet']
                self.d_masq_if_config.add_dhcp6_range_with_prefix_len(range_start, range_end, int(netmask), self.DEFAULT_LEASE_TIME, DHCPv6Modes.SLAAC)            

        # Get DHCP pool options and add them to DNSMasq
        dhcp_pool_options = self.dhcp_srv_db.get_dhcp_pool_options_db(self.dhcp_pool_name)
        self.log.debug(f"DHCP-Pool-options: {dhcp_pool_options}")
        for option in dhcp_pool_options:
            
            self.log.debug(f"DHCP-Pool-option: {option} -> OPTION: {option['option']}")
            
            option_code = DHCPOptionLookup().get_dhcpv4_option_code(option['option'])
            
            if option_code is not None:
                self.d_masq_if_config.add_dhcp_option(option_code, option['value'])
        
        # Add DHCP host reservations to DNSMasq
        for host in dhcp_hosts:
            if len(host) == 3:
                ethernet_address, ip_address, lease_time = host.values()
                self.d_masq_if_config.add_dhcp_host(ethernet_address, ip_address, lease_time)
            else:
                ethernet_address, ip_address = host.values()
                self.d_masq_if_config.add_dhcp_host(ethernet_address, ip_address)               
        
        self.log.debug(self.d_masq_if_config.generate_configuration())
        
        return STATUS_OK
    
    def deploy_configuration(self, deploy_type: DNSMasqDeploy) -> bool:
        """
        Deploy the DNSMasq configuration.

        Args:
            deploy_type (DNSMasqDeploy): The type of DNSMasq configuration to deploy (DNSMasqDeploy.GLOBAL or DNSMasqDeploy.INTERFACE).

        Returns:
            bool: STATUS_OK if the configuration was successfully deployed, STATUS_NOK otherwise.
        """
        if deploy_type == DNSMasqDeploy.GLOBAL:
            configurator = self.d_masq_global_config
        elif deploy_type == DNSMasqDeploy.INTERFACE:
            configurator = self.d_masq_if_config
        else:
            raise ValueError("Invalid deployment type")

        # Generate the DNSMasq INTERFACE/GLOBAL configuration
        config_text = configurator.generate_configuration()

        if deploy_type == DNSMasqDeploy.GLOBAL:
            filename = f"{self.DNSMASQ_GLOBAL_FILENAME}"
        elif deploy_type == DNSMasqDeploy.INTERFACE:
            if not self.dhcp_pool_name:
                self.log.error("Unable to create DNSMasq Configuration, DHCP-pool undefined")
                return STATUS_NOK
            filename = f"{self.dhcp_pool_name}{self.DNSMASQ_FILENAME_SUFFIX}"
        else:
            raise ValueError("Invalid deployment type")

        destination_file = os.path.join(self.DNSMASQ_CONFIG_DIR, filename)

        if os.path.exists(destination_file):
            os.remove(destination_file)

        with open(destination_file, "w") as file:
            file.write(config_text)

        return STATUS_OK

    def clear_configurations(self) -> bool:
        """
        Clear DNSMasq configurations for the DHCP pool.

        Returns:
            bool: STATUS_OK if configurations were successfully cleared, STATUS_NOK otherwise.
        """
        config_dir = self.DNSMASQ_CONFIG_DIR
        
        if os.path.exists(config_dir) and os.is_dir(config_dir):
            try:
                for filename in os.listdir(config_dir):
                    if filename.endswith(self.DNSMASQ_FILENAME_SUFFIX):
                        file_path = os.path.join(config_dir, filename)
                        os.remove(file_path)
            except Exception as e:
                self.log.debug(f"Error while clearing configurations: {str(e)}")
                return STATUS_NOK

        return STATUS_OK

    def check_dnsmasq_status(self) -> DNSMasqRunStatus:
        """
        Check the status of DNSMasq using 'systemctl status dnsmasq' command.

        Returns:
            DNSMasqRunStatus: An enum representing the DNSMasq status - STOPPED, RUNNING, or UNKNOWN.
        """
        try:
            result = self.run(['systemctl', 'status', 'dnsmasq'])

            if result.exit_code:
                return DNSMasqRunStatus.STOPPED
            else:
                return DNSMasqRunStatus.RUNNING
        
        except Exception as e:
            self.log.error(f"Error: {str(e)}")
            return DNSMasqRunStatus.UNKNOWN

class DNSMasqGlobalService(DNSMasqService):
    """
    Class for controlling the DNSMasq Interface Service.

    Args:
        dhcp_pool_name (str): Name of the DHCP pool.
        dhcp_pool_subnet (str): Subnet configuration for the DHCP pool.
        negate (bool): Whether to negate the configuration (default: False).

    Attributes:
        dhcp_pool_name (str): Name of the DHCP pool.
        dhcp_pool_subnet (str): Subnet configuration for the DHCP pool.
        negate (bool): Whether to negate the configuration.

    Example:
        service = DNSMasqService("home", "192.168.1.0/24")
    """

    def __init__(self, dhcp_pool_name: DhcpPoolName, dhcp_pool_subnet: InetCidrText, negate=False):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DNSMASQ_INTERFACE_SERVICE)    

# FILE: src/routershell/lib/network_services/dhcp/dnsmasq/dnsmasq_config_gen.py
import logging
from enum import Enum

from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import (
    ClientIdText,
    ClientName,
    DomainNameText,
    FilePath,
    InetAddressText,
    InetCidrText,
    InterfaceName,
    IpSetName,
    MacAddressText,
)


class DHCPv6Modes(Enum):

    '''
        For IPv6, the mode may be some combination of ra-only, slaac, ra-names, ra-stateless, ra-advrouter, off-link.

        - `ra-only` tells dnsmasq to offer Router Advertisement only on this subnet, and not DHCP.

        - `slaac` tells dnsmasq to offer Router Advertisement on this subnet and to set the A bit in the router advertisement, so that the client will use SLAAC addresses. When used with a DHCP range or static DHCP address this results in the client having both a DHCP-assigned and a SLAAC address.

        - `ra-stateless` sends router advertisements with the O and A bits set, and provides a stateless DHCP service. The client will use a SLAAC address, and use DHCP for other configuration information.

        - `ra-names` enables a mode which gives DNS names to dual-stack hosts which do SLAAC for IPv6. Dnsmasq uses the host's IPv4 lease to derive the name, network segment and MAC address and assumes that the host will also have an IPv6 address calculated using the SLAAC algorithm, on the same network segment. The address is pinged, and if a reply is received, an AAAA record is added to the DNS for this IPv6 address. Note that this is only happens for directly-connected networks, (not one doing DHCP via a relay) and it will not work if a host is using privacy extensions. ra-names can be combined with ra-stateless and slaac.

        - `ra-advrouter` enables a mode where router address(es) rather than prefix(es) are included in the advertisements. This is described in RFC-3775 section 7.2 and is used in mobile IPv6. In this mode the interval option is also included, as described in RFC-3775 section 7.3.

        - `off-link` tells dnsmasq to advertise the prefix without the on-link (aka L) bit set.    
    '''
    
    RA_ONLY = 'ra-only'
    RA_NAMES = 'ra-names'
    RA_STATELESS = 'ra-stateless'
    RA_ADV_ROUTER = 'ra-advrouter'
    SLAAC = 'slaac'
    OFF_LINK = 'off-link'

    @classmethod
    def get_key(cls, value):
        """Get the key for a given value in the enum."""
        for key, member in cls.__members__.items():
            if member.value == value:
                return key
            
        raise ValueError(f"No key found for value '{value}' in DHCPv6Modes enum.")
    
    @classmethod
    def get_mode(cls, value):
        """Get the enum member for a given value in the enum."""
        for member in cls:
            if member.value == value:
                return member

        raise ValueError(f"No mode found for value '{value}' in DHCPv6Modes enum.")


class DNSMasqConfigurator:
    '''
    For the latest DNSmasq configuration:
    https://thekelleys.org.uk/dnsmasq/docs/dnsmasq.conf.example
    
    https://thekelleys.org.uk/dnsmasq/docs/dnsmasq-man.html
    
    '''
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DNSMASQ_CONFIG)        
        self.config = []

    def add_listen_port(self, port: int):
        '''
        Add a listen port to the DNSMasq configuration.

        Args:
            port (int): The port number to listen on.
        '''
        self.config.append(f'port={port}')

    def enable_domain_filtering(self):
        '''
        Enable domain filtering in the DNSMasq configuration.
        '''
        self.config.append('domain-needed')
        self.config.append('bogus-priv')

    def enable_dnssec(self, trust_anchors_conf_path: str = None):
        '''
        Enable DNSSEC in the DNSMasq configuration.

        Args:
            trust_anchors_conf_path (str, optional): Path to a trust anchors configuration file.
        '''
        if trust_anchors_conf_path:
            self.config.append(f'conf-file={trust_anchors_conf_path}')
        self.config.append('dnssec')

    def enable_dnssec_check_unsigned(self):
        '''
        Enable DNSSEC check for unsigned domains in the DNSMasq configuration.
        '''
        self.config.append('dnssec-check-unsigned')

    def enable_filter_windows_dns_requests(self):
        '''
        Enable filtering of Windows DNS requests in the DNSMasq configuration.
        '''
        self.config.append('filterwin2k')

    def set_resolv_file(self, resolv_file_path: FilePath):
        '''
        Set the resolv file path in the DNSMasq configuration.

        Args:
            resolv_file_path (str): Path to the resolv file.
        '''
        self.config.append(f'resolv-file={resolv_file_path}')

    def set_strict_order(self):
        '''
        Set strict DNS server order in the DNSMasq configuration.
        '''
        self.config.append('strict-order')

    def disable_resolv_conf(self):
        '''
        Disable using the resolv.conf file in the DNSMasq configuration.
        '''
        self.config.append('no-resolv')

    def disable_poll_resolv_files(self):
        '''
        Disable polling resolv files in the DNSMasq configuration.
        '''
        self.config.append('no-poll')

    def add_name_server(self, domain: DomainNameText, ip_address: InetAddressText):
        '''
        Add a name server to the DNSMasq configuration.

        Args:
            domain (str): The domain to associate with the IP address.
            ip_address (str): The IP address of the name server.
        '''
        self.config.append(f'server=/{domain}/{ip_address}')

    def add_reverse_server(self, subnet: InetCidrText, nameserver: InetAddressText):
        '''
        Add a reverse DNS server to the DNSMasq configuration.

        Args:
            subnet (str): The subnet to associate with the nameserver.
            nameserver (str): The IP address of the nameserver.
        '''
        self.config.append(f'server=/{subnet}.in-addr.arpa/{nameserver}')

    def add_local_only_domain(self, local_domain: str):
        '''
        Add a local-only domain to the DNSMasq configuration.

        Args:
            local_domain (str): The local domain to add.
        '''
        self.config.append(f'local=/{local_domain}/')

    def force_domain_to_ip(self, domain: DomainNameText, ip_address: InetAddressText):
        '''
        Force a domain to resolve to a specific IP address in the DNSMasq configuration.

        Args:
            domain (str): The domain to force to the IP address.
            ip_address (str): The IP address to resolve the domain to.
        '''
        self.config.append(f'address=/{domain}/{ip_address}')

    def add_ipv6_address(self, domain: DomainNameText, ipv6_address: InetAddressText):
        '''
        Add an IPv6 address for a domain in the DNSMasq configuration.

        Args:
            domain (str): The domain to associate with the IPv6 address.
            ipv6_address (str): The IPv6 address of the domain.
        '''
        self.config.append(f'address=/{domain}/{ipv6_address}')

    def add_query_ips_to_ipset(self, domains: list[str], ipset_name: IpSetName):
        '''
        Add query IPs to an IPset in the DNSMasq configuration.

        Args:
            domains (list[str]): list of domains to associate with the IPset.
            ipset_name (str): Name of the IPset.
        '''
        self.config.append(f'ipset=/{"/".join(domains)}/{ipset_name}')

    def add_query_ips_to_netfilter_sets(self, domains: list[str], sets: list[str]):
        '''
        Add query IPs to netfilter sets in the DNSMasq configuration.

        Args:
            domains (list[str]): list of domains to associate with netfilter sets.
            sets (list[str]): list of netfilter sets to add the domains to.
        '''
        self.config.append(f'nftset=/{"/".join(domains)}/{",".join(sets)}')

    def add_ipv6_addresses_to_netfilter_sets(self, domains: list[str], sets: list[str]):
        '''
        Add IPv6 addresses to netfilter sets in the DNSMasq configuration.

        Args:
            domains (list[str]): list of domains to associate with netfilter sets.
            sets (list[str]): list of netfilter sets to add the domains to.
        '''
        for domain in domains:
            for set in sets:
                self.config.append(f'nftset=/{domain}/{set}')

    def set_server_routing(self, ip_address: InetAddressText, interface: InterfaceName | None = None, source_address: InetAddressText | None = None):
        '''
        Set server routing in the DNSMasq configuration.

        Args:
            ip_address (str): The IP address of the server.
            interface (str, optional): The network interface to bind to.
            source_address (str, optional): The source IP address to use.
        '''
        server_setting = f'server={ip_address}'
        if interface:
            server_setting += f'@{interface}'
        if source_address:
            server_setting += f'@{source_address}'
        self.config.append(server_setting)

    def set_uid_and_gid(self, user: str = None, group: str = None):
        '''
        Set the user and group for DNSMasq in the configuration.

        Args:
            user (str, optional): The user to run DNSMasq as.
            group (str, optional): The group to run DNSMasq as.
        '''
        if user or group:
            user_group_setting = 'user=' + \
                (user if user else '') + \
                (',' if user and group else '') + (group if group else '')
            self.config.append(user_group_setting)

    def set_listen_interfaces(self, interfaces: list[str]):
        '''
        Set listen interfaces for DNSMasq in the configuration.

        Args:
            interfaces (list[str]): list of network interfaces to listen on.
        '''
        for interface in interfaces:
            self.config.append(f'interface={interface}')

    def set_except_interfaces(self, interfaces: list[str]):
        '''
        Set exceptions for network interfaces in the DNSMasq configuration.

        Args:
            interfaces (list[str]): list of network interfaces to exclude.
        '''
        for interface in interfaces:
            self.config.append(f'except-interface={interface}')

    def set_listen_addresses(self, addresses: list[str]):
        '''
        Set listen addresses for DNSMasq in the configuration.

        Args:
            addresses (list[str]): list of IP addresses to listen on.
        '''
        for address in addresses:
            self.config.append(f'listen-address={address}')

    def disable_dhcp_on_interface(self, interface: InterfaceName):
        '''
        Disable DHCP on a specific network interface in the DNSMasq configuration.

        Args:
            interface (str): The network interface to disable DHCP on.
        '''
        self.config.append(f'no-dhcp-interface={interface}')

    def bind_only_to_listened_interfaces(self):
        '''
        Enable binding only to listened interfaces in the DNSMasq configuration.
        '''
        self.config.append('bind-interfaces')

    def disable_etc_hosts(self):
        '''
        Disable using the /etc/hosts file in the DNSMasq configuration.
        '''
        self.config.append('no-hosts')

    def set_additional_hosts_file(self, hosts_file_path: FilePath):
        '''
        Set an additional hosts file in the DNSMasq configuration.

        Args:
            hosts_file_path (str): Path to an additional hosts file.
        '''
        self.config.append(f'addn-hosts={hosts_file_path}')

    def set_expand_hosts(self):
        '''
        Enable expanding hosts in the DNSMasq configuration.
        '''
        self.config.append('expand-hosts')

    def set_domain(self, domain: DomainNameText):
        '''
        Set the domain in the DNSMasq configuration.

        Args:
            domain (str): The domain to set.
        '''
        self.config.append(f'domain={domain}')

    def set_domain_for_subnet(self, domain: DomainNameText, subnet: InetCidrText):
        '''
        Set a domain for a subnet in the DNSMasq configuration.

        Args:
            domain (str): The domain to associate with the subnet.
            subnet (str): The subnet to set the domain for.
        '''
        self.config.append(f'domain={domain},{subnet}')

    def set_domain_for_range(self, domain: DomainNameText, start_ip: str, end_ip: str):
        '''
        Set a domain for an IP range in the DNSMasq configuration.

        Args:
            domain (str): The domain to associate with the IP range.
            start_ip (str): The start IP address of the range.
            end_ip (str): The end IP address of the range.
        '''
        self.config.append(f'domain={domain},{start_ip},{end_ip}')

    def add_dhcp4_range(self, range_start: str, range_end: str, lease_time: int):
        '''
        Add a DHCP server range in the DNSMasq configuration for IPv4.

        Args:
            range_start (str): The start IP address of the DHCP range.
            range_end (str): The end IP address of the DHCP range.
            lease_time (int): The lease time for DHCP leases.
        '''
        self.config.append(
            f'dhcp-range={range_start},{range_end},{lease_time}')

    def add_dhcp4_range_with_netmask(self, range_start: str, range_end: str, netmask: str, lease_time: int):
        '''
        Add a DHCP server range with netmask in the DNSMasq configuration for IPv4.

        Args:
            range_start (str): The start IP address of the DHCP range.
            range_end (str): The end IP address of the DHCP range.
            netmask (str): The netmask for the DHCP range.
            lease_time (int): The lease time for DHCP leases.
        '''
        self.config.append(
            f'dhcp-range={range_start},{range_end},{netmask},{lease_time}')

    def add_dhcp4_range_with_tag(self, tag: str, range_start: str, range_end: str, lease_time: int):
        '''
        Add a DHCP server range with a tag in the DNSMasq configuration for IPv4.

        Args:
            tag (str): The tag to associate with the DHCP range.
            range_start (str): The start IP address of the DHCP range.
            range_end (str): The end IP address of the DHCP range.
            lease_time (int): The lease time for DHCP leases.
        '''
        self.config.append(
            f'dhcp-range=set:{tag},{range_start},{range_end},{lease_time}')

    def add_dhcp6_range(self, range_start: str, range_end: str, lease_time: int, mode: DHCPv6Modes):
        '''
        Add a DHCPv6 server range in the DNSMasq configuration.

        Args:
            range_start (str): The start IPv6 address of the DHCPv6 range.
            range_end (str): The end IPv6 address of the DHCPv6 range.
            lease_time (int): The lease time for DHCPv6 leases.
            mode (DHCPv6Modes): The DHCPv6 mode to configure.
        '''
        self.config.append(
            f'dhcp-range={range_start},{range_end},{lease_time},constructor:{self.interface},{mode.value}')

    def add_dhcp6_range_with_prefix_len(self, range_start: str, range_end: str, prefix_len: int, lease_time: int, mode: DHCPv6Modes):
        '''
        Add a DHCPv6 server range with prefix length in the DNSMasq configuration.

        Args:
            range_start (str): The start IPv6 address of the DHCPv6 range.
            range_end (str): The end IPv6 address of the DHCPv6 range.
            prefix_len (int): The prefix length for the DHCPv6 range.
            lease_time (int): The lease time for DHCPv6 leases.
            mode (DHCPv6Modes): The DHCPv6 mode to configure.
        '''
        self.config.append(
            f'dhcp-range={range_start},{range_end},{mode.value},{prefix_len},{lease_time}')

    def add_dhcp6_range_with_tag(self, tag: str, range_start: str, range_end: str, lease_time: int, mode: DHCPv6Modes):
        '''
        Add a DHCPv6 server range with a tag in the DNSMasq configuration.

        Args:
            tag (str): The tag to associate with the DHCPv6 range.
            range_start (str): The start IPv6 address of the DHCPv6 range.
            range_end (str): The end IPv6 address of the DHCPv6 range.
            lease_time (int): The lease time for DHCPv6 leases.
            mode (DHCPv6Modes): The DHCPv6 mode to configure.
        '''
        self.config.append(
            f'dhcp-range=set:{tag},{range_start},{range_end},{lease_time},constructor:{self.interface},{mode.value}')

    def set_tftp_server(self, root_directory: str):
        '''
        Set a TFTP server in the DNSMasq configuration.

        Args:
            root_directory (str): The root directory for TFTP.
        '''
        self.config.append(f'tftp-root={root_directory}')

    def set_boot_file(self, boot_file: FilePath):
        '''
        Set the boot file in the DNSMasq configuration.

        Args:
            boot_file (str): The boot file to set.
        '''
        self.config.append(f'pxe-service=x86PC,"{boot_file}"')

    def add_pxe_boot_option(self, option_number: int, option_value: str):
        '''
        Add a PXE boot option in the DNSMasq configuration.

        Args:
            option_number (int): The PXE option number.
            option_value (str): The value of the PXE option.
        '''
        self.config.append(f'pxe-service=x86PC,{option_number},{option_value}')

    def add_dhcp_option(self, option_number: int, option_value: str):
        '''
        Add a DHCP option in the DNSMasq configuration.

        Args:
            option_number (int): The DHCP option number.
            option_value (str): The value of the DHCP option.
        '''
        self.config.append(f'dhcp-option={option_number},{option_value}')

    def set_dhcp_option_66(self, tftp_server: str):
        '''
        Set DHCP option 66 (TFTP server) in the DNSMasq configuration.

        Args:
            tftp_server (str): The TFTP server address.
        '''
        self.config.append(f'dhcp-option=66,{tftp_server}')

    def set_dhcp_option_67(self, boot_file: FilePath):
        '''
        Set DHCP option 67 (Boot file) in the DNSMasq configuration.

        Args:
            boot_file (str): The boot file path.
        '''
        self.config.append(f'dhcp-option=67,{boot_file}')

    def set_dhcp_authoritative(self):
        """
        Set the DHCP server as authoritative in the configuration.
        """
        self.config.append('dhcp-authoritative')

    def add_dhcp_host(self, *args: str | int):
        '''
        Add a DHCP host configuration to the DNSMasq configuration.

        Args:
            *args (str | int): Variable number of arguments.
                - If only one argument is provided, it is assumed to be the Ethernet address.
                - If two arguments are provided, the first is assumed to be the Ethernet address, and the second is the IP address.
                - If three arguments are provided, the first is the Ethernet address, the second is the name, and the third is the IP address.
                - If four arguments are provided, the first is the Ethernet address, the second is the name, the third is the IP address, and the fourth is the lease time.

        Examples:
            - add_dhcp_host("11:22:33:44:55:66", "192.168.0.60")
            - add_dhcp_host("11:22:33:44:55:66", "fred")
            - add_dhcp_host("11:22:33:44:55:66", "fred", "192.168.0.60")
            - add_dhcp_host("11:22:33:44:55:66", "fred", "192.168.0.60", "45m")
        '''
        if len(args) == 1:
            self.config.append(f'dhcp-host={args[0]}')
        elif len(args) == 2:
            self.config.append(f'dhcp-host={args[0]},{args[1]}')
        elif len(args) == 3:
            self.config.append(f'dhcp-host={args[0]},{args[1]},{args[2]}')
        elif len(args) == 4:
            self.config.append(f'dhcp-host={args[0]},{args[1]},{args[2]},{args[3]}')

    def add_dhcp_host_with_client_id(self, client_id: ClientIdText, ip_address: InetAddressText):
        '''
        Add a DHCP host configuration with a client identifier to the DNSMasq configuration.

        Args:
            client_id (str): The client identifier.
            ip_address (str): The IP address.

        Example:
            add_dhcp_host_with_client_id("01:02:02:04", "192.168.0.60")
        '''
        self.config.append(f'dhcp-host=id:{client_id},{ip_address}')

    def add_dhcp_host_with_infiniband(self, hardware_address: MacAddressText, ip_address: InetAddressText):
        '''
        Add a DHCP host configuration with InfiniBand hardware address to the DNSMasq configuration.

        Args:
            hardware_address (str): The InfiniBand hardware address.
            ip_address (str): The IP address.

        Example:
            add_dhcp_host_with_infiniband("ff:00:00:00:00:00:02:00:00:02:c9:00:f4:52:14:03:00:28:05:81", "192.168.0.61")
        '''
        self.config.append(f'dhcp-host=id:{hardware_address},{ip_address}')

    def add_dhcp_host_with_name(self, client_name: ClientName, ip_address: InetAddressText, lease_time: str):
        '''
        Add a DHCP host configuration with a client name, IP address, and lease time to the DNSMasq configuration.

        Args:
            client_name (str): The client name.
            ip_address (str): The IP address.
            lease_time (str): The lease time.

        Example:
            add_dhcp_host_with_name("bert", "192.168.0.70", "infinite")
        '''
        self.config.append(f'dhcp-host={client_name},{ip_address},{lease_time}')

    def enable_dhcp_host_ignore(self, ethernet_address: MacAddressText):
        '''
        Enable ignoring DHCP requests from a specific host with the given Ethernet address.

        Args:
            ethernet_address (str): The Ethernet address to ignore.

        Example:
            enable_dhcp_host_ignore("11:22:33:44:55:66")
        '''
        self.config.append(f'dhcp-host={ethernet_address},ignore')

    def enable_dhcp_host_ignore_client_id(self, ethernet_address: MacAddressText):
        '''
        Enable ignoring DHCP client ID presented by a host with the given Ethernet address.

        Args:
            ethernet_address (str): The Ethernet address.

        Example:
            enable_dhcp_host_ignore_client_id("11:22:33:44:55:66")
        '''
        self.config.append(f'dhcp-host={ethernet_address},id:*')

    def enable_dhcp_host_set_extra_options(self, ethernet_address: MacAddressText, options_tag: str):
        '''
        Send extra options tagged with a specific identifier to a host with the given Ethernet address.

        Args:
            ethernet_address (str): The Ethernet address.
            options_tag (str): The options tag.

        Example:
            enable_dhcp_host_set_extra_options("11:22:33:44:55:66", "set:red")
        '''
        self.config.append(f'dhcp-host={ethernet_address},{options_tag}')

    def enable_dhcp_host_set_extra_options_pattern(self, ethernet_pattern: str, options_tag: str):
        '''
        Send extra options tagged with a specific identifier to any host with Ethernet addresses matching a pattern.

        Args:
            ethernet_pattern (str): The Ethernet address pattern.
            options_tag (str): The options tag.

        Example:
            enable_dhcp_host_set_extra_options_pattern("11:22:33:*:*:*", "set:red")
        '''
        self.config.append(f'dhcp-host={ethernet_pattern},{options_tag}')

    def generate_configuration(self):
        """
        Generate the DNSMasq configuration as a string.

        Returns:
            str: The DNSMasq configuration as a string.
        """
        return '\n'.join(self.config)

# FILE: src/routershell/lib/network_services/telnet/telnet_server.py
import logging

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import FilePath
from routershell.lib.network_manager.common.run_commands import RunCommand
from routershell.lib.network_services.common.network_ports import NetworkPorts
from routershell.lib.system.init_system import InitSystem, InitSystemChecker


class TelnetService(RunCommand):
    """
    A class to manage the Telnet service using either SysV init system or Systemd.

    Attributes:
        port (int): The port number on which the Telnet service listens.
        telnet_config_file (str | None): Path to the Telnet configuration file for SysV init.
        init_system (InitSystem): The init system in use (SysV or Systemd).
    """
    
    _instance: 'TelnetService | None' = None
    init_system: InitSystem
    port: int
    telnet_config_file: FilePath | None = None

    def __new__(cls, *args, **kwargs) -> 'TelnetService':
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self, port: int = NetworkPorts.TELNET) -> None:
        """
        Initializes the TelnetService with the specified port.

        Args:
            port (int): The port number for the Telnet service. Default is 23.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().TELNET_SERVER)
        
        self.init_system = InitSystemChecker().get_init_system()
        self.port = port
        
        # Set configuration file path based on init system
        if self.init_system == InitSystem.SYSV:
            self.telnet_config_file = '/etc/xinetd.d/telnet'
        else:
            self.telnet_config_file = None  # For Systemd, config management might differ

    def set_port(self, port: int) -> bool:
        """
        Sets a new port for the Telnet service and updates the configuration.

        Args:
            port (int): The new port number for the Telnet service.

        Returns:
            bool: STATUS_OK if the operation was successful, False otherwise.
        """
        self.log.debug(f'set_port() -> {port}')
        self.port = port
        
        if self.init_system == InitSystem.SYSV:
            return self.update_telnet_config()
        
        # For Systemd, port configuration might be managed differently
        return STATUS_OK
    
    def set_timeout(self, timeout: int=60) -> bool:
        '''timeout in seconds if no login is achived'''
        return STATUS_OK
    
    def set_max_login_attempts(self, max_attemps: int=3) -> bool:
        '''max login attempts the restart login'''
        return STATUS_OK
    
    def set_max_concurrent_users(self, max_users: int=5) -> bool:
        '''max concurrent users'''
        return STATUS_OK

    def update_telnet_config(self) -> bool:
        """
        Updates the Telnet configuration file with the new port and restarts the service.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        if self.telnet_config_file:
            try:
                with open(self.telnet_config_file) as file:
                    lines = file.readlines()
                
                with open(self.telnet_config_file, 'w') as file:
                    for line in lines:
                        if line.strip().startswith('port ='):
                            self.log.debug(f'Overwriting port to {self.port}')
                            file.write(f'port = {self.port}\n')
                        else:
                            file.write(line)
                            
                return self.restart_service()
            
            except OSError as e:
                self.log.error(f"An error occurred while updating the config file: {e}")
                return STATUS_NOK
            
        return STATUS_OK

    def start_service(self) -> bool:
        """
        Starts the Telnet service.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        if self.init_system == InitSystem.SYSV:
            rtn = self.run(['service', 'xinetd', 'start'])
            if rtn.exit_code:
                self.log.error(f'Unable to start telnet server service, reason: {rtn.stderr}')
                return STATUS_NOK
            
        elif self.init_system == InitSystem.SYSTEMD:
            rtn = self.run(['systemctl', 'start', 'telnet.service'])
            if rtn.exit_code:
                self.log.error(f'Unable to start telnet server service, reason: {rtn.stderr}')
                return STATUS_NOK
        
        self.log.debug(f'Telnet-Server-Start message: {rtn.stdout}')
        
        return STATUS_OK

    def stop_service(self) -> bool:
        """
        Stops the Telnet service.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        if self.init_system == InitSystem.SYSV:
            rtn = self.run(['service', 'xinetd', 'stop'])
            if rtn.exit_code:
                self.log.error(f'Unable to stop telnet server service, reason: {rtn.stderr}')
                return STATUS_NOK
            
        elif self.init_system == InitSystem.SYSTEMD:
            rtn = self.run(['systemctl', 'stop', 'telnet.service'])
            if rtn.exit_code:
                self.log.error(f'Unable to stop telnet server service, reason: {rtn.stderr}')
                return STATUS_NOK
        
        self.log.debug(f'Telnet-Server-Stop message: {rtn.stdout}')
            
        return STATUS_OK

    def restart_service(self) -> bool:
        """
        Restarts the Telnet service.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        if self.init_system == InitSystem.SYSV:
            rtn = self.run(['service', 'xinetd', 'restart'])
            if rtn.exit_code:
                self.log.error(f'Unable to restart telnet server service, reason: {rtn.stderr}')
                return STATUS_NOK
            
        elif self.init_system == InitSystem.SYSTEMD:
            rtn = self.run(['systemctl', 'restart', 'telnet.service'])
            if rtn.exit_code:
                self.log.error(f'Unable to restart telnet server service, reason: {rtn.stderr}')
                return STATUS_NOK
            
        self.log.debug(f'Telnet-Server-Restart message: {rtn.stdout}')
            
        return STATUS_OK

    def status_service(self) -> bool:
        """
        Checks the status of the Telnet service.

        Returns:
            bool: True if the service status check was successful, False otherwise.
        """
        if self.init_system == InitSystem.SYSV:
            result = self.run(['service', 'xinetd', 'status'])
        
        elif self.init_system == InitSystem.SYSTEMD:
            result = self.run(['systemctl', 'status', 'telnet.service'])
            
        else:
            self.log.error('Unsupported init system')
            return STATUS_NOK

        if result.exit_code:
            self.log.error(f'Unable to get status of telnet server service, reason: {result.stderr}')
            return STATUS_NOK

        self.log.debug(f'Telnet service status: {result.stdout}')
        return STATUS_OK

# FILE: src/routershell/lib/system/system.py
import logging

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import HostnameText
from routershell.lib.db.system_db import SystemDatabase
from routershell.lib.network_services.common.network_ports import NetworkPorts
from routershell.lib.network_services.telnet.telnet_server import TelnetService
from routershell.lib.system.system_call import SystemCall


class System:
    def __init__(self):
        """
        Initialize the System class with logging configuration.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().SYSTEM)
    
    def update_hostname(self, hostname: HostnameText) -> bool:
        """
        Update the hostname of the system both in the OS and the system database.

        Parameters:
        hostname (str): The new hostname to set.

        Returns:
        bool: STATUS_OK if successful, STATUS_NOK otherwise.
        """
        if SystemCall().set_hostname_os(hostname):
            self.log.error(f"Error: Failed to set the hostname: ({hostname}) to OS")
            return STATUS_NOK

        if SystemDatabase().set_hostname_db(hostname):
            self.log.error(f"Error: Failed to set the hostname: ({hostname}) to DB")
            return STATUS_NOK

        return STATUS_OK

    def update_telnet_server(self, enable: bool = True, port: int = NetworkPorts.TELNET) -> bool:
        """
        Update the Telnet server configuration.

        Args:
            enable (bool): Whether to enable or disable the Telnet server.
            port (int): The port for the Telnet server.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        self.log.debug(f'update_telnet_server() - enable: {enable} -> port: {port}')
        
        if enable:
            if TelnetService().set_port(port):
                self.log.error(f'Unable to update telnet server port: {port} to OS')
                return STATUS_NOK
            
            if TelnetService().restart_service():
                self.log.error(f'Unable to restart telnet server on port: {port}')
                return STATUS_NOK
            
        else:
            if TelnetService().stop_service():
                self.log.error('Unable to stop telnet server')
                return STATUS_NOK                

        if SystemDatabase().set_telnet_server_status(enable, port):
            self.log.error(f'Unable to add telnet server status: enable: {enable} and port: {port} to DB')
            return STATUS_NOK
            
        return STATUS_OK
    
    def update_ssh_server(self, enable: bool = True, port: int = NetworkPorts.SSH) -> bool:
        """
        Update the SSH server configuration.

        Args:
            enable (bool): Whether to enable or disable the SSH server.
            port (int): The port for the SSH server.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        print('SSH Server not implemented yet')
        return STATUS_OK

# FILE: src/routershell/lib/system/system_call.py
import logging
import os
import platform
import shutil
import textwrap

from routershell.lib.common.common import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import HostnameText
from routershell.lib.db.system_db import SystemDatabase
from routershell.lib.network_manager.common.run_commands import RunCommand, RunLog
from routershell.lib.system.init_system import InitSystemChecker


class InvalidSystemConfig(Exception):
    def __init__(self, message):
        super().__init__(message)

class SystemCall(RunCommand):

    def __init__(self, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().SYSTEM_CALL)
        self.arg = arg
        self.sys_db = SystemDatabase()

    def get_banner(self, max_line_length: int=0) -> str:
        """
        Retrieve the banner Message of the Day (Motd) from the RouterShell configuration.

        Args:
            cls: The RouterShellDB class.
            max_line_length (int): The maximum length for each line in the banner text.

        Returns:
            str: The formatted banner text with lines limited to the specified maximum length.
        """
        result, banner_text = self.sys_db.get_banner_motd()
                
        if result:
            return ""
        
        if max_line_length:
            return textwrap.fill(banner_text, width=max_line_length)

        return banner_text
            
    def set_banner(self, banner_motd: str) -> bool:
        """
        Set the banner Message of the Day (Motd) in the RouterShell configuration.

        Args:
            banner_motd (str): The new banner text.

        Returns:
            bool: STATUS_OK if the banner is successfully set, STATUS_NOK otherwise.
        """
        return self.sys_db.set_banner_motd(banner_motd)
    
    def del_banner(self) -> bool:
        """
        Delete the banner Message of the Day (MOTD).

        This method sets the banner MOTD in the system configuration to an empty string, effectively removing any existing banner.

        Returns:
            bool: True if the banner MOTD is successfully deleted, False otherwise.

        Example:
            To delete the banner MOTD, you can use the 'del_banner' method as follows:

            >>> result = SystemConfigurator().del_banner()
            >>> if result:
            ...     print("Banner MOTD deleted successfully.")
            ... else:
            ...     print("Failed to delete banner MOTD.")

        Note:
            - This method updates the system configuration using the 'set_banner_motd' method of the underlying 'SystemDatabase' class.
            - The 'set_banner_motd' method returns True if the update is successful, and False otherwise.
        """
        return self.sys_db.set_banner_motd('')

    def set_hostname_from_db(self) -> bool:
        """
        Sets the hostname from the system database if available; otherwise, uses the system configuration.

        Retrieves the hostname from the system database. If the database does not provide a hostname, it falls back to the system configuration.
        Attempts to set the system hostname to the retrieved value.

        Returns:
            bool: STATUS_OK if the hostname is successfully set, STATUS_NOK otherwise.
        """
        host_name = self.sys_db.get_hostname_db()
        self.log.debug(f'set_hostname_from_db() -> Retrieved hostname from DB: {host_name}')
        
        if not host_name:
            host_name = self.get_hostname_os()
            self.log.debug(f'No hostname found in DB, setting hostname: ({host_name}) to DB')
            
            if self.sys_db.set_hostname_db(host_name):
                self.log.error(f"Failed to set the hostname: ({host_name}) to DB")
                return STATUS_NOK
            return STATUS_OK

        if self.set_hostname_os(host_name):
            self.log.error(f"Failed to set the hostname: ({host_name}) via OS")
            return STATUS_NOK

        return STATUS_OK
    
    def set_hostname_os(self, hostname: HostnameText) -> bool:
        """
        Set the system hostname.
        
        This function sets the hostname of the system. Currently, it supports Linux.
        
        Parameters:
        hostname (str): The desired hostname to set.

        Returns:
        bool: STATUS_OK if successful, STATUS_NOK otherwise.
        """
        current_os = platform.system()

        if current_os == "Linux":
            try:
                if InitSystemChecker().is_sysv():
                    # Set the hostname permanently in /etc/hostname
                    with open('/etc/hostname', 'w') as f:
                        f.write(hostname + '\n')

                    # Check if the hostname command is available
                    if not shutil.which('hostname'):
                        self.log.fatal(f"hostname command not found on the system, unable to set hostname: {hostname}")
                        return STATUS_NOK

                    # Set the hostname temporarily until the next reboot
                    result = self.run(['hostname', hostname])
                    if result.exit_code:
                        self.log.error(f"Failed to set hostname (SysV): {result}, reason: {result.stderr}")
                        return STATUS_NOK

                elif InitSystemChecker().is_systemd():
                    # Set the hostname permanently using hostnamectl
                    result = self.run(['hostnamectl', 'set-hostname', hostname])
                    if result.exit_code:
                        self.log.error(f"Failed to set hostname (systemd): {result}, reason: {result.stderr}")
                        return STATUS_NOK

                else:
                    self.log.error("set_hostname_os(): Unsupported init system.")
                    return STATUS_NOK

                self.log.debug(f"set_hostname_os() -> Hostname successfully set to {hostname}")
                return STATUS_OK

            except Exception as e:
                self.log.error(f"set_hostname_os(): Failed to set hostname: {e}")
                return STATUS_NOK

        else:
            self.log.error(f"set_hostname_os(): Setting hostname not supported for OS: {current_os}")
            return STATUS_NOK
        
    def get_hostname_os(self) -> str:
        """
        Get the current static hostname using the `hostnamectl --static` command.

        Returns:
            str: The current static hostname.
        """
        hostname = os.uname().nodename
        self.log.debug(f'get_hostname() -> {hostname}')
        return hostname
    
    def get_run_log(self) -> list[str]:
        """
        Retrieve the run log from the RunLog utility class.

        Returns:
            list[str]: A list of strings representing each line of the run log file.

        Example:
            >>> instance = SomeOtherClass()
            >>> log_contents = instance.get_run_log()
            >>> for line in log_contents:
            >>>     print(line)
        """
        return RunLog().get_run_log()
    

# FILE: src/routershell/lib/system/system_service_control/system_service_control.py
import enum
import logging

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import ServiceName
from routershell.lib.network_manager.common.run_commands import RunCommand
from routershell.lib.system.init_system import InitSystem, InitSystemChecker


class SysServCntrlAction(enum.Enum):
    """
    Enumeration for system service actions.
    """
    START = 'start'
    RESTART = 'restart'
    STOP = 'stop'
    STATUS = 'status'

class SystemServiceControl(RunCommand):
    
    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().SYSTEM_SERVICE_CTRL)
        
        self.init_system = InitSystemChecker().get_init_system()

    def service_control(self, service_name: ServiceName, service_action: SysServCntrlAction) -> bool:
        """
        Controls a system service using the appropriate init system.

        Args:
            service_name (str): The name of the service to control.
            service_action (SysServCntrlAction): The action to perform on the service.

        Returns:
            bool: STATUS_OK if the command succeeds, STATUS_NOK otherwise.
        """
        if not service_name:
            self.log.error('Service name is not defined')
            return STATUS_NOK
        
        command = self._init_system_control(service_name, service_action)

        if not command:
            self.log.error('Service control command is not defined')
            return STATUS_NOK
        
        result = self.run(command)
        
        if result.exit_code:
            self.log.error(f"Failed to {service_action.value} service {service_name}. Exit code: {result.exit_code}")
            return STATUS_NOK

        self.log.debug(f"Service {service_name} {service_action.value}ed successfully.")
        return STATUS_OK

    def _init_system_control(self, service_name: ServiceName, service_action: SysServCntrlAction) -> list[str]:
        """
        Constructs the appropriate command for the current init system.

        Args:
            service_name (str): The name of the service to control.
            service_action (SysServCntrlAction): The action to perform on the service.

        Returns:
            list[str]: The command to run.
        """
        if self.init_system == InitSystem.SYSV:
            return ['service', service_name, service_action.value]
        elif self.init_system == InitSystem.SYSTEMD:
            return ['systemctl', service_action.value, service_name]
        else:
            self.log.error(f"Unsupported init system: {self.init_system}")
            return []

# FILE: src/routershell/logging_config.py
"""Central logging configuration for RouterShell."""

from __future__ import annotations

import logging
import logging.config
import os
from pathlib import Path

from routershell.lib.common.types import FilePath, LoggerName, LogLevelName

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
    def _resolve_bool(value: str | None, default: bool) -> bool:
        if value is None:
            return default

        normalized = value.strip().lower()
        if normalized in _TRUE_VALUES:
            return True
        if normalized in _FALSE_VALUES:
            return False
        return default

    @staticmethod
    def _can_write_log_file(log_file: Path) -> bool:
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

