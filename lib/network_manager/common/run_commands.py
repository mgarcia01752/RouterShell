import os
import subprocess
import logging
import datetime
from typing import List, NamedTuple

from lib.cli.common.cmd2_global import  Cmd2GlobalSettings as CGS
from lib.cli.common.cmd2_global import  RouterShellLoggingGlobalSettings as RSLGS

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
        self.debug = CGS().DEBUG_RUN
        
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
    
    def run(self, command:List[str], suppress_error:bool=False) -> RunResult:
        """
        Run a Linux command with sudo and log the result.

        Args:
            command (List[str]): The command and its arguments as a list.

        Returns:
            RunResult: A named tuple containing stdout, stderr, exit_code, and the command.
        """
        try:
            command = ['sudo'] + command
            process = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
                logging.error(f"Command failed: {e}: {cmd_str}")
            
            self.run_cmds_failed.append(cmd_str)
            self.log_command(cmd_str)
            
            return RunResult("", str(e), e.returncode, command)
