import os
import unittest
from unittest import mock
from unittest.mock import MagicMock

from eth_account import Account
from hexbytes import HexBytes
from trezorlib.client import TrezorClient
from trezorlib.exceptions import Cancelled, OutdatedFirmwareError, PinException
from trezorlib.messages import EthereumTypedDataSignature
from trezorlib.transport import TransportException
from trezorlib.ui import ClickUI

from gnosis.eth.eip712 import eip712_encode
from gnosis.safe import SafeTx
from gnosis.safe.tests.safe_test_case import SafeTestCaseMixin

from safe_cli.operators.exceptions import HardwareWalletException
from safe_cli.operators.hw_wallets.trezor_wallet import TrezorWallet


class TestTrezorManager(SafeTestCaseMixin, unittest.TestCase):
    @mock.patch(
        "safe_cli.operators.hw_wallets.trezor_wallet.get_trezor_client",
        return_value=None,
    )
    @mock.patch(
        "safe_cli.operators.hw_wallets.trezor_wallet.get_address",
        return_value=None,
    )
    def test_setup_trezor_wallet(
        self, mock_trezor_client: MagicMock, mock_get_address: MagicMock
    ):
        trezor_wallet = TrezorWallet("44'/60'/0'/0")
        self.assertIsNone(trezor_wallet.client)

    @mock.patch(
        "safe_cli.operators.hw_wallets.trezor_wallet.sign_typed_data_hash",
        autospec=True,
    )
    @mock.patch(
        "safe_cli.operators.hw_wallets.trezor_wallet.get_address",
        autospec=True,
    )
    @mock.patch(
        "safe_cli.operators.hw_wallets.trezor_wallet.get_trezor_client",
        autospec=True,
    )
    def test_hw_device_exception(
        self,
        mock_trezor_client: MagicMock,
        mock_trezor_get_address: MagicMock,
        mock_trezor_sign: MagicMock,
    ):
        derivation_path = "44'/60'/0'/0"
        transport_mock = MagicMock(auto_spec=True)
        mock_trezor_client.return_value = TrezorClient(
            transport_mock, ui=ClickUI(), _init_device=False
        )
        mock_trezor_client.return_value.is_outdated = MagicMock(return_value=False)
        random_domain_bytes = os.urandom(32)
        random_message_bytes = os.urandom(32)

        mock_trezor_get_address.side_effect = TransportException
        with self.assertRaises(HardwareWalletException):
            TrezorWallet(derivation_path)

        mock_trezor_get_address.side_effect = PinException
        with self.assertRaises(HardwareWalletException):
            TrezorWallet(derivation_path)

        mock_trezor_get_address.side_effect = Cancelled
        with self.assertRaises(HardwareWalletException):
            TrezorWallet(derivation_path)

        mock_trezor_get_address.side_effect = OutdatedFirmwareError
        with self.assertRaises(HardwareWalletException):
            TrezorWallet(derivation_path)

        mock_trezor_get_address.side_effect = None
        mock_trezor_get_address.return_value = Account.create().address
        mock_trezor_sign.side_effect = TransportException
        with self.assertRaises(HardwareWalletException):
            trezor_wallet = TrezorWallet(derivation_path)
            trezor_wallet.sign_typed_hash(random_domain_bytes, random_message_bytes)

        mock_trezor_sign.side_effect = PinException
        with self.assertRaises(HardwareWalletException):
            trezor_wallet = TrezorWallet(derivation_path)
            trezor_wallet.sign_typed_hash(random_domain_bytes, random_message_bytes)

        mock_trezor_sign.side_effect = Cancelled
        with self.assertRaises(HardwareWalletException):
            trezor_wallet = TrezorWallet(derivation_path)
            trezor_wallet.sign_typed_hash(random_domain_bytes, random_message_bytes)

        mock_trezor_sign.side_effect = OutdatedFirmwareError
        with self.assertRaises(HardwareWalletException):
            trezor_wallet = TrezorWallet(derivation_path)
            trezor_wallet.sign_typed_hash(random_domain_bytes, random_message_bytes)

    @mock.patch(
        "safe_cli.operators.hw_wallets.trezor_wallet.get_address",
        autospec=True,
    )
    @mock.patch(
        "safe_cli.operators.hw_wallets.trezor_wallet.get_trezor_client",
        autospec=True,
    )
    def test_sign_typed_hash(
        self, mock_trezor_client: MagicMock, mock_get_address: MagicMock
    ):
        owner = Account.create()
        to = Account.create()
        transport_mock = MagicMock(auto_spec=True)
        mock_trezor_client.return_value = TrezorClient(
            transport_mock, ui=ClickUI(), _init_device=False
        )
        mock_trezor_client.return_value.is_outdated = MagicMock(return_value=False)
        mock_get_address.return_value = owner.address
        trezor_wallet = TrezorWallet("44'/60'/0'/0")

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

        trezor_return_signature = EthereumTypedDataSignature(
            signature=expected_signature, address=trezor_wallet.address
        )
        mock_trezor_client.return_value.call = MagicMock(
            return_value=trezor_return_signature
        )
        signature = trezor_wallet.sign_typed_hash(encode_hash[1], encode_hash[2])
        self.assertEqual(expected_signature, signature)

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
    @mock.patch(
        "safe_cli.operators.hw_wallets.trezor_wallet.get_trezor_client",
        autospec=True,
    )
    def test_get_signed_raw_transaction(
        self,
        mock_trezor_client: MagicMock,
        mock_get_address: MagicMock,
        mock_sign_tx_eip1559: MagicMock,
        mock_sign_tx: MagicMock,
    ):
        owner = Account.create()
        to = Account.create()
        transport_mock = MagicMock(auto_spec=True)
        mock_trezor_client.return_value = TrezorClient(
            transport_mock, ui=ClickUI(), _init_device=False
        )
        mock_trezor_client.return_value.is_outdated = MagicMock(return_value=False)
        mock_get_address.return_value = owner.address
        trezor_wallet = TrezorWallet("44'/60'/0'/0")

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
        self.assertEqual(signed_fields.rawTransaction, HexBytes(raw_signed_tx))

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
        self.assertEqual(signed_fields.rawTransaction, HexBytes(raw_signed_tx))
