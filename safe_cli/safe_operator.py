import dataclasses
import os
from typing import Any, Dict, List, NoReturn, Optional, Set

from colorama import Fore, Style
from ens import ENS
from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_utils import ValidationError
from hexbytes import HexBytes
from packaging import version as semantic_version
from prompt_toolkit import HTML, print_formatted_text
from tabulate import tabulate
from web3 import Web3
from web3.exceptions import BadFunctionCallOutput

from gnosis.eth import EthereumClient
from gnosis.eth.constants import NULL_ADDRESS, SENTINEL_ADDRESS
from gnosis.eth.contracts import (get_erc20_contract, get_erc721_contract,
                                  get_safe_contract, get_safe_V1_3_0_contract)
from gnosis.eth.ethereum_client import EthereumNetwork
from gnosis.safe import InvalidInternalTx, Safe, SafeOperation, SafeTx
from gnosis.safe.multi_send import MultiSend, MultiSendOperation, MultiSendTx

from safe_cli.api.etherscan import Etherscan
from safe_cli.api.gnosis_relay import RelayService
from safe_cli.api.gnosis_transaction import TransactionService
from safe_cli.ethereum_hd_wallet import get_account_from_words
from safe_cli.safe_addresses import (LAST_DEFAULT_CALLBACK_HANDLER,
                                     LAST_MULTISEND_CONTRACT,
                                     LAST_SAFE_CONTRACT)
from safe_cli.utils import yes_or_no_question

try:
    from functools import cached_property
except ImportError:
    from cached_property import cached_property


@dataclasses.dataclass
class SafeCliInfo:
    address: str
    nonce: int
    threshold: int
    owners: List[str]
    master_copy: str
    modules: List[str]
    fallback_handler: str
    guard: str
    balance_ether: int
    version: str

    def __str__(self):
        return f'safe-version={self.version} nonce={self.nonce} threshold={self.threshold} owners={self.owners} ' \
               f'master-copy={self.master_copy} fallback-hander={self.fallback_handler} ' \
               f'modules={self.modules} balance-ether={self.balance_ether:.4f}'


class SafeOperatorException(Exception):
    pass


class ExistingOwnerException(SafeOperatorException):
    pass


class NonExistingOwnerException(SafeOperatorException):
    pass


class HashAlreadyApproved(SafeOperatorException):
    pass


class ThresholdLimitException(SafeOperatorException):
    pass


class SameFallbackHandlerException(SafeOperatorException):
    pass


class InvalidFallbackHandlerException(SafeOperatorException):
    pass


class FallbackHandlerNotSupportedException(SafeOperatorException):
    pass


class SameGuardException(SafeOperatorException):
    pass


class InvalidGuardException(SafeOperatorException):
    pass


class GuardNotSupportedException(SafeOperatorException):
    pass


class SameMasterCopyException(SafeOperatorException):
    pass


class SafeAlreadyUpdatedException(SafeOperatorException):
    pass


class UpdateAddressesNotValid(SafeOperatorException):
    pass


class SenderRequiredException(SafeOperatorException):
    pass


class AccountNotLoadedException(SafeOperatorException):
    pass


class NotEnoughSignatures(SafeOperatorException):
    pass


class InvalidMasterCopyException(SafeOperatorException):
    pass


class NotEnoughEtherToSend(SafeOperatorException):
    pass


class NotEnoughTokenToSend(SafeOperatorException):
    pass


class ServiceNotAvailable(SafeOperatorException):
    pass


class SafeOperator:
    def __init__(self, address: str, node_url: str):
        self.address = address
        self.node_url = node_url
        self.ethereum_client = EthereumClient(self.node_url)
        self.ens = ENS.fromWeb3(self.ethereum_client.w3)
        self.network: EthereumNetwork = self.ethereum_client.get_network()
        self.etherscan = Etherscan.from_network_number(self.network.value)
        self.safe_relay_service = RelayService.from_network_number(self.network.value)
        self.safe_tx_service = TransactionService.from_network_number(self.network.value)
        self.safe = Safe(address, self.ethereum_client)
        self.safe_contract = get_safe_V1_3_0_contract(self.ethereum_client.w3, address=self.address)
        self.safe_contract_1_1_0 = get_safe_contract(self.ethereum_client.w3, address=self.address)
        self.accounts: Set[LocalAccount] = set()
        self.default_sender: Optional[LocalAccount] = None
        self.executed_transactions: List[str] = []
        self._safe_cli_info: Optional[SafeCliInfo] = None  # Cache for SafeCliInfo
        self.require_all_signatures = True  # Require all signatures to be present to send a tx

    @cached_property
    def ens_domain(self) -> Optional[str]:
        # FIXME After web3.py fixes the middleware copy
        if self.network == EthereumNetwork.MAINNET:
            return self.ens.name(self.address)

    @property
    def safe_cli_info(self) -> SafeCliInfo:
        if not self._safe_cli_info:
            self._safe_cli_info = self.refresh_safe_cli_info()
        return self._safe_cli_info

    def _require_default_sender(self) -> NoReturn:
        """
        Throws SenderRequiredException if not default sender configured
        """
        if not self.default_sender:
            raise SenderRequiredException()

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

    def get_balances(self):
        if not self.safe_tx_service:  # TODO Maybe use Etherscan
            print_formatted_text(HTML(f'<ansired>No tx service available for '
                                      f'network={self.network.name}</ansired>'))
        else:
            balances = self.safe_tx_service.get_balances(self.address)
            headers = ['name', 'balance', 'symbol', 'decimals', 'tokenAddress']
            rows = []
            for balance in balances:
                if balance['tokenAddress']:  # Token
                    row = [balance['token']['name'],
                           f"{int(balance['balance']) / 10**int(balance['token']['decimals']):.5f}",
                           balance['token']['symbol'],
                           balance['token']['decimals'],
                           balance['tokenAddress']]
                else:  # Ether
                    row = ['ETHER',
                           f"{int(balance['balance']) / 10 ** 18:.5f}",
                           'Ξ',
                           18,
                           '']
                rows.append(row)
            print(tabulate(rows, headers=headers))

    def get_transaction_history(self):
        if not self.safe_tx_service:
            print_formatted_text(HTML(f'<ansired>No tx service available for '
                                      f'network={self.network.name}</ansired>'))
            if self.etherscan:
                url = f'{self.etherscan.base_url}/address/{self.address}'
                print_formatted_text(HTML(f'<b>Try Etherscan instead</b> {url}'))
        else:
            transactions = self.safe_tx_service.get_transactions(self.address)
            headers = ['nonce', 'to', 'value', 'transactionHash', 'safeTxHash']
            rows = []
            last_executed_tx = False
            for transaction in transactions:
                row = [transaction[header] for header in headers]
                data_decoded: Dict[str, Any] = transaction.get('dataDecoded')
                if data_decoded:
                    row.append(self.safe_tx_service.data_decoded_to_text(data_decoded))
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

    def load_cli_owners_from_words(self, words: List[str]):
        if len(words) == 1:  # Reading seed from Environment Variable
            words = os.environ.get(words[0], default="").strip().split(" ")
        parsed_words = ' '.join(words)
        try:
            for index in range(100):  # Try first accounts of seed phrase
                account = get_account_from_words(parsed_words, index=index)
                if account.address in self.safe_cli_info.owners:
                    self.load_cli_owners([account.key.hex()])
            if not index:
                print_formatted_text(HTML('<ansired>Cannot generate any valid owner for this Safe</ansired>'))
        except ValidationError:
            print_formatted_text(HTML('<ansired>Cannot load owners from words</ansired>'))

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
            print_formatted_text(HTML('<ansigreen>Accounts have been deleted</ansigreen>'))
        else:
            print_formatted_text(HTML('<ansired>No account was deleted</ansired>'))

    def show_cli_owners(self):
        if not self.accounts:
            print_formatted_text(HTML('<ansired>No accounts loaded</ansired>'))
        else:
            for account in self.accounts:
                print_formatted_text(HTML(f'<ansigreen><b>Account</b> {account.address} loaded</ansigreen>'))
            if self.default_sender:
                print_formatted_text(HTML(f'<ansigreen><b>Default sender:</b> {self.default_sender.address}'
                                          f'</ansigreen>'))
            else:
                print_formatted_text(HTML('<ansigreen>Not default sender set </ansigreen>'))

    def approve_hash(self, hash_to_approve: HexBytes, sender: str) -> bool:
        sender_account = [account for account in self.accounts if account.address == sender]
        if not sender_account:
            raise AccountNotLoadedException(sender)
        elif sender not in self.safe_cli_info.owners:
            raise NonExistingOwnerException(sender)
        elif self.safe.retrieve_is_hash_approved(self.default_sender.address, hash_to_approve):
            raise HashAlreadyApproved(hash_to_approve, self.default_sender.address)
        else:
            sender_account = sender_account[0]
            transaction_to_send = self.safe_contract.functions.approveHash(
                hash_to_approve
            ).buildTransaction({
                'from': sender_account.address,
                'nonce': self.ethereum_client.get_nonce_for_account(sender_account.address),
            })
            call_result = self.ethereum_client.w3.eth.call(transaction_to_send)
            if call_result:  # There's revert message
                return False
            else:
                signed_transaction = sender_account.sign_transaction(transaction_to_send)
                tx_hash = self.ethereum_client.send_raw_transaction(signed_transaction['rawTransaction'])
                print_formatted_text(HTML(f'<ansigreen>Sent tx with tx-hash {tx_hash.hex()} from owner '
                                          f'{self.default_sender.address}, waiting for receipt</ansigreen>'))
                if self.ethereum_client.get_transaction_receipt(tx_hash, timeout=120):
                    return True
                else:
                    print_formatted_text(HTML(f'<ansired>Tx with tx-hash {tx_hash.hex()} still not mined</ansired>'))
                    return False

    def add_owner(self, new_owner: str, threshold: Optional[int] = None) -> bool:
        threshold = threshold if threshold is not None else self.safe_cli_info.threshold
        if new_owner in self.safe_cli_info.owners:
            raise ExistingOwnerException(new_owner)
        else:
            # TODO Allow to set threshold
            transaction = self.safe_contract.functions.addOwnerWithThreshold(
                new_owner, threshold
            ).buildTransaction({'from': self.address, 'gas': 0, 'gasPrice': 0})
            if self.execute_safe_internal_transaction(transaction['data']):
                self.safe_cli_info.owners = self.safe.retrieve_owners()
                self.safe_cli_info.threshold = threshold
                return True
            return False

    def remove_owner(self, owner_to_remove: str, threshold: Optional[int] = None):
        threshold = threshold if threshold is not None else self.safe_cli_info.threshold
        if owner_to_remove not in self.safe_cli_info.owners:
            raise NonExistingOwnerException(owner_to_remove)
        elif len(self.safe_cli_info.owners) == threshold:
            raise ThresholdLimitException()
        else:
            index_owner = self.safe_cli_info.owners.index(owner_to_remove)
            prev_owner = self.safe_cli_info.owners[index_owner - 1] if index_owner else SENTINEL_ADDRESS
            transaction = self.safe_contract.functions.removeOwner(
                prev_owner, owner_to_remove, threshold
            ).buildTransaction({'from': self.address, 'gas': 0, 'gasPrice': 0})
            if self.execute_safe_internal_transaction(transaction['data']):
                self.safe_cli_info.owners = self.safe.retrieve_owners()
                self.safe_cli_info.threshold = threshold
                return True
            return False

    def send_custom(self, to: str, value: int, data: bytes, safe_nonce: Optional[int] = None,
                    delegate_call: bool = False) -> bool:
        if value > 0:
            safe_balance = self.ethereum_client.get_balance(self.address)
            if safe_balance < value:
                raise NotEnoughEtherToSend(safe_balance)
        operation = SafeOperation.DELEGATE_CALL if delegate_call else SafeOperation.CALL
        return self.execute_safe_transaction(to, value, data, operation, safe_nonce=safe_nonce)

    def send_ether(self, to: str, value: int, **kwargs) -> bool:
        return self.send_custom(to, value, b'', **kwargs)

    def send_erc20(self, to: str, token_address: str, amount: int, **kwargs) -> bool:
        transaction = get_erc20_contract(self.ethereum_client.w3, token_address).functions.transfer(
            to, amount
        ).buildTransaction({'from': self.address, 'gas': 0, 'gasPrice': 0})
        return self.send_custom(token_address, 0, HexBytes(transaction['data']), **kwargs)

    def send_erc721(self, to: str, token_address: str, token_id: int, **kwargs) -> bool:
        transaction = get_erc721_contract(self.ethereum_client.w3, token_address).functions.transferFrom(
            self.address, to, token_id
        ).buildTransaction({'from': self.address, 'gas': 0, 'gasPrice': 0})
        return self.send_custom(token_address, 0, transaction['data'], **kwargs)

    def change_fallback_handler(self, new_fallback_handler: str) -> bool:
        if new_fallback_handler == self.safe_cli_info.fallback_handler:
            raise SameFallbackHandlerException(new_fallback_handler)
        elif semantic_version.parse(self.safe_cli_info.version) < semantic_version.parse('1.1.0'):
            raise FallbackHandlerNotSupportedException()
        elif new_fallback_handler != NULL_ADDRESS and not self.ethereum_client.is_contract(new_fallback_handler):
            raise InvalidFallbackHandlerException(f'{new_fallback_handler} address is not a contract')
        else:
            transaction = self.safe_contract.functions.setFallbackHandler(
                new_fallback_handler
            ).buildTransaction({'from': self.address, 'gas': 0, 'gasPrice': 0})
            if self.execute_safe_internal_transaction(transaction['data']):
                self.safe_cli_info.fallback_handler = new_fallback_handler
                self.safe_cli_info.version = self.safe.retrieve_version()
                return True

    def change_guard(self, guard: str) -> bool:
        if guard == self.safe_cli_info.guard:
            raise SameGuardException(guard)
        elif semantic_version.parse(self.safe_cli_info.version) < semantic_version.parse('1.3.0'):
            raise GuardNotSupportedException()
        elif guard != NULL_ADDRESS and not self.ethereum_client.is_contract(guard):
            raise InvalidGuardException(f'{guard} address is not a contract')
        else:
            transaction = self.safe_contract.functions.setGuard(
                guard
            ).buildTransaction({'from': self.address, 'gas': 0, 'gasPrice': 0})
            if self.execute_safe_internal_transaction(transaction['data']):
                self.safe_cli_info.guard = guard
                self.safe_cli_info.version = self.safe.retrieve_version()
                return True

    def change_master_copy(self, new_master_copy: str) -> bool:
        # TODO Check that master copy is valid
        if new_master_copy == self.safe_cli_info.master_copy:
            raise SameMasterCopyException(new_master_copy)
        else:
            try:
                Safe(new_master_copy, self.ethereum_client).retrieve_version()
            except BadFunctionCallOutput:
                raise InvalidMasterCopyException(new_master_copy)

            transaction = self.safe_contract_1_1_0.functions.changeMasterCopy(
                new_master_copy
            ).buildTransaction({'from': self.address, 'gas': 0, 'gasPrice': 0})
            if self.execute_safe_internal_transaction(transaction['data']):
                self.safe_cli_info.master_copy = new_master_copy
                self.safe_cli_info.version = self.safe.retrieve_version()
                return True

    def update_version(self) -> Optional[bool]:
        """
        Update Safe Master Copy and Fallback handler to the last version
        :return:
        """
        if self.is_version_updated():
            raise SafeAlreadyUpdatedException()

        addresses = (LAST_SAFE_CONTRACT, LAST_DEFAULT_CALLBACK_HANDLER)
        if not all(self.ethereum_client.is_contract(contract)
                   for contract in addresses):
            raise UpdateAddressesNotValid('Not valid addresses to update Safe', *addresses)

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
        if module_address in self.safe_cli_info.modules:
            print_formatted_text(HTML(f'<ansired>Module {module_address} is already enabled</ansired>'))
        else:
            transaction = self.safe_contract.functions.enableModule(
                module_address
            ).buildTransaction({'from': self.address, 'gas': 0, 'gasPrice': 0})
            if self.execute_safe_internal_transaction(transaction['data']):
                self.safe_cli_info.modules = self.safe.retrieve_modules()

    def disable_module(self, module_address: str):
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
        if self.ens_domain:
            print_formatted_text(HTML(f'<b><ansigreen>Ens domain</ansigreen></b>='
                                      f'<ansiblue>{self.ens_domain}</ansiblue>'))
        if self.safe_tx_service:
            url = f'{self.safe_tx_service.base_url}/api/v1/safes/{self.address}/transactions/'
            print_formatted_text(HTML(f'<b><ansigreen>Safe Tx Service</ansigreen></b>='
                                      f'<ansiblue>{url}</ansiblue>'))

        if self.safe_relay_service:
            url = f'{self.safe_relay_service.base_url}/api/v1/safes/{self.address}/transactions/'
            print_formatted_text(HTML(f'<b><ansigreen>Safe Relay Service</ansigreen></b>='
                                      f'<ansiblue>{url}</ansiblue>'))

        if self.etherscan:
            url = f'{self.etherscan.base_url}/address/{self.address}'
            print_formatted_text(HTML(f'<b><ansigreen>Etherscan</ansigreen></b>='
                                      f'<ansiblue>{url}</ansiblue>'))

        if not self.is_version_updated():
            print_formatted_text(HTML('<ansired>Safe is not updated! You can use <b>update</b> command to update '
                                      'the Safe to a newest version</ansired>'))

    def get_safe_cli_info(self) -> SafeCliInfo:
        safe = self.safe
        balance_ether = Web3.fromWei(self.ethereum_client.get_balance(self.address), 'ether')
        safe_info = safe.retrieve_all_info()
        return SafeCliInfo(self.address, safe_info.nonce, safe_info.threshold,
                           safe_info.owners, safe_info.master_copy, safe_info.modules, safe_info.fallback_handler,
                           safe_info.guard, balance_ether, safe_info.version)

    def get_threshold(self):
        print_formatted_text(self.safe.retrieve_threshold())

    def get_nonce(self):
        print_formatted_text(self.safe.retrieve_nonce())

    def get_owners(self):
        print_formatted_text(self.safe.retrieve_owners())

    def execute_safe_internal_transaction(self, data: bytes) -> bool:
        return self.execute_safe_transaction(self.address, 0, data)

    def prepare_safe_transaction(self, to: str, value: int, data: bytes,
                                 operation: SafeOperation = SafeOperation.CALL,
                                 safe_nonce: Optional[int] = None) -> SafeTx:
        self._require_default_sender()  # Throws Exception if default sender not found
        safe_tx = self.safe.build_multisig_tx(to, value, data, operation=operation.value, safe_nonce=safe_nonce)
        self.sign_transaction(safe_tx)  # Raises exception if it cannot be signed
        return safe_tx

    def execute_safe_transaction(self, to: str, value: int, data: bytes,
                                 operation: SafeOperation = SafeOperation.CALL,
                                 safe_nonce: Optional[int] = None) -> bool:
        safe_tx = self.prepare_safe_transaction(to, value, data, operation, safe_nonce=safe_nonce)
        try:
            call_result = safe_tx.call(self.default_sender.address)
            print_formatted_text(HTML(f'Result: <ansigreen>{call_result}</ansigreen>'))
            if yes_or_no_question('Do you want to execute tx ' + str(safe_tx)):
                tx_hash, _ = safe_tx.execute(self.default_sender.key)
                self.executed_transactions.append(tx_hash.hex())
                print_formatted_text(HTML(f'<ansigreen>Sent tx with tx-hash {tx_hash.hex()} '
                                          f'and safe-nonce {safe_tx.safe_nonce}, waiting for receipt</ansigreen>'))
                if self.ethereum_client.get_transaction_receipt(tx_hash, timeout=120):
                    self.safe_cli_info.nonce += 1
                    return True
                else:
                    print_formatted_text(HTML(f'<ansired>Tx with tx-hash {tx_hash.hex()} still not mined</ansired>'))
                    return False
        except InvalidInternalTx as invalid_internal_tx:
            print_formatted_text(HTML(f'Result: <ansired>InvalidTx - {invalid_internal_tx}</ansired>'))
            return False

    # TODO Set sender so we can save gas in that signature
    def sign_transaction(self, safe_tx: SafeTx) -> NoReturn:
        owners = self.safe_cli_info.owners
        threshold = self.safe_cli_info.threshold
        selected_accounts: List[Account] = []  # Some accounts that are not an owner can be loaded
        for account in self.accounts:
            if account.address in owners:
                selected_accounts.append(account)
                threshold -= 1
                if threshold == 0:
                    break

        if self.require_all_signatures and threshold > 0:
            raise NotEnoughSignatures(threshold)

        for selected_account in selected_accounts:
            safe_tx.sign(selected_account.key)

        """
        selected_accounts.sort(key=lambda a: a.address.lower())
        signatures: bytes = b''
        for selected_account in selected_accounts:
            signatures += selected_account.signHash(safe_tx_hash)
        return signatures
        """

    def process_command(self, first_command: str, rest_command: List[str]) -> bool:
        if first_command == 'help':
            print_formatted_text('I still cannot help you')
        elif first_command == 'history':
            self.get_transaction_history()
        elif first_command == 'refresh':
            print_formatted_text('Reloading Safe information')
            self.refresh_safe_cli_info()

        return False
