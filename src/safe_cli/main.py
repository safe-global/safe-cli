#!/bin/env python3
import os
import sys
from typing import Annotated, List

import typer
from art import text2art
from eth_typing import ChecksumAddress
from hexbytes import HexBytes
from prompt_toolkit import HTML, print_formatted_text
from typer.main import get_command, get_command_name
from web3 import Web3

from . import VERSION
from .argparse_validators import check_hex_str
from .operators import SafeOperator
from .safe_cli import SafeCli
from .typer_validators import (
    ChecksumAddressParser,
    HexBytesParser,
    check_ethereum_address,
    check_private_keys,
)
from .utils import get_safe_from_owner

app = typer.Typer(name="Safe CLI")


def _build_safe_operator_and_load_keys(
    safe_address: ChecksumAddress,
    node_url: str,
    private_keys: List[str],
    interactive: bool,
) -> SafeOperator:
    safe_operator = SafeOperator(safe_address, node_url, interactive=interactive)
    safe_operator.load_cli_owners(private_keys)
    return safe_operator


def _check_interactive_mode(interactive_mode: bool) -> bool:
    if not interactive_mode:
        return False

    # --non-interactive arg > env var.
    env_var = os.getenv("SAFE_CLI_INTERACTIVE")
    if env_var:
        return env_var.lower() in ("true", "1", "yes")

    return True


# Common Options
safe_address_option = Annotated[
    ChecksumAddress,
    typer.Argument(
        help="The address of the Safe.",
        callback=check_ethereum_address,
        click_type=ChecksumAddressParser(),
        show_default=False,
    ),
]
node_url_option = Annotated[
    str, typer.Argument(help="Ethereum node url.", show_default=False)
]
to_option = Annotated[
    ChecksumAddress,
    typer.Argument(
        help="The address of destination.",
        callback=check_ethereum_address,
        click_type=ChecksumAddressParser(),
        show_default=False,
    ),
]
interactive_option = Annotated[
    bool,
    typer.Option(
        "--interactive/--non-interactive",
        help=(
            "Enable interactive mode to allow user input during execution. "
            "Use --non-interactive to disable prompts and run unattended. "
            "This is useful for scripting and automation where no user intervention is required."
        ),
        rich_help_panel="Optional Arguments",
        callback=_check_interactive_mode,
    ),
]


@app.command()
def send_ether(
    safe_address: safe_address_option,
    node_url: node_url_option,
    to: to_option,
    value: Annotated[
        int, typer.Argument(help="Amount of ether in wei to send.", show_default=False)
    ],
    private_key: Annotated[
        List[str],
        typer.Option(
            help="List of private keys of signers.",
            rich_help_panel="Optional Arguments",
            show_default=False,
            callback=check_private_keys,
        ),
    ] = None,
    safe_nonce: Annotated[
        int,
        typer.Option(
            help="Force nonce for tx_sender",
            rich_help_panel="Optional Arguments",
            show_default=False,
        ),
    ] = None,
    interactive: interactive_option = True,
):
    safe_operator = _build_safe_operator_and_load_keys(
        safe_address, node_url, private_key, interactive
    )
    safe_operator.send_ether(to, value, safe_nonce=safe_nonce)


@app.command()
def send_erc20(
    safe_address: safe_address_option,
    node_url: node_url_option,
    to: to_option,
    token_address: Annotated[
        ChecksumAddress,
        typer.Argument(
            help="Erc20 token address.",
            callback=check_ethereum_address,
            click_type=ChecksumAddressParser(),
            show_default=False,
        ),
    ],
    amount: Annotated[
        int,
        typer.Argument(
            help="Amount of erc20 tokens in wei to send.", show_default=False
        ),
    ],
    private_key: Annotated[
        List[str],
        typer.Option(
            help="List of private keys of signers.",
            rich_help_panel="Optional Arguments",
            show_default=False,
            callback=check_private_keys,
        ),
    ] = None,
    safe_nonce: Annotated[
        int,
        typer.Option(
            help="Force nonce for tx_sender",
            rich_help_panel="Optional Arguments",
            show_default=False,
        ),
    ] = None,
    interactive: interactive_option = True,
):
    safe_operator = _build_safe_operator_and_load_keys(
        safe_address, node_url, private_key, interactive
    )
    safe_operator.send_erc20(to, token_address, amount, safe_nonce=safe_nonce)


@app.command()
def send_erc721(
    safe_address: safe_address_option,
    node_url: node_url_option,
    to: to_option,
    token_address: Annotated[
        ChecksumAddress,
        typer.Argument(
            help="Erc721 token address.",
            callback=check_ethereum_address,
            click_type=ChecksumAddressParser(),
            show_default=False,
        ),
    ],
    token_id: Annotated[
        int, typer.Argument(help="Erc721 token id.", show_default=False)
    ],
    private_key: Annotated[
        List[str],
        typer.Option(
            help="List of private keys of signers.",
            rich_help_panel="Optional Arguments",
            show_default=False,
            callback=check_private_keys,
        ),
    ] = None,
    safe_nonce: Annotated[
        int,
        typer.Option(
            help="Force nonce for tx_sender",
            rich_help_panel="Optional Arguments",
            show_default=False,
        ),
    ] = None,
    interactive: interactive_option = True,
):
    safe_operator = _build_safe_operator_and_load_keys(
        safe_address, node_url, private_key, interactive
    )
    safe_operator.send_erc721(to, token_address, token_id, safe_nonce=safe_nonce)


@app.command()
def send_custom(
    safe_address: safe_address_option,
    node_url: node_url_option,
    to: to_option,
    value: Annotated[int, typer.Argument(help="Value to send.", show_default=False)],
    data: Annotated[
        HexBytes,
        typer.Argument(
            help="HexBytes data to send.",
            callback=check_hex_str,
            click_type=HexBytesParser(),
            show_default=False,
        ),
    ],
    private_key: Annotated[
        List[str],
        typer.Option(
            help="List of private keys of signers.",
            rich_help_panel="Optional Arguments",
            show_default=False,
            callback=check_private_keys,
        ),
    ] = None,
    safe_nonce: Annotated[
        int,
        typer.Option(
            help="Force nonce for tx_sender",
            rich_help_panel="Optional Arguments",
            show_default=False,
        ),
    ] = None,
    delegate: Annotated[
        bool,
        typer.Option(
            help="Use DELEGATE_CALL. By default use CALL",
            rich_help_panel="Optional Arguments",
        ),
    ] = False,
    interactive: interactive_option = True,
):
    safe_operator = _build_safe_operator_and_load_keys(
        safe_address, node_url, private_key, interactive
    )
    safe_operator.send_custom(
        to, value, data, safe_nonce=safe_nonce, delegate_call=delegate
    )


@app.command()
def version():
    print(f"Safe Cli v{VERSION}")


@app.command(
    hidden=True,
    name="attended-mode",
    help="""
        safe-cli [--history] [--get-safes-from-owner] address node_url\n
        Examples:\n
            safe-cli 0x0000000000000000000000000000000000000000 https://sepolia.drpc.org\n
            safe-cli --get-safes-from-owner 0x0000000000000000000000000000000000000000 https://sepolia.drpc.org\n\n\n\n
            safe-cli --history 0x0000000000000000000000000000000000000000 https://sepolia.drpc.org\n
            safe-cli --history --get-safes-from-owner 0x0000000000000000000000000000000000000000 https://sepolia.drpc.org\n\n\n\n
            safe-cli send-ether 0xsafeaddress https://sepolia.drpc.org 0xtoaddress wei-amount --private-key key1 --private-key key1 --private-key keyN [--non-interactive]\n
            safe-cli send-erc721 0xsafeaddress https://sepolia.drpc.org 0xtoaddress 0xtokenaddres id --private-key key1 --private-key key2 --private-key keyN [--non-interactive]\n
            safe-cli send-erc20 0xsafeaddress https://sepolia.drpc.org 0xtoaddress 0xtokenaddres wei-amount --private-key key1 --private-key key2 --private-key keyN [--non-interactive]\n
            safe-cli send-custom 0xsafeaddress https://sepolia.drpc.org 0xtoaddress value 0xtxdata --private-key key1 --private-key key2 --private-key keyN [--non-interactive]\n\n\n\n
    """,
    epilog="Commands available in unattended mode:\n\n\n\n"
    + "\n\n".join(
        [
            f"  {get_command_name(command)}"
            for command in get_command(app).commands.keys()
        ]
    )
    + "\n\n\n\nUse the --help option of each command to see the usage options.",
)
def default_attended_mode(
    address: Annotated[
        ChecksumAddress,
        typer.Argument(
            help="The address of the Safe, or an owner address if --get-safes-from-owner is specified.",
            callback=check_ethereum_address,
            click_type=ChecksumAddressParser(),
            show_default=False,
        ),
    ],
    node_url: node_url_option,
    history: Annotated[
        bool,
        typer.Option(
            help="Enable history. By default it's disabled due to security reasons",
            rich_help_panel="Optional Arguments",
        ),
    ] = False,
    get_safes_from_owner: Annotated[
        bool,
        typer.Option(
            help="Indicates that address is an owner (Safe Transaction Service is required for this feature)",
            rich_help_panel="Optional Arguments",
        ),
    ] = False,
) -> None:
    print_formatted_text(text2art("Safe CLI"))  # Print fancy text
    print_formatted_text(HTML(f"<b>Version: {VERSION}</b>"))

    if get_safes_from_owner:
        safe_address_listed = get_safe_from_owner(address, node_url)
        safe_cli = SafeCli(safe_address_listed, node_url, history)
    else:
        safe_cli = SafeCli(address, node_url, history)
    safe_cli.print_startup_info()
    safe_cli.loop()


def _is_safe_cli_default_command(arguments: List[str]) -> bool:
    # safe-cli
    if len(sys.argv) == 1:
        return True

    if sys.argv[1] == "--help":
        return True

    # Only added if is not a valid command, and it is an address. safe-cli 0xaddress http://url
    if sys.argv[1] not in [
        get_command_name(key) for key in get_command(app).commands.keys()
    ] and Web3.is_checksum_address(sys.argv[1]):
        return True

    return False


def main():
    # By default, the attended mode is initialised. Otherwise, the required command must be specified.
    if _is_safe_cli_default_command(sys.argv):
        sys.argv.insert(1, "attended-mode")
    app()
