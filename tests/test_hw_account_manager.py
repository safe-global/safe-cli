import unittest
from unittest import mock
from unittest.mock import MagicMock

from eth_account import Account
from ledgerblue.Dongle import Dongle

from gnosis.safe.tests.safe_test_case import SafeTestCaseMixin

from safe_cli.operators.hw_accounts.hw_account_manager import (
    HwAccountManager,
    HwWalletType,
)
from safe_cli.operators.hw_accounts.ledger_manager import LedgerManager


class TestLedgerManager(SafeTestCaseMixin, unittest.TestCase):
    def test_setup_hw_account_manager(self):
        # Should support Treezor and Ledger
        hw_acccount_manager = HwAccountManager()
        self.assertTrue(hw_acccount_manager.is_supported_hw_wallet(HwWalletType.TREZOR))
        self.assertTrue(hw_acccount_manager.is_supported_hw_wallet(HwWalletType.LEDGER))
        self.assertEqual(len(hw_acccount_manager.accounts), 0)

    @mock.patch(
        "safe_cli.operators.hw_accounts.ledger_manager.init_dongle",
        autospec=True,
        return_value=Dongle(),
    )
    @mock.patch(
        "safe_cli.operators.hw_accounts.ledger_manager.LedgerManager.get_address",
        autospec=True,
    )
    def test_get_accounts(
        self, mock_get_address: MagicMock, mock_init_dongle: MagicMock
    ):
        hw_account_manager = HwAccountManager()
        addresses = [Account.create().address, Account.create().address]
        derivation_paths = ["44'/60'/0'/0/0", "44'/60'/1'/0/0"]
        mock_get_address.side_effect = addresses
        # Choosing LEDGER because function is mocked for LEDGER
        hw_accounts = hw_account_manager.get_accounts(
            HwWalletType.LEDGER, number_accounts=2
        )
        self.assertEqual(len(hw_accounts), 2)
        for hw_account, expected_address, expected_derivation_path in zip(
            hw_accounts, addresses, derivation_paths
        ):
            address, derivation_path = hw_account
            self.assertEqual(expected_address, address)
            self.assertEqual(expected_derivation_path, derivation_path)

    @mock.patch(
        "safe_cli.operators.hw_accounts.ledger_manager.init_dongle",
        autospec=True,
        return_value=Dongle(),
    )
    @mock.patch(
        "safe_cli.operators.hw_accounts.ledger_manager.LedgerManager.get_address",
        autospec=True,
    )
    def test_add_account(
        self, mock_get_address: MagicMock, mock_init_dongle: MagicMock
    ):
        hw_account_manager = HwAccountManager()
        derivation_path = "44'/60'/0'/0"
        account_address = Account.create().address
        mock_get_address.return_value = account_address

        self.assertEqual(len(hw_account_manager.accounts), 0)
        # Choosing LEDGER because function is mocked for LEDGER
        self.assertEqual(
            hw_account_manager.add_account(HwWalletType.LEDGER, derivation_path),
            account_address,
        )

        self.assertEqual(len(hw_account_manager.accounts), 1)
        ledger_manager = list(hw_account_manager.accounts)[0]
        self.assertEqual(ledger_manager.address, account_address)
        self.assertEqual(ledger_manager.derivation_path, derivation_path)
        # Shouldn't duplicate accounts
        self.assertEqual(
            hw_account_manager.add_account(HwWalletType.LEDGER, derivation_path),
            account_address,
        )
        self.assertEqual(len(hw_account_manager.accounts), 1)

        # Should accept derivation paths starting with master
        master_derivation_path = "m/44'/60'/0'/0"
        self.assertEqual(
            hw_account_manager.add_account(HwWalletType.LEDGER, master_derivation_path),
            account_address,
        )

    @mock.patch(
        "safe_cli.operators.hw_accounts.ledger_manager.init_dongle",
        autospec=True,
        return_value=Dongle(),
    )
    @mock.patch(
        "safe_cli.operators.hw_accounts.ledger_manager.LedgerManager.get_address",
        autospec=True,
    )
    def test_delete_account(
        self, mock_get_address: MagicMock, mock_init_dongle: MagicMock
    ):
        hw_account_manager = HwAccountManager()
        random_address = Account.create().address
        random_address_2 = Account.create().address
        self.assertEqual(len(hw_account_manager.accounts), 0)
        self.assertEqual(len(hw_account_manager.delete_accounts([random_address])), 0)

        mock_get_address.return_value = random_address_2
        hw_account_manager.accounts.add(LedgerManager("44'/60'/0'/0"))
        self.assertEqual(len(hw_account_manager.delete_accounts([random_address])), 0)
        self.assertEqual(len(hw_account_manager.accounts), 1)
        self.assertEqual(len(hw_account_manager.delete_accounts([])), 0)

        mock_get_address.return_value = random_address
        hw_account_manager.accounts.add(LedgerManager("44'/60'/0'/1"))
        self.assertEqual(len(hw_account_manager.accounts), 2)
        self.assertEqual(len(hw_account_manager.delete_accounts([random_address])), 1)
        self.assertEqual(len(hw_account_manager.accounts), 1)
        hw_account_manager.accounts.add(LedgerManager("44'/60'/0'/1"))
        self.assertEqual(len(hw_account_manager.accounts), 2)
        self.assertEqual(
            len(hw_account_manager.delete_accounts([random_address, random_address_2])),
            2,
        )
        self.assertEqual(len(hw_account_manager.accounts), 0)
