from lib.common.common import Common

class PromptResponse:
    
    @staticmethod
    def _print_message(message: str):
        """
        Prints a message to the console.

        Args:
            message (str): The message to be printed.
        """
        print(message)

    @staticmethod
    def print_invalid_cmd_response(response: str):
        """
        Prints a message indicating that an invalid command was received, 
        after processing the response to remove specific substrings.

        Args:
            response (str): The command response that is considered invalid.
        """
        message = f'Invalid command: {Common.flatten_list(response)}'
        PromptResponse._print_message(message)

    @staticmethod    
    def print_success_response(response: str):
        """
        Prints a success message.

        Args:
            response (str): The success message to be printed.
        """
        message = f'Success: {response}'
        PromptResponse._print_message(message)
    
    @staticmethod    
    def print_error_response(response: str):
        """
        Prints an error message.

        Args:
            response (str): The error message to be printed.
        """
        message = f'Error: {response}'
        PromptResponse._print_message(message)
    
    @staticmethod    
    def print_missing_args_response(command: str, required_args: list):
        """
        Prints an error message indicating that required arguments are missing 
        for a given command.

        Args:
            command (str): The command that is missing required arguments.
            required_args (list): A list of required arguments that are missing.
        """
        args_list = ', '.join(required_args)
        message = f'Error: The command "{command}" is missing required arguments: {args_list}.'
        PromptResponse._print_message(message)
