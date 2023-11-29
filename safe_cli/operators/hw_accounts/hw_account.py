import re
from abc import ABC, abstractmethod
from typing import Tuple

from eth_typing import ChecksumAddress

BIP32_ETH_PATTERN = r"^(m/)?44'/60'/[0-9]+'/[0-9]+/[0-9]+$"
BIP32_LEGACY_LEDGER_PATTERN = r"^(m/)?44'/60'/[0-9]+'/[0-9]+$"


class HwAccount(ABC):
    def __init__(self, derivation_path: str, address: ChecksumAddress):
        self.derivation_path = derivation_path
        self.address = address

    @property
    def get_derivation_path(self):
        return self.derivation_path

    @property
    def get_address(self):
        return self.address

    @staticmethod
    def is_valid_derivation_path(derivation_path: str):
        """
        Detect if a string is a valid derivation path
        """
        return (
            re.match(BIP32_ETH_PATTERN, derivation_path) is not None
            or re.match(BIP32_LEGACY_LEDGER_PATTERN, derivation_path) is not None
        )

    @staticmethod
    @abstractmethod
    def get_address_by_derivation_path(derivation_path: str) -> ChecksumAddress:
        """

        :param derivation_path:
        :return: public address for provided derivation_path
        """

    @abstractmethod
    def sign_typed_hash(self, domain_hash, message_hash) -> Tuple[bytes, bytes, bytes]:
        """

        :param domain_hash:
        :param message_hash:
        :return: tuple os signature v, r, s
        """

    def __eq__(self, other):
        if isinstance(other, HwAccount):
            return (
                self.derivation_path == other.derivation_path
                and self.address == other.address
            )
        return False

    def __hash__(self):
        return hash((self.derivation_path, self.address))
