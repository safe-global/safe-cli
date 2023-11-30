from functools import lru_cache

from eth_typing import ChecksumAddress
from trezorlib import tools
from trezorlib.client import TrezorClient, get_default_client
from trezorlib.ethereum import get_address, sign_typed_data_hash
from trezorlib.ui import ClickUI

from safe_cli.operators.hw_accounts.hw_account import HwAccount
from safe_cli.operators.hw_accounts.trezor_exceptions import (
    raise_trezor_exception_as_hw_account_exception,
)


@lru_cache(maxsize=None)
@raise_trezor_exception_as_hw_account_exception
def get_trezor_client() -> TrezorClient:
    """
    Return default trezor configuration that store passphrase on host.
    This method is cached to share the same configuration between trezor calls while the class is not instantiated.
    :return:
    """
    ui = ClickUI(passphrase_on_host=True)
    client = get_default_client(ui=ui)
    return client


class TrezorManager(HwAccount):
    def __init__(self, derivation_path: str, address: ChecksumAddress):
        self.client = get_trezor_client()
        super().__init__(derivation_path, address)

    @raise_trezor_exception_as_hw_account_exception
    def get_address_by_derivation_path(derivation_path: str) -> ChecksumAddress:
        """

        :param derivation_path:
        :return: public address for provided derivation_path
        """
        if TrezorManager.is_valid_derivation_path(derivation_path):
            client = get_trezor_client()
            address_n = tools.parse_path(derivation_path)
            return get_address(client=client, n=address_n)

    @raise_trezor_exception_as_hw_account_exception
    def sign_typed_hash(self, domain_hash, message_hash) -> bytes:
        address_n = tools.parse_path(self.derivation_path)
        signed = sign_typed_data_hash(
            self.client, n=address_n, domain_hash=domain_hash, message_hash=message_hash
        )
        return signed.signature
