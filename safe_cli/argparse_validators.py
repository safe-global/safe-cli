import argparse
from binascii import Error

from eth_account import Account
from eth_typing import ChecksumAddress
from hexbytes import HexBytes
from web3 import Web3


def check_positive_integer(number: str) -> int:
    """
    Positive integer validator for Argparse

    :param number:
    :return: Positive integer
    """
    number = int(number)
    if number <= 0:
        raise argparse.ArgumentTypeError(
            f"{number} is not a valid threshold. Must be > 0"
        )
    return number


def check_ethereum_address(address: str) -> ChecksumAddress:
    """
    Ethereum address validator for Argparse

    :param address:
    :return: Checksummed ethereum address
    """
    if not Web3.is_checksum_address(address):
        raise argparse.ArgumentTypeError(
            f"{address} is not a valid checksummed ethereum address"
        )
    return ChecksumAddress(address)


def check_private_key(private_key: str) -> str:
    """
    Ethereum private key validator for ArgParse

    :param private_key: Ethereum Private key
    :return: Ethereum Private key
    """
    try:
        Account.from_key(private_key)
    except (ValueError, Error):  # TODO Report `Error` exception as a bug of eth_account
        raise argparse.ArgumentTypeError(f"{private_key} is not a valid private key")
    return private_key


def check_hex_str(hex_str: str) -> HexBytes:
    """
    Hexadecimal string validator for Argparse

    :param hex_str:
    :return: HexBytes from the provided hex string
    """
    try:
        return HexBytes(hex_str)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{hex_str} is not a valid hexadecimal string")


def check_keccak256_hash(hex_str: str) -> HexBytes:
    """
    Hexadecimal keccak256 validator for Argparse

    :param hex_str:
    :return: HexBytes from the provided hex string
    """
    hex_str_bytes = check_hex_str(hex_str)
    if len(hex_str_bytes) != 32:
        raise argparse.ArgumentTypeError(
            f"{hex_str} is not a valid keccak256 hash hexadecimal string"
        )
    return hex_str_bytes
