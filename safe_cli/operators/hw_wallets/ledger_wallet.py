from typing import Optional

from eth_typing import ChecksumAddress, HexStr
from ledgerblue.Dongle import Dongle
from ledgereth import create_transaction, sign_typed_data_draft
from ledgereth.accounts import get_account_by_path
from ledgereth.comms import init_dongle
from web3.types import TxParams

from gnosis.safe.signatures import signature_to_bytes

from .hw_wallet import HwWallet
from .ledger_exceptions import raise_ledger_exception_as_hw_wallet_exception


class LedgerWallet(HwWallet):
    @raise_ledger_exception_as_hw_wallet_exception
    def __init__(self, derivation_path: str):
        self.dongle: Optional[Dongle] = None
        self.connect()
        super().__init__(derivation_path)

    @raise_ledger_exception_as_hw_wallet_exception
    def connect(self) -> bool:
        """
        Connect with ledger
        :return: True if connection was successful or False in other case
        """
        self.dongle = init_dongle(self.dongle)

    @raise_ledger_exception_as_hw_wallet_exception
    def get_address(self) -> ChecksumAddress:
        """

        :return: public address for provided derivation_path
        """
        account = get_account_by_path(self.derivation_path)
        return account.address

    @raise_ledger_exception_as_hw_wallet_exception
    def sign_typed_hash(self, domain_hash: bytes, message_hash: bytes) -> bytes:
        """

        :param domain_hash:
        :param message_hash:
        :return: signature bytes
        """
        signed = sign_typed_data_draft(
            domain_hash, message_hash, self.derivation_path, self.dongle
        )

        return signature_to_bytes(signed.v, signed.r, signed.s)

    @raise_ledger_exception_as_hw_wallet_exception
    def get_signed_raw_transaction(self, tx_parameters: TxParams) -> HexStr:
        """

        :param tx_parameters:
        :return:
        """
        signed_transaction = create_transaction(
            destination=tx_parameters["to"],
            amount=tx_parameters["value"],
            gas=tx_parameters["gas"],
            nonce=tx_parameters["nonce"],
            data=tx_parameters["data"],
            max_priority_fee_per_gas=tx_parameters["maxPriorityFeePerGas"],
            max_fee_per_gas=tx_parameters["maxPriorityFeePerGas"],
            chain_id=5,
            sender_path=self.derivation_path,
            dongle=self.dongle,
        )
        return signed_transaction.raw_transaction()
