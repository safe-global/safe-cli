#!/bin/env python3
import argparse
import secrets
import sys
from binascii import Error
from typing import List

import pyfiglet
from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_typing import URI
from hexbytes import HexBytes
from prompt_toolkit import print_formatted_text

from gnosis.eth import EthereumClient
from gnosis.eth.constants import NULL_ADDRESS
from gnosis.eth.contracts import get_safe_V1_3_0_contract
from gnosis.safe import ProxyFactory

from safe_cli.prompt_parser import check_ethereum_address
from safe_cli.safe_addresses import (
    LAST_DEFAULT_CALLBACK_HANDLER,
    LAST_PROXY_FACTORY_CONTRACT,
    LAST_SAFE_CONTRACT,
    LAST_SAFE_L2_CONTRACT,
)
from safe_cli.utils import yes_or_no_question


def positive_integer(number: str) -> int:
    number = int(number)
    if number <= 0:
        raise argparse.ArgumentTypeError(
            f"{number} is not a valid threshold. Must be > 0"
        )
    return number


def check_private_key(private_key: str) -> str:
    """
    Ethereum private key validator for ArgParse
    :param private_key: Ethereum Private key
    :return: Ethereum Private key
    """
    try:
        Account.from_key(private_key)
    except (ValueError, Error):  # TODO Report `Error` exception as a bug of eth_account
        raise argparse.ArgumentTypeError(f"{private_key} is not a valid private key")
    return private_key


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
        type=positive_integer,
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
        default=LAST_PROXY_FACTORY_CONTRACT,
        type=check_ethereum_address,
    )
    parser.add_argument(
        "--callback-handler",
        help="Use a custom fallback handler. It is not required for Safe Master Copies "
        "with version < 1.1.0",
        default=LAST_DEFAULT_CALLBACK_HANDLER,
        type=check_ethereum_address,
    )
    parser.add_argument(
        "--salt-nonce",
        help="Use a custom nonce for the deployment. Same nonce with same deployment configuration will "
        "lead to the same Safe address ",
        default=secrets.SystemRandom().randint(
            0, 2**256 - 1
        ),  # TODO Add support for CPK
        type=int,
    )

    parser.add_argument(
        "--l2",
        help="Use L2 deployment of the Safe instead of the regular one. Recommended for every network but mainnet",
        default=False,
        action="store_true",
    )
    return parser


def main(*args, **kwargs):
    parser = setup_argument_parser()
    print_formatted_text(
        pyfiglet.figlet_format("Gnosis Safe Creator")
    )  # Print fancy text
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

    safe_contract_address = args.safe_contract or (
        LAST_SAFE_L2_CONTRACT if args.l2 else LAST_SAFE_CONTRACT
    )
    proxy_factory_address = args.proxy_factory
    fallback_handler = args.callback_handler
    ethereum_client = EthereumClient(node_url)
    ethereum_network = ethereum_client.get_network()

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
            ethereum_client.w3.fromWei(account_balance, "ether"), 6
        )
        print_formatted_text(
            f"Network {ethereum_client.get_network().name} - Sender {account.address} - "
            f"Balance: {ether_account_balance}Ξ"
        )

    if not ethereum_client.w3.eth.getCode(
        safe_contract_address
    ) or not ethereum_client.w3.eth.getCode(proxy_factory_address):
        print_formatted_text("Network not supported")
        sys.exit(1)

    print_formatted_text(
        f"Creating new Safe with owners={owners} threshold={threshold} salt-nonce={salt_nonce}"
    )
    print_formatted_text(
        f"Proxy factory={proxy_factory_address} safe-master-copy={safe_contract_address} and "
        f"fallback-handler={fallback_handler}"
    )
    if yes_or_no_question("Do you want to continue?"):
        safe_contract = get_safe_V1_3_0_contract(
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
        ethereum_tx_sent = proxy_factory.deploy_proxy_contract_with_nonce(
            account, safe_contract_address, safe_creation_tx_data, salt_nonce
        )
        print_formatted_text(
            f"Tx with tx-hash={ethereum_tx_sent.tx_hash.hex()} "
            f"will create safe={ethereum_tx_sent.contract_address}"
        )
        print_formatted_text(f"Tx parameters={ethereum_tx_sent.tx}")
