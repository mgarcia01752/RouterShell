from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion

class NATCompleter(Completer):
    def __init__(self):
        self.commands = {
            'nat': {
                'pool': {
                    '<pool-name>': {
                        '[inside|outside]': ['inside', 'outside'],
                        'source': {
                            'list': {
                                '<access-control-list-id>': []
                            }
                        }
                    }
                }
            }
        }
        self.variable_params = {
            '<pool-name>': ['pool1', 'pool2', 'pool3'],  # Example values for pool-name
            '<access-control-list-id>': ['acl1', 'acl2', 'acl3']  # Example values for access-control-list-id
        }

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.strip()
        words = text.split()

        if not words:
            # Provide initial command suggestions (e.g., 'nat')
            for cmd in self.commands.keys():
                yield Completion(cmd, start_position=0)
            return

        # Traverse the command hierarchy based on user input
        options = self.commands
        for i, word in enumerate(words):
            if word in options:
                options = options[word]
            elif any(param in options for param in self.variable_params):
                # Handle variable parameters
                for param in self.variable_params:
                    if param in options:
                        options = options[param]
                        break
            else:
                options = None
                break

        # Provide suggestions for the current word
        if options:
            current_word = words[-1]
            if isinstance(options, dict):
                for option in options.keys():
                    if option.startswith(current_word):
                        yield Completion(option, start_position=-len(current_word))
                # Provide variable parameter suggestions if applicable
                for param in self.variable_params:
                    if param in options:
                        for value in self.variable_params[param]:
                            if value.startswith(current_word):
                                yield Completion(value, start_position=-len(current_word))
            elif isinstance(options, list):
                for option in options:
                    if option.startswith(current_word):
                        yield Completion(option, start_position=-len(current_word))

def main():
    completer = NATCompleter()
    session = PromptSession(completer=completer)

    while True:
        try:
            text = session.prompt('> ')
            print(f'You entered: {text}')
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

if __name__ == '__main__':
    main()
