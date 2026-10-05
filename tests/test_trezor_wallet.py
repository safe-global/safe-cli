import os
import unittest
from unittest import mock
from unittest.mock import MagicMock

from eth_account import Account
from hexbytes import HexBytes
from safe_eth.eth.eip712 import eip712_encode
from safe_eth.safe import SafeTx
from safe_eth.safe.signatures import signature_split, signature_to_bytes
from safe_eth.safe.tests.safe_test_case import SafeTestCaseMixin
from trezorlib import messages, models
from trezorlib.exceptions import (
    Cancelled,
    InvalidSessionError,
    OutdatedFirmwareError,
    PassphraseError,
    PinException,
    TrezorException,
)
from trezorlib.messages import EthereumTypedDataSignature
from trezorlib.transport import DeviceIsBusy, TransportException

from safe_cli.operators.exceptions import HardwareWalletException
from safe_cli.operators.hw_wallets import trezor_wallet as trezor_wallet_module
from safe_cli.operators.hw_wallets.trezor_wallet import (
    TrezorWallet,
    ask_pin,
    get_trezor_session,
    typed_data_for_trezor,
)


def trezor_client_mock(model: models.TrezorModel = models.T2T1) -> MagicMock:
    client = MagicMock()
    client.model = model
    return client


@mock.patch(
    "safe_cli.operators.hw_wallets.trezor_wallet.get_trezor_session",
    autospec=True,
)
@mock.patch(
    "safe_cli.operators.hw_wallets.trezor_wallet.get_trezor_client",
    autospec=True,
)
class TestTrezorManager(SafeTestCaseMixin, unittest.TestCase):
    def build_safe_tx(self, owner_address: str) -> SafeTx:
        safe = self.deploy_test_safe(
            owners=[owner_address],
            threshold=1,
            initial_funding_wei=self.w3.to_wei(0.1, "ether"),
        )
        return SafeTx(
            self.ethereum_client,
            safe.address,
            Account.create().address,
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

    @mock.patch(
        "safe_cli.operators.hw_wallets.trezor_wallet.get_address",
        return_value=Account.create().address,
    )
    def test_setup_trezor_wallet(
        self,
        mock_get_address: MagicMock,
        mock_trezor_client: MagicMock,
        mock_trezor_session: MagicMock,
    ):
        mock_trezor_client.return_value = None
        trezor_wallet = TrezorWallet("44'/60'/0'/0")
        self.assertIsNone(trezor_wallet.client)
        self.assertEqual(trezor_wallet.address, mock_get_address.return_value)
        mock_get_address.assert_called_once_with(
            mock_trezor_session.return_value,
            trezor_wallet.address_n,
            show_display=False,
        )

    @mock.patch(
        "safe_cli.operators.hw_wallets.trezor_wallet.forget_trezor",
        autospec=True,
    )
    @mock.patch(
        "safe_cli.operators.hw_wallets.trezor_wallet.sign_typed_data_hash",
        autospec=True,
    )
    @mock.patch(
        "safe_cli.operators.hw_wallets.trezor_wallet.get_address",
        autospec=True,
    )
    def test_hw_device_exception(
        self,
        mock_trezor_get_address: MagicMock,
        mock_trezor_sign: MagicMock,
        mock_forget_trezor: MagicMock,
        mock_trezor_client: MagicMock,
        mock_trezor_session: MagicMock,
    ):
        derivation_path = "44'/60'/0'/0"
        mock_trezor_client.return_value = trezor_client_mock()
        random_domain_bytes = os.urandom(32)
        random_message_bytes = os.urandom(32)

        for exception in (
            TransportException,
            DeviceIsBusy,
            PinException(None, "Wrong PIN"),
            PassphraseError("Passphrase protection is disabled on this device."),
            Cancelled,
            OutdatedFirmwareError,
            TrezorException("Unexpected"),
        ):
            with self.subTest(exception=exception):
                mock_trezor_get_address.side_effect = exception
                with self.assertRaises(HardwareWalletException):
                    TrezorWallet(derivation_path)

        mock_trezor_get_address.side_effect = None
        mock_trezor_get_address.return_value = Account.create().address
        trezor_wallet = TrezorWallet(derivation_path)
        for exception in (
            TransportException,
            PinException(None, "Wrong PIN"),
            Cancelled,
            OutdatedFirmwareError,
        ):
            with self.subTest(exception=exception):
                mock_trezor_sign.side_effect = exception
                with self.assertRaises(HardwareWalletException):
                    trezor_wallet.sign_typed_hash(
                        random_domain_bytes, random_message_bytes
                    )

        # Only a lost connection drops the cached client and session
        self.assertEqual(mock_forget_trezor.call_count, 3)

    @mock.patch(
        "safe_cli.operators.hw_wallets.trezor_wallet.forget_trezor",
        autospec=True,
    )
    @mock.patch(
        "safe_cli.operators.hw_wallets.trezor_wallet.get_address",
        autospec=True,
    )
    def test_invalid_session_is_retried(
        self,
        mock_trezor_get_address: MagicMock,
        mock_forget_trezor: MagicMock,
        mock_trezor_client: MagicMock,
        mock_trezor_session: MagicMock,
    ):
        address = Account.create().address
        # The device locked: the session is dropped and the call runs again
        mock_trezor_get_address.side_effect = [InvalidSessionError(b"id"), address]
        self.assertEqual(TrezorWallet("44'/60'/0'/0").address, address)
        mock_trezor_session.cache_clear.assert_called_once()
        mock_forget_trezor.assert_not_called()

        # Invalid again: everything is dropped and the error is reported
        mock_trezor_get_address.side_effect = InvalidSessionError(b"id")
        with self.assertRaises(HardwareWalletException):
            TrezorWallet("44'/60'/0'/0")
        mock_forget_trezor.assert_called_once()

    @mock.patch(
        "safe_cli.operators.hw_wallets.trezor_wallet.sign_typed_data_hash",
        autospec=True,
    )
    @mock.patch(
        "safe_cli.operators.hw_wallets.trezor_wallet.get_address",
        autospec=True,
    )
    def test_sign_typed_hash(
        self,
        mock_get_address: MagicMock,
        mock_sign_typed_data_hash: MagicMock,
        mock_trezor_client: MagicMock,
        mock_trezor_session: MagicMock,
    ):
        owner = Account.create()
        mock_trezor_client.return_value = trezor_client_mock()
        mock_get_address.return_value = owner.address
        trezor_wallet = TrezorWallet("44'/60'/0'/0")

        safe_tx = self.build_safe_tx(owner.address)
        encode_hash = eip712_encode(safe_tx.eip712_structured_data)
        expected_signature = safe_tx.sign(owner.key)
        mock_sign_typed_data_hash.return_value = EthereumTypedDataSignature(
            signature=expected_signature, address=trezor_wallet.address
        )
        signature = trezor_wallet.sign_typed_hash(encode_hash[1], encode_hash[2])
        self.assertEqual(expected_signature, signature)
        mock_sign_typed_data_hash.assert_called_once_with(
            mock_trezor_session.return_value,
            trezor_wallet.address_n,
            encode_hash[1],
            encode_hash[2],
        )

    @mock.patch(
        "safe_cli.operators.hw_wallets.trezor_wallet.sign_typed_data_hash",
        autospec=True,
    )
    @mock.patch(
        "safe_cli.operators.hw_wallets.trezor_wallet.sign_typed_data",
        autospec=True,
    )
    @mock.patch(
        "safe_cli.operators.hw_wallets.trezor_wallet.get_address",
        autospec=True,
    )
    def test_sign_typed_data(
        self,
        mock_get_address: MagicMock,
        mock_sign_typed_data: MagicMock,
        mock_sign_typed_data_hash: MagicMock,
        mock_trezor_client: MagicMock,
        mock_trezor_session: MagicMock,
    ):
        owner = Account.create()
        mock_get_address.return_value = owner.address
        safe_tx = self.build_safe_tx(owner.address)
        typed_data = safe_tx.eip712_structured_data
        _, domain_hash, message_hash = eip712_encode(typed_data)
        expected_signature = safe_tx.sign(owner.key)
        trezor_signature = EthereumTypedDataSignature(
            signature=expected_signature, address=owner.address
        )
        mock_sign_typed_data.return_value = trezor_signature
        mock_sign_typed_data_hash.return_value = trezor_signature

        # Model T and newer get every field
        mock_trezor_client.return_value = trezor_client_mock(models.T2T1)
        trezor_wallet = TrezorWallet("44'/60'/0'/0")
        self.assertEqual(trezor_wallet.sign_typed_data(typed_data), expected_signature)
        mock_sign_typed_data.assert_called_once_with(
            mock_trezor_session.return_value,
            trezor_wallet.address_n,
            typed_data_for_trezor(typed_data),
            metamask_v4_compat=True,
            show_message_hash=message_hash,
        )
        mock_sign_typed_data_hash.assert_not_called()

        # Model One only gets the hashes
        mock_sign_typed_data.reset_mock()
        mock_trezor_client.return_value = trezor_client_mock(models.T1B1)
        trezor_wallet = TrezorWallet("44'/60'/0'/0")
        self.assertEqual(trezor_wallet.sign_typed_data(typed_data), expected_signature)
        mock_sign_typed_data.assert_not_called()
        mock_sign_typed_data_hash.assert_called_once_with(
            mock_trezor_session.return_value,
            trezor_wallet.address_n,
            domain_hash,
            message_hash,
        )

    @mock.patch(
        "safe_cli.operators.hw_wallets.trezor_wallet.sign_tx",
        autospec=True,
    )
    @mock.patch(
        "safe_cli.operators.hw_wallets.trezor_wallet.sign_tx_eip1559",
        autospec=True,
    )
    @mock.patch(
        "safe_cli.operators.hw_wallets.trezor_wallet.get_address",
        autospec=True,
    )
    def test_get_signed_raw_transaction(
        self,
        mock_get_address: MagicMock,
        mock_sign_tx_eip1559: MagicMock,
        mock_sign_tx: MagicMock,
        mock_trezor_client: MagicMock,
        mock_trezor_session: MagicMock,
    ):
        owner = Account.create()
        mock_trezor_client.return_value = trezor_client_mock()
        mock_get_address.return_value = owner.address
        trezor_wallet = TrezorWallet("44'/60'/0'/0")

        safe_tx = self.build_safe_tx(owner.address)
        safe_tx.sign(owner.key)
        # Legacy transaction
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

        mock_sign_tx.return_value = (
            HexBytes(signed_fields.v),
            HexBytes(signed_fields.r),
            HexBytes(signed_fields.s),
        )

        raw_signed_tx = trezor_wallet.get_signed_raw_transaction(
            safe_tx.tx, safe_tx.ethereum_client.get_chain_id()
        )  # return raw signed transaction
        mock_sign_tx.assert_called_once()
        self.assertEqual(signed_fields.raw_transaction, HexBytes(raw_signed_tx))

        # EIP1559 transaction
        tx_parameters = {
            "from": owner.address,
            "maxPriorityFeePerGas": safe_tx.w3.eth.gas_price,
            "maxFeePerGas": safe_tx.w3.eth.gas_price,
            "nonce": 1,
            "gas": safe_tx.recommended_gas(),
        }
        safe_tx.tx = safe_tx.w3_tx.build_transaction(tx_parameters)
        signed_fields = safe_tx.w3.eth.account.sign_transaction(
            safe_tx.tx, private_key=owner.key
        )

        mock_sign_tx_eip1559.return_value = (
            signed_fields.v,
            HexBytes(signed_fields.r),
            HexBytes(signed_fields.s),
        )
        raw_signed_tx = trezor_wallet.get_signed_raw_transaction(
            safe_tx.tx, safe_tx.ethereum_client.get_chain_id()
        )  # return raw signed transaction
        mock_sign_tx_eip1559.assert_called_once()
        self.assertEqual(signed_fields.raw_transaction, HexBytes(raw_signed_tx))

    @mock.patch(
        "safe_cli.operators.hw_wallets.trezor_wallet.sign_message",
        autospec=True,
    )
    @mock.patch(
        "safe_cli.operators.hw_wallets.trezor_wallet.get_address",
        autospec=True,
    )
    def test_get_sign_message(
        self,
        mock_get_address: MagicMock,
        mock_sign_message: MagicMock,
        mock_trezor_client: MagicMock,
        mock_trezor_session: MagicMock,
    ):
        owner = Account.create()
        mock_trezor_client.return_value = trezor_client_mock()
        mock_get_address.return_value = owner.address
        trezor_wallet = TrezorWallet("44'/60'/0'/0")
        expected_signature = HexBytes(
            "0xbc941061f14cfbf055332537a282834dd66f4e944b3b4608aea062e203c7fd505b5e74c0a984d62ec088cd1d82c00d7c6f5f71076d6bc536fcc02be463d9128820"
        )
        safe_message_hash = HexBytes(
            "0x08a1b4472ed4f7f71ac2a8ec9978da670476b3675720b8c4e11fe71a75b56f38"
        )
        v, r, s = signature_split(expected_signature)
        mock_trezor_signed = MagicMock()
        # Checking that v is incremented by sign_message by 4
        mock_trezor_signed.signature = signature_to_bytes(v - 4, r, s)
        mock_sign_message.return_value = mock_trezor_signed
        signature = trezor_wallet.sign_message(safe_message_hash)
        self.assertEqual(HexBytes(signature), expected_signature)


class TestTrezorHelpers(unittest.TestCase):
    def test_typed_data_for_trezor(self):
        typed_data = {
            "primaryType": "Mail",
            "message": {
                "contents": b"\x01\x02",
                "tags": [b"\xaa" * 32],
                "amount": 5,
                "to": "0x0000000000000000000000000000000000000001",
            },
        }
        self.assertEqual(
            typed_data_for_trezor(typed_data),
            {
                "primaryType": "Mail",
                "message": {
                    "contents": "0x0102",
                    "tags": ["0x" + "aa" * 32],
                    "amount": 5,
                    "to": "0x0000000000000000000000000000000000000001",
                },
            },
        )

    def test_ask_pin(self):
        # Cancelled is what makes trezorlib cancel the PIN flow on the device
        with self.assertRaises(Cancelled):
            ask_pin(
                messages.PinMatrixRequest(type=messages.PinMatrixRequestType.NewFirst)
            )
        current = messages.PinMatrixRequest(type=messages.PinMatrixRequestType.Current)
        for wrong_pin in ("", "105", "12a"):
            with self.subTest(pin=wrong_pin):
                with mock.patch.object(
                    trezor_wallet_module, "prompt", return_value=wrong_pin
                ):
                    with self.assertRaises(Cancelled):
                        ask_pin(current)
        with mock.patch.object(
            trezor_wallet_module, "prompt", return_value="159"
        ) as mock_prompt:
            self.assertEqual(
                ask_pin(
                    messages.PinMatrixRequest(
                        type=messages.PinMatrixRequestType.Current
                    )
                ),
                "159",
            )
            self.assertTrue(mock_prompt.call_args.kwargs["is_password"])

    @mock.patch(
        "safe_cli.operators.hw_wallets.trezor_wallet.get_trezor_default_session",
        autospec=True,
    )
    @mock.patch(
        "safe_cli.operators.hw_wallets.trezor_wallet.get_trezor_client",
        autospec=True,
    )
    def test_get_trezor_session(
        self, mock_trezor_client: MagicMock, mock_default_session: MagicMock
    ):
        get_trezor_session.cache_clear()
        try:
            session = get_trezor_session()
            # Cached: the passphrase is asked only once
            self.assertIs(get_trezor_session(), session)
            mock_default_session.assert_called_once_with(
                mock_trezor_client.return_value,
                passphrase_callback=trezor_wallet_module.ask_passphrase,
            )
        finally:
            get_trezor_session.cache_clear()
