import argparse

import pyfiglet
from prompt_parser import get_prompt_parser
from prompt_toolkit import HTML, PromptSession, print_formatted_text
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.lexers import PygmentsLexer
from safe_completer import SafeCompleter
from safe_completer_constants import safe_commands
from safe_lexer import SafeLexer
from safe_operator import SafeOperator

parser = argparse.ArgumentParser()
parser.add_argument('safe_address', help='Address of Safe to use')
parser.add_argument('node_url', help='Ethereum node url')
args = parser.parse_args()

safe_address = args.safe_address
node_url = args.node_url


session = PromptSession()


def process_command(command: str, safe_operator: SafeOperator):
    if not command:
        return

    commands = command.strip().split()
    first_command = commands[0].lower()
    rest_command = commands[1:]

    if first_command not in safe_commands:
        print_formatted_text(HTML(f'<b><ansired>Use a command in the list:</ansired></b> '
                                  f'<ansigreen>{safe_commands}</ansigreen>'))
    else:
        if first_command == 'help':
            print_formatted_text('I still cannot help you')
        else:
            return safe_operator.process_command(first_command, rest_command)


if __name__ == '__main__':
    safe_operator = SafeOperator(safe_address, node_url)
    print_formatted_text(pyfiglet.figlet_format('Gnosis Safe CLI'))
    safe_operator.print_info()

    # Test parsers
    prompt_parser = get_prompt_parser(safe_operator)

    while True:
        try:
            command = session.prompt(HTML(f'<bold><ansiblue>{safe_address}</ansiblue><ansired> > </ansired></bold>'),
                                     auto_suggest=AutoSuggestFromHistory(),
                                     bottom_toolbar=safe_operator.bottom_toolbar,
                                     lexer=PygmentsLexer(SafeLexer),
                                     completer=SafeCompleter())
            if not command.strip():
                continue

            args = prompt_parser.parse_args(command.split())
            args.func(args)
        except EOFError:
            break
        except KeyboardInterrupt:
            continue
        except (argparse.ArgumentError, argparse.ArgumentTypeError, SystemExit):  # FIXME
            process_command(command, safe_operator)
