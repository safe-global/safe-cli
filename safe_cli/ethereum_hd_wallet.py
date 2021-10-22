from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_typing import ChecksumAddress

ETHEREUM_DEFAULT_PATH = "m/44'/60'/0'/0/0"
ETHEREUM_BASE_PATH = "m/44'/60'/0'/0"


def get_account_from_words(
    words: str, index: int = 0, hd_path: str = ETHEREUM_DEFAULT_PATH
) -> LocalAccount:
    """
    :param words: Mnemonic words(BIP39) for a Hierarchical Deterministic Wallet(BIP32)
    :param index: Index of account
    :param hd_path: BIP44 Path. By default Ethereum with 0 index is used
    :return: Ethereum Account
    :raises: eth_utils.ValidationError
    """
    Account.enable_unaudited_hdwallet_features()
    if index:
        hd_path = f"{ETHEREUM_BASE_PATH}/{index}"
    return Account.from_mnemonic(words, account_path=hd_path)


def get_address_from_words(
    words: str, index: int = 0, hd_path: str = ETHEREUM_DEFAULT_PATH
) -> ChecksumAddress:
    """
    :param words: Mnemonic words(BIP39) for a Hierarchical Deterministic Wallet(BIP32)
    :param index: Index of account
    :param hd_path: BIP44 Path. By default Ethereum with 0 index is used
    :return: Ethereum checksummed public address
    :raises: eth_utils.ValidationError
    """
    return get_account_from_words(words, index, hd_path).address
