from functools import lru_cache

import rlp
from eth_typing import ChecksumAddress
from hexbytes import HexBytes
from trezorlib import tools
from trezorlib.client import TrezorClient, get_default_client
from trezorlib.ethereum import (
    get_address,
    sign_tx,
    sign_tx_eip1559,
    sign_typed_data_hash,
)
from trezorlib.ui import ClickUI
from web3.types import TxParams

from .hw_wallet import HwWallet
from .trezor_exceptions import raise_trezor_exception_as_hw_wallet_exception


@lru_cache(maxsize=None)
@raise_trezor_exception_as_hw_wallet_exception
def get_trezor_client() -> TrezorClient:
    """
    Return default trezor configuration that store passphrase on host.
    This method is cached to share the same configuration between trezor calls while the class is not instantiated.
    :return:
    """
    ui = ClickUI(passphrase_on_host=True, always_prompt=True)
    client = get_default_client(ui=ui)
    return client


class TrezorWallet(HwWallet):
    def __init__(self, derivation_path: str):
        self.client: TrezorClient = get_trezor_client()
        super().__init__(derivation_path)

    @raise_trezor_exception_as_hw_wallet_exception
    def get_address(self) -> ChecksumAddress:
        """
        :return: public address for derivation_path
        """
        address_n = tools.parse_path(self.derivation_path)
        return get_address(client=self.client, n=address_n)

    @raise_trezor_exception_as_hw_wallet_exception
    def sign_typed_hash(self, domain_hash: bytes, message_hash: bytes) -> bytes:
        """

        :param domain_hash:
        :param message_hash:
        :return: signature bytes
        """
        address_n = tools.parse_path(self.derivation_path)
        signed = sign_typed_data_hash(
            self.client, n=address_n, domain_hash=domain_hash, message_hash=message_hash
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
        address_n = tools.parse_path(self.derivation_path)
        if tx_parameters.get("maxPriorityFeePerGas"):
            # EIP1559
            v, r, s = sign_tx_eip1559(
                self.client,
                n=address_n,
                nonce=tx_parameters["nonce"],
                gas_limit=tx_parameters["gas"],
                to=tx_parameters["to"],
                value=tx_parameters["value"],
                data=HexBytes(tx_parameters["data"]),
                chain_id=chain_id,
                max_gas_fee=tx_parameters.get("maxFeePerGas"),
                max_priority_fee=tx_parameters.get("maxPriorityFeePerGas"),
            )

            encoded_transaction = (
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
                self.client,
                n=address_n,
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
            ).hex()

        return HexBytes(encoded_transaction)
