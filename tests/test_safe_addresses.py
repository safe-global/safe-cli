import unittest

from eth_account import Account

from safe_cli.safe_addresses import _get_valid_contract

from .safe_cli_test_case_mixin import SafeCliTestCaseMixin


class TestSafeAddresses(SafeCliTestCaseMixin, unittest.TestCase):
    def test_get_valid_contract(self):
        addresses = [
            Account.create().address,
            Account.create().address,
            self.safe_contract_V1_4_1.address,
            Account.create().address,
        ]
        expected_address = self.safe_contract_V1_4_1.address
        self.assertEqual(
            _get_valid_contract(self.ethereum_client, addresses), expected_address
        )

        with self.assertRaisesRegex(
            ValueError,
            f"Network {self.ethereum_client.get_network().name} is not supported",
        ):
            _get_valid_contract(self.ethereum_client, addresses[:1])


if __name__ == "__main__":
    unittest.main()
