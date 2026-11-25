"""
Trezor support on top of `trezorlib` 0.20 (clients, sessions and callbacks).

- PIN: the Model One asks the host for the PIN as positions on a scrambled
  matrix shown on the device. The other models take it on the device screen.
- Passphrase: typed on the device when it supports it (`PassphraseEntry`
  capability), otherwise on the host. An empty passphrase opens the standard
  wallet.
- Pairing: new models pair through the Trezor Host Protocol. The first
  connection shows a code on the device that must be typed on the host.
- EIP-712: the Model One only signs the domain and message hashes. The other
  models get the full typed data, so every SafeTx field is shown on the device.

`TREZOR_PATH` selects the transport (e.g. `udp:127.0.0.1:21324` for the
emulator). Without it the first connected device is used.
"""

from functools import cache, wraps
from typing import Any

import rlp
from eth_typing import ChecksumAddress
from hexbytes import HexBytes
from prompt_toolkit import HTML, print_formatted_text, prompt
from safe_eth.eth.eip712 import eip712_encode
from safe_eth.eth.utils import fast_to_checksum_address
from safe_eth.safe.signatures import signature_split, signature_to_bytes
from trezorlib import messages, models, tools
from trezorlib.client import (
    Session,
    TrezorClient,
    get_default_client,
    get_default_session as get_trezor_default_session,
)
from trezorlib.ethereum import (
    get_address,
    sign_message,
    sign_tx,
    sign_tx_eip1559,
    sign_typed_data,
    sign_typed_data_hash,
)
from trezorlib.exceptions import Cancelled, InvalidSessionError
from trezorlib.transport import TransportException
from web3.types import TxParams

from .hw_wallet import HwWallet
from .trezor_exceptions import raise_trezor_exception_as_hw_wallet_exception

APP_NAME = "Safe CLI"


def cancel_pin(reason: str):
    """
    trezorlib only cancels the PIN flow on the device for `Cancelled`. Any other
    error leaves the device waiting for a PIN, and the next call fails.
    """
    print_formatted_text(HTML(f"<ansired>{reason}</ansired>"))
    raise Cancelled()


def ask_pin(request: messages.PinMatrixRequest) -> str:
    if request.type in (
        messages.PinMatrixRequestType.NewFirst,
        messages.PinMatrixRequestType.NewSecond,
    ):
        cancel_pin("Trezor asks to set a new PIN, do it in Trezor Suite")
    pin = prompt(
        "Enter the Trezor PIN using the matrix positions shown on the device "
        "(7 8 9 / 4 5 6 / 1 2 3): ",
        is_password=True,
    )
    if not pin or any(digit not in "123456789" for digit in pin):
        cancel_pin("The PIN must be matrix positions, digits 1 to 9")
    return pin


def ask_passphrase() -> str:
    return prompt(
        "Enter the Trezor passphrase (empty for the standard wallet): ",
        is_password=True,
    )


def ask_pairing_code() -> str:
    return prompt("Enter the pairing code shown on the Trezor: ")


@cache
def get_trezor_client() -> TrezorClient:
    """
    Cached to share one connection between all the TrezorWallet instances.

    :return: client for the connected Trezor
    """
    return get_default_client(
        APP_NAME, pin_callback=ask_pin, code_entry_callback=ask_pairing_code
    )


@cache
def get_trezor_session() -> Session:
    """
    Cached so the passphrase is asked once and every derivation path uses the
    same wallet.

    :return: session for the standard or the passphrase wallet
    """
    return get_trezor_default_session(
        get_trezor_client(), passphrase_callback=ask_passphrase
    )


def forget_trezor() -> None:
    get_trezor_session.cache_clear()
    get_trezor_client.cache_clear()


def trezor_call(function):
    """
    Map Trezor errors to HardwareWalletException.

    - An unplugged Trezor leaves a dead client and session in the cache, so they
      are dropped and the next call connects again.
    - A session becomes invalid when the device locks or restarts. The call is
      retried once with a new session, which asks for PIN and passphrase again.
    """

    @wraps(function)
    @raise_trezor_exception_as_hw_wallet_exception
    def wrapper(*args, **kwargs):
        try:
            try:
                return function(*args, **kwargs)
            except InvalidSessionError:
                get_trezor_session.cache_clear()
                return function(*args, **kwargs)
        except (TransportException, InvalidSessionError):
            forget_trezor()
            raise

    return wrapper


def typed_data_for_trezor(value: Any) -> Any:
    """
    trezorlib encodes `bytes` fields from hex strings. It walks the declared
    `types` itself, so keys that are not declared never reach the device.

    :param value: EIP-712 typed data, or a part of it
    :return: the same data with bytes values as hex strings
    """
    if isinstance(value, dict):
        return {key: typed_data_for_trezor(item) for key, item in value.items()}
    if isinstance(value, list):
        return [typed_data_for_trezor(item) for item in value]
    if isinstance(value, (bytes, bytearray, memoryview)):
        return "0x" + bytes(value).hex()
    return value


class TrezorWallet(HwWallet):
    def __init__(self, derivation_path: str):
        self.address_n = tools.parse_path(derivation_path)
        super().__init__(derivation_path)

    @property
    def client(self) -> TrezorClient:
        return get_trezor_client()

    @property
    def session(self) -> Session:
        return get_trezor_session()

    def is_legacy_model(self) -> bool:
        return self.client.model in models.LEGACY_MODELS

    @trezor_call
    def get_address(self) -> ChecksumAddress:
        """
        :return: public address for derivation_path
        """
        return fast_to_checksum_address(
            get_address(self.session, self.address_n, show_display=False)
        )

    @trezor_call
    def sign_typed_hash(self, domain_hash: bytes, message_hash: bytes) -> bytes:
        """

        :param domain_hash:
        :param message_hash:
        :return: signature bytes
        """
        signed = sign_typed_data_hash(
            self.session,
            self.address_n,
            domain_hash,
            message_hash,
        )
        return signed.signature

    @trezor_call
    def sign_typed_data(self, typed_data: dict[str, Any]) -> bytes:
        """
        The Model One cannot parse typed data, so it signs the hashes. The other
        models show every field, and also the message hash the CLI prints.

        :param typed_data: EIP-712 typed data
        :return: signature bytes
        """
        if self.is_legacy_model():
            return super().sign_typed_data(typed_data)
        _, _, message_hash = eip712_encode(typed_data)
        signed = sign_typed_data(
            self.session,
            self.address_n,
            typed_data_for_trezor(typed_data),
            metamask_v4_compat=True,
            show_message_hash=message_hash,
        )
        return signed.signature

    @trezor_call
    def get_signed_raw_transaction(
        self, tx_parameters: TxParams, chain_id: int
    ) -> bytes:
        """

        :param chain_id:
        :param tx_parameters:
        :return: raw transaction signed
        """
        if tx_parameters.get("maxPriorityFeePerGas"):
            # EIP1559
            v, r, s = sign_tx_eip1559(
                self.session,
                self.address_n,
                nonce=tx_parameters["nonce"],
                gas_limit=tx_parameters["gas"],
                to=tx_parameters["to"],
                value=tx_parameters["value"],
                data=HexBytes(tx_parameters["data"]),
                chain_id=chain_id,
                max_gas_fee=tx_parameters.get("maxFeePerGas"),
                max_priority_fee=tx_parameters.get("maxPriorityFeePerGas"),
            )

            encoded_transaction = HexBytes(
                "0x02"
                + rlp.encode(
                    [
                        chain_id,
                        tx_parameters["nonce"],
                        tx_parameters.get("maxPriorityFeePerGas"),
                        tx_parameters.get("maxFeePerGas"),
                        tx_parameters["gas"],
                        HexBytes(tx_parameters["to"]),
                        tx_parameters["value"],
                        HexBytes(tx_parameters["data"]),
                        [],
                        v,
                        HexBytes(r),
                        HexBytes(s),
                    ]
                ).hex()
            )
        else:
            # Legacy transaction
            v, r, s = sign_tx(
                self.session,
                self.address_n,
                nonce=tx_parameters["nonce"],
                gas_price=tx_parameters["gasPrice"],
                gas_limit=tx_parameters["gas"],
                to=tx_parameters["to"],
                value=tx_parameters["value"],
                data=HexBytes(tx_parameters["data"]),
                chain_id=chain_id,
            )

            encoded_transaction = rlp.encode(
                [
                    tx_parameters["nonce"],
                    tx_parameters["gasPrice"],
                    tx_parameters["gas"],
                    HexBytes(tx_parameters["to"]),
                    tx_parameters["value"],
                    HexBytes(tx_parameters["data"]),
                    v,
                    HexBytes(r),
                    HexBytes(s),
                ]
            )

        return encoded_transaction

    @trezor_call
    def sign_message(self, message: bytes) -> bytes:
        """
        Call sign message of Trezor wallet

        :param message:
        :return: bytes signature
        """
        signed = sign_message(self.session, self.address_n, message)
        # V field must be greater than 30 for signed messages. https://github.com/safe-global/safe-smart-account/blob/main/contracts/Safe.sol#L309
        v, r, s = signature_split(signed.signature)
        return signature_to_bytes(v + 4, r, s)
