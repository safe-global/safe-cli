import unittest
from unittest import mock
from unittest.mock import MagicMock

from eth_account import Account
from ledgerblue.Dongle import Dongle
from ledgereth.accounts import LedgerAccount
from ledgereth.exceptions import LedgerLocked, LedgerNotFound

from gnosis.eth.eip712 import eip712_encode
from gnosis.safe import SafeTx
from gnosis.safe.signatures import signature_split
from gnosis.safe.tests.safe_test_case import SafeTestCaseMixin

from safe_cli.operators.hw_accounts.ledger_manager import LedgerManager


class TestLedgerManager(SafeTestCaseMixin, unittest.TestCase):
    def test_setup_ledger_manager(self):
        ledger_manager = LedgerManager()
        self.assertIsNone(ledger_manager.dongle)
        self.assertEqual(len(ledger_manager.accounts), 0)
        self.assertEqual(ledger_manager.connected, False)

    @mock.patch("safe_cli.operators.hw_accounts.ledger_manager.init_dongle")
    @mock.patch("safe_cli.operators.hw_accounts.ledger_manager.get_account_by_path")
    def test_connected(
        self, mock_get_account_by_path: MagicMock, mock_init_dongle: MagicMock
    ):
        ledger_manager = LedgerManager()
        mock_init_dongle.side_effect = LedgerNotFound()

        self.assertEqual(ledger_manager.connected, False)

        mock_init_dongle.side_effect = None
        mock_init_dongle.return_value = Dongle()
        mock_get_account_by_path.side_effect = LedgerLocked()

        self.assertEqual(ledger_manager.connected, True)

    @mock.patch(
        "safe_cli.operators.hw_accounts.ledger_manager.LedgerManager.LEDGER_SEARCH_DEEP",
        2,
    )
    @mock.patch(
        "safe_cli.operators.hw_accounts.ledger_manager.get_account_by_path",
        autospec=True,
    )
    def test_get_accounts(self, mock_get_account_by_path: MagicMock):
        ledger_manager = LedgerManager()

        addresses = [Account.create().address, Account.create().address]
        derivation_paths = ["44'/60'/0'/0", "44'/60'/0'/1"]
        mock_get_account_by_path.side_effect = [
            LedgerAccount(derivation_paths[0], addresses[0]),
            LedgerAccount(derivation_paths[1], addresses[1]),
        ]
        ledger_accounts = ledger_manager.get_accounts()
        self.assertEqual(len(ledger_accounts), 2)
        for ledger_account, expected_address, expected_derivation_path in zip(
            ledger_accounts, addresses, derivation_paths
        ):
            ledger_address, ledger_path = ledger_account
            self.assertEqual(expected_address, ledger_address)
            self.assertEqual(expected_derivation_path, ledger_path)

    @mock.patch(
        "safe_cli.operators.hw_accounts.ledger_manager.get_account_by_path",
        autospec=True,
    )
    def test_add_account(self, mock_get_account_by_path: MagicMock):
        ledger_manager = LedgerManager()
        derivation_path = "44'/60'/0'/0"
        account_address = Account.create().address
        mock_get_account_by_path.return_value = LedgerAccount(
            derivation_path, account_address
        )
        self.assertEqual(len(ledger_manager.accounts), 0)

        ledger_manager.add_account(derivation_path)

        self.assertEqual(len(ledger_manager.accounts), 1)
        ledger_account = list(ledger_manager.accounts)[0]
        self.assertEqual(ledger_account.address, account_address)
        self.assertEqual(ledger_account.path, derivation_path)

    @mock.patch(
        "safe_cli.operators.hw_accounts.ledger_manager.init_dongle",
        autospec=True,
        return_value=Dongle(),
    )
    def test_sign_eip712(self, mock_init_dongle: MagicMock):
        ledger_manager = LedgerManager()
        owner = Account.create()
        to = Account.create()
        ledger_account = LedgerAccount("44'/60'/0'/0", owner.address)
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
        encode_hash = eip712_encode(safe_tx.eip712_structured_data)
        # We need to split to change the bytes signature order to v + r + s like ledger return signature
        expected_v, expected_r, expected_s = signature_split(safe_tx.sign(owner.key))

        signature = (
            expected_v.to_bytes(1, byteorder="big")
            + expected_r.to_bytes(32, byteorder="big")
            + expected_s.to_bytes(32, byteorder="big")
        )
        mock_init_dongle.return_value.exchange = MagicMock(return_value=signature)
        v, r, s = signature_split(
            ledger_manager.sign_eip712(encode_hash[1], encode_hash[2], ledger_account)
        )
        self.assertEqual(expected_v, v)
        self.assertEqual(expected_r, r)
        self.assertEqual(expected_s, s)

        # Check that dongle exchange is called with the expected payload
        # https://github.com/LedgerHQ/app-ethereum/blob/master/doc/ethapp.adoc#sign-eth-eip-712
        command = "e00c0000" + "51"  # command + payload length
        payload = (
            "04" + "8000002c8000003c8000000000000000"
        )  # number of derivations + 44'/60'/0'/0
        expected_exchange_payload = (
            bytes.fromhex(command)
            + bytes.fromhex(payload)
            + encode_hash[1]
            + encode_hash[2]
        )
        mock_init_dongle.return_value.exchange.assert_called_once_with(
            expected_exchange_payload
        )
