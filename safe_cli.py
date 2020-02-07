import argparse

from prompt_toolkit import HTML, PromptSession, print_formatted_text
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.shell import BashLexer
from safe_operator import SafeOperator

parser = argparse.ArgumentParser()
parser.add_argument('safe_address', help='Address of Safe to use')
parser.add_argument('infura_project_id', help='Infura Project id')
args = parser.parse_args()

safe_address = args.safe_address
infura_project_id = args.infura_project_id


session = PromptSession()
safe_commands = ['help', 'get_threshold', 'get_nonce', 'get_owners', 'load_cli_owner', 'unload_cli_owner',
                 'change_master_copy', 'show_cli_owners', 'add_owner', 'change_threshold', 'remove_owner', 'refresh']
safe_command_completer = WordCompleter(safe_commands, ignore_case=True)


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
    safe_operator = SafeOperator(safe_address, infura_project_id)
    while True:
        try:
            command = session.prompt(HTML(f'<bold><ansiblue>{safe_address}</ansiblue><ansired> > </ansired></bold>'),
                                     auto_suggest=AutoSuggestFromHistory(),
                                     bottom_toolbar=safe_operator.bottom_toolbar,
                                     lexer=PygmentsLexer(BashLexer),
                                     completer=safe_command_completer)
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        else:
            process_command(command, safe_operator)
