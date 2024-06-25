import unittest

import typer
from eth_account import Account
from eth_typing import ChecksumAddress
from hexbytes import HexBytes

from safe_cli.typer_validators import (
    ChecksumAddressParser,
    HexBytesParser,
    check_ethereum_address,
    check_hex_str,
    check_private_keys,
)


class TestTyperValidators(unittest.TestCase):

    def test_check_ethereum_address(self):
        address = "0x4127839cdf4F73d9fC9a2C2861d8d1799e9DF40C"
        self.assertEqual(check_ethereum_address(address), ChecksumAddress(address))

        not_valid_address = "0x4127839CDf4F73d9fC9a2C2861d8d1799e9DF40C"
        with self.assertRaises(typer.BadParameter):
            check_ethereum_address(not_valid_address)

    def test_check_private_keys(self):
        account = Account.create()
        self.assertEqual(check_private_keys([account.key.hex()]), [account.key.hex()])

        with self.assertRaises(typer.BadParameter):
            check_private_keys(["Random"])
            check_private_keys([])

    def test_check_hex_str(self):
        self.assertEqual(check_hex_str("0x12"), HexBytes("0x12"))

        with self.assertRaises(typer.BadParameter):
            check_hex_str("0x12x")

    def test_parse_checksum_address(self):
        address = "0x4127839cdf4F73d9fC9a2C2861d8d1799e9DF40C"
        self.assertEqual(
            ChecksumAddressParser().convert(address, None, None),
            ChecksumAddress(address),
        )

    def test_parse_hex_str(self):
        self.assertEqual(HexBytesParser().convert("0x12", None, None), HexBytes("0x12"))


if __name__ == "__main__":
    unittest.main()
