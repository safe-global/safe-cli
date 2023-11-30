from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from eth_typing import ChecksumAddress
from prompt_toolkit import HTML, print_formatted_text

from gnosis.eth.eip712 import eip712_encode
from gnosis.safe import SafeTx

from safe_cli.operators.hw_accounts.hw_account import HwAccount


class HwWalletType(Enum):
    TREZOR = "Trezor"
    LEDGER = "Ledger"


class HwAccountManager:
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(HwAccountManager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.accounts: Set[HwAccount] = set()
        self.supported_hw_wallets: Dict[str, HwAccount] = {}
        try:
            from safe_cli.operators.hw_accounts.ledger_manager import LedgerManager

            self.supported_hw_wallets[HwWalletType.LEDGER] = LedgerManager
        except (ModuleNotFoundError, IOError):
            pass

        try:
            from safe_cli.operators.hw_accounts.trezor_manager import TrezorManager

            self.supported_hw_wallets[HwWalletType.TREZOR] = TrezorManager
        except (ModuleNotFoundError, IOError):
            pass

    def is_supported_hw_wallet(self, hw_wallet_type: HwWalletType):
        return hw_wallet_type in self.supported_hw_wallets

    def get_hw_wallet(self, hw_wallet_type: HwWalletType):
        if hw_wallet_type in self.supported_hw_wallets:
            return self.supported_hw_wallets[hw_wallet_type]
        # TODO add unsupported exception

    def get_accounts(
        self,
        hw_wallet_type: HwWalletType,
        legacy_account: Optional[bool] = False,
        number_accounts: Optional[int] = 5,
    ) -> Tuple[ChecksumAddress, str]:
        """

        :param hw_wallet: Trezor or Ledger
        :param legacy_account:
        :param number_accounts:  number of accounts requested to ledger
        :return: a list of tuples with address and derivation path
        """
        accounts = []
        hw_wallet = self.get_hw_wallet(hw_wallet_type)
        for i in range(number_accounts):
            if legacy_account:
                path_string = f"44'/60'/0'/{i}"
            else:
                path_string = f"44'/60'/{i}'/0/0"

            address = hw_wallet.get_address_by_derivation_path(path_string)
            accounts.append((address, path_string))
        return accounts

    def add_account(
        self, hw_wallet_type: HwWalletType, derivation_path: str
    ) -> ChecksumAddress:
        """
        Add an account to ledger manager set and return the added address

        :param derivation_path:
        :return:
        """

        hw_wallet = self.get_hw_wallet(hw_wallet_type)

        address = hw_wallet.get_address_by_derivation_path(derivation_path)
        self.accounts.add(hw_wallet(derivation_path, address))
        return address

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

    def sign_eip712(self, safe_tx: SafeTx, accounts: List[HwAccount]) -> SafeTx:
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
                    "<ansired>Make sure in your ledger before signing that domain_hash and message_hash are both correct</ansired>"
                )
            )
            print_formatted_text(HTML(f"Domain_hash: <b>{domain_hash.hex()}</b>"))
            print_formatted_text(HTML(f"Message_hash: <b>{message_hash.hex()}</b>"))
            signature = account.sign_typed_hash(domain_hash, message_hash)

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
