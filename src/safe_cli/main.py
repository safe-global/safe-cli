#!/bin/env python3
import sys
from typing import Annotated, List

import typer
from art import text2art
from eth_typing import ChecksumAddress
from hexbytes import HexBytes
from prompt_toolkit import HTML, print_formatted_text
from typer.main import get_command, get_command_name

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
    safe_address: ChecksumAddress, node_url: str, private_keys: List[str]
) -> SafeOperator:
    safe_operator = SafeOperator(safe_address, node_url, no_input=True)
    safe_operator.load_cli_owners(private_keys)
    return safe_operator


@app.command()
def send_ether(
    safe_address: Annotated[
        ChecksumAddress,
        typer.Argument(
            help="The address of the Safe.",
            callback=check_ethereum_address,
            click_type=ChecksumAddressParser(),
            show_default=False,
        ),
    ],
    node_url: Annotated[
        str, typer.Argument(help="Ethereum node url.", show_default=False)
    ],
    to: Annotated[
        ChecksumAddress,
        typer.Argument(
            help="The address of destination.",
            callback=check_ethereum_address,
            click_type=ChecksumAddressParser(),
            show_default=False,
        ),
    ],
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
):
    safe_operator = _build_safe_operator_and_load_keys(
        safe_address, node_url, private_key
    )
    safe_operator.send_ether(to, value, safe_nonce=safe_nonce)


@app.command()
def send_erc20(
    safe_address: Annotated[
        ChecksumAddress,
        typer.Argument(
            help="The address of the Safe.",
            callback=check_ethereum_address,
            click_type=ChecksumAddressParser(),
            show_default=False,
        ),
    ],
    node_url: Annotated[
        str, typer.Argument(help="Ethereum node url.", show_default=False)
    ],
    to: Annotated[
        ChecksumAddress,
        typer.Argument(
            help="The address of destination.",
            callback=check_ethereum_address,
            click_type=ChecksumAddressParser(),
            show_default=False,
        ),
    ],
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
):
    safe_operator = _build_safe_operator_and_load_keys(
        safe_address, node_url, private_key
    )
    safe_operator.send_erc20(to, token_address, amount, safe_nonce=safe_nonce)


@app.command()
def send_erc721(
    safe_address: Annotated[
        ChecksumAddress,
        typer.Argument(
            help="The address of the Safe.",
            callback=check_ethereum_address,
            click_type=ChecksumAddressParser(),
            show_default=False,
        ),
    ],
    node_url: Annotated[
        str, typer.Argument(help="Ethereum node url.", show_default=False)
    ],
    to: Annotated[
        ChecksumAddress,
        typer.Argument(
            help="The address of destination.",
            callback=check_ethereum_address,
            click_type=ChecksumAddressParser(),
            show_default=False,
        ),
    ],
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
):
    safe_operator = _build_safe_operator_and_load_keys(
        safe_address, node_url, private_key
    )
    safe_operator.send_erc721(to, token_address, token_id, safe_nonce=safe_nonce)


@app.command()
def send_custom(
    safe_address: Annotated[
        ChecksumAddress,
        typer.Argument(
            help="The address of the Safe.",
            callback=check_ethereum_address,
            click_type=ChecksumAddressParser(),
            show_default=False,
        ),
    ],
    node_url: Annotated[
        str, typer.Argument(help="Ethereum node url.", show_default=False)
    ],
    to: Annotated[
        ChecksumAddress,
        typer.Argument(
            help="The address of destination.",
            callback=check_ethereum_address,
            click_type=ChecksumAddressParser(),
            show_default=False,
        ),
    ],
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
):
    safe_operator = _build_safe_operator_and_load_keys(
        safe_address, node_url, private_key
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
            safe-cli send-ether 0xsafeaddress https://sepolia.drpc.org 0xtoaddress wei-amount --private-key key1 --private-key key1 --private-key keyN\n
            safe-cli send-erc721 0xsafeaddress https://sepolia.drpc.org 0xtoaddress 0xtokenaddres id --private-key key1 --private-key key2 --private-key keyN\n
            safe-cli send-erc20 0xsafeaddress https://sepolia.drpc.org 0xtoaddress 0xtokenaddres wei-amount --private-key key1 --private-key key2 --private-key keyN\n
            safe-cli send-custom 0xsafeaddress https://sepolia.drpc.org 0xtoaddress value 0xtxdata --private-key key1 --private-key key2 --private-key keyN\n\n\n\n
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
    node_url: Annotated[
        str, typer.Argument(help="Ethereum node url.", show_default=False)
    ],
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


def main():
    # By default, the attended mode is initialised. Otherwise, the required command must be specified.
    if len(sys.argv) == 1 or sys.argv[1] not in [
        get_command_name(key) for key in get_command(app).commands.keys()
    ]:
        sys.argv.insert(1, "attended-mode")
    app()
