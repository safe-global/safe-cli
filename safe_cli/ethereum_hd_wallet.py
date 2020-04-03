from bip_utils import Bip32, Bip39SeedGenerator
from eth_account import Account
from ethereum.utils import checksum_encode, encode_int32, sha3

ETHEREUM_PATH = "m/44'/60'/0'/0"


def get_account_from_words(words: str, index: int = 0, hd_path: str = ETHEREUM_PATH) -> Account:
    """
    :param words: Mnemonic words generated using Bip39
    :param index: Index of account
    :param hd_path: Bip44 Path. By default Ethereum is used
    :return: List of ethereum public addresses
    """
    seed = Bip39SeedGenerator(words).Generate()
    bip32_ctx = Bip32.FromSeedAndPath(seed, hd_path)
    return Account.from_key(bip32_ctx.ChildKey(index).PrivateKeyBytes())


def get_address_from_words(words: str, index: int = 0, hd_path: str = ETHEREUM_PATH) -> str:
    """
    :param words: Mnemonic words generated using Bip39
    :param index: Index of account
    :param hd_path: Bip44 Path. By default Ethereum is used
    :return: List of ethereum public addresses
    """
    seed = Bip39SeedGenerator(words).Generate()
    bip32_ctx = Bip32.FromSeedAndPath(seed, hd_path)
    pub_key = bip32_ctx.ChildKey(index).m_ver_key.pubkey
    return checksum_encode(sha3(encode_int32(pub_key.point.x()) + encode_int32(pub_key.point.y()))[12:])
