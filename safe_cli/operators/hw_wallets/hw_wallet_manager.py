from enum import Enum
from functools import lru_cache
from typing import Dict, List, Optional, Set, Tuple

from eth_typing import ChecksumAddress
from prompt_toolkit import HTML, print_formatted_text

from gnosis.eth.eip712 import eip712_encode
from gnosis.safe import SafeTx

from .hw_wallet import HwWallet


class HwWalletType(Enum):
    TREZOR = 0
    LEDGER = 1


@lru_cache(maxsize=None)
def get_hw_wallet_manager():
    return HwWalletManager()


class HwWalletManager:
    def __init__(self):
        self.wallets: Set[HwWallet] = set()
        self.supported_hw_wallet_types: Dict[str, HwWallet] = {}
        try:
            from .ledger_wallet import LedgerWallet

            self.supported_hw_wallet_types[HwWalletType.LEDGER] = LedgerWallet
        except (ImportError):
            pass

        try:
            from .trezor_wallet import TrezorWallet

            self.supported_hw_wallet_types[HwWalletType.TREZOR] = TrezorWallet
        except (ImportError):
            pass

    def is_supported_hw_wallet(self, hw_wallet_type: HwWalletType) -> bool:
        return hw_wallet_type in self.supported_hw_wallet_types

    def get_hw_wallet(self, hw_wallet_type: HwWalletType) -> Optional[HwWallet]:
        if hw_wallet_type in self.supported_hw_wallet_types:
            return self.supported_hw_wallet_types[hw_wallet_type]

    def get_accounts(
        self,
        hw_wallet_type: HwWalletType,
        legacy_account: Optional[bool] = False,
        number_accounts: Optional[int] = 5,
    ) -> List[Tuple[ChecksumAddress, str]]:
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

            accounts.append((hw_wallet(path_string).address, path_string))
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

        address = hw_wallet(derivation_path).address
        self.wallets.add(hw_wallet(derivation_path))
        return address

    def delete_accounts(self, addresses: List[ChecksumAddress]) -> Set:
        """
        Remove ledger accounts from address

        :param accounts:
        :return: list with the delete accounts
        """
        accounts_to_remove = set()
        for address in addresses:
            for account in self.wallets:
                if account.address == address:
                    accounts_to_remove.add(account)
        self.wallets = self.wallets.difference(accounts_to_remove)
        return accounts_to_remove

    def sign_eip712(self, safe_tx: SafeTx, wallets: List[HwWallet]) -> SafeTx:
        """
        Sign a safeTx EIP-712 hashes with supported hw wallet devices

        :param domain_hash:
        :param message_hash:
        :param wallets: list of HwWallet
        :return: signed safeTx
        """
        encode_hash = eip712_encode(safe_tx.eip712_structured_data)
        domain_hash = encode_hash[1]
        message_hash = encode_hash[2]
        for wallet in wallets:
            print_formatted_text(
                HTML(
                    f"<ansired>Make sure before signing in your {wallet} that the domain_hash and message_hash are both correct</ansired>"
                )
            )
            print_formatted_text(HTML(f"Domain_hash: <b>{domain_hash.hex()}</b>"))
            print_formatted_text(HTML(f"Message_hash: <b>{message_hash.hex()}</b>"))
            signature = wallet.sign_typed_hash(domain_hash, message_hash)

            # Insert signature sorted
            if wallet.address not in safe_tx.signers:
                new_owners = safe_tx.signers + [wallet.address]
                new_owner_pos = sorted(new_owners, key=lambda x: int(x, 16)).index(
                    wallet.address
                )
                safe_tx.signatures = (
                    safe_tx.signatures[: 65 * new_owner_pos]
                    + signature
                    + safe_tx.signatures[65 * new_owner_pos :]
                )

        return safe_tx
