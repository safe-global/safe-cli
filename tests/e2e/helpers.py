"""
Shared pieces of the end-to-end tests: deploy a Safe on the chain and run the
CLI flow with a hardware wallet as owner and sender.
"""

from collections.abc import Callable

from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_typing import ChecksumAddress
from safe_eth.eth import EthereumClient
from safe_eth.eth.constants import NULL_ADDRESS
from safe_eth.safe import Safe
from safe_eth.safe.safe_signature import SafeSignatureEthSign

from safe_cli.operators import SafeOperator
from safe_cli.operators.hw_wallets.hw_wallet_manager import (
    HwWalletType,
    get_hw_wallet_manager,
)


def fund(
    client: EthereumClient, deployer: LocalAccount, to: ChecksumAddress, wei: int
) -> None:
    tx_hash = client.send_eth_to(deployer.key, to, client.w3.eth.gas_price, wei)
    client.get_transaction_receipt(tx_hash, timeout=60)


def deploy_safe(
    client: EthereumClient,
    deployer: LocalAccount,
    safe_contracts: tuple[str, str],
    owners: list[ChecksumAddress],
    threshold: int,
    funding_wei: int = 10**17,
) -> ChecksumAddress:
    master_copy, factory = safe_contracts
    safe_address = Safe.create(
        client,
        deployer,
        master_copy,
        owners,
        threshold,
        fallback_handler=NULL_ADDRESS,
        proxy_factory_address=factory,
    ).contract_address
    assert safe_address is not None
    fund(client, deployer, safe_address, funding_wei)
    return safe_address


def run_cli_flow(
    client: EthereumClient,
    deployer: LocalAccount,
    safe_contracts: tuple[str, str],
    hw_wallet_type: HwWalletType,
    template_derivation_path: str,
    derivation_path: str,
    address: ChecksumAddress,
    load_owner: Callable[[SafeOperator], None],
) -> None:
    """
    The hardware wallet lists its accounts, is loaded as owner and sender of a
    Safe, signs and executes an ether transfer and signs a Safe message.
    """
    fund(client, deployer, address, 10**18)
    hw_wallet_manager = get_hw_wallet_manager()
    accounts = hw_wallet_manager.get_accounts(
        hw_wallet_type, template_derivation_path, number_accounts=2
    )
    assert (address, derivation_path) in accounts, accounts

    safe_address = deploy_safe(
        client, deployer, safe_contracts, [address, deployer.address], 1
    )
    safe_operator = SafeOperator(
        safe_address, client.ethereum_node_url, interactive=False
    )
    load_owner(safe_operator)
    assert hw_wallet_manager.sender is not None
    assert hw_wallet_manager.sender.address == address
    assert [wallet.address for wallet in hw_wallet_manager.wallets] == [address]

    # Signed with EIP-712 and executed with a raw transaction, both on the device
    recipient = Account.create().address
    assert safe_operator.send_ether(recipient, 12345)
    assert client.get_balance(recipient) == 12345
    assert safe_operator.safe.retrieve_nonce() == 1

    safe_message_hash = safe_operator.safe.get_message_hash(b"Hello from safe-cli")
    [signature] = hw_wallet_manager.sign_message(
        safe_message_hash, list(hw_wallet_manager.wallets)
    )
    assert isinstance(signature, SafeSignatureEthSign)
    assert signature.owner == address
