from eth_account.datastructures import SignedTransaction
from hexbytes import HexBytes
from ledgerblue import Dongle
from ledgereth import create_transaction, sign_typed_data_draft
from web3 import Web3
from web3.types import TxParams


class LedgerAccount:
    def __init__(self, path, address):
        """
        Initialize a new ledger account (no private key)

        :param path: path derivation
        :param ~eth_account.account.Account account: the key-unaware management API
        """
        self._address = address
        self.path = path

    @property
    def address(self):
        return self._address

    def signMessage(self, domain_hash: bytes, message_hash: bytes, dongle: Dongle):
        signed = sign_typed_data_draft(domain_hash, message_hash, self.path, dongle)
        return (signed.v, signed.r, signed.s)

    def sign_transaction(self, tx: TxParams, dongle: Dongle) -> SignedTransaction:
        signed = create_transaction(
            destination=tx["to"],
            amount=tx["value"],
            gas=tx["gas"],
            max_priority_fee_per_gas=tx["maxPriorityFeePerGas"],
            max_fee_per_gas=tx["maxFeePerGas"],
            data=tx["data"],
            nonce=tx["nonce"],
            chain_id=tx["chainId"],
            sender_path=self.path,
            dongle=dongle,
        )
        raw_transaction = signed.raw_transaction()
        return SignedTransaction(
            HexBytes(raw_transaction),
            Web3.keccak(HexBytes(raw_transaction)),
            signed.sender_r,
            signed.sender_s,
            signed.y_parity,
        )
