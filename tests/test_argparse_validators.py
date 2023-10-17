import argparse
import unittest

from eth_account import Account
from hexbytes import HexBytes

from safe_cli.argparse_validators import (
    check_ethereum_address,
    check_hex_str,
    check_keccak256_hash,
    check_private_key,
)
from safe_cli.safe_creator import check_positive_integer

from .safe_cli_test_case_mixin import SafeCliTestCaseMixin


class TestArgparseValidators(SafeCliTestCaseMixin, unittest.TestCase):
    def test_check_positive_integer(self):
        self.assertEqual(check_positive_integer(1), 1)
        self.assertEqual(check_positive_integer(500), 500)

        with self.assertRaises(argparse.ArgumentTypeError):
            self.assertEqual(check_positive_integer(0), 0)
        with self.assertRaises(argparse.ArgumentTypeError):
            check_positive_integer(-1)

    def test_check_ethereum_address(self):
        address = "0x4127839cdf4F73d9fC9a2C2861d8d1799e9DF40C"
        self.assertEqual(check_ethereum_address(address), address)

        not_valid_address = "0x4127839CDf4F73d9fC9a2C2861d8d1799e9DF40C"
        with self.assertRaises(argparse.ArgumentTypeError):
            check_ethereum_address(not_valid_address)

    def test_check_private_key(self):
        account = Account.create()
        self.assertEqual(check_private_key(account.key.hex()), account.key.hex())

        with self.assertRaises(argparse.ArgumentTypeError):
            check_private_key("Random")

    def test_check_hex_str(self):
        self.assertEqual(check_hex_str("0x12"), HexBytes("0x12"))

        with self.assertRaises(argparse.ArgumentTypeError):
            check_hex_str("0x12x")

    def test_check_keccak256_hash(self):
        random_hash = (
            "0x8aca9664752dbae36135fd0956c956fc4a370feeac67485b49bcd4b99608ae41"
        )
        self.assertEqual(check_keccak256_hash(random_hash), HexBytes(random_hash))

        with self.assertRaisesRegex(
            argparse.ArgumentTypeError,
            f"{random_hash[:-2]} is not a valid keccak256 hash hexadecimal string",
        ):
            # Size must match
            check_keccak256_hash(random_hash[:-2])

        with self.assertRaisesRegex(
            argparse.ArgumentTypeError, "0x12x is not a valid hexadecimal string"
        ):
            check_keccak256_hash("0x12x")


if __name__ == "__main__":
    unittest.main()
