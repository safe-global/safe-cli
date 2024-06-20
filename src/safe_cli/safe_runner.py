#!/bin/env python3
import json
from pathlib import Path
from typing import Annotated, List

import typer
from eth_typing import ChecksumAddress
from hexbytes import HexBytes

from safe_cli import VERSION
from safe_cli.argparse_validators import check_hex_str
from safe_cli.operators import SafeOperator
from safe_cli.tx_builder.tx_builder_file_decoder import convert_to_proposed_transactions
from safe_cli.typer_validators import (
    check_ethereum_address,
    check_private_keys,
    parse_checksum_address,
    parse_hex_str,
)

app = typer.Typer()


def _build_safe_operator(
    safe_address: ChecksumAddress, node_url: str, private_keys: List[str]
) -> SafeOperator:
    safe_operator = SafeOperator(safe_address, node_url, script_mode=True)
    safe_operator.load_cli_owners(private_keys)
    return safe_operator


@app.command()
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
    safe_operator = _build_safe_operator(safe_address, node_url, private_key)
    safe_operator.send_ether(to, value, safe_nonce=safe_nonce)


@app.command()
def send_erc20(
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
    token_address: Annotated[
        ChecksumAddress,
        typer.Argument(
            help="Erc20 token address.",
            callback=check_ethereum_address,
            parser=parse_checksum_address,
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
    safe_operator = _build_safe_operator(safe_address, node_url, private_key)
    safe_operator.send_erc20(to, token_address, amount, safe_nonce=safe_nonce)


@app.command()
def send_erc721(
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
    token_address: Annotated[
        ChecksumAddress,
        typer.Argument(
            help="Erc721 token address.",
            callback=check_ethereum_address,
            parser=parse_checksum_address,
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
    safe_operator = _build_safe_operator(safe_address, node_url, private_key)
    safe_operator.send_erc721(to, token_address, token_id, safe_nonce=safe_nonce)


@app.command()
def send_custom(
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
    value: Annotated[int, typer.Argument(help="Value to send.", show_default=False)],
    data: Annotated[
        HexBytes,
        typer.Argument(
            help="HexBytes data to send.",
            callback=check_hex_str,
            parser=parse_hex_str,
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
    safe_operator = _build_safe_operator(safe_address, node_url, private_key)
    safe_operator.send_custom(
        to, value, data, safe_nonce=safe_nonce, delegate_call=delegate
    )


@app.command()
def tx_builder(
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
    file_path: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
            help="File path with tx_builder data.",
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
):
    safe_operator = _build_safe_operator(safe_address, node_url, private_key)
    data = json.loads(file_path.read_text())
    safe_txs = []
    for tx in convert_to_proposed_transactions(data):
        safe_txs.append(
            safe_operator.prepare_safe_transaction(tx.to, tx.value, tx.data)
        )

    if len(safe_txs) == 0:
        raise typer.BadParameter("No transactions found.")

    if len(safe_txs) == 1:
        safe_operator.execute_safe_transaction(safe_txs[0])
        return

    multisend_tx = safe_operator.batch_safe_txs(safe_operator.get_nonce(), safe_txs)
    if multisend_tx is not None:
        safe_operator.execute_safe_transaction(multisend_tx)


@app.command()
def version():
    print(f"Safe Runner v{VERSION}")


def main():
    app()
