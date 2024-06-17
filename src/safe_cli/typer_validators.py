from binascii import Error
from typing import List

import typer
from eth_account import Account
from eth_typing import ChecksumAddress
from web3 import Web3


def check_ethereum_address(address: str) -> ChecksumAddress:
    """
    Ethereum address validator
    """
    if not Web3.is_checksum_address(address):
        raise typer.BadParameter("Invalid ethereum address")
    return ChecksumAddress(address)


def check_private_keys(private_keys: List[str]) -> List[str]:
    """
    Private Keys validator
    """
    if private_keys is None:
        raise typer.BadParameter("At least one private key is required")
    for private_key in private_keys:
        try:
            Account.from_key(private_key)
        except (ValueError, Error):
            raise typer.BadParameter(f"{private_key} is not a valid private key")
    return private_keys


def parse_checksum_address(address: str) -> ChecksumAddress:
    return ChecksumAddress(address)
