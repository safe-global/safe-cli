from enum import Enum
from functools import lru_cache
from typing import Dict, List, Optional, Set, Tuple

from eth_typing import ChecksumAddress
from hexbytes import HexBytes
from prompt_toolkit import HTML, print_formatted_text
from web3.types import TxParams, Wei

from gnosis.eth import TxSpeed
from gnosis.eth.eip712 import eip712_encode, eip712_encode_hash
from gnosis.safe import SafeTx
from gnosis.safe.safe_signature import SafeSignature, SafeSignatureEOA

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
        self.sender: Optional[HwWallet] = None
        try:
            from .ledger_wallet import LedgerWallet

            self.supported_hw_wallet_types[HwWalletType.LEDGER] = LedgerWallet
        except ImportError:
            pass

        try:
            from .trezor_wallet import TrezorWallet

            self.supported_hw_wallet_types[HwWalletType.TREZOR] = TrezorWallet
        except ImportError:
            pass

    def is_supported_hw_wallet(self, hw_wallet_type: HwWalletType) -> bool:
        return hw_wallet_type in self.supported_hw_wallet_types

    def get_hw_wallet(self, hw_wallet_type: HwWalletType) -> Optional[HwWallet]:
        if hw_wallet_type in self.supported_hw_wallet_types:
            return self.supported_hw_wallet_types[hw_wallet_type]

    def get_accounts(
        self,
        hw_wallet_type: HwWalletType,
        template_derivation_path: str,
        number_accounts: Optional[int] = 5,
    ) -> List[Tuple[ChecksumAddress, str]]:
        """

        :param hw_wallet: Trezor or Ledger
        :param template_derivation_path: formatted string to indicate which path iterate
        :param number_accounts:  number of accounts requested to ledger
        :return: a list of tuples with address and derivation path
        """
        accounts = []
        hw_wallet = self.get_hw_wallet(hw_wallet_type)
        for i in range(number_accounts):
            path_string = template_derivation_path.format(i=i)
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

        wallet = hw_wallet(derivation_path)
        self.wallets.add(wallet)
        return wallet.address

    def set_sender(self, hw_wallet_type: HwWalletType, derivation_path: str):
        """
        Set a harware wallet as a sender to enable execute transaction from it.
        :param hw_wallet_type:
        :param derivation_path:
        :return:
        """
        hw_wallet = self.get_hw_wallet(hw_wallet_type)
        self.sender = hw_wallet(derivation_path)

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
                    if self.sender and self.sender.address == address:
                        self.sender = None
                    accounts_to_remove.add(account)
        self.wallets = self.wallets.difference(accounts_to_remove)
        return accounts_to_remove

    def sign_eip712(self, eip712_message: Dict, wallets: List[HwWallet]) -> HexBytes:
        """
        Sign an EIP712 message

        :param eip712_message:
        :param wallets:
        :return: Appended sorted signatures for all the provided wallets
        """
        _, domain_hash, message_hash = eip712_encode(eip712_message)
        eip712_message_hash = eip712_encode_hash(eip712_message)
        safe_signatures: List[SafeSignature] = []
        for wallet in wallets:
            print_formatted_text(
                HTML(
                    f"<ansired>Make sure before signing in your {wallet} that the domain_hash and message_hash are both correct</ansired>"
                )
            )
            print_formatted_text(HTML(f"Domain_hash: <b>{domain_hash.hex()}</b>"))
            print_formatted_text(HTML(f"Message_hash: <b>{message_hash.hex()}</b>"))
            signature = wallet.sign_typed_hash(domain_hash, message_hash)
            safe_signatures.append(SafeSignatureEOA(signature, eip712_message_hash))

        return SafeSignature.export_signatures(safe_signatures)

    def sign_safe_tx(self, safe_tx: SafeTx, wallets: List[HwWallet]) -> SafeTx:
        """
        Sign a safe transaction with the provided hardware wallets

        :param safe_tx:
        :param wallets:
        :return: SafeTx with signature.
        """
        signatures = self.sign_eip712(safe_tx.eip712_structured_data, wallets)
        safe_tx.signatures = signatures
        return safe_tx

    def execute_safe_tx(
        self,
        safe_tx: SafeTx,
        tx_gas: Optional[int] = None,
        tx_gas_price: Optional[int] = None,
        tx_nonce: Optional[int] = None,
        eip1559_speed: Optional[TxSpeed] = None,
    ) -> Tuple[HexBytes, TxParams]:
        """
        Send multisig tx to the Safe

        :param safe_tx: Safe transaction to sign
        :param tx_gas: Gas for the external tx. If not, `(safe_tx_gas + base_gas) * 2` will be used
        :param tx_gas_price: Gas price of the external tx. If not, `gas_price` will be used
        :param tx_nonce: Force nonce for `tx_sender`
        :param eip1559_speed: If provided, use EIP1559 transaction
        :return: Tuple(tx_hash, tx)
        """

        if eip1559_speed and safe_tx.ethereum_client.is_eip1559_supported():
            tx_parameters = safe_tx.ethereum_client.set_eip1559_fees(
                {
                    "from": self.sender.address,
                },
                tx_speed=eip1559_speed,
            )
        else:
            tx_parameters = {
                "from": self.sender.address,
                "gasPrice": tx_gas_price or safe_tx.w3.eth.gas_price,
            }

        if tx_gas:
            tx_parameters["gas"] = tx_gas

        if tx_nonce is not None:
            tx_parameters["nonce"] = tx_nonce
        else:
            tx_parameters["nonce"] = safe_tx.ethereum_client.get_nonce_for_account(
                self.sender.address, block_identifier="latest"
            )
        safe_tx.tx = safe_tx.w3_tx.build_transaction(tx_parameters)
        safe_tx.tx["gas"] = Wei(
            tx_gas or (max(safe_tx.tx["gas"] + 75000, safe_tx.recommended_gas()))
        )
        signed_raw_transaction = self.sender.get_signed_raw_transaction(
            safe_tx.tx, safe_tx.ethereum_client.get_chain_id()
        )  # sign with ledger
        safe_tx.tx_hash = safe_tx.ethereum_client.w3.eth.send_raw_transaction(
            signed_raw_transaction
        )
        # Set signatures empty after executing the tx. `Nonce` is increased even if it fails,
        # so signatures are not valid anymore
        safe_tx.signatures = b""
        return safe_tx.tx_hash, safe_tx.tx
