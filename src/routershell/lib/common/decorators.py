from enum import Enum
import functools

class Color(Enum):
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    RESET = "\033[0m"

def colorize_log(color_code: str):
    def decorator_log(func):
        @functools.wraps(func)
        def wrapper(self, message, *args, **kwargs):
            color_message = f"{color_code}{message}\033[0m"
            return func(self, color_message, *args, **kwargs)
        return wrapper
    return decorator_log

