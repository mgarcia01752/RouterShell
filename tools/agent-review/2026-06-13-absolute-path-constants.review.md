### Summary
RouterShell absolute Linux runtime paths are now centralized in src/routershell/lib/common/constants.py. Runtime logging, command logs, init-system detection, system log reads, hostname writes, DNSMasq/Telnet config paths, runtime DB fallback paths, and ARP procfs paths now reference shared constants or a shared procfs helper.

### Modified Files
- src/routershell/lib/common/constants.py
- src/routershell/logging_config.py
- src/routershell/lib/network_manager/common/run_commands.py
- src/routershell/lib/network_manager/common/sysctl.py
- src/routershell/lib/common/common.py
- src/routershell/lib/system/init_system.py
- src/routershell/lib/system/system_call.py
- src/routershell/lib/db/sqlite_db/router_shell_db.py
- src/routershell/lib/network_services/dhcp/dnsmasq/dnsmasq.py
- src/routershell/lib/network_services/telnet/telnet_server.py
- src/routershell/lib/network_manager/network_operations/arp.py
- tests/packaging/test_typing_contract.py

### Commands Executed And Results
- `rg -n '/(etc|var|tmp|opt|usr|home|run|lib|bin|sbin|dev|proc|sys)' src/routershell tests` -> pass; remaining live source literals are centralized constants, docstrings, or test assertions
- `/opt/routershell/venv/bin/python -m compileall -q src/routershell tests/packaging/test_typing_contract.py` -> pass
- `/opt/routershell/venv/bin/python -m pytest tests/packaging/test_typing_contract.py tests/packaging/test_runtime_database.py` -> pass; 5 tests passed
- `PYTHONPATH=src /opt/routershell/venv/bin/python - <<'PY' ...` -> pass; imported central constants and dependent modules
- `/opt/routershell/venv/bin/python tools/release/qa_checker.py --skip-pycycle` -> pass; Ruff passed and pytest passed with 21 tests

### Tests
- `pytest tests/packaging/test_typing_contract.py tests/packaging/test_runtime_database.py` -> pass; common path constants and DB path behavior covered
- `pytest` -> pass; 21 tests passed through the QA checker
- `ruff` -> pass; All checks passed through the QA checker

### Notes / Warnings
- Documentation, examples, generated review bundles, and backup files still contain absolute path examples by design.
- HostAPD `/var/run/hostapd` remains only in an explanatory docstring, not executable path construction.

### Remaining TODOs / Follow-Ups
- Consider a future cleanup for backup files under src/routershell/lib/*-bak.py if those are still intended to be maintained.

# FILE: src/routershell/lib/common/constants.py
import os
from enum import Enum, auto
from pathlib import Path

from routershell.lib.common.types import InterfaceName, StatusResult

STATUS_OK = StatusResult(False)
STATUS_NOK = StatusResult(True)

ROUTER_CONFIG_DIR = 'config'
ROUTER_CONFIG = os.path.join(ROUTER_CONFIG_DIR, 'startup-config.cfg')

ROUTERSHELL_STATE_DIR = Path("/var/lib/routershell")
ROUTERSHELL_RUNTIME_LOG_DIR = Path("/tmp/log")
ROUTERSHELL_DEFAULT_LOG_FILE = ROUTERSHELL_RUNTIME_LOG_DIR / "routershell.log"
ROUTERSHELL_COMMAND_LOG_FILE = ROUTERSHELL_RUNTIME_LOG_DIR / "routershell-command.log"
ROUTERSHELL_SYSCTL_LOG_FILE = ROUTERSHELL_RUNTIME_LOG_DIR / "sysctl.log"

SYSTEMD_RUNTIME_DIR = Path("/run/systemd/system")
SYSV_INIT_DIR = Path("/etc/init")
ETC_HOSTNAME_FILE = Path("/etc/hostname")
SYSV_MESSAGES_LOG_FILE = Path("/var/log/messages")
SYSV_BOOT_LOG_FILE = Path("/var/log/boot")

DNSMASQ_CONFIG_DIR = Path("/etc/dnsmasq.d")
DNSMASQ_LEASE_FILE_PATH = Path("/var/lib/misc/dnsmasq.leases")
HOSTAPD_CONF_DIR = Path("/etc/hostapd")
HOSTAPD_CONF_FILE = "hostapd.conf"
TELNET_SYSV_CONFIG_FILE = Path("/etc/xinetd.d/telnet")

PROC_SYS_NET_IPV4_CONF_DIR = Path("/proc/sys/net/ipv4/conf")

ROUTER_SHELL_DB = 'routershell.db'
ROUTER_SHELL_DB_FILE_ENV = 'ROUTERSHELL_DB_FILE'
ROUTER_SHELL_PROJECT_ROOT_ENV = 'ROUTERSHELL_PROJECT_ROOT'
ROUTER_SHELL_SQL_STARTUP = 'db_schema.sql'


def proc_ipv4_conf_path(interface_name: InterfaceName, setting_name: str) -> Path:
    return PROC_SYS_NET_IPV4_CONF_DIR / interface_name / setting_name

class Status(Enum):
    ENABLE = auto()
    DISABLE = auto()

# FILE: src/routershell/logging_config.py
"""Central logging configuration for RouterShell."""

from __future__ import annotations

import logging
import logging.config
import os
from pathlib import Path

from routershell.lib.common.constants import ROUTERSHELL_DEFAULT_LOG_FILE
from routershell.lib.common.types import FilePath, LoggerName, LogLevelName, PredicateResult, StatusResult

DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FILE = ROUTERSHELL_DEFAULT_LOG_FILE
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

# FILE: src/routershell/lib/network_manager/common/run_commands.py
import datetime
import logging
import os
import subprocess
from typing import NamedTuple

from routershell.lib.common.constants import ROUTERSHELL_COMMAND_LOG_FILE, ROUTERSHELL_RUNTIME_LOG_DIR
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import StatusResult


class RunResult(NamedTuple):
    """
    Represents the result of running a command.

    Attributes:
        stdout (str): The standard output of the command.
        stderr (str): The standard error output of the command.
        exit_code (int): The exit code of the command.
        command (list[str]): The list of command arguments used.
    """

    stdout: str
    stderr: str
    exit_code: int
    command: list[str]

class RunLog:
    """
    Utility class to retrieve the run log from a specified file.

    Attributes:
        None

    Methods:
        get_run_log(): Retrieves the contents of a run log file as a list of strings.

    Usage:
        log = RunLog()
        log_contents = log.get_run_log()
        for line in log_contents:
            print(line)
    """
    @staticmethod
    def get_run_log() -> list[str]:
        """
        Retrieve the contents of the run log file.

        Returns:
            list[str]: A list of strings representing each line of the run log file.

        Example:
            >>> log = RunLog()
            >>> log_contents = log.get_run_log()
            >>> for line in log_contents:
            >>>     print(line)
        """
        cmd = f'cat {RunCommand.log_cmd}'.split()
        result = RunCommand().run(cmd)
        return result.stdout.split("\n")
    
    @staticmethod
    def clear_run_log() -> StatusResult:
        cmd = f'rm {RunCommand.log_cmd}'.split()
        result = RunCommand().run(cmd)
        return result.exit_code

class RunCommand:
    """
    A class for running Linux commands with sudo and logging successful and failed commands.
    """
    
    run_cmds_successful: list[str] = []
    run_cmds_failed: list[str] = []
    log_dir = ROUTERSHELL_RUNTIME_LOG_DIR
    log_cmd = ROUTERSHELL_COMMAND_LOG_FILE
    
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().RUN)
        
        # Check if the log directory exists, and create it if not
        if not os.path.exists(RunCommand.log_dir):
            os.makedirs(RunCommand.log_dir)

    def log_command(self, command:str):
        """
        Log the executed command along with a timestamp.

        Args:
            command (str): The command that was executed.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {command}"

        with open(RunCommand.log_cmd, "a") as log_file:
            log_file.write(log_entry + "\n")
    
    def run(self, command: list[str], suppress_error: bool = False, shell: bool = False, sudo: bool = True) -> RunResult:
        """
        Run a command in the Linux environment and log the result.

        Args:
            command (list[str]): The command and its arguments as a list.
            suppress_error (bool, optional): If True, suppress logging of errors. Defaults to False.
            shell (bool, optional): If True, execute the command using a shell. Defaults to False.
            sudo (bool, optional): If True, prepend 'sudo' to the command. Defaults to True.

        Returns:
            RunResult: A named tuple containing stdout, stderr, exit_code, and the command.
            
        """
        try:

            if sudo:
                command = ['sudo'] + command
                            
            process = subprocess.run(command, shell=shell, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            exit_code = process.returncode
            stdout = process.stdout.decode("utf-8")
            stderr = process.stderr.decode("utf-8")

            cmd_str = " ".join(command)

            self.log.debug(f"run({exit_code}) -> cmd -> {cmd_str}")
            self.log_command(cmd_str)

            return RunResult(stdout, stderr, exit_code, command)

        except subprocess.CalledProcessError as e:
            cmd_str = " ".join(command)

            if not suppress_error:
                self.log.error(f"Command failed: {e}: {cmd_str}")
                self.log.error(f"Error output: {e.stderr.strip()}")

            RunCommand.run_cmds_failed.append(cmd_str)
            self.log_command(cmd_str)

            return RunResult("", str(e), e.returncode, command)

# FILE: src/routershell/lib/network_manager/common/sysctl.py
import datetime
import logging
import os

from routershell.lib.common.constants import (
    ROUTERSHELL_RUNTIME_LOG_DIR,
    ROUTERSHELL_SYSCTL_LOG_FILE,
    STATUS_NOK,
    STATUS_OK,
)
from routershell.lib.common.types import StatusResult
from routershell.lib.network_manager.common.run_commands import RunCommand


class SysCtl(RunCommand):
    """
    sysctl is used to modify kernel parameters at runtime.
    The parameters available are those listed under /proc/sys/.
    Procfs is required for sysctl support in Linux.
    You can use sysctl to both read and write sysctl data.
    """

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.sys_ctl_log_dir = ROUTERSHELL_RUNTIME_LOG_DIR
        if not os.path.exists(self.sys_ctl_log_dir):
            os.makedirs(self.sys_ctl_log_dir)

    def write_sysctl(self, sysctl_param: str, value:str) -> StatusResult:
        """
        Write a value to a sysctl parameter using sudo and log the action.

        :param sysctl_param: The sysctl parameter to be modified (e.g., 'net.ipv4.neigh.default.gc_stale_time').
        :param value: The value to write to the sysctl parameter.
        :return: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
            
        command = ['sysctl', '-w', f"{sysctl_param}={value}"]
        self.log.debug(f"write_sysctl() -> CMD: ({command})")
        results = self.run(command)

        self.log_command(f"Writing '{value}' to {sysctl_param}")
        
        if results.exit_code:
            self.log_command(f"Failed to write '{value}' to {sysctl_param}: {results.stderr}")
            return STATUS_NOK
                        
        return STATUS_OK
    
    def read_sysctl(self, sysctl_param:str) -> str:
        """
        Read a sysctl parameter value.

        :param sysctl_param: The sysctl parameter to read (e.g., 'net.ipv4.tcp_syncookies').
        :return: The value of the sysctl parameter if successful, None otherwise.
        """
        try:
            command = ["sysctl", "-n", sysctl_param]
            result = self.run(command)

            if result.exit_code == 0:
                value = result.stdout.strip()
                self.log_command(f"Reading '{sysctl_param}': {value}")
                return value
            else:
                self.log_command(f"Failed to read '{sysctl_param}': {result.stderr.strip()}")
                return None
        except Exception as e:
            self.log_command(f"Error while reading '{sysctl_param}': {e}")
            return None

    def log_command(self, command:str):
        """
        Log the executed command along with a timestamp.

        Args:
            command (str): The command that was executed.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {command}"
        log_path = ROUTERSHELL_SYSCTL_LOG_FILE
        
        self.log.debug(log_entry)

        with open(log_path, "a") as log_file:
            log_file.write(log_entry + "\n")

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

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK, SYSTEMD_RUNTIME_DIR, SYSV_INIT_DIR
from routershell.lib.common.types import EnvironmentVariableName, HostnameText, InterfaceName, PredicateResult
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
        # Check if the SysV init directory exists.
        if os.path.exists(SYSV_INIT_DIR):
            return 'sudo init 6'  # Use SysV init reboot command

        # Check if the systemd runtime directory exists.
        if os.path.exists(SYSTEMD_RUNTIME_DIR):
            return 'sudo systemctl reboot'  # Use systemd reboot command

        # Default to 'sudo reboot' if neither init system is found
        return 'sudo reboot'
    
    @staticmethod
    def get_shutdown_command() -> str:

        # Check if the SysV init directory exists.
        if os.path.exists(SYSV_INIT_DIR):
            return 'sudo init 0'  # Use SysV init reboot command

        # Check if the systemd runtime directory exists.
        if os.path.exists(SYSTEMD_RUNTIME_DIR):
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
    def is_valid_ip(ip_str: str) -> PredicateResult:
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
    def is_valid_hostname(hostname: HostnameText) -> PredicateResult:
        """
        Check if a hostname is valid based on DNS standards.

        Args:
            hostname (str): The hostname to be validated.

        Returns:
            StatusResult: True if the hostname is valid, False otherwise.
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
    def is_loopback_if_name_valid(interface_name: InterfaceName, add_loopback_if_name: list[str] = None) -> PredicateResult:
        """
        Check if the given interface name is in the loopback format or starts with any of the specified prefixes.

        Args:
            interface_name (str): The name of the network interface.
            loopback_if_check_list (list[str], optional): list of additional interface name prefixes to check against. Default is None.

        Returns:
            StatusResult: True if the interface name matches the loopback format or any prefix in if_check_list, False otherwise.
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

# FILE: src/routershell/lib/system/init_system.py
import os
import re
from enum import Enum

from routershell.lib.common.constants import SYSTEMD_RUNTIME_DIR, SYSV_BOOT_LOG_FILE, SYSV_MESSAGES_LOG_FILE
from routershell.lib.common.types import PredicateResult
from routershell.lib.network_manager.common.run_commands import RunCommand


class InitSystem(Enum):
    SYSTEMD = 'systemd'
    SYSV = 'sysv'
    UNKNOWN = 'unknown'

class InitSystemChecker(RunCommand):
    """
    A class to check whether the Linux system is using SysV init or Systemd, implemented as a Singleton.
    """

    _instance: 'InitSystemChecker | None' = None
    _init_system: InitSystem | None = None

    def __new__(cls, *args, **kwargs) -> 'InitSystemChecker':
        """
        Creates a new instance of InitSystemChecker if one does not already exist.

        Args:
            *args: Positional arguments to pass to the class constructor.
            **kwargs: Keyword arguments to pass to the class constructor.

        Returns:
            InitSystemChecker: The singleton instance of InitSystemChecker.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """
        Initializes the singleton instance by detecting the init system.
        """
        self._init_system = self._detect_init_system()

    def _detect_init_system(self) -> InitSystem:
        """
        Detects the current init system.

        Returns:
            InitSystem: An enum representing the init system.
        """
        try:
            if os.path.exists(SYSTEMD_RUNTIME_DIR):
                return InitSystem.SYSTEMD
            
            result = self.run(['systemctl', '--version'], suppress_error=True)
            if result.exit_code == 0:
                return InitSystem.SYSTEMD
            
        except FileNotFoundError:
            pass
        
        except Exception as e:
            print(f"An error occurred while checking Systemd: {e}")
        
        return InitSystem.SYSV

    def is_systemd(self) -> PredicateResult:
        """
        Checks if the system is using Systemd.

        Returns:
            StatusResult: True if Systemd is in use, False otherwise.
        """
        return self._init_system == InitSystem.SYSTEMD

    def is_sysv(self) -> PredicateResult:
        """
        Checks if the system is using SysV init.

        Returns:
            StatusResult: True if SysV is in use, False otherwise.
        """
        return self._init_system == InitSystem.SYSV
    
    def get_init_system(self) -> InitSystem:
        """
        Gets the current init system.

        Returns:
            InitSystem: The enum representing the current init system.
        """
        return self._init_system
    
class SysV:
    """
    A class for running commands on a SysV init system.
    """

    def __init__(self):
        self.run_command = RunCommand()
    
    def get_messages(self, grep: str | None = None) -> list[str]:
        """
        Retrieves the system messages from the /var/log/messages file.

        Args:
            grep (str | None): A regular expression string to filter the log messages. If None, all messages are returned.

        Returns:
            list[str]: A list of log messages from /var/log/messages. If the command fails, an empty list is returned.
        """
        command = ['cat', str(SYSV_MESSAGES_LOG_FILE)]
        result = self.run_command.run(command, suppress_error=True)
        
        if result.exit_code:
            return []

        lines = result.stdout.split('\n')
        if grep:
            pattern = re.compile(grep)
            lines = [line for line in lines if pattern.search(line)]
        
        return lines
    
    def get_boot_log(self, grep: str | None = None) -> list[str]:
        """
        Retrieves the system messages from the /var/log/boot file.

        Args:
            grep (str | None): A regular expression string to filter the log messages. If None, all messages are returned.

        Returns:
            list[str]: A list of boot log messages from /var/log/boot. If the command fails, an empty list is returned.
        """
        command = ['cat', str(SYSV_BOOT_LOG_FILE)]
        result = self.run_command.run(command, suppress_error=True)
        
        if result.exit_code:
            return []

        lines = result.stdout.split('\n')
        if grep:
            pattern = re.compile(grep)
            lines = [line for line in lines if pattern.search(line)]
        
        return lines
        
        

# FILE: src/routershell/lib/system/system_call.py
import logging
import os
import platform
import shutil
import textwrap

from routershell.lib.common.common import STATUS_NOK, STATUS_OK
from routershell.lib.common.constants import ETC_HOSTNAME_FILE
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import HostnameText, StatusResult
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
            
    def set_banner(self, banner_motd: str) -> StatusResult:
        """
        Set the banner Message of the Day (Motd) in the RouterShell configuration.

        Args:
            banner_motd (str): The new banner text.

        Returns:
            StatusResult: STATUS_OK if the banner is successfully set, STATUS_NOK otherwise.
        """
        return self.sys_db.set_banner_motd(banner_motd)
    
    def del_banner(self) -> StatusResult:
        """
        Delete the banner Message of the Day (MOTD).

        This method sets the banner MOTD in the system configuration to an empty string, effectively removing any existing banner.

        Returns:
            StatusResult: True if the banner MOTD is successfully deleted, False otherwise.

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

    def set_hostname_from_db(self) -> StatusResult:
        """
        Sets the hostname from the system database if available; otherwise, uses the system configuration.

        Retrieves the hostname from the system database. If the database does not provide a hostname, it falls back to the system configuration.
        Attempts to set the system hostname to the retrieved value.

        Returns:
            StatusResult: STATUS_OK if the hostname is successfully set, STATUS_NOK otherwise.
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
    
    def set_hostname_os(self, hostname: HostnameText) -> StatusResult:
        """
        Set the system hostname.
        
        This function sets the hostname of the system. Currently, it supports Linux.
        
        Parameters:
        hostname (str): The desired hostname to set.

        Returns:
        StatusResult: STATUS_OK if successful, STATUS_NOK otherwise.
        """
        current_os = platform.system()

        if current_os == "Linux":
            try:
                if InitSystemChecker().is_sysv():
                    # Set the hostname permanently.
                    with open(ETC_HOSTNAME_FILE, 'w') as f:
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
    

# FILE: src/routershell/lib/db/sqlite_db/router_shell_db.py
import logging
import os
import sqlite3
from pathlib import Path

from tabulate import tabulate

from routershell.lib.common.constants import (
    ROUTER_SHELL_DB,
    ROUTER_SHELL_DB_FILE_ENV,
    ROUTER_SHELL_PROJECT_ROOT_ENV,
    ROUTER_SHELL_SQL_STARTUP,
    ROUTERSHELL_STATE_DIR,
    STATUS_NOK,
    STATUS_OK,
)
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.singleton import Singleton
from routershell.lib.common.types import (
    BridgeName,
    DbFilePath,
    DhcpPoolName,
    HostnameText,
    InetAddressText,
    InetCidrText,
    InterfaceName,
    MacAddressText,
    NatPoolName,
    SsidText,
    StatusResult,
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

    @staticmethod
    def default_db_file_path() -> DbFilePath:
        """
        Return the runtime SQLite database file path.

        RouterShell must not write runtime database files into the installed
        Python package directory. The installer sets `ROUTERSHELL_DB_FILE`;
        development/local installs can fall back to
        `ROUTERSHELL_PROJECT_ROOT/.routershell/routershell.db`.

        Returns:
            DbFilePath: The SQLite database file path RouterShell should use.
        """
        configured_db_file = os.environ.get(ROUTER_SHELL_DB_FILE_ENV)
        if configured_db_file:
            return configured_db_file

        project_root = os.environ.get(ROUTER_SHELL_PROJECT_ROOT_ENV)
        if project_root:
            return Path(project_root) / ".routershell" / ROUTER_SHELL_DB

        return ROUTERSHELL_STATE_DIR / ROUTER_SHELL_DB

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().ROUTER_SHELL_DB)

        self.db_file_path = self.default_db_file_path()
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

    def create_database(self) -> StatusResult:
        """
        Create an SQLite database file and populate it with tables and data from an SQL file.

        Returns:
            StatusResult: STATUS_OK if the database is created successfully, STATUS_NOK if there is an error.
        """
        self.log.debug("create_database()")

        try:
            Path(self.db_file_path).parent.mkdir(parents=True, exist_ok=True)
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

    def open_connection(self) -> StatusResult:
        """
        Open a connection to the SQLite database.

        Returns:
            StatusResult: STATUS_OK if the connection is successful, STATUS_NOK if there is an error.
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

    def reset_database(self) -> StatusResult:
        """
        Remove the existing database file and create a new one.

        Returns:
            StatusResult: STATUS_OK if the reset is successful, STATUS_NOK if there is an error.
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
            StatusResult: True if the specified NAT direction exists, False otherwise.
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

# FILE: src/routershell/lib/network_services/dhcp/dnsmasq/dnsmasq.py
import logging
import os
from enum import Enum, auto

from routershell.lib.common.constants import DNSMASQ_CONFIG_DIR as DEFAULT_DNSMASQ_CONFIG_DIR
from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.string_formats import StringFormats
from routershell.lib.common.types import DhcpPoolName, InetCidrText, StatusResult
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
        
    def control_service(self, service_action: SysServCntrlAction) -> StatusResult:
        """
        Control the DNSMasq service with the specified action.

        Args:
            service_action (SysServCntrlAction): The action to perform on the service (start, restart, stop, status).

        Returns:
            StatusResult: STATUS_OK if the command succeeds, STATUS_NOK otherwise.
        """
        result = SystemServiceControl().service_control('dnsmasq', service_action)
        if result == STATUS_OK:
            self.log.debug(f"DNSMasq service {service_action.value}ed successfully.")
        else:
            self.log.error(f"Failed to {service_action.value} DNSMasq service.")
        return result
        
    def start_dnsmasq(self) -> StatusResult:
        """
        Start the DNSMasq service.

        Returns:
            StatusResult: STATUS_OK if the command succeeds, STATUS_NOK otherwise.
        """
        return self.control_service(SysServCntrlAction.START)

    def restart_dnsmasq(self) -> StatusResult:
        """
        Restart the DNSMasq service.

        Returns:
            StatusResult: STATUS_OK if the command succeeds, STATUS_NOK otherwise.
        """
        return self.control_service(SysServCntrlAction.RESTART)

    def stop_dnsmasq(self) -> StatusResult:
        """
        Stop the DNSMasq service.

        Returns:
            StatusResult: STATUS_OK if the command succeeds, STATUS_NOK otherwise.
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
    DNSMASQ_CONFIG_DIR = DEFAULT_DNSMASQ_CONFIG_DIR
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

    def _build_global_configuration(self) -> StatusResult:
        self.d_masq_global_config.add_listen_port(self.DEFAULT_DNS_LISTEN_PORT)
        return STATUS_OK
    
    def build_interface_configuration(self) -> StatusResult:
        """
        Build the interface configuration for DNSMasq.

        This method configures DNSMasq for the specified DHCP pool by setting the listen interfaces,
        DHCP pool ranges, and DHCP host reservations.

        Returns:
            StatusResult: STATUS_OK if the configuration was successfully built, STATUS_NOK otherwise.
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
    
    def deploy_configuration(self, deploy_type: DNSMasqDeploy) -> StatusResult:
        """
        Deploy the DNSMasq configuration.

        Args:
            deploy_type (DNSMasqDeploy): The type of DNSMasq configuration to deploy (DNSMasqDeploy.GLOBAL or DNSMasqDeploy.INTERFACE).

        Returns:
            StatusResult: STATUS_OK if the configuration was successfully deployed, STATUS_NOK otherwise.
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

    def clear_configurations(self) -> StatusResult:
        """
        Clear DNSMasq configurations for the DHCP pool.

        Returns:
            StatusResult: STATUS_OK if configurations were successfully cleared, STATUS_NOK otherwise.
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

# FILE: src/routershell/lib/network_services/telnet/telnet_server.py
import logging

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK, TELNET_SYSV_CONFIG_FILE
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import FilePath, StatusResult
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
            self.telnet_config_file = TELNET_SYSV_CONFIG_FILE
        else:
            self.telnet_config_file = None  # For Systemd, config management might differ

    def set_port(self, port: int) -> StatusResult:
        """
        Sets a new port for the Telnet service and updates the configuration.

        Args:
            port (int): The new port number for the Telnet service.

        Returns:
            StatusResult: STATUS_OK if the operation was successful, False otherwise.
        """
        self.log.debug(f'set_port() -> {port}')
        self.port = port
        
        if self.init_system == InitSystem.SYSV:
            return self.update_telnet_config()
        
        # For Systemd, port configuration might be managed differently
        return STATUS_OK
    
    def set_timeout(self, timeout: int=60) -> StatusResult:
        '''timeout in seconds if no login is achived'''
        return STATUS_OK
    
    def set_max_login_attempts(self, max_attemps: int=3) -> StatusResult:
        '''max login attempts the restart login'''
        return STATUS_OK
    
    def set_max_concurrent_users(self, max_users: int=5) -> StatusResult:
        '''max concurrent users'''
        return STATUS_OK

    def update_telnet_config(self) -> StatusResult:
        """
        Updates the Telnet configuration file with the new port and restarts the service.

        Returns:
            StatusResult: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
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

    def start_service(self) -> StatusResult:
        """
        Starts the Telnet service.

        Returns:
            StatusResult: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
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

    def stop_service(self) -> StatusResult:
        """
        Stops the Telnet service.

        Returns:
            StatusResult: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
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

    def restart_service(self) -> StatusResult:
        """
        Restarts the Telnet service.

        Returns:
            StatusResult: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
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

    def status_service(self) -> StatusResult:
        """
        Checks the status of the Telnet service.

        Returns:
            StatusResult: True if the service status check was successful, False otherwise.
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

# FILE: src/routershell/lib/network_manager/network_operations/arp.py
import json
import logging
from enum import Enum

from tabulate import tabulate

from routershell.lib.common.constants import STATUS_NOK, STATUS_OK, proc_ipv4_conf_path
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import InetAddressText, InterfaceName, MacAddressText, PredicateResult, StatusResult
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

    def is_arp_entry_exists(self, ip_address: InetAddressText, interface: InterfaceName | None = None) -> PredicateResult:
        """
        Check if an ARP entry already exists for a specific IP address on a given interface.

        Parameters:
            ip_address (str): The IP address to check.
            interface (str): The network interface to check. If None, checks all interfaces.

        Returns:
            StatusResult: True if the ARP entry exists, False otherwise.
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

    def set_os_timeout(self, arp_time_out: int = 300) -> StatusResult:
        """
        Sets the ARP cache timeout in the operating system.

        This method writes the given ARP cache timeout value to the system configuration
        using the `sysctl` interface. It sets the timeout value for the ARP cache entries.

        Args:
            arp_time_out (int): The desired timeout value for ARP cache entries in seconds.
                                Default is 300 seconds.

        Returns:
            StatusResult: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        sysctl_param = "net.ipv4.neigh.default.gc_stale_time"
        
        if SysCtl().write_sysctl(sysctl_param, str(arp_time_out)):
            print(f"Unable to set ARP cache timeout to {arp_time_out} seconds.")
            return STATUS_NOK
        else:
            print(f"Set ARP cache timeout to {arp_time_out} seconds.")
        
        return STATUS_OK

    def set_os_arp_accept(self, ifName: InterfaceName = "all", enable: bool = True) -> StatusResult:
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
            StatusResult: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        arp_accept_file = proc_ipv4_conf_path(ifName, "arp_accept")
        value = "1" if enable else "0"
        
        return SysCtl().write_sysctl(arp_accept_file, value)

        def set_os_arp_announce(self, ifName:InterfaceName, value:int) -> StatusResult:
            """
            Set the ARP announce value for a specific network interface.

            :param ifName: The name of the network interface.
            :param value: The ARP announce value (0, 1, or 2).
            :return: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
            """
            arp_announce_file = proc_ipv4_conf_path(ifName, "arp_announce")
            return SysCtl().write_sysctl(arp_announce_file, str(value))

    def set_os_arp_evict_nocarrier(self, ifName: InterfaceName = "all", enable: bool = True) -> StatusResult:
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
            StatusResult: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        arp_evict_file = proc_ipv4_conf_path(ifName, "arp_evict_nocarrier")
        value = "1" if enable else "0"
        return SysCtl().write_sysctl(arp_evict_file, value)

    def set_os_arp_filter(self, ifName: InterfaceName = "all", enable: bool = True) -> StatusResult:
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
            StatusResult: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        arp_filter_file = proc_ipv4_conf_path(ifName, "arp_filter")
        value = "1" if enable else "0"
        return SysCtl.write_sysctl(arp_filter_file, value)

    def set_os_arp_ignore(self, ifName: InterfaceName="all", enable: bool=True) -> StatusResult:
        """
        Set the ARP ignore value for a specific network interface.

        :param ifName: The name of the network interface. Default is 'all' to apply to all interfaces.
        :param value: The ARP ignore value (0, 1, or 2).
        :return: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        arp_ignore_file = proc_ipv4_conf_path(ifName, "arp_ignore")
        value = "1" if enable else "0"
        return SysCtl().write_sysctl(arp_ignore_file, str(value))

    def set_os_arp_notify(self, ifName: InterfaceName = "all", enable: bool = True) -> StatusResult:
        """
        Enable or disable ARP notifications for a specific network interface.

        Args:
            ifName (str): The name of the network interface. Default is 'all' to apply to all interfaces.
            enable (bool): True to enable ARP notifications, False to disable them.

        Returns:
            StatusResult: STATUS_OK if the operation was successful, STATUS_NOK otherwise. Most of the time, it will be one of these values.
        """
        arp_notify_file = proc_ipv4_conf_path(ifName, "arp_notify")
        value = "1" if enable else "0"
        
        return SysCtl().write_sysctl(arp_notify_file, value)

    def set_os_drop_gratuitous_arp(self, if_name: InterfaceName = "all", enable: bool = True) -> StatusResult:
        """
        Enable or disable the dropping of gratuitous ARP packets for a specific network interface.

        Args:
            ifName (str): The name of the network interface. Default is 'all' to apply to all interfaces.
            enable (bool): True to enable dropping of gratuitous ARP packets, False to disable it.

        Returns:
            StatusResult: STATUS_OK if the operation was successful, STATUS_NOK otherwise. Most of the time, it will be one of these values.
        """

        value = "1" if enable else "0"
        arp_file = proc_ipv4_conf_path(if_name, "drop_gratuitous_arp")
        
        command = ["sh", "-c", f"echo {value} > {arp_file}"]
        
        results = self.run(command)
        
        self.log.debug(f"set_drop_gratuitous_arp(ifname: {if_name} -> enable: {enable}) -> Cmd: {command}")
        
        if results.exit_code:
            self.log.error(f"Failed to set gratuitous ARP to {value} due to {results.stderr}")
            return STATUS_NOK
        else:
            self.log.debug(f"Set gratuitous ARP to {value}")
            return STATUS_OK

    def set_os_proxy_arp(self, if_name: InterfaceName = 'all', enable: bool = True) -> StatusResult:
        """
        Enable or disable proxy ARP for a specific network interface.

        Args:
            ifName (str): The name of the network interface. Default is 'all' to apply to all interfaces.
            enable (bool): True to enable proxy ARP, False to disable it.

        Returns:
            StatusResult: STATUS_OK for success, STATUS_NOK for failure.
        """       
        value = "1" if enable else "0"
        
        arp_file = proc_ipv4_conf_path(if_name, "proxy_arp")
        
        command = ["sh", "-c", f"echo {value} > {arp_file}"]

        results = self.run(command)
        
        self.log.debug(f"set_proxy_arp(ifname: {if_name} -> enable: {enable}) -> Cmd: {command}")
        
        if results.exit_code:
            self.log.error(f"Failed to set proxy ARP to {value} due to {results.stderr}")
            return STATUS_NOK
        else:
            self.log.debug(f"Set proxy ARP to {value}")
            return STATUS_OK
            
    def set_os_proxy_arp_pvlan(self, ifName: InterfaceName, enable: bool) -> StatusResult:
        """
        Enable or disable proxy ARP for Private VLAN (PVLAN) on a specific network interface.

        Args:
            ifName (str): The name of the network interface.
            enable (bool): True to enable proxy ARP for PVLAN, False to disable it.

        Returns:
            StatusResult: STATUS_OK for success, STATUS_NOK for failure.
        """

        proxy_arp_pvlan_file = proc_ipv4_conf_path(ifName, "proxy_arp_pvlan")
        value = "1" if enable else "0"
        
        self.log.debug(f"set_proxy_arp(ifname: {ifName}) -> File: {proxy_arp_pvlan_file} -> enable: {enable}")
                
        return SysCtl().write_sysctl(proxy_arp_pvlan_file, value)

    def set_os_static_arp(self, interface_name:InterfaceName, inet:InetAddressText, mac_address:MacAddressText, encap:Encapsulate=Encapsulate.ARPA, add_arp_entry:bool=True) -> StatusResult:
        """
        Configure or remove a static ARP entry using iproute2.

        Args:
            interface_name (str): The name of the network interface.
            inet (str): The IPv4 address for the static ARP entry.
            mac_address (str): The MAC address for the static ARP entry.
            encap (Encapsulate, optional): The ARP encapsulation type (default is ARPA).
            add_arp_entry (bool, optional): True to configure the entry (default), False to remove it.

        Returns:
            StatusResult: STATUS_OK if the operation was successful, STATUS_NOK otherwise.

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

# FILE: tests/packaging/test_typing_contract.py
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

