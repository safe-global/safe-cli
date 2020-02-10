import argparse

from prompt_toolkit import HTML, PromptSession, print_formatted_text
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.shell import BashLexer
from safe_operator import SafeOperator
from safe_completer import SafeCompleter
from safe_completer_constants import safe_commands

parser = argparse.ArgumentParser()
parser.add_argument('safe_address', help='Address of Safe to use')
parser.add_argument('node_url', help='Ethereum node url')
args = parser.parse_args()

safe_address = args.safe_address
node_url = args.node_url


session = PromptSession()


# TODO Auto load owners (e.g. if in PRIVATE_KEYS environment var)

def process_command(command: str, safe_operator: SafeOperator):
    if not command:
        return

    commands = command.strip().split()
    first_command = commands[0].lower()
    rest_command = commands[1:]

    if first_command not in safe_commands:
        print_formatted_text(f'Use a command in the list <ansired>{safe_commands}</ansired>')
    else:
        if first_command == 'help':
            print_formatted_text('I still cannot help you')
        else:
            return safe_operator.process_command(first_command, rest_command)


if __name__ == '__main__':
    safe_operator = SafeOperator(safe_address, node_url)
    while True:
        try:
            command = session.prompt(HTML(f'<bold><ansiblue>{safe_address}</ansiblue><ansired> > </ansired></bold>'),
                                     auto_suggest=AutoSuggestFromHistory(),
                                     bottom_toolbar=safe_operator.bottom_toolbar,
                                     lexer=PygmentsLexer(BashLexer),
                                     completer=SafeCompleter())
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        else:
            process_command(command, safe_operator)
