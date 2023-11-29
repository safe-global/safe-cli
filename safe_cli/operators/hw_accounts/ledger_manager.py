from typing import Tuple

from eth_typing import ChecksumAddress
from ledgereth import sign_typed_data_draft
from ledgereth.accounts import get_account_by_path
from ledgereth.comms import init_dongle
from ledgereth.exceptions import LedgerNotFound

from safe_cli.operators.hw_accounts.exceptions import raise_as_hw_account_exception
from safe_cli.operators.hw_accounts.hw_account import HwAccount


class LedgerManager(HwAccount):
    def __init__(self, derivation_path: str, address: ChecksumAddress):
        self.dongle = None
        self.connect()
        super().__init__(derivation_path, address)

    def connect(self) -> bool:
        """
        Connect with ledger
        :return: True if connection was successful or False in other case
        """
        try:
            self.dongle = init_dongle(self.dongle)
            return True
        except LedgerNotFound:
            return False

    @property
    @raise_as_hw_account_exception
    def connected(self) -> bool:
        """
        :return: True if ledger is connected or False in other case
        """
        return self.connect()

    @raise_as_hw_account_exception
    def get_address_by_derivation_path(derivation_path: str) -> ChecksumAddress:
        """

        :param derivation_path:
        :return: public address for provided derivation_path
        """
        if derivation_path[0:2] == "m/":
            derivation_path = derivation_path.replace("m/", "")
        account = get_account_by_path(derivation_path)
        return account.address

    @raise_as_hw_account_exception
    def sign_typed_hash(self, domain_hash, message_hash) -> Tuple[bytes, bytes, bytes]:
        signed = sign_typed_data_draft(
            domain_hash, message_hash, self.derivation_path, self.dongle
        )
        return (signed.v, signed.r, signed.s)
