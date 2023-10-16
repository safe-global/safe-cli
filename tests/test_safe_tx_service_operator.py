import unittest
from unittest import mock
from unittest.mock import MagicMock

from eth_account import Account
from web3 import Web3

from gnosis.safe.api import TransactionServiceApi

from safe_cli.operators import SafeOperatorMode, SafeTxServiceOperator

from .safe_cli_test_case_mixin import SafeCliTestCaseMixin


class TestSafeTxServiceOperator(SafeCliTestCaseMixin, unittest.TestCase):
    def test_setup_operator(self):
        safe_operator = self.setup_operator(
            number_owners=4, mode=SafeOperatorMode.TX_SERVICE
        )
        self.assertIsInstance(safe_operator, SafeTxServiceOperator)

    def test_approve_hash(self):
        safe_operator = self.setup_operator(
            number_owners=1, mode=SafeOperatorMode.TX_SERVICE
        )
        safe_tx_hash = Web3.keccak(text="random-test")
        with self.assertRaises(NotImplementedError):
            safe_operator.approve_hash(
                safe_tx_hash, list(safe_operator.accounts)[0].address
            )

    @mock.patch.object(TransactionServiceApi, "get_delegates")
    def test_get_delegates(self, get_delegates_mock: MagicMock):
        get_delegates_mock.return_value = [
            {
                "safe": "0x172766BDBf2e05405a890BBfa120C726CA862a6c",
                "delegate": "0xFACA096a40a68557516202B75447c7494c83b522",
                "delegator": "0xaf2F9D5D7991Ba570203f2bf2Ff7ecC90d4B906D",
                "label": "Testing",
            },
            {
                "safe": "0x172766BDBf2e05405a890BBfa120C726CA862a6c",
                "delegate": "0xFACA096a40a68557516202B75447c7494c83b522",
                "delegator": "0xd6e1eF1B88BE12b39785d24aD21235FcF48C6409",
                "label": "Testing",
            },
        ]
        safe_operator = self.setup_operator(
            number_owners=1, mode=SafeOperatorMode.TX_SERVICE
        )
        self.assertEqual(
            safe_operator.get_delegates(),
            [
                [
                    "0xFACA096a40a68557516202B75447c7494c83b522",
                    "0xaf2F9D5D7991Ba570203f2bf2Ff7ecC90d4B906D",
                    "Testing",
                ],
                [
                    "0xFACA096a40a68557516202B75447c7494c83b522",
                    "0xd6e1eF1B88BE12b39785d24aD21235FcF48C6409",
                    "Testing",
                ],
            ],
        )

    @mock.patch.object(TransactionServiceApi, "add_delegate", return_value=None)
    def test_add_delegate(self, add_delegate_mock: MagicMock):
        safe_operator = self.setup_operator(
            number_owners=1, mode=SafeOperatorMode.TX_SERVICE
        )
        delegate_address = Account.create().address
        label = "Test"
        signer = list(safe_operator.accounts)[0]
        self.assertTrue(
            safe_operator.add_delegate(delegate_address, label, signer.address)
        )
        add_delegate_mock.assert_called_with(
            safe_operator.address, delegate_address, label, signer
        )

    @mock.patch.object(TransactionServiceApi, "remove_delegate", return_value=None)
    def test_remove_delegate(self, remove_delegate_mock: MagicMock):
        safe_operator = self.setup_operator(
            number_owners=1, mode=SafeOperatorMode.TX_SERVICE
        )
        delegate_address = Account.create().address
        signer = list(safe_operator.accounts)[0]
        self.assertTrue(safe_operator.remove_delegate(delegate_address, signer.address))
        remove_delegate_mock.assert_called_with(
            safe_operator.address, delegate_address, signer
        )

    def test_submit_signatures(self):
        safe_operator = self.setup_operator(
            number_owners=1, mode=SafeOperatorMode.TX_SERVICE
        )


if __name__ == "__main__":
    unittest.main()
