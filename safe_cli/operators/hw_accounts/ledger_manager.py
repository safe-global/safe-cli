from typing import List, Optional, Set, Tuple

from eth_typing import ChecksumAddress
from ledgereth import sign_typed_data_draft
from ledgereth.accounts import LedgerAccount, get_account_by_path
from ledgereth.comms import init_dongle
from ledgereth.exceptions import LedgerNotFound
from prompt_toolkit import HTML, print_formatted_text

from gnosis.safe.signatures import signature_to_bytes

from safe_cli.operators.hw_accounts.hw_exceptions import hw_account_exception


class LedgerManager:

    LEDGER_SEARCH_DEEP = 5

    def __init__(self):
        self.dongle = None
        self.accounts: Set[LedgerAccount] = set()
        self.connect()

    def connect(self) -> bool:
        try:
            self.dongle = init_dongle(self.dongle)
            return True
        except LedgerNotFound:
            return False

    @property
    @hw_account_exception
    def connected(self) -> bool:
        return self.connect()

    @hw_account_exception
    def get_accounts(
        self, legacy_account: Optional[bool] = False
    ) -> List[Tuple[ChecksumAddress, str]]:
        """
        :param legacy_account:
        :return: a list of tuples with address and derivation path
        """
        accounts = []
        for i in range(self.LEDGER_SEARCH_DEEP):
            if legacy_account:
                path_string = f"44'/60'/0'/{i}"
            else:
                path_string = f"44'/60'/{i}'/0/0"

            account = get_account_by_path(path_string, self.dongle)
            accounts.append((account.address, account.path))
        return accounts

    @hw_account_exception
    def add_account(self, derivation_path: str):
        """
        Add account to ledger manager list

        :param derivation_path:
        :return:
        """
        account = get_account_by_path(derivation_path, self.dongle)
        self.accounts.add(LedgerAccount(account.path, account.address))

    @hw_account_exception
    def sign_eip712(
        self, domain_hash: bytes, message_hash: bytes, account: LedgerAccount
    ) -> bytes:
        """
        Sign eip712 hashes

        :param domain_hash:
        :param message_hash:
        :param account: ledger account
        :return: bytes signature
        """
        print_formatted_text(
            HTML(
                "Ensure to compare in your ledger before to sign that domain_hash and message_hash are  both correct"
            )
        )
        print_formatted_text(HTML(f"Domain_hash: <b>{domain_hash.hex()}</b>"))
        print_formatted_text(HTML(f"Message_hash: <b>{message_hash.hex()}</b>"))
        signed = sign_typed_data_draft(
            domain_hash, message_hash, account.path, self.dongle
        )

        return signature_to_bytes(signed.v, signed.r, signed.s)
