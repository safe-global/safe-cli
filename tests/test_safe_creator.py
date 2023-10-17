import argparse
import unittest
from unittest import mock
from unittest.mock import MagicMock

from eth_account import Account

from gnosis.safe import Safe

from safe_cli.safe_creator import main

from .safe_cli_test_case_mixin import SafeCliTestCaseMixin


class TestSafeCreator(SafeCliTestCaseMixin, unittest.TestCase):
    @mock.patch(
        "argparse.ArgumentParser.parse_args",
    )
    def test_main(self, mock_parse_args: MagicMock):
        owner_account = self.get_ethereum_test_account()
        owners = [Account.create().address]
        threshold = 1
        mock_parse_args.return_value = argparse.Namespace(
            owners=owners,
            threshold=threshold,
            salt_nonce=4815,
            node_url=self.ethereum_node_url,
            private_key=owner_account.key.hex(),
            safe_contract=self.safe_contract.address,
            proxy_factory=self.proxy_factory_contract.address,
            callback_handler=self.compatibility_fallback_handler.address,
        )

        safe_address = main().contract_address
        safe = Safe(safe_address, self.ethereum_client)
        safe_info = safe.retrieve_all_info()
        self.assertEqual(safe_info.owners, owners)
        self.assertEqual(safe_info.threshold, 1)
        self.assertEqual(safe_info.master_copy, self.safe_contract.address)
        self.assertEqual(
            safe_info.fallback_handler, self.compatibility_fallback_handler.address
        )


if __name__ == "__main__":
    unittest.main()
