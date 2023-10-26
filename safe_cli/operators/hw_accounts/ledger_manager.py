from typing import List, Optional, Set, Tuple

from eth_typing import ChecksumAddress
from ledgereth import sign_typed_data_draft
from ledgereth.accounts import LedgerAccount, get_account_by_path
from ledgereth.comms import init_dongle
from ledgereth.exceptions import LedgerNotFound
from prompt_toolkit import HTML, print_formatted_text

from gnosis.eth.eip712 import eip712_encode
from gnosis.safe import SafeTx
from gnosis.safe.signatures import signature_to_bytes

from safe_cli.operators.hw_accounts.hw_exceptions import hw_account_exception


class LedgerManager:
    def __init__(self):
        self.dongle = None
        self.accounts: Set[LedgerAccount] = set()
        self.connect()

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
    @hw_account_exception
    def connected(self) -> bool:
        """
        :return: True if ledger is connected or False in other case
        """
        return self.connect()

    @hw_account_exception
    def get_accounts(
        self, legacy_account: Optional[bool] = False, number_accounts: Optional[int] = 5
    ) -> List[Tuple[ChecksumAddress, str]]:
        """
        Request to ledger device the first n accounts

        :param legacy_account:
        :param number_accounts: number of accounts requested to ledger
        :return: a list of tuples with address and derivation path
        """
        accounts = []
        for i in range(number_accounts):
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
        Add an account to ledger manager set

        :param derivation_path:
        :return:
        """
        account = get_account_by_path(derivation_path, self.dongle)
        self.accounts.add(LedgerAccount(account.path, account.address))

    def delete_accounts(self, addresses: List[ChecksumAddress]) -> Set:
        """
        Remove ledger accounts from address

        :param accounts:
        :return: list with the delete accounts
        """
        accounts_to_remove = set()
        for address in addresses:
            for account in self.accounts:
                if account.address == address:
                    accounts_to_remove.add(account)
        self.accounts = self.accounts.difference(accounts_to_remove)
        return accounts_to_remove

    @hw_account_exception
    def sign_eip712(self, safe_tx: SafeTx, accounts: List[LedgerAccount]) -> SafeTx:
        """
        Call ledger ethereum app method to sign eip712 hashes with a ledger account

        :param domain_hash:
        :param message_hash:
        :param account: ledger account
        :return: bytes of signature
        """
        encode_hash = eip712_encode(safe_tx.eip712_structured_data)
        domain_hash = encode_hash[1]
        message_hash = encode_hash[2]
        for account in accounts:
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

            signature = signature_to_bytes(signed.v, signed.r, signed.s)
            # TODO should be refactored on safe_eth_py function insert_signature_sorted
            # Insert signature sorted
            if account.address not in safe_tx.signers:
                new_owners = safe_tx.signers + [account.address]
                new_owner_pos = sorted(new_owners, key=lambda x: int(x, 16)).index(
                    account.address
                )
                safe_tx.signatures = (
                    safe_tx.signatures[: 65 * new_owner_pos]
                    + signature
                    + safe_tx.signatures[65 * new_owner_pos :]
                )

        return safe_tx
