import os
from binascii import Error
from typing import List

import click
import typer
from eth_account import Account
from eth_typing import ChecksumAddress
from hexbytes import HexBytes
from web3 import Web3


def check_ethereum_address(address: str) -> ChecksumAddress:
    """
    Ethereum address validator
    """
    if not Web3.is_checksum_address(address):
        raise typer.BadParameter("Invalid ethereum address")
    return ChecksumAddress(address)


class ChecksumAddressParser(click.ParamType):
    name = "ChecksumAddress"

    def convert(self, value, param, ctx):
        """
        ChecksumAddress parser from str
        """
        return ChecksumAddress(value)


def check_private_keys(private_keys: List[str]) -> List[str]:
    """
    Private Keys validator
    """
    if private_keys is None:
        raise typer.BadParameter("At least one private key is required")
    for private_key in private_keys:
        try:
            Account.from_key(os.environ.get(private_key, default=private_key))
        except (ValueError, Error):
            raise typer.BadParameter(f"{private_key} is not a valid private key")
    return private_keys


def check_hex_str(hex_str: str) -> HexBytes:
    """
    HexBytes string validator
    """
    try:
        return HexBytes(hex_str)
    except ValueError:
        raise typer.BadParameter(f"{hex_str} is not a valid hexadecimal string")


class HexBytesParser(click.ParamType):
    name = "HexBytes"

    def convert(self, value, param, ctx):
        """
        HexBytes string parser from str
        """
        return HexBytes(value)
