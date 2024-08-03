import os
import socket
import subprocess
import termios
import psutil

class UserConnectionType:
    def __init__(self, username: str):
        self.username = username
        self.connection_type = self.detect_connection_type()

    def detect_connection_type(self) -> str:
        for proc in psutil.process_iter(['username', 'terminal']):
            if proc.info['username'] == self.username:
                terminal = proc.info['terminal']
                if terminal:
                    if self.is_serial_terminal(terminal):
                        return "Serial Terminal"
                    elif self.is_pty(terminal):
                        return "PTY"
                    elif self.is_network_connection(proc):
                        return "Network"
        return "Unknown"

    def is_serial_terminal(self, terminal: str) -> bool:
        # Check for typical serial device names
        if 'ttyS' in terminal or 'ttyUSB' in terminal or 'ttyAMA' in terminal:
            return True
        return False

    def is_pty(self, terminal: str) -> bool:
        # Check for PTY device names
        if 'pts' in terminal:
            return True
        return False

    def is_network_connection(self, proc: psutil.Process) -> bool:
        try:
            # Check if the process has an SSH connection
            if 'SSH_CONNECTION' in proc.environ():
                return True
            
            # Check if the process has any network connections
            for conn in proc.connections():
                if conn.status == 'ESTABLISHED':
                    return True
            
            # Check if we have a default gateway
            result = subprocess.run(['ip', 'route'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if 'default' in result.stdout.decode():
                return True
            
            # Try to connect to an external site
            socket.create_connection(("www.google.com", 80), 2)
            return True
        except (psutil.Error, socket.error, subprocess.SubprocessError):
            return False

    def get_connection_type(self) -> str:
        return self.connection_type

# Usage example
if __name__ == "__main__":
    username = "dev01"  # Replace with the username you want to check
    user_connection = UserConnectionType(username)
    print(f"Connection type for user {username}: {user_connection.get_connection_type()}")
