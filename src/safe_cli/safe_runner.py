from typing import Annotated, List

import typer
from eth_typing import ChecksumAddress

from safe_cli.operators import SafeOperator
from safe_cli.prompt_parser import safe_exception
from safe_cli.typer_validators import (
    check_ethereum_address,
    check_private_keys,
    parse_checksum_address,
)

app = typer.Typer()


@app.command()
@safe_exception
def send_ether(
    safe_address: Annotated[
        ChecksumAddress,
        typer.Argument(
            help="The address of the Safe.",
            callback=check_ethereum_address,
            parser=parse_checksum_address,
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
            parser=parse_checksum_address,
            show_default=False,
        ),
    ],
    value: Annotated[int, typer.Argument(help="Amount to send.", show_default=False)],
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
    safe_operator = SafeOperator(safe_address, node_url, batch_mode=True)
    safe_operator.load_cli_owners(private_key)
    safe_operator.send_ether(to, value, safe_nonce=safe_nonce)


@app.command()
def test():
    print("Test")


def main():
    app()
