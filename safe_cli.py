import argparse
from typing import List

from eth_account import Account
from prompt_toolkit import HTML, PromptSession, print_formatted_text
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.shell import BashLexer
from safe_operator import SafeOperator

from gnosis.eth import EthereumClient
from gnosis.safe import Safe

parser = argparse.ArgumentParser()
parser.add_argument('safe_address', help='Address of Safe to use')
parser.add_argument('infura_project_id', help='Infura Project id')
args = parser.parse_args()

safe_address = args.safe_address
infura_project_id = args.infura_project_id
safe_operator = SafeOperator(safe_address, infura_project_id)


session = PromptSession()
safe_commands = ['help', 'get_threshold', 'get_nonce', 'get_owners', 'load_cli_owner', 'unload_cli_owner',
                 'show_cli_owners', 'add_owner', 'change_threshold', 'remove_owner', 'refresh']
safe_command_completer = WordCompleter(safe_commands, ignore_case=True)


def bottom_toolbar():
    return HTML(f'nonce=Safe-Cli <b><style bg="ansired">v0.0.1</style></b>!')


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
        if not command:
            continue

        commands = command.strip().split()
        first_command = commands[0].lower()
        rest_command = commands[1:]

        if first_command not in safe_commands:
            print_formatted_text('I still cannot help you')
        else:
            if first_command == 'help':
                print_formatted_text('I still cannot help you')
            else:
                safe_operator.process_command(first_command, rest_command)
