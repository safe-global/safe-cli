import argparse
import secrets
import sys
from binascii import Error
from typing import List

import pyfiglet
from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_typing import URI
from prompt_toolkit import print_formatted_text

from gnosis.eth import EthereumClient
from gnosis.safe import ProxyFactory, Safe

from safe_cli.prompt_parser import check_ethereum_address
from safe_cli.safe_addresses import (LAST_DEFAULT_CALLBACK_HANDLER,
                                     LAST_PROXY_FACTORY_CONTRACT,
                                     LAST_SAFE_CONTRACT)


def positive_integer(number: str) -> int:
    number = int(number)
    if number <= 0:
        raise argparse.ArgumentTypeError(f'{number} is not a valid threshold. Must be > 0')
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
        raise argparse.ArgumentTypeError(f'{private_key} is not a valid private key')
    return private_key


parser = argparse.ArgumentParser()
parser.add_argument('node_url', help='Ethereum node url')
parser.add_argument('private_key', help='Deployer private_key', type=check_private_key)
parser.add_argument('--threshold', help='Number of owners required to execute transactions on the created Safe. It must'
                                        'be greater than 0 and less or equal than the number of owners',
                    type=positive_integer, default=1)
parser.add_argument('--owners', help='Owners. By default it will be just the deployer', nargs='+',
                    type=check_ethereum_address)
parser.add_argument('--safe-contract', help='Use a custom Safe master copy',
                    default=LAST_SAFE_CONTRACT, type=check_ethereum_address)
parser.add_argument('--proxy-factory', help='Use a custom proxy factory',
                    default=LAST_PROXY_FACTORY_CONTRACT, type=check_ethereum_address)
parser.add_argument('--callback-handler',
                    help='Use a custom fallback handler. It is not required for Safe Master Copies '
                         'with version < 1.1.0',
                    default=LAST_DEFAULT_CALLBACK_HANDLER, type=check_ethereum_address)

if __name__ == '__main__':
    print_formatted_text(pyfiglet.figlet_format('Gnosis Safe Creator'))  # Print fancy text
    args = parser.parse_args()
    node_url: URI = args.node_url
    account: LocalAccount = Account.from_key(args.private_key)
    owners: List[str] = list(set(args.owners)) if args.owners else [account.address]
    threshold: int = args.threshold
    if len(owners) < threshold:
        print_formatted_text('Threshold cannot be bigger than the number of unique owners')
        sys.exit(1)

    safe_contract_address = args.safe_contract
    proxy_factory_address = args.proxy_factory
    callback_handler_address = args.callback_handler
    ethereum_client = EthereumClient(node_url)

    account_balance: int = ethereum_client.get_balance(account.address)
    if not account_balance:
        print_formatted_text('Client does not have any funds')
        sys.exit(1)
    else:
        ether_account_balance = round(ethereum_client.w3.fromWei(account_balance, 'ether'), 6)
        print_formatted_text(f'Sender {account.address} - Balance: {ether_account_balance}Ξ')

    if not ethereum_client.w3.eth.getCode(safe_contract_address) \
            or not ethereum_client.w3.eth.getCode(proxy_factory_address):
        print_formatted_text('Network not supported')
        sys.exit(1)

    salt_nonce = secrets.SystemRandom().randint(0, 2**256 - 1)  # TODO Add support for CPK
    print_formatted_text(f'Creating new Safe with owners={owners} threshold={threshold} and sat-nonce={salt_nonce}')
    gas_price = 0
    safe_creation_tx = Safe.build_safe_create2_tx(ethereum_client, safe_contract_address,
                                                  proxy_factory_address, salt_nonce, owners, threshold, gas_price,
                                                  fallback_handler=callback_handler_address,
                                                  payment_token=None)
    proxy_factory = ProxyFactory(proxy_factory_address, ethereum_client)
    ethereum_tx_sent = proxy_factory.deploy_proxy_contract_with_nonce(account,
                                                                      safe_contract_address,
                                                                      safe_creation_tx.safe_setup_data,
                                                                      safe_creation_tx.salt_nonce)
    print_formatted_text(f'Tx with tx-hash={ethereum_tx_sent.tx_hash.hex()} '
                         f'will create safe={ethereum_tx_sent.contract_address}')
