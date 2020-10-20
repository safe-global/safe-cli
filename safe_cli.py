import argparse
import os
import sys

import pyfiglet
from prompt_toolkit import HTML, PromptSession, print_formatted_text
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import PygmentsLexer

from safe_cli.prompt_parser import PromptParser
from safe_cli.safe_completer import SafeCompleter
from safe_cli.safe_lexer import SafeLexer
from safe_cli.safe_operator import SafeOperator

parser = argparse.ArgumentParser()
parser.add_argument('safe_address', help='Address of Safe to use')
parser.add_argument('node_url', help='Ethereum node url')
parser.add_argument('--history', action='store_true',
                    help="Enable history. By default it's disabled due to security reasons")
args = parser.parse_args()

safe_address = args.safe_address
node_url = args.node_url
history = args.history


class SafeCli:
    def __init__(self):
        if history:
            self.session = PromptSession(history=FileHistory(os.path.join(sys.path[0], '.history')))
        else:
            self.session = PromptSession()
        self.safe_operator = SafeOperator(safe_address, node_url)
        self.prompt_parser = PromptParser(self.safe_operator)

    def print_startup_info(self):
        print_formatted_text(pyfiglet.figlet_format('Gnosis Safe CLI'))  # Print fancy text
        print_formatted_text(HTML(f'<b><ansigreen>Loading Safe information...</ansigreen></b>'))
        self.safe_operator.print_info()

    def get_prompt_text(self):
        return HTML(f'<bold><ansiblue>{safe_address}</ansiblue><ansired> > </ansired></bold>')

    def get_bottom_toolbar(self):
        return HTML(f'<b><style fg="ansiyellow">network={self.safe_operator.network_name} '
                    f'{self.safe_operator.safe_cli_info}</style></b>')

    def loop(self):
        while True:
            try:
                command = self.session.prompt(self.get_prompt_text,
                                              auto_suggest=AutoSuggestFromHistory(),
                                              bottom_toolbar=self.get_bottom_toolbar,
                                              lexer=PygmentsLexer(SafeLexer),
                                              completer=SafeCompleter())
                if not command.strip():
                    continue

                self.prompt_parser.process_command(command)
            except EOFError:
                break
            except KeyboardInterrupt:
                continue
            except (argparse.ArgumentError, argparse.ArgumentTypeError, SystemExit):
                pass


if __name__ == '__main__':
    safe_cli = SafeCli()
    safe_cli.print_startup_info()
    safe_cli.loop()
