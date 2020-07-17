import argparse

import pyfiglet
from prompt_toolkit import HTML, PromptSession, print_formatted_text
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.lexers import PygmentsLexer

from safe_cli.prompt_parser import PromptParser
from safe_cli.safe_completer import SafeCompleter
from safe_cli.safe_lexer import SafeLexer
from safe_cli.safe_operator import SafeOperator

parser = argparse.ArgumentParser()
parser.add_argument('safe_address', help='Address of Safe to use')
parser.add_argument('node_url', help='Ethereum node url')
args = parser.parse_args()

safe_address = args.safe_address
node_url = args.node_url


session = PromptSession()

if __name__ == '__main__':
    safe_operator = SafeOperator(safe_address, node_url)
    print_formatted_text(pyfiglet.figlet_format('Gnosis Safe CLI'))  # Print fancy text
    print_formatted_text(HTML(f'<b><ansigreen>Loading Safe information...</ansigreen></b>'))
    safe_operator.print_info()
    prompt_parser = PromptParser(safe_operator)

    def get_prompt_text():
        return HTML(f'<bold><ansiblue>{safe_address}</ansiblue><ansired> > </ansired></bold>')

    def bottom_toolbar():
        return HTML(f'<b><style fg="ansiyellow">network={safe_operator.network_name} '
                    f'{safe_operator.safe_cli_info}</style></b>')

    while True:
        try:
            command = session.prompt(get_prompt_text,
                                     auto_suggest=AutoSuggestFromHistory(),
                                     bottom_toolbar=bottom_toolbar,
                                     lexer=PygmentsLexer(SafeLexer),
                                     completer=SafeCompleter())
            if not command.strip():
                continue

            prompt_parser.process_command(command)
        except EOFError:
            break
        except KeyboardInterrupt:
            continue
        except (argparse.ArgumentError, argparse.ArgumentTypeError, SystemExit):
            pass  # FIXME
