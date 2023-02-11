import warnings

from eth_account.signers.base import BaseAccount
from ledgerblue import Dongle
from ledgereth import sign_typed_data_draft, create_transaction
from web3.types import TxParams


class LedgerAccount(BaseAccount):
    def __init__(self, path, address, dongle: Dongle):
        """
        Initialize a new ledger account (no private key)

        :param path: path derivation
        :param ~eth_account.account.Account account: the key-unaware management API
        """
        self._address = address
        self.path = path
        self.dongle = dongle

    @property
    def address(self):
        return self._address

    @property
    def privateKey(self):
        """
        .. CAUTION:: Deprecated for :meth:`~eth_account.signers.local.LocalAccount.key`.
            This attribute will be removed in v0.5
        """
        warnings.warn(
            "privateKey is deprecated in favor of key",
            category=DeprecationWarning,
        )
        return None

    @property
    def key(self):
        """
        Get the private key.
        """
        return None

    def encrypt(self, password, kdf=None, iterations=None):
        """
        Generate a string with the encrypted key.

        This uses the same structure as in
        :meth:`~eth_account.account.Account.encrypt`, but without a private key argument.
        """
        # return self._publicapi.encrypt(self.key, password, kdf=kdf, iterations=iterations)
        # TODO with ledger
        pass

    def signHash(self, domain_hash: bytes, message_hash: bytes):
        signed = sign_typed_data_draft(domain_hash, message_hash, dongle=self.dongle)
        return (signed.v, signed.r, signed.s)

    def sign_message(self, signable_message):
        """
        Generate a string with the encrypted key.

        This uses the same structure as in
        :meth:`~eth_account.account.Account.sign_message`, but without a private key argument.
        """
        # TODO with ledger
        pass

    def signTransaction(self, transaction_dict):
        warnings.warn(
            "signTransaction is deprecated in favor of sign_transaction",
            category=DeprecationWarning,
        )
        pass

    def sign_transaction(self, tx: TxParams):
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
            dongle=self.dongle
        )
        return signed

    def __bytes__(self):
        return self.key
