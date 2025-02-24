import unittest
from unittest import mock
from unittest.mock import MagicMock

from eth_account import Account
from hexbytes import HexBytes
from ledgereth.objects import LedgerAccount
from safe_eth.eth import EthereumClient
from safe_eth.safe import SafeTx
from safe_eth.safe.api import SafeAPIException, TransactionServiceApi
from safe_eth.util.util import to_0x_hex_str
from web3 import Web3

from safe_cli.operators import SafeOperatorMode, SafeTxServiceOperator

from .mocks.balances_mock import balances_mock
from .mocks.data_decoded_mock import data_decoded_mock
from .mocks.multisig_tx_mock import GetMultisigTxRequestMock
from .mocks.txs_mock import txs_mock
from .safe_cli_test_case_mixin import SafeCliTestCaseMixin


class TestSafeTxServiceOperator(SafeCliTestCaseMixin, unittest.TestCase):
    def test_setup_operator(self):
        safe_operator = self.setup_operator(
            number_owners=1, mode=SafeOperatorMode.TX_SERVICE
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

        expected_hash = safe_operator.safe_tx_service.create_delegate_message_hash(
            delegate_address
        )
        expected_signature = signer.unsafe_sign_hash(expected_hash)

        self.assertTrue(
            safe_operator.add_delegate(delegate_address, label, signer.address)
        )
        add_delegate_mock.assert_called_with(
            delegate_address,
            signer.address,
            label,
            expected_signature.signature,
            safe_address=safe_operator.address,
        )

    @mock.patch.object(TransactionServiceApi, "remove_delegate", return_value=None)
    def test_remove_delegate(self, remove_delegate_mock: MagicMock):
        safe_operator = self.setup_operator(
            number_owners=1, mode=SafeOperatorMode.TX_SERVICE
        )
        delegate_address = Account.create().address
        signer = list(safe_operator.accounts)[0]

        expected_hash = safe_operator.safe_tx_service.create_delegate_message_hash(
            delegate_address
        )
        expected_signature = signer.unsafe_sign_hash(expected_hash)

        self.assertTrue(safe_operator.remove_delegate(delegate_address, signer.address))

        remove_delegate_mock.assert_called_with(
            delegate_address,
            signer.address,
            expected_signature.signature,
            safe_address=safe_operator.address,
        )

    @mock.patch.object(TransactionServiceApi, "delete_transaction", return_value=None)
    @mock.patch.object(TransactionServiceApi, "get_safe_transaction")
    @mock.patch(
        "safe_eth.safe.api.transaction_service_api.transaction_service_messages.get_totp",
        return_value=8365,
    )
    def test_remove_transaction(
        self,
        mock_get_totp,
        get_transaction_mock: MagicMock,
        remove_transaction_mock: MagicMock,
    ):
        safe_operator = self.setup_operator(
            number_owners=1, mode=SafeOperatorMode.TX_SERVICE
        )
        safe_operator.address = "0x23793e7Ce4f2Fd31C993893f658181fD39fB5dEb"
        signer = list(safe_operator.accounts)[0]
        safe_tx_mock = MagicMock()
        get_transaction_mock.return_value = (safe_tx_mock, None)
        safe_tx_hash = HexBytes(
            "0x07eeea19b7d005b561f367e714bf65734d0ecc477de3e8b1fbc20ccb18c8747b"
        )
        expected_signature = "0xbc305f59a62c5bbb002645f658ee62cfa1966f20aca4dc1922b813e9d41bf1f02abd356891a3725af2066dd1758c930574298b4ba180117dc6146bbc4369cc0c1c"
        safe_tx_mock.proposer = signer.address
        self.assertTrue(safe_operator.remove_proposed_transaction(safe_tx_hash))
        remove_transaction_mock.assert_called_with(
            to_0x_hex_str(safe_tx_hash), expected_signature
        )
        # Different proposer should return False
        safe_tx_mock.proposer = Account.create().address
        self.assertFalse(safe_operator.remove_proposed_transaction(safe_tx_hash))

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
        get_safe_transaction_mock.return_value = GetMultisigTxRequestMock(
            executed=False
        )
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
        # Now signatures must be submitted
        self.assertTrue(safe_operator.submit_signatures(safe_tx_hash))

        # Cannot sign executed transactions
        get_safe_transaction_mock.return_value = GetMultisigTxRequestMock(executed=True)
        self.assertFalse(safe_operator.submit_signatures(safe_tx_hash))

        # Test ledger signers
        with mock.patch.object(
            SafeTx, "signers", return_value=["signer"], new_callable=mock.PropertyMock
        ) as mock_safe_tx:
            safe_operator.hw_wallet_manager.sign_safe_tx = MagicMock(
                return_value=mock_safe_tx
            )
            get_safe_transaction_mock.return_value = GetMultisigTxRequestMock(
                executed=False
            )
            safe_operator.hw_wallet_manager.wallets.add(
                LedgerAccount("44'/60'/0'/0", Account.create().address)
            )
            get_permitted_signers_mock.return_value = {
                list(safe_operator.hw_wallet_manager.wallets)[0].address
            }
            self.assertTrue(safe_operator.submit_signatures(safe_tx_hash))

    @mock.patch.object(TransactionServiceApi, "post_transaction", return_value=True)
    @mock.patch.object(
        SafeTx, "safe_version", return_value="1.4.1", new_callable=mock.PropertyMock
    )
    @mock.patch.object(EthereumClient, "is_contract", return_value=True)
    @mock.patch.object(TransactionServiceApi, "_get_request")
    def test_batch_txs(
        self,
        get_safe_transaction_mock: MagicMock,
        is_contract_mock: MagicMock,
        safe_version_mock: mock.PropertyMock,
        post_transaction_mock: MagicMock,
    ):
        safe_operator = self.setup_operator(
            number_owners=1, mode=SafeOperatorMode.TX_SERVICE
        )
        get_safe_transaction_mock.return_value = GetMultisigTxRequestMock(
            executed=False
        )
        safe_tx_hash = HexBytes(
            "0xeb5fa8e85dd530397172da07792c5d05dff9ffe5816fc0a260d672e924825b01"
        )
        safe_nonce = 0
        safe_operator.batch_txs(safe_nonce, [safe_tx_hash])

    @mock.patch.object(
        TransactionServiceApi, "get_balances", return_value=balances_mock
    )
    def test_get_balances(
        self,
        get_balances_mock: MagicMock,
    ):
        safe_operator = self.setup_operator(
            number_owners=1, mode=SafeOperatorMode.TX_SERVICE
        )
        expected = [
            ["ETHER", "0.17100", "Ξ", 18, ""],
            [
                "Basic Attention Token",
                "1.00000",
                "BAT",
                18,
                "0x70cBa46d2e933030E2f274AE58c951C800548AeF",
            ],
            [
                " best tron wallet | tronscan | tronlink | bttc",
                "8888.00000",
                "tronAddress.org",
                0,
                "0x4644A362B7041aff2CF792fD61671b9F75234C27",
            ],
            [
                "CoW Protocol Token",
                "7.45545",
                "COW",
                18,
                "0x91056D4A53E1faa1A84306D4deAEc71085394bC8",
            ],
            [
                "CoW Protocol Token",
                "8.04516",
                "COW",
                18,
                "0x3430d04E42a722c5Ae52C5Bffbf1F230C2677600",
            ],
            [
                "Dai",
                "1000.00000",
                "DAI",
                18,
                "0xdc31Ee1784292379Fbb2964b3B9C4124D8F89C60",
            ],
            [
                "Elden Ring Token",
                "10000.00000",
                "ERT",
                18,
                "0x64685e9733d57Ccc3870ceD50ed9B1f576Fd61B1",
            ],
            [
                "ethAddress.io",
                "888888.00000",
                "ethAddress.io",
                0,
                "0xD14DD51BE76e6dC28756a442dF786845e03a1D60",
            ],
            [
                "GiantETHLP",
                "0.00100",
                "gETH",
                18,
                "0x4c6FFFda6b732b495c974Fb284e9bB38b9f061C8",
            ],
            [
                "Gnosis Token",
                "0.40000",
                "GNO",
                18,
                "0x02ABBDbAaa7b1BB64B5c878f7ac17f8DDa169532",
            ],
            [
                "Liquid staked Ether 2.0",
                "0.03020",
                "stETH",
                18,
                "0x1643E812aE58766192Cf7D2Cf9567dF2C37e9B7F",
            ],
            [
                "RareTron.io",
                "66666.00000",
                "RareTron.io",
                0,
                "0x54FA517F05e11Ffa87f4b22AE87d91Cec0C2D7E1",
            ],
            [
                "Safe Token",
                "10362.07000",
                "SAFE",
                18,
                "0x61fD3b6d656F39395e32f46E2050953376c3f5Ff",
            ],
            [
                "Super ETH",
                "0.00500",
                "ETHx",
                18,
                "0x5943F705aBb6834Cad767e6E4bB258Bc48D9C947",
            ],
            [
                "Uniswap",
                "0.02130",
                "UNI",
                18,
                "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
            ],
            [
                "USD Coin",
                "10.00000",
                "USDC",
                6,
                "0xD87Ba7A50B2E7E660f678A895E4B72E7CB4CCd9C",
            ],
            [
                "USD Coin",
                "0.92509",
                "USDC",
                6,
                "0xe0C9275E44Ea80eF17579d33c55136b7DA269aEb",
            ],
            [
                "VanityTron.io",
                "6666666.00000",
                "VanityTron.io",
                0,
                "0x38d9639da06f7a726cAf40c2E1010ac88517A085",
            ],
            [
                "VanityTRX.org",
                "888888.00000",
                "VanityTRX.org",
                0,
                "0x1B809925ba90c541d895D19f0b7D70eE281a987F",
            ],
            [
                "Wrapped Ether",
                "0.00050",
                "WETH",
                18,
                "0xdFCeA9088c8A88A76FF74892C1457C17dfeef9C1",
            ],
            [
                "Wrapped Ether",
                "0.00560",
                "WETH",
                18,
                "0xB4FBF271143F4FBf7B91A5ded31805e42b2208d6",
            ],
        ]
        self.assertEqual(safe_operator.get_balances(), expected)

    @mock.patch.object(TransactionServiceApi, "get_transactions", return_value=txs_mock)
    def test_get_transaction_history(
        self,
        get_transactions_mock: MagicMock,
    ):
        safe_operator = self.setup_operator(
            number_owners=1, mode=SafeOperatorMode.TX_SERVICE
        )
        expected = [
            ["ETHER", "0.17100", "Ξ", 18, ""],
            [
                "Basic Attention Token",
                "1.00000",
                "BAT",
                18,
                "0x70cBa46d2e933030E2f274AE58c951C800548AeF",
            ],
            [
                " best tron wallet | tronscan | tronlink | bttc",
                "8888.00000",
                "tronAddress.org",
                0,
                "0x4644A362B7041aff2CF792fD61671b9F75234C27",
            ],
            [
                "CoW Protocol Token",
                "7.45545",
                "COW",
                18,
                "0x91056D4A53E1faa1A84306D4deAEc71085394bC8",
            ],
            [
                "CoW Protocol Token",
                "8.04516",
                "COW",
                18,
                "0x3430d04E42a722c5Ae52C5Bffbf1F230C2677600",
            ],
            [
                "Dai",
                "1000.00000",
                "DAI",
                18,
                "0xdc31Ee1784292379Fbb2964b3B9C4124D8F89C60",
            ],
            [
                "Elden Ring Token",
                "10000.00000",
                "ERT",
                18,
                "0x64685e9733d57Ccc3870ceD50ed9B1f576Fd61B1",
            ],
            [
                "ethAddress.io",
                "888888.00000",
                "ethAddress.io",
                0,
                "0xD14DD51BE76e6dC28756a442dF786845e03a1D60",
            ],
            [
                "GiantETHLP",
                "0.00100",
                "gETH",
                18,
                "0x4c6FFFda6b732b495c974Fb284e9bB38b9f061C8",
            ],
            [
                "Gnosis Token",
                "0.40000",
                "GNO",
                18,
                "0x02ABBDbAaa7b1BB64B5c878f7ac17f8DDa169532",
            ],
            [
                "Liquid staked Ether 2.0",
                "0.03020",
                "stETH",
                18,
                "0x1643E812aE58766192Cf7D2Cf9567dF2C37e9B7F",
            ],
            [
                "RareTron.io",
                "66666.00000",
                "RareTron.io",
                0,
                "0x54FA517F05e11Ffa87f4b22AE87d91Cec0C2D7E1",
            ],
            [
                "Safe Token",
                "10362.07000",
                "SAFE",
                18,
                "0x61fD3b6d656F39395e32f46E2050953376c3f5Ff",
            ],
            [
                "Super ETH",
                "0.00500",
                "ETHx",
                18,
                "0x5943F705aBb6834Cad767e6E4bB258Bc48D9C947",
            ],
            [
                "Uniswap",
                "0.02130",
                "UNI",
                18,
                "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
            ],
            [
                "USD Coin",
                "10.00000",
                "USDC",
                6,
                "0xD87Ba7A50B2E7E660f678A895E4B72E7CB4CCd9C",
            ],
            [
                "USD Coin",
                "0.92509",
                "USDC",
                6,
                "0xe0C9275E44Ea80eF17579d33c55136b7DA269aEb",
            ],
            [
                "VanityTron.io",
                "6666666.00000",
                "VanityTron.io",
                0,
                "0x38d9639da06f7a726cAf40c2E1010ac88517A085",
            ],
            [
                "VanityTRX.org",
                "888888.00000",
                "VanityTRX.org",
                0,
                "0x1B809925ba90c541d895D19f0b7D70eE281a987F",
            ],
            [
                "Wrapped Ether",
                "0.00050",
                "WETH",
                18,
                "0xdFCeA9088c8A88A76FF74892C1457C17dfeef9C1",
            ],
            [
                "Wrapped Ether",
                "0.00560",
                "WETH",
                18,
                "0xB4FBF271143F4FBf7B91A5ded31805e42b2208d6",
            ],
        ]
        expected = [
            [
                "\x1b[0m\x1b[1m\x1b[32m213",
                "0x4127839cdf4F73d9fC9a2C2861d8d1799e9DF40C",
                "100000",
                "0x6d1de5637d9b78a498145e5bcf13219ac88bb2fef8753887722b31c4290c2bf4",
                "0xf10a3c13a7b8cac3e343ca5f2f328c15b1aeb6031a7b1cbc4b9a65547d4d7070",
            ],
            [
                "\x1b[0m\x1b[32m212",
                "0xB4FBF271143F4FBf7B91A5ded31805e42b2208d6",
                "0",
                "0xf59007f3240cada5a9514aee3eb9de4d84bd8de8ff6507f26d6b309a8b07ee4b",
                "0xa26abcadcad3176b51f91bc0bd4c4c35d9afe1db5467268642452e2911316606",
                "transfer: 0xc6b82bA149CFA113f8f48d5E3b1F78e933e16DfD,1000000000000000000",
            ],
        ]
        self.assertEqual(safe_operator.get_transaction_history(), expected)

    def test_data_decoded_to_text(self):
        safe_operator = self.setup_operator(
            number_owners=1, mode=SafeOperatorMode.TX_SERVICE
        )
        decoded_data_text = safe_operator.safe_tx_service.data_decoded_to_text(
            data_decoded_mock
        )
        self.assertIn(
            "- changeMasterCopy: 0x34CfAC646f301356fAa8B21e94227e3583Fe3F5F",
            decoded_data_text,
        )
        self.assertIn(
            "- setFallbackHandler: 0xd5D82B6aDDc9027B22dCA772Aa68D5d74cdBdF44",
            decoded_data_text,
        )

    @mock.patch.object(
        TransactionServiceApi, "post_message_signature", return_value=True
    )
    @mock.patch.object(TransactionServiceApi, "get_message", return_value=None)
    def test_confirm_message(
        self, get_message: MagicMock, post_message_signature: MagicMock
    ):
        safe_operator = self.setup_operator(
            number_owners=1, mode=SafeOperatorMode.TX_SERVICE
        )
        # confirm_message just need the raw message to print
        get_message.return_value = {"message": "We just need a message"}
        safe_message_hash = HexBytes(
            "0xfbf5d6f7faaec8fd7770cb532f87e38fb82ecb47f58474cbeb29a174f1afd829"
        )
        expected_signature = HexBytes(
            "0x82484cd1f17430915f940d7c589e1687253de7f4062748b6807d29c67af52e3957b90427a9202ba4bc2104a129183387d994be2e4a8623a1f1ba2bad75d3546d1b"
        )
        sender = list(safe_operator.accounts)[0]
        self.assertTrue(
            safe_operator.confirm_message(safe_message_hash, sender.address)
        )
        post_message_signature.assert_called_with(safe_message_hash, expected_signature)

        post_message_signature.side_effect = SafeAPIException(
            "Error posting message signature"
        )
        self.assertFalse(
            safe_operator.confirm_message(safe_message_hash, sender.address)
        )

    def test_drain(self):
        # TODO Drain is a complex to mock
        pass


if __name__ == "__main__":
    unittest.main()
