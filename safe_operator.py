import argparse
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from eth_account import Account
from prompt_toolkit import HTML, PromptSession, print_formatted_text
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.shell import BashLexer
from web3 import Web3

from gnosis.eth import EthereumClient
from gnosis.eth.constants import SENTINEL_ADDRESS
from gnosis.safe import Safe, SafeTx

INFURA_ENDPOINTS = {
    'mainnet': 'https://mainnet.infura.io/v3/',
    'goerli': 'https://goerli.infura.io/v3/',
    'kovan': 'https://kovan.infura.io/v3/',
    'rinkeby': 'https://rinkeby.infura.io/v3/',
    'ropsten': 'https://ropsten.infura.io/v3/',
}


@dataclass
class SafeInfo:
    address: str
    nonce: int
    threshold: int
    owners: List[str]
    master_copy: str
    version: str


class SafeOperator:
    def __init__(self, address: str, infura_project_id: str, network: str = 'rinkeby'):
        self.address = address
        self.infura_project_id = infura_project_id
        self.node_url = INFURA_ENDPOINTS[network] + infura_project_id
        self.ethereum_client = EthereumClient(self.node_url)
        self.safe = Safe(address, self.ethereum_client)
        self.safe_contract = self.safe.get_contract()
        self.safe_info: SafeInfo = self.get_safe_info()
        self.accounts: Set[Account] = set()
        self.default_sender: Optional[Account] = None

    def bottom_toolbar(self):
        return HTML(f'<b><style fg="ansiyellow">safe-version={self.safe_info.version} nonce={self.safe_info.nonce} '
                    f'threshold={self.safe_info.threshold} owners={self.safe_info.owners} '
                    f'master-copy={self.safe_info.master_copy} node-url={self.node_url}</style></b>')

    def get_safe_info(self) -> SafeInfo:
        safe = self.safe
        return SafeInfo(self.address, safe.retrieve_nonce(), safe.retrieve_threshold(),
                        safe.retrieve_owners(), safe.retrieve_master_copy_address(), safe.retrieve_version())

    def refresh_safe_info(self) -> SafeInfo:
        self.safe_info = self.get_safe_info()
        return self.safe_info

    def require_default_sender(self) -> bool:
        if not self.default_sender:
            print_formatted_text(HTML(f'<ansired>Please load a default sender</ansired>'))
            return False
        return True

    def process_command(self, first_command: str, rest_command: List[str]) -> bool:
        if first_command == 'help':
            print_formatted_text('I still cannot help you')
        elif first_command == 'get_threshold':
            print_formatted_text(self.safe.retrieve_threshold())
        elif first_command == 'get_nonce':
            print_formatted_text(self.safe.retrieve_nonce())
        elif first_command == 'get_owners':
            print_formatted_text(self.safe.retrieve_owners())
        elif first_command == 'refresh':
            print_formatted_text('Reloading Safe information')
            self.refresh_safe_info()
        elif first_command == 'show_cli_owners':
            if not self.accounts:
                print_formatted_text(HTML(f'<ansired>No accounts loaded</ansired>'))
            else:
                for account in self.accounts:
                    print_formatted_text(HTML(f'<ansigreen>Account {account.address} loaded</ansigreen>'))
        elif first_command == 'load_cli_owner':
            keys = rest_command
            if not keys:
                print_formatted_text('Specify a private key to load')
            for key in keys:
                try:
                    account = Account.from_key(key)
                except ValueError:
                    print_formatted_text(HTML(f'<ansired>Cannot load key=f{key}</ansired>'))
                self.accounts.add(account)
                balance = self.ethereum_client.get_balance(account.address)
                print_formatted_text(HTML(f'Loaded account <b>{account.address}</b> '
                                          f'with balance={Web3.fromWei(balance, "ether")}'))
                if not self.default_sender and balance > 0:
                    print_formatted_text(HTML(f'Set account <b>{account.address}</b> as default sender of txs'))
                    self.default_sender = account
        elif first_command == 'unload_cli_owner':
            owners = rest_command
            accounts_to_remove: Set[Account] = set()
            for owner in owners:
                if not self.ethereum_client.w3.isChecksumAddress(owner):
                    print_formatted_text(HTML(f'<ansired>Owner=f{owner} has invalid format</ansired>'))
                else:
                    for account in self.accounts:
                        if account.address == owners:
                            accounts_to_remove.add(account)
                            break
            self.accounts = self.accounts.difference(accounts_to_remove)
        elif first_command == 'change_threshold':
            if not self.require_default_sender():
                return False
            try:
                threshold = int(rest_command[0])
            except ValueError:
                print_formatted_text(HTML(f'<ansired>Cannot parse threshold</ansired>'))

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
        elif first_command == 'add_owner':
            try:
                new_owner = rest_command[0]
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
            except ValueError:
                print_formatted_text(HTML(f'<ansired>Cannot parse owner. Is it checksummed?</ansired>'))
        elif first_command == 'remove_owner':
            try:
                owner_to_remove = rest_command[0]
                if not Web3.isChecksumAddress(owner_to_remove):
                    raise ValueError(owner_to_remove)
                elif owner_to_remove not in self.safe_info.owners:
                    print_formatted_text(HTML(f'<ansired>Owner {owner_to_remove} is not an owner of the Safe'
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
            except ValueError:
                print_formatted_text(HTML(f'<ansired>Cannot parse owner. Is it checksummed?</ansired>'))
        return True

    def execute_safe_internal_transaction(self, data: bytes) -> bool:
        safe_tx = self.safe.build_multisig_tx(self.address, 0, data)
        if not self.sign_transaction(safe_tx):
            return False
        print_formatted_text(HTML(f'Result: <ansigreen>{safe_tx.call(self.default_sender.address)}'
                                  f'</ansigreen>'))
        tx_hash, _ = safe_tx.execute(self.default_sender.key)
        print_formatted_text(HTML(f'<ansigreen>Executed tx with tx-hash={tx_hash.hex()}, waiting for receipt'
                                  f'</ansigreen>'))
        if self.ethereum_client.get_transaction_receipt(tx_hash, timeout=120):
            self.safe_info.nonce += 1
            return True
        else:
            print_formatted_text(HTML(f'<ansired>Tx with tx-hash={tx_hash.hex()} still not mined</ansired>'))
        return False

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
