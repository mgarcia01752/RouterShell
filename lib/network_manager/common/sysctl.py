import datetime
import logging
import os
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.common.run_commands import RunCommand

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
        self.sys_ctl_log_dir = '/tmp/log'
        if not os.path.exists(self.sys_ctl_log_dir):
            os.makedirs(self.sys_ctl_log_dir)

    def write_sysctl(self, sysctl_param: str, value:str) -> bool:
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
        log_path = f"{self.sys_ctl_log_dir}/sysctl.log"
        
        self.log.debug(log_entry)

        with open(log_path, "a") as log_file:
            log_file.write(log_entry + "\n")
