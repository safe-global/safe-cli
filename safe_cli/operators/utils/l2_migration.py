"""
Handles migration from non L2 to L2

https://github.com/safe-global/safe-contracts/blob/main/contracts/libraries/SafeToL2Migration.sol

For reference and testing, polygon migration contract is deployed at 0x1Ba30910CE8Eb45b276aa7c89C38FC52228B85CB
"""
from eth_typing import ChecksumAddress
from hexbytes import HexBytes
from web3.constants import ADDRESS_ZERO
from web3.contract import Contract

from gnosis.eth import EthereumClient
from gnosis.eth.utils import get_empty_tx_params
from gnosis.safe import Safe

from .safe_to_l2_migration import safe_to_l2_migration


def get_l2_migration_contract(ethereum_client: EthereumClient) -> Contract:
    return ethereum_client.w3.eth.contract(
        ADDRESS_ZERO, abi=safe_to_l2_migration["abi"]
    )


def get_l2_migration_v111_data(
    safe: Safe,
    safe_l2_singleton_address: ChecksumAddress,
    safe_fallback_handler: ChecksumAddress,
) -> HexBytes:
    """
    Get data for migrating from v1.1.1 to v130/v141 L2

    :param safe:
    :param safe_l2_singleton_address:
    :param safe_fallback_handler:
    :return:
    """
    migration_contract = get_l2_migration_contract(safe.ethereum_client)
    # Migrate from V111
    return HexBytes(
        migration_contract.functions.migrateFromV111(
            safe_l2_singleton_address, safe_fallback_handler
        ).build_transaction(get_empty_tx_params())["data"]
    )


def get_l2_migration_v130_data(
    safe: Safe, safe_l2_singleton_address: ChecksumAddress
) -> HexBytes:
    """
    Get data for migrating from v130/v141 not L2 to v130/v141 L2

    :param safe:
    :param safe_l2_singleton_address:
    :return:
    """
    migration_contract = get_l2_migration_contract(safe.ethereum_client)
    # Migrate from V130/141
    return HexBytes(
        migration_contract.functions.migrateToL2(
            safe_l2_singleton_address
        ).build_transaction(get_empty_tx_params())["data"]
    )
