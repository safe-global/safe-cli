import unittest
from unittest import mock
from unittest.mock import MagicMock

from eth_account import Account
from hexbytes import HexBytes
from web3 import Web3

from gnosis.safe import SafeTx
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

    @mock.patch.object(SafeTxServiceOperator, "get_permitted_signers", return_value=[])
    @mock.patch.object(
        SafeTx, "safe_version", return_value="1.4.1", new_callable=mock.PropertyMock
    )
    @mock.patch.object(TransactionServiceApi, "post_signatures", return_value=None)
    @mock.patch.object(TransactionServiceApi, "_get_request")
    def test_submit_signatures(
        self,
        get_safe_transaction_mock: MagicMock,
        post_signatures_mock: MagicMock,
        safe_version_mock: mock.PropertyMock,
        get_permitted_signers_mock: MagicMock,
    ):
        class GetRequestMock:
            ok = True

            def __init__(self, executed: bool):
                self.executed = executed

            def json(self):
                return {
                    "safe": "0x389416768c1811168ba89940fD7dFD0C190c53a1",
                    "to": "0x5aC255889882aCd3da2aA939679E3f3d4cea221e",
                    "value": "1000000000000000",
                    "data": None,
                    "operation": 0,
                    "gasToken": "0x0000000000000000000000000000000000000000",
                    "safeTxGas": 0,
                    "baseGas": 0,
                    "gasPrice": "0",
                    "refundReceiver": "0x0000000000000000000000000000000000000000",
                    "nonce": 6,
                    "executionDate": "2023-02-28T20:18:24Z",
                    "submissionDate": "2023-02-28T20:18:24Z",
                    "modified": "2023-02-28T20:18:24Z",
                    "blockNumber": 8573938,
                    "transactionHash": "0x7d229cdd1a197acdd23787cedcb7ec4d746ce0e730dff75e209359894af7fb52"
                    if self.executed
                    else None,
                    "safeTxHash": "0xeb5fa8e85dd530397172da07792c5d05dff9ffe5816fc0a260d672e924825b01",
                    "proposer": None,
                    "executor": "0x5aC255889882aCd3da2aA939679E3f3d4cea221e",
                    "isExecuted": True,
                    "isSuccessful": True,
                    "ethGasPrice": "37052821773",
                    "maxFeePerGas": "100000000000",
                    "maxPriorityFeePerGas": "1500000000",
                    "gasUsed": 59925,
                    "fee": "2220390344747025",
                    "origin": "{}",
                    "dataDecoded": None,
                    "confirmationsRequired": 1,
                    "confirmations": [
                        {
                            "owner": "0x5aC255889882aCd3da2aA939679E3f3d4cea221e",
                            "submissionDate": "2023-02-28T20:18:24Z",
                            "transactionHash": None,
                            "signature": "0x0000000000000000000000005ac255889882acd3da2aa939679e3f3d4cea221e000000000000000000000000000000000000000000000000000000000000000001",
                            "signatureType": "APPROVED_HASH",
                        }
                    ],
                    "trusted": True,
                    "signatures": "0x0000000000000000000000005ac255889882acd3da2aa939679e3f3d4cea221e000000000000000000000000000000000000000000000000000000000000000001",
                }

        get_safe_transaction_mock.return_value = GetRequestMock(executed=False)
        post_signatures_mock.return_value = None

        safe_tx_hash = HexBytes(
            "0xeb5fa8e85dd530397172da07792c5d05dff9ffe5816fc0a260d672e924825b01"
        )
        safe_operator = self.setup_operator(
            number_owners=1, mode=SafeOperatorMode.TX_SERVICE
        )
        # No suitable signers
        self.assertFalse(safe_operator.submit_signatures(safe_tx_hash))
        get_permitted_signers_mock.return_value = {
            list(safe_operator.accounts)[0].address
        }
        # Now signatures must be submited
        self.assertTrue(safe_operator.submit_signatures(safe_tx_hash))

        # Cannot sign executed transactions
        get_safe_transaction_mock.return_value = GetRequestMock(executed=True)
        self.assertFalse(safe_operator.submit_signatures(safe_tx_hash))


if __name__ == "__main__":
    unittest.main()
