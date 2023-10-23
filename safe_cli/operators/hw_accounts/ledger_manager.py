from enum import Enum
from typing import List, Optional, Set, Tuple

from eth_typing import ChecksumAddress
from ledgereth.accounts import get_account_by_path
from ledgereth.comms import init_dongle
from ledgereth.constants import DEFAULT_PATH_STRING
from ledgereth.exceptions import LedgerAppNotOpened, LedgerLocked, LedgerNotFound
from prompt_toolkit import HTML, print_formatted_text

from gnosis.safe.signatures import signature_to_bytes

from safe_cli.operators.hw_accounts.ledger_account import LedgerAccount


class LedgerStatus(Enum):
    DISCONNECTED = 0
    LOCKED = 1  # Connected but locked
    APP_CLOSED = 2  # Connected, unlocked but app is closed
    READY = 3  # Ready to communicate


class LedgerManager:

    LEDGER_SEARCH_DEEP = 10

    def __init__(self):
        self.dongle = None
        self.accounts: Set[LedgerAccount] = set()
        self.connected: bool

    def _print_error_message(self, message: str):
        print_formatted_text(HTML(f"<ansired>{message}</ansired>"))

    def check_status(self, print_message: bool = False) -> LedgerStatus:
        try:
            self.dongle = init_dongle(self.dongle)
            # Get default derivation to check following status
            get_account_by_path(DEFAULT_PATH_STRING)
        except LedgerNotFound:
            if print_message:
                self._print_error_message("Ledger is disconnected")
            return LedgerStatus.DISCONNECTED
        except LedgerLocked:
            if print_message:
                self._print_error_message("Ledger is locked")
            return LedgerStatus.LOCKED
        except LedgerAppNotOpened:
            if print_message:
                self._print_error_message("Ledger is disconnected")
            return LedgerStatus.APP_CLOSED

        return LedgerStatus.READY

    @property
    def connected(self) -> bool:
        if self.check_status() != LedgerStatus.DISCONNECTED:
            return True
        return False

    def get_accounts(
        self, legacy_account: Optional[bool] = False
    ) -> List[Tuple[ChecksumAddress, str]]:
        """
        :param legacy_account:
        :return: a list of tuples with address and derivation path
        """
        accounts = []
        if self.check_status(True) != LedgerStatus.READY:
            return []
        for i in range(self.LEDGER_SEARCH_DEEP):
            if legacy_account:
                path_string = f"44'/60'/0'/{i}"
            else:
                path_string = f"44'/60'/{i}'/0/0"
            try:
                account = get_account_by_path(path_string, self.dongle)
            except LedgerLocked as ledger_error:
                print(f"Ledger exception: {ledger_error}")
            accounts.append((account.address, account.path))
        return accounts

    def add_account(self, derivation_path: str) -> bool:
        """
        Add account to ledger manager list

        :param derivation_path:
        :return:
        """
        if self.check_status(True) != LedgerStatus.READY:
            return False
        account = get_account_by_path(derivation_path, self.dongle)
        self.accounts.add(LedgerAccount(account.path, account.address))
        return True

    def sign_eip712(
        self, domain_hash: bytes, message_hash: bytes, account: LedgerAccount
    ) -> bytes | None:
        """
        Sign eip712 hashes

        :param domain_hash:
        :param message_hash:
        :param account: ledger account
        :return: bytes signature
        """
        if self.check_status(True) != LedgerStatus.READY:
            return None

        v, r, s = account.signMessage(domain_hash, message_hash, self.dongle)

        return signature_to_bytes(v, r, s)
