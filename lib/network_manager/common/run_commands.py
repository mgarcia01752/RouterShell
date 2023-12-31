import os
import subprocess
import logging
import datetime
from typing import List, NamedTuple

from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS

class RunResult(NamedTuple):
    """
    Represents the result of running a command.

    Attributes:
        stdout (str): The standard output of the command.
        stderr (str): The standard error output of the command.
        exit_code (int): The exit code of the command.
        command (List[str]): The list of command arguments used.
    """

    stdout: str
    stderr: str
    exit_code: int
    command: List[str]

class RunCommand:
    """
    A class for running Linux commands with sudo and logging successful and failed commands.
    """
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().RUN)
        
        self.run_cmds_successful: List[str] = []
        self.run_cmds_failed: List[str] = []
        self.log_dir = '/tmp/log'

        # Check if the log directory exists, and create it if not
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def log_command(self, command:str):
        """
        Log the executed command along with a timestamp.

        Args:
            command (str): The command that was executed.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {command}"
        log_path = f"{self.log_dir}/routershell-command.log"

        with open(log_path, "a") as log_file:
            log_file.write(log_entry + "\n")
    
    def run(self, command: List[str], suppress_error: bool = False, shell: bool = False, sudo: bool = True) -> RunResult:
        """
        Run a command in the Linux environment and log the result.

        Args:
            command (List[str]): The command and its arguments as a list.
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
                self.log.error(f"Error output: {e.stderr.decode('utf-8')}")

            self.run_cmds_failed.append(cmd_str)
            self.log_command(cmd_str)

            return RunResult("", str(e), e.returncode, command)

