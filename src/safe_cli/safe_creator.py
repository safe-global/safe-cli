#!/bin/env python3
import argparse
import secrets
import sys
from typing import List

from art import text2art
from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_typing import URI
from hexbytes import HexBytes
from prompt_toolkit import print_formatted_text

from gnosis.eth import EthereumClient, EthereumTxSent
from gnosis.eth.constants import NULL_ADDRESS
from gnosis.eth.contracts import get_safe_V1_4_1_contract
from gnosis.safe import ProxyFactory, Safe

from safe_cli.safe_addresses import (
    get_default_fallback_handler_address,
    get_proxy_factory_address,
    get_safe_contract_address,
    get_safe_l2_contract_address,
)
from safe_cli.utils import yes_or_no_question

from .argparse_validators import (
    check_ethereum_address,
    check_positive_integer,
    check_private_key,
)


def setup_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("node_url", help="Ethereum node url")
    parser.add_argument(
        "private_key", help="Deployer private_key", type=check_private_key
    )
    parser.add_argument(
        "--threshold",
        help="Number of owners required to execute transactions on the created Safe. It must"
        "be greater than 0 and less or equal than the number of owners",
        type=check_positive_integer,
        default=1,
    )
    parser.add_argument(
        "--owners",
        help="Owners. By default it will be just the deployer",
        nargs="+",
        type=check_ethereum_address,
    )
    parser.add_argument(
        "--safe-contract",
        help="Use a custom Safe master copy",
        default=None,
        type=check_ethereum_address,
    )
    parser.add_argument(
        "--proxy-factory",
        help="Use a custom proxy factory",
        default=None,
        type=check_ethereum_address,
    )
    parser.add_argument(
        "--callback-handler",
        help="Use a custom fallback handler. It is not required for Safe Master Copies "
        "with version < 1.1.0",
        default=None,
        type=check_ethereum_address,
    )
    parser.add_argument(
        "--salt-nonce",
        help="Use a custom nonce for the deployment. Same nonce with same deployment configuration will "
        "lead to the same Safe address ",
        default=secrets.randbits(256),
        type=int,
    )

    parser.add_argument(
        "--without-events",
        help="Use non events deployment of the Safe instead of the regular one. Recommended for mainnet to save gas costs when using the Safe",
        default=False,
        action="store_true",
    )
    return parser


def main(*args, **kwargs) -> EthereumTxSent:
    parser = setup_argument_parser()
    print_formatted_text(text2art("Safe Creator"))  # Print fancy text
    args = parser.parse_args()
    node_url: URI = args.node_url
    account: LocalAccount = Account.from_key(args.private_key)
    owners: List[str] = args.owners if args.owners else [account.address]
    threshold: int = args.threshold
    salt_nonce: int = args.salt_nonce
    to = NULL_ADDRESS
    data = b""
    payment_token = NULL_ADDRESS
    payment = 0
    payment_receiver = NULL_ADDRESS

    if len(owners) < threshold:
        print_formatted_text(
            "Threshold cannot be bigger than the number of unique owners"
        )
        sys.exit(1)

    ethereum_client = EthereumClient(node_url)
    ethereum_network = ethereum_client.get_network()

    safe_contract_address = args.safe_contract or (
        get_safe_contract_address(ethereum_client)
        if args.without_events
        else get_safe_l2_contract_address(ethereum_client)
    )
    proxy_factory_address = args.proxy_factory or get_proxy_factory_address(
        ethereum_client
    )
    fallback_handler = args.callback_handler or get_default_fallback_handler_address(
        ethereum_client
    )

    if not ethereum_client.is_contract(safe_contract_address):
        print_formatted_text(
            f"Safe contract address {safe_contract_address} "
            f"does not exist on network {ethereum_network.name}"
        )
        sys.exit(1)
    elif not ethereum_client.is_contract(proxy_factory_address):
        print_formatted_text(
            f"Proxy contract address {proxy_factory_address} "
            f"does not exist on network {ethereum_network.name}"
        )
        sys.exit(1)
    elif fallback_handler != NULL_ADDRESS and not ethereum_client.is_contract(
        fallback_handler
    ):
        print_formatted_text(
            f"Fallback handler address {fallback_handler} "
            f"does not exist on network {ethereum_network.name}"
        )
        sys.exit(1)

    account_balance: int = ethereum_client.get_balance(account.address)
    if not account_balance:
        print_formatted_text(
            "Client does not have any funds. Let's try anyway in case it's a network without gas costs"
        )
    else:
        ether_account_balance = round(
            ethereum_client.w3.from_wei(account_balance, "ether"), 6
        )
        print_formatted_text(
            f"Network {ethereum_client.get_network().name} - Sender {account.address} - "
            f"Balance: {ether_account_balance}Ξ"
        )

    if not ethereum_client.w3.eth.get_code(
        safe_contract_address
    ) or not ethereum_client.w3.eth.get_code(proxy_factory_address):
        print_formatted_text("Network not supported")
        sys.exit(1)

    print_formatted_text(
        f"Creating new Safe with owners={owners} threshold={threshold} salt-nonce={salt_nonce}"
    )
    safe_version = Safe(safe_contract_address, ethereum_client).retrieve_version()
    print_formatted_text(
        f"Safe-master-copy={safe_contract_address} version={safe_version}\n"
        f"Fallback-handler={fallback_handler}\n"
        f"Proxy factory={proxy_factory_address}"
    )
    if yes_or_no_question("Do you want to continue?"):
        safe_contract = get_safe_V1_4_1_contract(
            ethereum_client.w3, safe_contract_address
        )
        safe_creation_tx_data = HexBytes(
            safe_contract.functions.setup(
                owners,
                threshold,
                to,
                data,
                fallback_handler,
                payment_token,
                payment,
                payment_receiver,
            ).build_transaction({"gas": 1, "gasPrice": 1})["data"]
        )

        proxy_factory = ProxyFactory(proxy_factory_address, ethereum_client)
        expected_safe_address = proxy_factory.calculate_proxy_address(
            safe_contract_address, safe_creation_tx_data, salt_nonce
        )
        if ethereum_client.is_contract(expected_safe_address):
            print_formatted_text(f"Safe on {expected_safe_address} is already deployed")
            sys.exit(1)

        if yes_or_no_question(
            f"Safe will be deployed on {expected_safe_address}, looks good?"
        ):
            ethereum_tx_sent = proxy_factory.deploy_proxy_contract_with_nonce(
                account, safe_contract_address, safe_creation_tx_data, salt_nonce
            )
            print_formatted_text(
                f"Sent tx with tx-hash={ethereum_tx_sent.tx_hash.hex()} "
                f"Safe={ethereum_tx_sent.contract_address} is being created"
            )
            print_formatted_text(f"Tx parameters={ethereum_tx_sent.tx}")
            return ethereum_tx_sent
