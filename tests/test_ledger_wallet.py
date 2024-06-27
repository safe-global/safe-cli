import os
import unittest
from unittest import mock
from unittest.mock import MagicMock

from eth_account import Account
from hexbytes import HexBytes
from ledgerblue.Dongle import Dongle
from ledgereth.exceptions import (
    LedgerAppNotOpened,
    LedgerCancel,
    LedgerLocked,
    LedgerNotFound,
)
from ledgereth.objects import LedgerAccount, SignedMessage, SignedTransaction

from gnosis.eth.eip712 import eip712_encode
from gnosis.safe import SafeTx
from gnosis.safe.signatures import signature_split
from gnosis.safe.tests.safe_test_case import SafeTestCaseMixin

from safe_cli.operators.exceptions import HardwareWalletException
from safe_cli.operators.hw_wallets.ledger_wallet import LedgerWallet


class Testledger_wallet(SafeTestCaseMixin, unittest.TestCase):
    @mock.patch(
        "safe_cli.operators.hw_wallets.ledger_wallet.init_dongle",
        return_value=Dongle(),
    )
    def test_setup_ledger_wallet(self, mock_init_dongle: MagicMock):
        derivation_path = "44'/60'/0'/0"
        address = Account.create().address
        with self.assertRaises(HardwareWalletException):
            LedgerWallet(derivation_path)
        with mock.patch(
            "safe_cli.operators.hw_wallets.ledger_wallet.get_account_by_path",
            return_value=LedgerAccount(derivation_path, address),
        ):
            ledger_wallet = LedgerWallet(derivation_path)
            self.assertIsNotNone(ledger_wallet.dongle)
            self.assertEqual(ledger_wallet.address, address)

    @mock.patch(
        "safe_cli.operators.hw_wallets.ledger_wallet.sign_typed_data_draft",
        autospec=True,
    )
    @mock.patch(
        "safe_cli.operators.hw_wallets.ledger_wallet.get_account_by_path",
        autospec=True,
    )
    @mock.patch(
        "safe_cli.operators.hw_wallets.ledger_wallet.init_dongle",
        return_value=Dongle(),
    )
    def test_hw_device_exception(
        self,
        mock_init_dongle: MagicMock,
        mock_get_account_by_path: MagicMock,
        mock_sign: MagicMock,
    ):
        derivation_path = "44'/60'/0'/0"
        address = Account.create().address
        random_domain_bytes = os.urandom(32)
        random_message_bytes = os.urandom(32)
        mock_get_account_by_path.side_effect = LedgerNotFound
        with self.assertRaises(HardwareWalletException):
            LedgerWallet(derivation_path)

        mock_get_account_by_path.side_effect = LedgerLocked
        with self.assertRaises(HardwareWalletException):
            LedgerWallet(derivation_path)

        mock_get_account_by_path.side_effect = LedgerAppNotOpened
        with self.assertRaises(HardwareWalletException):
            LedgerWallet(derivation_path)

        # Test sign exceptions
        mock_get_account_by_path.side_effect = None
        mock_get_account_by_path.return_value = LedgerAccount(derivation_path, address)
        mock_sign.side_effect = LedgerNotFound
        with self.assertRaises(HardwareWalletException):
            ledger_wallet = LedgerWallet(derivation_path)
            ledger_wallet.sign_typed_hash(random_domain_bytes, random_message_bytes)

        mock_sign.side_effect = LedgerLocked
        with self.assertRaises(HardwareWalletException):
            ledger_wallet = LedgerWallet(derivation_path)
            ledger_wallet.sign_typed_hash(random_domain_bytes, random_message_bytes)

        mock_sign.side_effect = LedgerAppNotOpened
        with self.assertRaises(HardwareWalletException):
            ledger_wallet = LedgerWallet(derivation_path)
            ledger_wallet.sign_typed_hash(random_domain_bytes, random_message_bytes)

        mock_sign.side_effect = LedgerCancel
        with self.assertRaises(HardwareWalletException):
            ledger_wallet = LedgerWallet(derivation_path)
            ledger_wallet.sign_typed_hash(random_domain_bytes, random_message_bytes)

    @mock.patch(
        "safe_cli.operators.hw_wallets.ledger_wallet.get_account_by_path",
        autospec=True,
    )
    @mock.patch(
        "safe_cli.operators.hw_wallets.ledger_wallet.init_dongle",
        autospec=True,
        return_value=Dongle(),
    )
    def test_sign_typed_hash(
        self, mock_init_dongle: MagicMock, mock_get_account_by_path: MagicMock
    ):
        owner = Account.create()
        to = Account.create()
        derivation_path = "44'/60'/0'/0"
        mock_get_account_by_path.return_value = LedgerAccount(
            derivation_path, owner.address
        )
        ledger_wallet = LedgerWallet(derivation_path)

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
        expected_signature = safe_tx.sign(owner.key)
        # We need to split to change the bytes signature order to v + r + s like ledger return signature
        v, r, s = signature_split(expected_signature)

        ledger_return_signature = (
            v.to_bytes(1, byteorder="big")
            + r.to_bytes(32, byteorder="big")
            + s.to_bytes(32, byteorder="big")
        )
        mock_init_dongle.return_value.exchange = MagicMock(
            return_value=ledger_return_signature
        )
        signature = ledger_wallet.sign_typed_hash(encode_hash[1], encode_hash[2])
        self.assertEqual(expected_signature, signature)

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

    @mock.patch(
        "safe_cli.operators.hw_wallets.ledger_wallet.create_transaction",
        autospec=True,
        return_value=Dongle(),
    )
    @mock.patch(
        "safe_cli.operators.hw_wallets.ledger_wallet.get_account_by_path",
        autospec=True,
    )
    @mock.patch(
        "safe_cli.operators.hw_wallets.ledger_wallet.init_dongle",
        autospec=True,
        return_value=Dongle(),
    )
    def test_get_signed_raw_transaction(
        self,
        mock_init_dongle: MagicMock,
        mock_get_account_by_path: MagicMock,
        mock_ledger_create_transaction: MagicMock,
    ):
        owner = Account.create()
        to = Account.create()
        derivation_path = "44'/60'/0'/0"
        mock_get_account_by_path.return_value = LedgerAccount(
            derivation_path, owner.address
        )
        ledger_wallet = LedgerWallet(derivation_path)
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

        raw_signed_tx = ledger_wallet.get_signed_raw_transaction(
            safe_tx.tx, safe_tx.ethereum_client.get_chain_id()
        )  # return raw signed transaction
        self.assertEqual(signed_fields.rawTransaction, HexBytes(raw_signed_tx))

    @mock.patch(
        "safe_cli.operators.hw_wallets.ledger_wallet.sign_message",
        autospec=True,
        return_value=Dongle(),
    )
    @mock.patch(
        "safe_cli.operators.hw_wallets.ledger_wallet.get_account_by_path",
        autospec=True,
    )
    @mock.patch(
        "safe_cli.operators.hw_wallets.ledger_wallet.init_dongle",
        autospec=True,
        return_value=Dongle(),
    )
    def test_sign_message(
        self,
        mock_init_dongle: MagicMock,
        mock_get_account_by_path: MagicMock,
        mock_ledger_sign_message: MagicMock,
    ):
        owner = Account.create()
        derivation_path = "44'/60'/0'/0"
        mock_get_account_by_path.return_value = LedgerAccount(
            derivation_path, owner.address
        )
        ledger_wallet = LedgerWallet(derivation_path)
        expected_signature = HexBytes(
            "0xbc941061f14cfbf055332537a282834dd66f4e944b3b4608aea062e203c7fd505b5e74c0a984d62ec088cd1d82c00d7c6f5f71076d6bc536fcc02be463d9128820"
        )
        safe_message_hash = HexBytes(
            "0x08a1b4472ed4f7f71ac2a8ec9978da670476b3675720b8c4e11fe71a75b56f38"
        )
        v, r, s = signature_split(expected_signature)
        # Checking that v is incremented by sign_message by 4
        mock_ledger_sign_message.return_value = SignedMessage(
            safe_message_hash, v - 4, r, s
        )

        signature = ledger_wallet.sign_message(safe_message_hash)
        self.assertEqual(signature, expected_signature)
