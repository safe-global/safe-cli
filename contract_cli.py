import argparse

import pyfiglet
from prompt_toolkit import HTML, PromptSession, print_formatted_text
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.lexers import PygmentsLexer
from safe_completer_constants import safe_commands
from prompt_toolkit.completion import WordCompleter
from contract_operator import ContractOperator
from contract_lexer import ContractLexer
from web3 import Web3
from typing import List, Optional, Type, Dict
from web3.contract import Contract
parser = argparse.ArgumentParser()
parser.add_argument('contract_address', help='Address of Contract to use', default=None)
parser.add_argument('contract_abi', help='ABI of Contract to use')
args = parser.parse_args()

contract_address = args.contract_address
contract_abi = args.contract_abi
test_path = './GnosisSafeV1.1.1.json'

print(contract_address, contract_abi)
session = PromptSession()


def process_command(command: str, contract_operator: ContractOperator,
                    contract: Type[Contract], contract_methods: Dict, execution_type: List[bool]):
    if not command:
        return

    commands = command.strip().split()
    first_command = commands[0].lower()
    rest_command = commands[1:]
    try:
        # Access to the instance will be needed here, to be dispatched to the ContractOperator
        # Call
        if execution_type[0]:
            print(first_command, rest_command, execution_type)
            contract_operator.call(first_command, rest_command, contract, contract_methods)
        # Transact
        elif execution_type[1]:
            contract_operator.transact(first_command, rest_command, contract, contract_methods)
        # Queue
        elif execution_type[2]:
            print('?')
        return True
    except Exception as err:
        print(type(err), err)


if __name__ == '__main__':
    contract_operator = ContractOperator()
    print_formatted_text(pyfiglet.figlet_format('Gnosis Safe CLI'))
    # process_command('info', safe_operator)
    contract, contract_methods = contract_operator.load(contract_abi, contract_address)
    command_names = []
    # Call, Transact, Queue
    execution_type = [True, False, False]
    for method in contract_methods:
        command_names.append(contract_methods[method]['name'])
    # Fixme: the default commands needs to be read from temp, to make it part of the contract_lexer flow,
    #  so it can be used
    # contract_lexer = ContractLexer.contract_keywords = set(command_names)

    while True:
        try:
            command = session.prompt(HTML(f'<bold><ansiblue>{contract_address}</ansiblue><ansired> > </ansired></bold>'),
                                     auto_suggest=AutoSuggestFromHistory(),
                                     lexer=PygmentsLexer(ContractLexer),
                                     completer=WordCompleter(command_names))
            if not command.strip():
                continue

            # args = prompt_parser.parse_args(command.split())

            process_command(command, contract_operator, contract, contract_methods, execution_type)
        except EOFError:
            break
        except KeyboardInterrupt:
            continue
        except (argparse.ArgumentError, argparse.ArgumentTypeError, SystemExit):  # FIXME
            continue
