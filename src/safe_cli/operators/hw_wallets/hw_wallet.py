import re
from abc import ABC, abstractmethod

from web3.types import TxParams

from .constants import BIP32_ETH_PATTERN, BIP32_LEGACY_LEDGER_PATTERN
from .exceptions import InvalidDerivationPath


class HwWallet(ABC):
    def __init__(self, derivation_path: str):
        derivation_path = derivation_path.replace("m/", "")
        if self._is_valid_derivation_path(derivation_path):
            self.derivation_path = derivation_path
        self.address = self.get_address()

    @property
    def get_derivation_path(self):
        return self.derivation_path

    @abstractmethod
    def get_address(self):
        """

        :return:
        """

    def _is_valid_derivation_path(self, derivation_path: str):
        """
        Detect if a string is a valid derivation path
        """
        if not (
            re.match(BIP32_ETH_PATTERN, derivation_path) is not None
            or re.match(BIP32_LEGACY_LEDGER_PATTERN, derivation_path) is not None
        ):
            raise InvalidDerivationPath()

        return True

    @abstractmethod
    def sign_typed_hash(self, domain_hash: bytes, message_hash: bytes) -> bytes:
        """

        :param domain_hash:
        :param message_hash:
        :return: signature bytes
        """

    @abstractmethod
    def get_signed_raw_transaction(
        self, tx_parameters: TxParams, chain_id: int
    ) -> bytes:
        """

        :param chain_id:
        :param tx_parameters:
        :return: raw transaction signed
        """

    def __str__(self):
        return f"{self.__class__.__name__} device with address {self.address}"

    def __eq__(self, other):
        if isinstance(other, HwWallet):
            return (
                self.derivation_path == other.derivation_path
                and self.address == other.address
            )
        return False

    def __hash__(self):
        return hash((self.derivation_path, self.address))
