import subprocess
import sys

class ShellInterface:
    def __init__(self):
        """
        Initialize the ShellInterface class.
        """
        pass

    def run_command(self, command):
        """
        Execute a shell command and return the output.

        Args:
            command (str): The command to execute.

        Returns:
            tuple: A tuple containing the standard output and standard error of the command.
        """
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            return result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return e.stdout, e.stderr

    def open_interactive_shell(self):
        """
        Open an interactive bash shell session.

        This method opens an interactive bash shell session using subprocess.Popen,
        allowing the user to interact with the shell in real time.
        """
        try:
            # Open an interactive shell session
            process = subprocess.Popen("/usr/bin/env bash", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            print("Entering interactive shell. Type 'exit' to leave the shell.")
            
            while True:
                # Read command from user input
                user_input = input("$ ")
                
                if user_input.strip().lower() == 'exit':
                    break
                
                # Send command to the shell
                process.stdin.write(user_input + '\n')
                process.stdin.flush()

                # Read and print the output and errors
                stdout = process.stdout.readline()
                stderr = process.stderr.readline()
                
                if stdout:
                    print(stdout, end='')
                if stderr:
                    print(stderr, end='', file=sys.stderr)

            process.terminate()
            print("Shell session terminated.")

        except Exception as e:
            print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    shell_interface = ShellInterface()

    # Open an interactive shell session
    shell_interface.open_interactive_shell()
