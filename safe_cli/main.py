#!/bin/env python3
import argparse
import os
import sys
from typing import Optional

import pyfiglet
from prompt_toolkit import HTML, PromptSession, print_formatted_text
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import PygmentsLexer
from web3 import Web3

from safe_cli.operators import (
    SafeOperator,
    SafeRelayOperator,
    SafeServiceNotAvailable,
    SafeTxServiceOperator,
)
from safe_cli.prompt_parser import PromptParser, to_checksummed_ethereum_address
from safe_cli.safe_completer import SafeCompleter
from safe_cli.safe_lexer import SafeLexer

from .version import version

parser = argparse.ArgumentParser()
parser.add_argument(
    "safe_address", help="Address of Safe to use", type=to_checksummed_ethereum_address
)
parser.add_argument("node_url", help="Ethereum node url")
parser.add_argument(
    "--history",
    action="store_true",
    help="Enable history. By default it's disabled due to security reasons",
)

args = parser.parse_args()

safe_address = args.safe_address
node_url = args.node_url
history = args.history


class SafeCli:
    def __init__(self):
        if history:
            self.session = PromptSession(
                history=FileHistory(os.path.join(sys.path[0], ".history"))
            )
        else:
            self.session = PromptSession()
        self.safe_operator = SafeOperator(safe_address, node_url)
        self.prompt_parser = PromptParser(self.safe_operator)

    def print_startup_info(self):
        print_formatted_text(
            pyfiglet.figlet_format("Gnosis Safe CLI")
        )  # Print fancy text
        print_formatted_text(HTML(f"<b><ansigreen>Version {version}</ansigreen></b>"))
        print_formatted_text(
            HTML("<b><ansigreen>Loading Safe information...</ansigreen></b>")
        )
        self.safe_operator.print_info()

    def get_prompt_text(self):
        if isinstance(self.prompt_parser.safe_operator, SafeRelayOperator):
            return HTML(
                f"<bold><ansiblue>relay-service > {safe_address}</ansiblue><ansired> > </ansired></bold>"
            )
        elif isinstance(self.prompt_parser.safe_operator, SafeTxServiceOperator):
            return HTML(
                f"<bold><ansiblue>tx-service > {safe_address}</ansiblue><ansired> > </ansired></bold>"
            )
        elif isinstance(self.prompt_parser.safe_operator, SafeOperator):
            return HTML(
                f"<bold><ansiblue>blockchain > {safe_address}</ansiblue><ansired> > </ansired></bold>"
            )

    def get_bottom_toolbar(self):
        return HTML(
            f'<b><style fg="ansiyellow">network={self.safe_operator.network.name} '
            f"{self.safe_operator.safe_cli_info}</style></b>"
        )

    def parse_operator_mode(self, command: str) -> Optional[SafeOperator]:
        """
        Parse operator mode to switch between blockchain (default), relay-service, and tx-service
        :param command:
        :return: SafeOperator if detected
        """
        split_command = command.split()
        try:
            if (split_command[0]) == "tx-service":
                print_formatted_text(
                    HTML("<b><ansigreen>Sending txs to tx service</ansigreen></b>")
                )
                return SafeTxServiceOperator(safe_address, node_url)
            elif split_command[0] == "relay-service":
                if len(split_command) == 2 and Web3.isChecksumAddress(split_command[1]):
                    gas_token = split_command[1]
                else:
                    gas_token = None
                print_formatted_text(
                    HTML(
                        f"<b><ansigreen>Sending txs trough relay service gas-token={gas_token}</ansigreen></b>"
                    )
                )
                return SafeRelayOperator(safe_address, node_url, gas_token=gas_token)
            elif split_command[0] == "blockchain":
                print_formatted_text(
                    HTML("<b><ansigreen>Sending txs to blockchain</ansigreen></b>")
                )
                return self.safe_operator
        except SafeServiceNotAvailable:
            print_formatted_text(
                HTML("<b><ansired>Mode not supported on this network</ansired></b>")
            )

    def loop(self):
        while True:
            try:
                command = self.session.prompt(
                    self.get_prompt_text,
                    auto_suggest=AutoSuggestFromHistory(),
                    bottom_toolbar=self.get_bottom_toolbar,
                    lexer=PygmentsLexer(SafeLexer),
                    completer=SafeCompleter(),
                )
                if not command.strip():
                    continue

                new_operator = self.parse_operator_mode(command)
                if new_operator:
                    self.prompt_parser = PromptParser(new_operator)
                    new_operator.refresh_safe_cli_info()  # ClI info needs to be initialized
                else:
                    self.prompt_parser.process_command(command)
            except EOFError:
                break
            except KeyboardInterrupt:
                continue
            except (argparse.ArgumentError, argparse.ArgumentTypeError, SystemExit):
                pass


def main(*args, **kwgars):
    """
    Entry point for the Safe-CLI
    """
    safe_cli = SafeCli()
    safe_cli.print_startup_info()
    safe_cli.loop()


if __name__ == "__main__":
    main()
