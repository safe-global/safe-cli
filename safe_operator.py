import dataclasses
import os
from typing import Any, Dict, List, Optional, Set

import requests
from colorama import Fore, Style
from eth_account import Account
from prompt_toolkit import HTML, print_formatted_text
from tabulate import tabulate
from web3 import Web3

from gnosis.eth import EthereumClient
from gnosis.eth.constants import SENTINEL_ADDRESS
from gnosis.eth.contracts import get_erc20_contract
from gnosis.safe import Safe, SafeTx

ETHERSCAN_BY_NETWORK = {
    1: 'https://etherscan.io',
    3: 'https://ropsten.etherscan.io',
    4: 'https://rinkeby.etherscan.io',
    5: 'https://goerli.etherscan.io',
    42: 'https://kovan.etherscan.io',
}

SAFE_TX_SERVICE_BY_NETWORK = {
    1: 'https://safe-transaction.mainnet.gnosis.io',
    # 3:
    4: 'https://safe-transaction.rinkeby.gnosis.io',
    # 5:
    # 42
}

SAFE_RELAY_SERVICE_BY_NETWORK = {
    1: 'https://safe-relay.gnosis.io',
    # 3:
    4: 'https://safe-relay.rinkeby.gnosis.io',
    # 5:
    # 42
}

@dataclasses.dataclass
class SafeInfo:
    address: str
    nonce: int
    threshold: int
    owners: List[str]
    master_copy: str
    fallback_handler: str
    balance_ether: int
    version: str

    def __str__(self):
        return f'safe-version={self.version} nonce={self.nonce} threshold={self.threshold} owners={self.owners} ' \
               f'master-copy={self.master_copy} fallback-hander={self.fallback_handler} ' \
               f'balance_ether={self.balance_ether}'


class SafeOperator:
    def __init__(self, address: str, node_url: str):
        self.address = address
        self.node_url = node_url
        self.ethereum_client = EthereumClient(self.node_url)
        self.network = self.ethereum_client.get_network()
        self.network_name = self.network.name
        self.etherscan_address: Optional[str] = ETHERSCAN_BY_NETWORK.get(self.network.value)
        self.safe_tx_service_url: Optional[str] = SAFE_TX_SERVICE_BY_NETWORK.get(self.network.value)
        self.safe_relay_service_url: Optional[str] = SAFE_RELAY_SERVICE_BY_NETWORK.get(self.network.value)
        self.safe = Safe(address, self.ethereum_client)
        self.safe_contract = self.safe.get_contract()
        self.safe_info: SafeInfo = self.get_safe_info()
        self.accounts: Set[Account] = set()
        self.default_sender: Optional[Account] = None
        self.executed_transactions: List[str] = []

    def bottom_toolbar(self):
        return HTML(f'<b><style fg="ansiyellow">network={self.network_name} {self.safe_info}</style></b>')

    def get_transaction_history(self):
        if not self.safe_tx_service_url:
            print_formatted_text(HTML(f'<ansired>No tx service available for '
                                      f'network={self.network_name}</ansired>'))
            if self.etherscan_address:
                url = f'{self.etherscan_address}/address/{self.address}'
                print_formatted_text(HTML(f'<b>Try Etherscan instead</b> {url}'))
        else:
            # FIXME Split this in a module with proper tests
            url = f'{self.safe_tx_service_url}/api/v1/safes/{self.address}/transactions/'
            print_formatted_text(url)
            response = requests.get(url)
            if response.ok:
                transactions = response.json().get('results', [])
                headers = ['nonce', 'to', 'value', 'transactionHash', 'safeTxHash']
                rows = []
                last_executed_tx = False
                for transaction in transactions:
                    row = [transaction[header] for header in headers]
                    data_decoded: Dict[str, Any] = transaction.get('dataDecoded')
                    if data_decoded:
                        row.append(str(list(data_decoded.keys())))
                    if transaction['transactionHash'] and transaction['isSuccessful']:
                        row[0] = Fore.GREEN + str(row[0])  # For executed transactions we use green
                        if not last_executed_tx:
                            row[0] = Style.BRIGHT + row[0]
                            last_executed_tx = True
                    elif transaction['transactionHash']:
                        row[0] = Fore.RED + str(row[0])  # For transactions failed
                    else:
                        row[0] = Fore.YELLOW + str(row[0])  # For non executed transactions we use yellow

                    row[0] = Style.RESET_ALL + row[0]  # Reset all just in case
                    rows.append(row)

                headers.append('dataDecoded')
                headers[0] = Style.BRIGHT + headers[0]
                print(tabulate(rows, headers=headers))
            else:
                print_formatted_text(f'Cannot get transactions from {url}')

    def load_cli_owners(self, keys: List[str]):
        for key in keys:
            try:
                account = Account.from_key(os.environ.get(key, default=key))  # Try to get key from `environ`
            except ValueError:
                print_formatted_text(HTML(f'<ansired>Cannot load key=f{key}</ansired>'))
            self.accounts.add(account)
            balance = self.ethereum_client.get_balance(account.address)
            print_formatted_text(HTML(f'Loaded account <b>{account.address}</b> '
                                      f'with balance={Web3.fromWei(balance, "ether")} ether'))
            if not self.default_sender and balance > 0:
                print_formatted_text(HTML(f'Set account <b>{account.address}</b> as default sender of txs'))
                self.default_sender = account

    def unload_cli_owners(self, owners: List[str]):
        accounts_to_remove: Set[Account] = set()
        for owner in owners:
            for account in self.accounts:
                if account.address == owner:
                    if self.default_sender and self.default_sender.address == owner:
                        self.default_sender = None
                    accounts_to_remove.add(account)
                    break
        self.accounts = self.accounts.difference(accounts_to_remove)
        if accounts_to_remove:
            print_formatted_text(HTML(f'<ansigreen>Accounts have been deleted</ansigreen>'))
        else:
            print_formatted_text(HTML(f'<ansired>No account was deleted</ansired>'))

    def show_cli_owners(self):
        if not self.accounts:
            print_formatted_text(HTML(f'<ansired>No accounts loaded</ansired>'))
        else:
            for account in self.accounts:
                print_formatted_text(HTML(f'<ansigreen><b>Account</b> {account.address} loaded</ansigreen>'))
            if self.default_sender:
                print_formatted_text(HTML(f'<ansigreen><b>Default sender:</b> {self.default_sender.address}'
                                          f'</ansigreen>'))
            else:
                print_formatted_text(HTML(f'<ansigreen>Not default sender set </ansigreen>'))

    def add_owner(self, new_owner: str):
        if not Web3.isChecksumAddress(new_owner):
            raise ValueError(new_owner)
        elif new_owner in self.safe_info.owners:
            print_formatted_text(HTML(f'<ansired>Owner {new_owner} is already an owner of the Safe'
                                      f'</ansired>'))
        else:
            # TODO Allow to set threshold
            threshold = self.safe_info.threshold
            transaction = self.safe_contract.functions.addOwnerWithThreshold(
                new_owner, threshold
            ).buildTransaction({'from': self.address, 'gas': 0, 'gasPrice': 0})
            if self.execute_safe_internal_transaction(transaction['data']):
                self.safe_info.owners = self.safe.retrieve_owners()
                self.safe_info.threshold = threshold

    def remove_owner(self, owner_to_remove: str):
        if not Web3.isChecksumAddress(owner_to_remove):
            raise ValueError(owner_to_remove)
        elif owner_to_remove not in self.safe_info.owners:
            print_formatted_text(HTML(f'<ansired>Owner {owner_to_remove} is not an owner of the Safe'
                                      f'</ansired>'))
        elif len(self.safe_info.owners) == self.safe_info.threshold:
            print_formatted_text(HTML(f'<ansired>Having less owners than threshold is not allowed'
                                      f'</ansired>'))
        else:
            index_owner = self.safe_info.owners.index(owner_to_remove)
            prev_owner = self.safe_info.owners[index_owner - 1] if index_owner else SENTINEL_ADDRESS
            threshold = self.safe_info.threshold
            transaction = self.safe_contract.functions.removeOwner(
                prev_owner, owner_to_remove, threshold
            ).buildTransaction({'from': self.address, 'gas': 0, 'gasPrice': 0})
            if self.execute_safe_internal_transaction(transaction['data']):
                self.safe_info.owners = self.safe.retrieve_owners()
                self.safe_info.threshold = threshold

    def send_ether(self, address: str, value: int) -> bool:
        return self.execute_safe_transaction(address, value, b'')

    def send_erc20(self, address: str, token_address: str, value: int) -> bool:
        transaction = get_erc20_contract(self.ethereum_client.w3, token_address).functions.transfer(
            address, value
        ).buildTransaction({'from': self.address, 'gas': 0, 'gasPrice': 0})
        return self.execute_safe_transaction(token_address, 0, transaction['data'])

    def change_master_copy(self, new_master_copy: str):
        # TODO Check that master copy is valid
        if not Web3.isChecksumAddress(new_master_copy):
            raise ValueError(new_master_copy)
        elif new_master_copy == self.safe_info.master_copy:
            print_formatted_text(HTML(f'<ansired>Master copy {new_master_copy} is the current one</ansired>'))
        else:
            transaction = self.safe_contract.functions.changeMasterCopy(
                new_master_copy
            ).buildTransaction({'from': self.address, 'gas': 0, 'gasPrice': 0})
            if self.execute_safe_internal_transaction(transaction['data']):
                self.safe_info.master_copy = new_master_copy
                self.safe_info.version = self.safe.retrieve_version()

    def change_threshold(self, threshold: int):
        if not self.require_default_sender():
            return False
        if threshold == self.safe_info.threshold:
            print_formatted_text(HTML(f'<ansired>Threshold is already {threshold}</ansired>'))
        elif threshold > len(self.safe_info.owners):
            print_formatted_text(HTML(f'<ansired>Threshold={threshold} bigger than number '
                                      f'of owners={len(self.safe_info.owners)}</ansired>'))
        else:
            transaction = self.safe_contract.functions.changeThreshold(
                threshold
            ).buildTransaction({'from': self.address, 'gas': 0, 'gasPrice': 0})

            if self.execute_safe_internal_transaction(transaction['data']):
                self.safe_info.threshold = threshold

    def print_info(self):
        for key, value in dataclasses.asdict(self.safe_info).items():
            print_formatted_text(HTML(f'<b><ansigreen>{key.capitalize()}</ansigreen></b>='
                                      f'<ansiblue>{value}</ansiblue>'))
        if self.safe_tx_service_url:
            url = f'{self.safe_tx_service_url}/api/v1/safes/{self.address}/transactions/'
            print_formatted_text(HTML(f'<b><ansigreen>Safe Tx Service</ansigreen></b>='
                                      f'<ansiblue>{url}</ansiblue>'))

        if self.safe_relay_service_url:
            url = f'{self.safe_relay_service_url}/api/v1/safes/{self.address}/transactions/'
            print_formatted_text(HTML(f'<b><ansigreen>Safe Relay Service</ansigreen></b>='
                                      f'<ansiblue>{url}</ansiblue>'))

        if self.etherscan_address:
            url = f'{self.etherscan_address}/address/{self.address}'
            print_formatted_text(HTML(f'<b><ansigreen>Etherscan</ansigreen></b>='
                                      f'<ansiblue>{url}</ansiblue>'))

    def get_safe_info(self) -> SafeInfo:
        safe = self.safe
        balance_ether = Web3.fromWei(self.ethereum_client.get_balance(self.address), 'ether')
        return SafeInfo(self.address, safe.retrieve_nonce(), safe.retrieve_threshold(),
                        safe.retrieve_owners(), safe.retrieve_master_copy_address(), safe.retrieve_fallback_handler(),
                        balance_ether, safe.retrieve_version())

    def get_threshold(self):
        print_formatted_text(self.safe.retrieve_threshold())

    def get_nonce(self):
        print_formatted_text(self.safe.retrieve_nonce())

    def get_owners(self):
        print_formatted_text(self.safe.retrieve_owners())

    def refresh_safe_info(self) -> SafeInfo:
        self.safe_info = self.get_safe_info()
        return self.safe_info

    def require_default_sender(self) -> bool:
        if not self.default_sender:
            print_formatted_text(HTML(f'<ansired>Please load a default sender</ansired>'))
            return False
        return True

    def execute_safe_internal_transaction(self, data: bytes) -> bool:
        return self.execute_safe_transaction(self.address, 0, data)

    def execute_safe_transaction(self, to: str, value: int, data: bytes) -> bool:
        safe_tx = self.safe.build_multisig_tx(to, value, data)
        if not self.sign_transaction(safe_tx):
            return False
        print_formatted_text(HTML(f'Result: <ansigreen>{safe_tx.call(self.default_sender.address)}'
                                  f'</ansigreen>'))
        tx_hash, _ = safe_tx.execute(self.default_sender.key)
        self.executed_transactions.append(tx_hash.hex())
        print_formatted_text(HTML(f'<ansigreen>Executed tx with tx-hash={tx_hash.hex()}, waiting for receipt'
                                  f'</ansigreen>'))
        if self.ethereum_client.get_transaction_receipt(tx_hash, timeout=120):
            self.safe_info.nonce += 1
            return True
        else:
            print_formatted_text(HTML(f'<ansired>Tx with tx-hash={tx_hash.hex()} still not mined</ansired>'))
        return False

    # TODO Set sender so we can save gas in that signature
    def sign_transaction(self, safe_tx: SafeTx) -> bool:
        owners = self.safe_info.owners
        threshold = self.safe_info.threshold
        selected_accounts: List[Account] = []  # Need to be sorted
        for account in self.accounts:
            if account.address in owners:
                selected_accounts.append(account)
                threshold -= 1
                if threshold == 0:
                    break

        if threshold > 0:
            print_formatted_text(HTML(f'<ansired>Cannot find enough owners to sign. {threshold} missing</ansired>'))
            return False

        for selected_account in selected_accounts:
            safe_tx.sign(selected_account.key)

        """
        selected_accounts.sort(key=lambda a: a.address.lower())
        signatures: bytes = b''
        for selected_account in selected_accounts:
            signatures += selected_account.signHash(safe_tx_hash)
        return signatures
        """

        return True

    def process_command(self, first_command: str, rest_command: List[str]) -> bool:
        if first_command == 'help':
            print_formatted_text('I still cannot help you')
        elif first_command == 'history':
            self.get_transaction_history()
        elif first_command == 'refresh':
            print_formatted_text('Reloading Safe information')
            self.refresh_safe_info()

        return False
