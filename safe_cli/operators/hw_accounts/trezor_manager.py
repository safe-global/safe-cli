from typing import Tuple

from eth_typing import ChecksumAddress

from safe_cli.operators.hw_accounts.hw_account import HwAccount


class TrezorManager(HwAccount):
    def __init__(self, derivation_path: str, address: ChecksumAddress):
        self.client = None
        super().__init__(derivation_path, address)

    def get_address_by_derivation_path(derivation_path: str) -> ChecksumAddress:
        """

        :param derivation_path:
        :return: public address for provided derivation_path
        """
        raise NotImplementedError

    def sign_typed_hash(self, domain_hash, message_hash) -> Tuple[bytes, bytes, bytes]:
        raise NotImplementedError
