import unittest
from unittest import mock
from unittest.mock import MagicMock

from eth_account import Account
from hexbytes import HexBytes
from ledgerblue.Dongle import Dongle
from ledgereth import SignedTransaction
from safe_eth.safe import SafeTx
from safe_eth.safe.tests.safe_test_case import SafeTestCaseMixin

from safe_cli.operators.hw_wallets.hw_wallet_manager import (
    HwWalletManager,
    HwWalletType,
    get_hw_wallet_manager,
)
from safe_cli.operators.hw_wallets.ledger_wallet import LedgerWallet


class Testledger_wallet(SafeTestCaseMixin, unittest.TestCase):
    def test_setup_hw_wallet_manager(self):
        # Should support Treezor and Ledger
        hw_wallet_manager = get_hw_wallet_manager()
        self.assertTrue(hw_wallet_manager.is_supported_hw_wallet(HwWalletType.TREZOR))
        self.assertTrue(hw_wallet_manager.is_supported_hw_wallet(HwWalletType.LEDGER))
        self.assertEqual(len(hw_wallet_manager.wallets), 0)

        # Should get the same instance
        other_hw_wallet_manager = get_hw_wallet_manager()
        self.assertEqual(other_hw_wallet_manager, hw_wallet_manager)

    @mock.patch(
        "safe_cli.operators.hw_wallets.ledger_wallet.init_dongle",
        autospec=True,
        return_value=Dongle(),
    )
    @mock.patch(
        "safe_cli.operators.hw_wallets.ledger_wallet.LedgerWallet.get_address",
        autospec=True,
    )
    def test_get_accounts(
        self, mock_get_address: MagicMock, mock_init_dongle: MagicMock
    ):
        hw_wallet_manager = HwWalletManager()
        addresses = [Account.create().address, Account.create().address]
        derivation_paths = ["44'/60'/0'/0/0", "44'/60'/1'/0/0"]
        mock_get_address.side_effect = addresses
        # Choosing LEDGER because function is mocked for LEDGER
        hw_wallets = hw_wallet_manager.get_accounts(
            HwWalletType.LEDGER, "44'/60'/{i}'/0/0", number_accounts=2
        )
        self.assertEqual(len(hw_wallets), 2)
        for hw_wallet, expected_address, expected_derivation_path in zip(
            hw_wallets, addresses, derivation_paths
        ):
            address, derivation_path = hw_wallet
            self.assertEqual(expected_address, address)
            self.assertEqual(expected_derivation_path, derivation_path)

    @mock.patch(
        "safe_cli.operators.hw_wallets.ledger_wallet.init_dongle",
        autospec=True,
        return_value=Dongle(),
    )
    @mock.patch(
        "safe_cli.operators.hw_wallets.ledger_wallet.LedgerWallet.get_address",
        autospec=True,
    )
    def test_add_account(
        self, mock_get_address: MagicMock, mock_init_dongle: MagicMock
    ):
        hw_wallet_manager = HwWalletManager()
        derivation_path = "44'/60'/0'/0"
        account_address = Account.create().address
        mock_get_address.return_value = account_address

        self.assertEqual(len(hw_wallet_manager.wallets), 0)
        # Choosing LEDGER because function is mocked for LEDGER
        self.assertEqual(
            hw_wallet_manager.add_account(HwWalletType.LEDGER, derivation_path),
            account_address,
        )

        self.assertEqual(len(hw_wallet_manager.wallets), 1)
        ledger_wallet = list(hw_wallet_manager.wallets)[0]
        self.assertEqual(ledger_wallet.address, account_address)
        self.assertEqual(ledger_wallet.derivation_path, derivation_path)
        # Shouldn't duplicate accounts
        self.assertEqual(
            hw_wallet_manager.add_account(HwWalletType.LEDGER, derivation_path),
            account_address,
        )
        self.assertEqual(len(hw_wallet_manager.wallets), 1)

        # Should accept derivation paths starting with master
        master_derivation_path = "m/44'/60'/0'/0"
        self.assertEqual(
            hw_wallet_manager.add_account(HwWalletType.LEDGER, master_derivation_path),
            account_address,
        )

    @mock.patch(
        "safe_cli.operators.hw_wallets.ledger_wallet.init_dongle",
        autospec=True,
        return_value=Dongle(),
    )
    @mock.patch(
        "safe_cli.operators.hw_wallets.ledger_wallet.LedgerWallet.get_address",
        autospec=True,
    )
    def test_delete_account(
        self, mock_get_address: MagicMock, mock_init_dongle: MagicMock
    ):
        hw_wallet_manager = HwWalletManager()
        random_address = Account.create().address
        random_address_2 = Account.create().address
        self.assertEqual(len(hw_wallet_manager.wallets), 0)
        self.assertEqual(len(hw_wallet_manager.delete_accounts([random_address])), 0)

        mock_get_address.return_value = random_address_2
        hw_wallet_manager.wallets.add(LedgerWallet("44'/60'/0'/0"))
        self.assertEqual(len(hw_wallet_manager.delete_accounts([random_address])), 0)
        self.assertEqual(len(hw_wallet_manager.wallets), 1)
        self.assertEqual(len(hw_wallet_manager.delete_accounts([])), 0)

        mock_get_address.return_value = random_address
        hw_wallet_manager.wallets.add(LedgerWallet("44'/60'/0'/1"))
        self.assertEqual(len(hw_wallet_manager.wallets), 2)
        self.assertEqual(len(hw_wallet_manager.delete_accounts([random_address])), 1)
        self.assertEqual(len(hw_wallet_manager.wallets), 1)
        hw_wallet_manager.wallets.add(LedgerWallet("44'/60'/0'/1"))
        self.assertEqual(len(hw_wallet_manager.wallets), 2)
        self.assertEqual(
            len(hw_wallet_manager.delete_accounts([random_address, random_address_2])),
            2,
        )
        self.assertEqual(len(hw_wallet_manager.wallets), 0)

    @mock.patch(
        "safe_cli.operators.hw_wallets.ledger_wallet.create_transaction",
        autospec=True,
        return_value=Dongle(),
    )
    @mock.patch(
        "safe_cli.operators.hw_wallets.ledger_wallet.LedgerWallet.get_address",
        autospec=True,
    )
    @mock.patch(
        "safe_cli.operators.hw_wallets.ledger_wallet.init_dongle",
        autospec=True,
        return_value=Dongle(),
    )
    def test_execute(
        self,
        mock_init_dongle: MagicMock,
        mock_get_address: MagicMock,
        mock_ledger_create_transaction: MagicMock,
    ):
        owner = self.ethereum_test_account
        to = Account.create()
        derivation_path = "44'/60'/0'/0"
        hw_wallet_manager = HwWalletManager()
        mock_get_address.return_value = owner.address
        hw_wallet_manager.add_account(HwWalletType.LEDGER, derivation_path)
        hw_wallet_manager.set_sender(HwWalletType.LEDGER, derivation_path)
        self.assertEqual(hw_wallet_manager.sender.address, owner.address)
        safe = self.deploy_test_safe(
            owners=[owner.address],
            threshold=1,
            initial_funding_wei=self.w3.to_wei(0.1, "ether"),
        )
        safe_tx = SafeTx(
            self.ethereum_client,
            safe.address,
            to.address,
            10,
            b"",
            0,
            200000,
            200000,
            self.gas_price,
            None,
            None,
            safe_nonce=0,
        )
        safe_tx.sign(owner.key)
        tx_parameters = {
            "from": owner.address,
            "gasPrice": safe_tx.w3.eth.gas_price,
            "nonce": 0,
            "gas": safe_tx.recommended_gas(),
        }
        safe_tx.tx = safe_tx.w3_tx.build_transaction(tx_parameters)
        signed_fields = safe_tx.w3.eth.account.sign_transaction(
            safe_tx.tx, private_key=owner.key
        )

        mocked_signed_transaction_response = SignedTransaction(
            nonce=0,
            gas_price=safe_tx.tx["gasPrice"],
            gas_limit=safe_tx.tx["gas"],
            destination=HexBytes(safe_tx.tx["to"]),
            amount=safe_tx.tx["value"],
            data=HexBytes(safe_tx.tx["data"]),
            v=signed_fields.v,
            r=signed_fields.r,
            s=signed_fields.s,
        )

        mock_ledger_create_transaction.return_value = mocked_signed_transaction_response
        tx_hash, tx = hw_wallet_manager.execute_safe_tx(safe_tx)
        self.assertEqual(tx["data"], safe_tx.tx["data"])
        self.assertIsNotNone(
            self.ethereum_client.w3.eth.get_transaction_receipt(tx_hash)
        )
