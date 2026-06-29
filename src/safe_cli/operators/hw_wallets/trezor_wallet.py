from functools import cache

import rlp
from eth_typing import ChecksumAddress
from hexbytes import HexBytes
from safe_eth.safe.signatures import signature_split, signature_to_bytes
from trezorlib import tools
from trezorlib.cli import get_code_entry_code, get_passphrase
from trezorlib.cli.ui import ClickUI
from trezorlib.client import (
    Session,
    get_default_client,
    get_default_session,
)
from trezorlib.ethereum import (
    get_address,
    sign_message,
    sign_tx,
    sign_tx_eip1559,
    sign_typed_data_hash,
)
from web3.types import TxParams

from .hw_wallet import HwWallet
from .trezor_exceptions import raise_trezor_exception_as_hw_wallet_exception


@cache
@raise_trezor_exception_as_hw_wallet_exception
def get_trezor_session() -> Session:
    """
    Return a default Trezor session, entering the passphrase on the host unless the device requires on-device entry.
    This method is cached to share the same session between trezor calls while the class is not instantiated.
    :return:
    """
    ui = ClickUI(always_prompt=True)
    client = get_default_client(
        "safe-cli",
        button_callback=ui.button_request,
        pin_callback=ui.get_pin,
        code_entry_callback=get_code_entry_code,
    )
    return get_default_session(client, passphrase_callback=get_passphrase)


class TrezorWallet(HwWallet):
    def __init__(self, derivation_path: str):
        self.session: Session = get_trezor_session()
        self.address_n = tools.parse_path(derivation_path)
        super().__init__(derivation_path)

    @raise_trezor_exception_as_hw_wallet_exception
    def get_address(self) -> ChecksumAddress:
        """
        :return: public address for derivation_path
        """
        return get_address(self.session, n=self.address_n)

    @raise_trezor_exception_as_hw_wallet_exception
    def sign_typed_hash(self, domain_hash: bytes, message_hash: bytes) -> bytes:
        """

        :param domain_hash:
        :param message_hash:
        :return: signature bytes
        """
        signed = sign_typed_data_hash(
            self.session,
            n=self.address_n,
            domain_hash=domain_hash,
            message_hash=message_hash,
        )
        return signed.signature

    @raise_trezor_exception_as_hw_wallet_exception
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
                n=self.address_n,
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
                n=self.address_n,
                nonce=tx_parameters["nonce"],
                gas_price=tx_parameters["gasPrice"],
                gas_limit=tx_parameters["gas"],
                to=tx_parameters["to"],
                value=tx_parameters["value"],
                data=HexBytes(tx_parameters.get("data")),
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

    @raise_trezor_exception_as_hw_wallet_exception
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
