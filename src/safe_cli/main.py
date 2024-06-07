#!/bin/env python3
import argparse
import os
import sys
from typing import Optional

from art import text2art
from eth_typing import ChecksumAddress
from prompt_toolkit import HTML, PromptSession, print_formatted_text
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import PygmentsLexer

from safe_cli.argparse_validators import check_ethereum_address
from safe_cli.operators import (
    SafeOperator,
    SafeServiceNotAvailable,
    SafeTxServiceOperator,
)
from safe_cli.prompt_parser import PromptParser
from safe_cli.safe_completer import SafeCompleter
from safe_cli.safe_lexer import SafeLexer
from safe_cli.utils import get_safe_from_owner

from . import VERSION


class SafeCli:
    def __init__(self, safe_address: ChecksumAddress, node_url: str, history: bool):
        """
        :param safe_address: Safe address
        :param node_url: Ethereum RPC url
        :param history: If `True` keep command history, otherwise history is not kept after closing the CLI
        """
        self.safe_address = safe_address
        self.node_url = node_url
        if history:
            self.session = PromptSession(
                history=FileHistory(os.path.join(sys.path[0], ".history"))
            )
        else:
            self.session = PromptSession()
        self.safe_operator = SafeOperator(safe_address, node_url)
        self.prompt_parser = PromptParser(self.safe_operator)

    def print_startup_info(self):
        print_formatted_text(text2art("Safe CLI"))  # Print fancy text
        print_formatted_text(HTML(f"<b><ansigreen>Version {VERSION}</ansigreen></b>"))
        print_formatted_text(
            HTML("<b><ansigreen>Loading Safe information...</ansigreen></b>")
        )
        self.safe_operator.print_info()

    def get_prompt_text(self):
        mode: Optional[str] = "blockchain"
        if isinstance(self.prompt_parser.safe_operator, SafeTxServiceOperator):
            mode = "tx-service"

        return HTML(
            f"<bold><ansiblue>{mode} > {self.safe_address}</ansiblue><ansired> > </ansired></bold>"
        )

    def get_bottom_toolbar(self):
        return HTML(
            f'<b><style fg="ansiyellow">network={self.safe_operator.network.name} '
            f"{self.safe_operator.safe_cli_info}</style></b>"
        )

    def parse_operator_mode(self, command: str) -> Optional[SafeOperator]:
        """
        Parse operator mode to switch between blockchain (default) and tx-service
        :param command:
        :return: SafeOperator if detected
        """
        split_command = command.split()
        try:
            if (split_command[0]) == "tx-service":
                print_formatted_text(
                    HTML("<b><ansigreen>Sending txs to tx service</ansigreen></b>")
                )
                return SafeTxServiceOperator(self.safe_address, self.node_url)
            elif split_command[0] == "blockchain":
                print_formatted_text(
                    HTML("<b><ansigreen>Sending txs to blockchain</ansigreen></b>")
                )
                return self.safe_operator
        except SafeServiceNotAvailable:
            print_formatted_text(
                HTML("<b><ansired>Mode not supported on this network</ansired></b>")
            )

    def get_command(self) -> str:
        return self.session.prompt(
            self.get_prompt_text,
            auto_suggest=AutoSuggestFromHistory(),
            bottom_toolbar=self.get_bottom_toolbar,
            lexer=PygmentsLexer(SafeLexer),
            completer=SafeCompleter(),
        )

    def loop(self):
        while True:
            try:
                command = self.get_command()
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


def build_safe_cli() -> Optional[SafeCli]:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "address",
        help="The address of the Safe, or an owner address if --get-safes-from-owner is specified.",
        type=check_ethereum_address,
    )
    parser.add_argument("node_url", help="Ethereum node url")
    parser.add_argument(
        "--history",
        action="store_true",
        help="Enable history. By default it's disabled due to security reasons",
        default=False,
    )
    parser.add_argument(
        "--get-safes-from-owner",
        action="store_true",
        help="Indicates that address is an owner (Safe Transaction Service is required for this feature)",
        default=False,
    )

    args = parser.parse_args()
    if args.get_safes_from_owner:
        if (
            safe_address := get_safe_from_owner(args.address, args.node_url)
        ) is not None:
            return SafeCli(safe_address, args.node_url, args.history)
    else:
        return SafeCli(args.address, args.node_url, args.history)


def main(*args, **kwargs):
    safe_cli = build_safe_cli()
    safe_cli.print_startup_info()
    safe_cli.loop()


if __name__ == "__main__":
    main()
