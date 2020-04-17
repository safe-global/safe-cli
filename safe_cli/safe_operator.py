import dataclasses
import os
from typing import Any, Dict, List, Optional, Set

import requests
from colorama import Fore, Style
from eth_account import Account
from packaging import version as semantic_version
from prompt_toolkit import HTML, print_formatted_text
from tabulate import tabulate
from web3 import Web3
from web3.exceptions import BadFunctionCallOutput

from gnosis.eth import EthereumClient
from gnosis.eth.constants import SENTINEL_ADDRESS
from gnosis.eth.contracts import get_erc20_contract, get_safe_contract
from gnosis.safe import InvalidInternalTx, Safe, SafeOperation, SafeTx
from gnosis.safe.multi_send import MultiSend, MultiSendOperation, MultiSendTx

from safe_cli.safe_addresses import (LAST_DEFAULT_CALLBACK_HANDLER,
                                     LAST_MULTISEND_CONTRACT,
                                     LAST_SAFE_CONTRACT)

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
class SafeCliInfo:
    address: str
    nonce: int
    threshold: int
    owners: List[str]
    master_copy: str
    modules: List[str]
    fallback_handler: str
    balance_ether: int
    version: str

    def __str__(self):
        return f'safe-version={self.version} nonce={self.nonce} threshold={self.threshold} owners={self.owners} ' \
               f'master-copy={self.master_copy} fallback-hander={self.fallback_handler} ' \
               f'modules={self.modules} balance-ether={self.balance_ether:.4f}'


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
        self.accounts: Set[Account] = set()
        self.default_sender: Optional[Account] = None
        self.executed_transactions: List[str] = []
        self._safe_cli_info: Optional[SafeCliInfo] = None  # Cache for SafeCliInfo

    @property
    def safe_cli_info(self) -> SafeCliInfo:
        if not self._safe_cli_info:
            self._safe_cli_info = self.refresh_safe_cli_info()
        return self._safe_cli_info

    def is_version_updated(self) -> bool:
        """
        :return: True if Safe Master Copy is updated, False otherwise
        """

        if self._safe_cli_info.master_copy == LAST_SAFE_CONTRACT:
            return True
        else:  # Check versions, maybe safe-cli addresses were not updated
            safe_contract = get_safe_contract(self.ethereum_client.w3, LAST_SAFE_CONTRACT)
            try:
                safe_contract_version = safe_contract.functions.VERSION().call()
            except BadFunctionCallOutput:  # Safe master copy is not deployed or errored, maybe custom network
                return True  # We cannot say you are not updated ¯\_(ツ)_/¯
            return semantic_version.parse(self.safe_cli_info.version) >= semantic_version.parse(safe_contract_version)

    def refresh_safe_cli_info(self) -> SafeCliInfo:
        self._safe_cli_info = self.get_safe_cli_info()
        return self._safe_cli_info

    def bottom_toolbar(self):
        return HTML(f'<b><style fg="ansiyellow">network={self.network_name} {self.safe_cli_info}</style></b>')

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
                self.accounts.add(account)
                balance = self.ethereum_client.get_balance(account.address)
                print_formatted_text(HTML(f'Loaded account <b>{account.address}</b> '
                                          f'with balance={Web3.fromWei(balance, "ether")} ether'))
                if not self.default_sender and balance > 0:
                    print_formatted_text(HTML(f'Set account <b>{account.address}</b> as default sender of txs'))
                    self.default_sender = account
            except ValueError:
                print_formatted_text(HTML(f'<ansired>Cannot load key=f{key}</ansired>'))

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
        elif new_owner in self.safe_cli_info.owners:
            print_formatted_text(HTML(f'<ansired>Owner {new_owner} is already an owner of the Safe'
                                      f'</ansired>'))
        else:
            # TODO Allow to set threshold
            threshold = self.safe_cli_info.threshold
            transaction = self.safe_contract.functions.addOwnerWithThreshold(
                new_owner, threshold
            ).buildTransaction({'from': self.address, 'gas': 0, 'gasPrice': 0})
            if self.execute_safe_internal_transaction(transaction['data']):
                self.safe_cli_info.owners = self.safe.retrieve_owners()
                self.safe_cli_info.threshold = threshold

    def remove_owner(self, owner_to_remove: str):
        if not Web3.isChecksumAddress(owner_to_remove):
            raise ValueError(owner_to_remove)
        elif owner_to_remove not in self.safe_cli_info.owners:
            print_formatted_text(HTML(f'<ansired>Owner {owner_to_remove} is not an owner of the Safe'
                                      f'</ansired>'))
        elif len(self.safe_cli_info.owners) == self.safe_cli_info.threshold:
            print_formatted_text(HTML(f'<ansired>Having less owners than threshold is not allowed'
                                      f'</ansired>'))
        else:
            index_owner = self.safe_cli_info.owners.index(owner_to_remove)
            prev_owner = self.safe_cli_info.owners[index_owner - 1] if index_owner else SENTINEL_ADDRESS
            threshold = self.safe_cli_info.threshold
            transaction = self.safe_contract.functions.removeOwner(
                prev_owner, owner_to_remove, threshold
            ).buildTransaction({'from': self.address, 'gas': 0, 'gasPrice': 0})
            if self.execute_safe_internal_transaction(transaction['data']):
                self.safe_cli_info.owners = self.safe.retrieve_owners()
                self.safe_cli_info.threshold = threshold

    def send_ether(self, address: str, value: int) -> bool:
        return self.execute_safe_transaction(address, value, b'')

    def send_erc20(self, address: str, token_address: str, value: int) -> bool:
        transaction = get_erc20_contract(self.ethereum_client.w3, token_address).functions.transfer(
            address, value
        ).buildTransaction({'from': self.address, 'gas': 0, 'gasPrice': 0})
        return self.execute_safe_transaction(token_address, 0, transaction['data'])

    def change_fallback_handler(self, new_fallback_handler: str):
        # TODO Check that fallback handler is valid
        if not Web3.isChecksumAddress(new_fallback_handler):
            raise ValueError(new_fallback_handler)
        elif new_fallback_handler == self.safe_cli_info.fallback_handler:
            print_formatted_text(HTML(f'<ansired>Fallback handler {new_fallback_handler} is the current one</ansired>'))
        elif semantic_version.parse(self.safe_cli_info.version) < semantic_version.parse('1.1.0'):
            print_formatted_text(HTML(f'<ansired>Fallback handler is not supported for your Safe, '
                                      f'you need to <b>update</b> first</ansired>'))
        else:
            transaction = self.safe_contract.functions.setFallbackHandler(
                new_fallback_handler
            ).buildTransaction({'from': self.address, 'gas': 0, 'gasPrice': 0})
            if self.execute_safe_internal_transaction(transaction['data']):
                self.safe_cli_info.fallback_handler = new_fallback_handler
                self.safe_cli_info.version = self.safe.retrieve_version()

    def change_master_copy(self, new_master_copy: str):
        # TODO Check that master copy is valid
        if not Web3.isChecksumAddress(new_master_copy):
            raise ValueError(new_master_copy)
        elif new_master_copy == self.safe_cli_info.master_copy:
            print_formatted_text(HTML(f'<ansired>Master copy {new_master_copy} is the current one</ansired>'))
        else:
            transaction = self.safe_contract.functions.changeMasterCopy(
                new_master_copy
            ).buildTransaction({'from': self.address, 'gas': 0, 'gasPrice': 0})
            if self.execute_safe_internal_transaction(transaction['data']):
                self.safe_cli_info.master_copy = new_master_copy
                self.safe_cli_info.version = self.safe.retrieve_version()

    def update_version(self) -> Optional[bool]:
        """
        Update Safe Master Copy and Fallback handler to the last version
        :return:
        """
        if self.is_version_updated():
            print_formatted_text(HTML(f'<ansired>Safe is already updated</ansired>'))
            return

        multisend = MultiSend(LAST_MULTISEND_CONTRACT, self.ethereum_client)
        tx_params = {'from': self.address, 'gas': 0, 'gasPrice': 0}
        multisend_txs = [MultiSendTx(MultiSendOperation.CALL, self.address, 0, data) for data in
                         (self.safe_contract.functions.changeMasterCopy(LAST_SAFE_CONTRACT
                                                                        ).buildTransaction(tx_params)['data'],
                          self.safe_contract.functions.setFallbackHandler(LAST_DEFAULT_CALLBACK_HANDLER
                                                                          ).buildTransaction(tx_params)['data'])
                         ]

        multisend_data = multisend.build_tx_data(multisend_txs)

        if self.execute_safe_transaction(multisend.address, 0, multisend_data, operation=SafeOperation.DELEGATE_CALL):
            self.safe_cli_info.master_copy = LAST_SAFE_CONTRACT
            self.safe_cli_info.fallback_handler = LAST_DEFAULT_CALLBACK_HANDLER
            self.safe_cli_info.version = self.safe.retrieve_version()

    def change_threshold(self, threshold: int):
        if not self.require_default_sender():
            return False
        if threshold == self.safe_cli_info.threshold:
            print_formatted_text(HTML(f'<ansired>Threshold is already {threshold}</ansired>'))
        elif threshold > len(self.safe_cli_info.owners):
            print_formatted_text(HTML(f'<ansired>Threshold={threshold} bigger than number '
                                      f'of owners={len(self.safe_cli_info.owners)}</ansired>'))
        else:
            transaction = self.safe_contract.functions.changeThreshold(
                threshold
            ).buildTransaction({'from': self.address, 'gas': 0, 'gasPrice': 0})

            if self.execute_safe_internal_transaction(transaction['data']):
                self.safe_cli_info.threshold = threshold

    def enable_module(self, module_address: str):
        if not self.require_default_sender():
            return False
        if module_address in self.safe_cli_info.modules:
            print_formatted_text(HTML(f'<ansired>Module {module_address} is already enabled</ansired>'))
        else:
            transaction = self.safe_contract.functions.enableModule(
                module_address
            ).buildTransaction({'from': self.address, 'gas': 0, 'gasPrice': 0})
            if self.execute_safe_internal_transaction(transaction['data']):
                self.safe_cli_info.modules = self.safe.retrieve_modules()

    def disable_module(self, module_address: str):
        if not self.require_default_sender():
            return False
        if module_address not in self.safe_cli_info.modules:
            print_formatted_text(HTML(f'<ansired>Module {module_address} is not enabled</ansired>'))
        else:
            pos = self.safe_cli_info.modules.index(module_address)
            if pos == 0:
                previous_address = SENTINEL_ADDRESS
            else:
                previous_address = self.safe_cli_info.modules[pos - 1]
            transaction = self.safe_contract.functions.disableModule(
                previous_address, module_address
            ).buildTransaction({'from': self.address, 'gas': 0, 'gasPrice': 0})
            if self.execute_safe_internal_transaction(transaction['data']):
                self.safe_cli_info.modules = self.safe.retrieve_modules()

    def print_info(self):
        for key, value in dataclasses.asdict(self.safe_cli_info).items():
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

        if not self.is_version_updated():
            print_formatted_text(HTML(f'<ansired>Safe is not updated! You can use <b>update</b> command to update '
                                      f'the Safe to a newest version</ansired>'))

    def get_safe_cli_info(self) -> SafeCliInfo:
        print_formatted_text(HTML(f'<b><ansigreen>Loading Safe information...</ansigreen></b>'))
        safe = self.safe
        balance_ether = Web3.fromWei(self.ethereum_client.get_balance(self.address), 'ether')
        safe_info = safe.retrieve_all_info()
        return SafeCliInfo(self.address, safe_info.nonce, safe_info.threshold,
                           safe_info.owners, safe_info.master_copy, safe_info.modules, safe_info.fallback_handler,
                           balance_ether, safe_info.version)

    def get_threshold(self):
        print_formatted_text(self.safe.retrieve_threshold())

    def get_nonce(self):
        print_formatted_text(self.safe.retrieve_nonce())

    def get_owners(self):
        print_formatted_text(self.safe.retrieve_owners())

    def require_default_sender(self) -> bool:
        if not self.default_sender:
            print_formatted_text(HTML(f'<ansired>Please load a default sender</ansired>'))
            return False
        return True

    def execute_safe_internal_transaction(self, data: bytes) -> bool:
        return self.execute_safe_transaction(self.address, 0, data)

    def execute_safe_transaction(self, to: str, value: int, data: bytes,
                                 operation: SafeOperation = SafeOperation.CALL) -> bool:
        safe_tx = self.safe.build_multisig_tx(to, value, data, operation=operation.value)
        if not self.sign_transaction(safe_tx):
            return False

        try:
            call_result = safe_tx.call(self.default_sender.address)
            print_formatted_text(HTML(f'Result: <ansigreen>{call_result}</ansigreen>'))
            tx_hash, _ = safe_tx.execute(self.default_sender.key)
            self.executed_transactions.append(tx_hash.hex())
            print_formatted_text(HTML(f'<ansigreen>Executed tx with tx-hash={tx_hash.hex()} '
                                      f'and safe-nonce={safe_tx.safe_nonce}, waiting for receipt</ansigreen>'))
            if self.ethereum_client.get_transaction_receipt(tx_hash, timeout=120):
                self.safe_cli_info.nonce += 1
                return True
            else:
                print_formatted_text(HTML(f'<ansired>Tx with tx-hash={tx_hash.hex()} still not mined</ansired>'))
            return False
        except InvalidInternalTx as invalid_internal_tx:
            print_formatted_text(HTML(f'Result: <ansired>InvalidTx - {invalid_internal_tx}</ansired>'))
            return False

    # TODO Set sender so we can save gas in that signature
    def sign_transaction(self, safe_tx: SafeTx) -> bool:
        owners = self.safe_cli_info.owners
        threshold = self.safe_cli_info.threshold
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
            self.refresh_safe_cli_info()

        return False
