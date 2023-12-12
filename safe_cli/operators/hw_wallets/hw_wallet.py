import re
from abc import ABC, abstractmethod

BIP32_ETH_PATTERN = r"^44'/60'/[0-9]+'/[0-9]+/[0-9]+$"
BIP32_LEGACY_LEDGER_PATTERN = r"^44'/60'/[0-9]+'/[0-9]+$"


class InvalidDerivationPath(Exception):
    message = "The provided derivation path is not valid"


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
            raise InvalidDerivationPath

        return True

    @abstractmethod
    def sign_typed_hash(self, domain_hash, message_hash) -> bytes:
        """

        :param domain_hash:
        :param message_hash:
        :return: signature
        """

    def __eq__(self, other):
        if isinstance(other, HwWallet):
            return (
                self.derivation_path == other.derivation_path
                and self.address == other.address
            )
        return False

    def __hash__(self):
        return hash((self.derivation_path, self.address))
