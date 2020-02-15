import argparse

from prompt_toolkit import HTML, PromptSession, print_formatted_text
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.lexers import PygmentsLexer
from safe_completer import SafeCompleter
from safe_completer_constants import safe_commands
from safe_lexer import SafeLexer
from safe_operator import SafeOperator
from web3 import Web3

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
        print_formatted_text(HTML(f'<b><ansired>Use a command in the list:</ansired></b> '
                                  f'<ansigreen>{safe_commands}</ansigreen>'))
    else:
        if first_command == 'help':
            print_formatted_text('I still cannot help you')
        else:
            return safe_operator.process_command(first_command, rest_command)


def check_ethereum_address(address: str) -> bool:
    if not Web3.isChecksumAddress(address):
        raise argparse.ArgumentTypeError(f'{address} is not a valid checksummed ethereum address')
    return address


if __name__ == '__main__':
    safe_operator = SafeOperator(safe_address, node_url)

    def send_ether(args):
        safe_operator.send_ether(args.address, args.value)

    # Test parsers
    prompt_parser = argparse.ArgumentParser(prog='')
    subparsers = prompt_parser.add_subparsers()
    parser_send_ether = subparsers.add_parser('send_ether')
    parser_send_ether.add_argument('address', type=check_ethereum_address)
    parser_send_ether.add_argument('value', type=int)
    parser_send_ether.set_defaults(func=send_ether)

    while True:
        try:
            command = session.prompt(HTML(f'<bold><ansiblue>{safe_address}</ansiblue><ansired> > </ansired></bold>'),
                                     auto_suggest=AutoSuggestFromHistory(),
                                     bottom_toolbar=safe_operator.bottom_toolbar,
                                     lexer=PygmentsLexer(SafeLexer),
                                     completer=SafeCompleter())
            if not command.strip():
                continue

            # args = prompt_parser.parse_args(command.split())
            # args.func(args)
            process_command(command, safe_operator)
        except EOFError:
            break
        except KeyboardInterrupt:
            continue
        except (argparse.ArgumentError, argparse.ArgumentTypeError, SystemExit):  # FIXME
            process_command(command, safe_operator)
