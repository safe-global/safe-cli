import dataclasses
import json
import os
from functools import cached_property, wraps
from typing import List, Optional, Sequence, Set, Tuple

from ens import ENS
from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_typing import ChecksumAddress
from eth_utils import ValidationError
from hexbytes import HexBytes
from packaging import version as semantic_version
from prompt_toolkit import HTML, print_formatted_text
from web3 import Web3
from web3.contract import Contract
from web3.exceptions import BadFunctionCallOutput

from gnosis.eth import (
    EthereumClient,
    EthereumNetwork,
    EthereumNetworkNotSupported,
    TxSpeed,
)
from gnosis.eth.clients import EtherscanClient, EtherscanClientConfigurationProblem
from gnosis.eth.constants import NULL_ADDRESS, SENTINEL_ADDRESS
from gnosis.eth.contracts import (
    get_erc20_contract,
    get_erc721_contract,
    get_safe_V1_1_1_contract,
    get_sign_message_lib_contract,
)
from gnosis.eth.eip712 import eip712_encode
from gnosis.eth.utils import get_empty_tx_params
from gnosis.safe import InvalidInternalTx, Safe, SafeOperationEnum, SafeTx
from gnosis.safe.api import TransactionServiceApi
from gnosis.safe.multi_send import MultiSend, MultiSendOperation, MultiSendTx
from gnosis.safe.safe_deployments import safe_deployments

from safe_cli.ethereum_hd_wallet import get_account_from_words
from safe_cli.operators.exceptions import (
    AccountNotLoadedException,
    ExistingOwnerException,
    FallbackHandlerNotSupportedException,
    GuardNotSupportedException,
    HashAlreadyApproved,
    InvalidFallbackHandlerException,
    InvalidGuardException,
    InvalidMasterCopyException,
    InvalidMigrationContractException,
    InvalidNonceException,
    NonExistingOwnerException,
    NotEnoughEtherToSend,
    NotEnoughSignatures,
    SafeAlreadyUpdatedException,
    SafeVersionNotSupportedException,
    SameFallbackHandlerException,
    SameGuardException,
    SameMasterCopyException,
    SenderRequiredException,
    ThresholdLimitException,
    UpdateAddressesNotValid,
)
from safe_cli.safe_addresses import (
    get_default_fallback_handler_address,
    get_last_sign_message_lib_address,
    get_safe_contract_address,
    get_safe_l2_contract_address,
)
from safe_cli.utils import choose_option_from_list, get_erc_20_list, yes_or_no_question

from ..contracts import safe_to_l2_migration
from .hw_wallets.hw_wallet import HwWallet
from .hw_wallets.hw_wallet_manager import HwWalletType, get_hw_wallet_manager


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
        return (
            f"safe-version={self.version} nonce={self.nonce} threshold={self.threshold} owners={self.owners} "
            f"master-copy={self.master_copy} fallback-hander={self.fallback_handler} "
            f"modules={self.modules} balance-ether={self.balance_ether:.4f}"
        )


def require_tx_service(f):
    @wraps(f)
    def decorated(self, *args, **kwargs):
        if not self.safe_tx_service:
            print_formatted_text(
                HTML(
                    f"<ansired>No tx service available for "
                    f"network={self.network.name}</ansired>"
                )
            )
            if self.etherscan:
                url = f"{self.etherscan.base_url}/address/{self.address}"
                print_formatted_text(HTML(f"<b>Try Etherscan instead</b> {url}"))
        else:
            return f(self, *args, **kwargs)

    return decorated


def require_default_sender(f):
    """
    Throws SenderRequiredException if not default sender configured
    """

    @wraps(f)
    def decorated(self, *args, **kwargs):
        if not self.default_sender and not self.hw_wallet_manager.sender:
            raise SenderRequiredException()
        else:
            return f(self, *args, **kwargs)

    return decorated


class SafeOperator:
    address: ChecksumAddress
    node_url: str
    ethereum_client: EthereumClient
    ens: ENS
    network: EthereumNetwork
    etherscan: Optional[EtherscanClient]
    safe_tx_service: Optional[TransactionServiceApi]
    safe: Safe
    safe_contract: Contract
    safe_contract_1_1_0: Contract
    accounts: Set[LocalAccount] = set()
    default_sender: Optional[LocalAccount]
    executed_transactions: List[str]
    _safe_cli_info: Optional[SafeCliInfo]
    require_all_signatures: bool

    def __init__(self, address: ChecksumAddress, node_url: str):
        self.address = address
        self.node_url = node_url
        self.ethereum_client = EthereumClient(self.node_url)
        self.ens = ENS.from_web3(self.ethereum_client.w3)
        self.network: EthereumNetwork = self.ethereum_client.get_network()
        try:
            self.etherscan = EtherscanClient(self.network)
        except EtherscanClientConfigurationProblem:
            self.etherscan = None

        try:
            self.safe_tx_service = TransactionServiceApi.from_ethereum_client(
                self.ethereum_client
            )
        except EthereumNetworkNotSupported:
            self.safe_tx_service = None

        self.safe = Safe(address, self.ethereum_client)
        self.safe_contract = self.safe.contract
        self.safe_contract_1_1_0 = get_safe_V1_1_1_contract(
            self.ethereum_client.w3, address=self.address
        )
        self.accounts: Set[LocalAccount] = set()
        self.default_sender: Optional[LocalAccount] = None
        self.executed_transactions: List[str] = []
        self._safe_cli_info: Optional[SafeCliInfo] = None  # Cache for SafeCliInfo
        self.require_all_signatures = (
            True  # Require all signatures to be present to send a tx
        )
        self.hw_wallet_manager = get_hw_wallet_manager()

    @cached_property
    def last_default_fallback_handler_address(self) -> ChecksumAddress:
        """
        :return: Address for last version of default fallback handler contract
        """
        return get_default_fallback_handler_address(self.ethereum_client)

    @cached_property
    def last_safe_contract_address(self) -> ChecksumAddress:
        """
        :return: Last version of the Safe Contract. Use events version for every network but mainnet
        """
        if self.network == EthereumNetwork.MAINNET:
            return get_safe_contract_address(self.ethereum_client)
        else:
            return get_safe_l2_contract_address(self.ethereum_client)

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

    def refresh_safe_cli_info(self) -> SafeCliInfo:
        self._safe_cli_info = self.get_safe_cli_info()
        return self._safe_cli_info

    def is_version_updated(self) -> bool:
        """
        :return: True if Safe Master Copy is updated, False otherwise
        """

        last_safe_contract_address = self.last_safe_contract_address
        if self.safe_cli_info.master_copy == last_safe_contract_address:
            return True
        else:  # Check versions, maybe safe-cli addresses were not updated
            try:
                safe_contract_version = Safe(
                    last_safe_contract_address, self.ethereum_client
                ).retrieve_version()
            except (
                BadFunctionCallOutput
            ):  # Safe master copy is not deployed or errored, maybe custom network
                return True  # We cannot say you are not updated ¯\_(ツ)_/¯

            return semantic_version.parse(
                self.safe_cli_info.version
            ) >= semantic_version.parse(safe_contract_version)

    def load_cli_owners_from_words(self, words: List[str]):
        if len(words) == 1:  # Reading seed from Environment Variable
            words = os.environ.get(words[0], default="").strip().split(" ")
        parsed_words = " ".join(words)
        try:
            for index in range(100):  # Try first accounts of seed phrase
                account = get_account_from_words(parsed_words, index=index)
                if account.address in self.safe_cli_info.owners:
                    self.load_cli_owners([account.key.hex()])
            if not index:
                print_formatted_text(
                    HTML(
                        "<ansired>Cannot generate any valid owner for this Safe</ansired>"
                    )
                )
        except ValidationError:
            print_formatted_text(
                HTML("<ansired>Cannot load owners from words</ansired>")
            )

    def load_cli_owners(self, keys: List[str]):
        for key in keys:
            try:
                account = Account.from_key(
                    os.environ.get(key, default=key)
                )  # Try to get key from `environ`
                self.accounts.add(account)
                balance = self.ethereum_client.get_balance(account.address)
                print_formatted_text(
                    HTML(
                        f"Loaded account <b>{account.address}</b> "
                        f'with balance={Web3.from_wei(balance, "ether")} ether'
                    )
                )
                if (
                    not self.default_sender
                    and not self.hw_wallet_manager.sender
                    and balance > 0
                ):
                    print_formatted_text(
                        HTML(
                            f"Set account <b>{account.address}</b> as default sender of txs"
                        )
                    )
                    self.default_sender = account
            except ValueError:
                print_formatted_text(HTML(f"<ansired>Cannot load key={key}</ansired>"))

    def load_hw_wallet(
        self,
        hw_wallet_type: HwWalletType,
        derivation_path: str,
        template_derivation_path: str,
    ):
        if not self.hw_wallet_manager.is_supported_hw_wallet(hw_wallet_type):
            return None
        if derivation_path is None:
            ledger_accounts = self.hw_wallet_manager.get_accounts(
                hw_wallet_type, template_derivation_path
            )
            if len(ledger_accounts) == 0:
                return None

            option = choose_option_from_list(
                "Select the owner address", ledger_accounts
            )
            if option is None:
                return None
            _, derivation_path = ledger_accounts[option]
        address = self.hw_wallet_manager.add_account(hw_wallet_type, derivation_path)
        balance = self.ethereum_client.get_balance(address)

        print_formatted_text(
            HTML(
                f"Loaded account <b>{address}</b> "
                f'with balance={Web3.from_wei(balance, "ether")} ether.'
            )
        )

        if (
            not self.default_sender
            and not self.hw_wallet_manager.sender
            and balance > 0
        ):
            self.hw_wallet_manager.set_sender(hw_wallet_type, derivation_path)
            print_formatted_text(HTML(f"HwDevice {address} added as sender"))
        else:
            print_formatted_text(HTML(f"HwDevice {address} wasn't added as sender"))

    def load_ledger_cli_owners(
        self, derivation_path: str = None, legacy_account: bool = False
    ):
        if legacy_account:
            self.load_hw_wallet(HwWalletType.LEDGER, derivation_path, "44'/60'/0'/{i}")
        else:
            self.load_hw_wallet(
                HwWalletType.LEDGER, derivation_path, "44'/60'/{i}'/0/0"
            )

    def load_trezor_cli_owners(
        self, derivation_path: str = None, legacy_account: bool = False
    ):
        if legacy_account:
            self.load_hw_wallet(HwWalletType.TREZOR, derivation_path, "44'/60'/0'/{i}")
        else:
            self.load_hw_wallet(
                HwWalletType.TREZOR, derivation_path, "44'/60'/0'/0/{i}"
            )

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
        # Check if there are ledger owners
        if self.hw_wallet_manager.wallets and len(accounts_to_remove) < len(owners):
            accounts_to_remove = (
                accounts_to_remove | self.hw_wallet_manager.delete_accounts(owners)
            )

        if accounts_to_remove:
            print_formatted_text(
                HTML("<ansigreen>Accounts have been deleted</ansigreen>")
            )
        else:
            print_formatted_text(HTML("<ansired>No account was deleted</ansired>"))

    def show_cli_owners(self):
        accounts = self.accounts | self.hw_wallet_manager.wallets
        if not accounts:
            print_formatted_text(HTML("<ansired>No accounts loaded</ansired>"))
        else:
            for account in accounts:
                print_formatted_text(
                    HTML(
                        f"<ansigreen><b>Account</b> {account.address} loaded</ansigreen>"
                    )
                )
            if self.default_sender:
                print_formatted_text(
                    HTML(
                        f"<ansigreen><b>Default sender:</b> {self.default_sender.address}"
                        f"</ansigreen>"
                    )
                )
            elif self.hw_wallet_manager.sender:
                print_formatted_text(
                    HTML(
                        f"<ansigreen><b>HwDevice sender:</b> {self.hw_wallet_manager.sender}"
                        f"</ansigreen>"
                    )
                )
            else:
                print_formatted_text(
                    HTML("<ansigreen>Not default sender set </ansigreen>")
                )

    def approve_hash(self, hash_to_approve: HexBytes, sender: str) -> bool:
        sender_account = [
            account for account in self.accounts if account.address == sender
        ]
        if not sender_account:
            raise AccountNotLoadedException(sender)
        elif sender not in self.safe_cli_info.owners:
            raise NonExistingOwnerException(sender)
        elif self.safe.retrieve_is_hash_approved(
            self.default_sender.address, hash_to_approve
        ):
            raise HashAlreadyApproved(hash_to_approve, self.default_sender.address)
        else:
            sender_account = sender_account[0]
            transaction_to_send = self.safe_contract.functions.approveHash(
                hash_to_approve
            ).build_transaction(
                {
                    "from": sender_account.address,
                    "nonce": self.ethereum_client.get_nonce_for_account(
                        sender_account.address
                    ),
                }
            )
            if self.ethereum_client.is_eip1559_supported():
                transaction_to_send = self.ethereum_client.set_eip1559_fees(
                    transaction_to_send
                )
            call_result = self.ethereum_client.w3.eth.call(transaction_to_send)
            if call_result:  # There's revert message
                return False
            else:
                signed_transaction = sender_account.sign_transaction(
                    transaction_to_send
                )
                tx_hash = self.ethereum_client.send_raw_transaction(
                    signed_transaction["rawTransaction"]
                )
                print_formatted_text(
                    HTML(
                        f"<ansigreen>Sent tx with tx-hash {tx_hash.hex()} from owner "
                        f"{self.default_sender.address}, waiting for receipt</ansigreen>"
                    )
                )
                if self.ethereum_client.get_transaction_receipt(tx_hash, timeout=120):
                    return True
                else:
                    print_formatted_text(
                        HTML(
                            f"<ansired>Tx with tx-hash {tx_hash.hex()} still not mined</ansired>"
                        )
                    )
                    return False

    def sign_message(
        self,
        eip191_message: Optional[str] = None,
        eip712_message_path: Optional[str] = None,
    ) -> bool:
        if eip712_message_path:
            try:
                message = json.load(open(eip712_message_path, "r"))
                message_bytes = b"".join(eip712_encode(message))
            except ValueError:
                raise ValueError
        else:
            message = eip191_message
            message_bytes = eip191_message.encode("UTF-8")

        safe_message_hash = self.safe.get_message_hash(message_bytes)

        sign_message_lib_address = get_last_sign_message_lib_address(
            self.ethereum_client
        )
        contract = get_sign_message_lib_contract(self.ethereum_client.w3, self.address)
        sign_message_data = HexBytes(
            contract.functions.signMessage(message_bytes).build_transaction(
                get_empty_tx_params(),
            )["data"]
        )
        print_formatted_text(HTML(f"Signing message: \n {message}"))
        if self.prepare_and_execute_safe_transaction(
            sign_message_lib_address,
            0,
            sign_message_data,
            operation=SafeOperationEnum.DELEGATE_CALL,
        ):
            print_formatted_text(
                HTML(f"Message was signed correctly: {safe_message_hash.hex()}")
            )

    def add_owner(self, new_owner: str, threshold: Optional[int] = None) -> bool:
        threshold = threshold if threshold is not None else self.safe_cli_info.threshold
        if new_owner in self.safe_cli_info.owners:
            raise ExistingOwnerException(new_owner)
        else:
            # TODO Allow to set threshold
            transaction = self.safe_contract.functions.addOwnerWithThreshold(
                new_owner, threshold
            ).build_transaction({"from": self.address, "gas": 0, "gasPrice": 0})
            if self.execute_safe_internal_transaction(transaction["data"]):
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
            prev_owner = (
                self.safe_cli_info.owners[index_owner - 1]
                if index_owner
                else SENTINEL_ADDRESS
            )
            transaction = self.safe_contract.functions.removeOwner(
                prev_owner, owner_to_remove, threshold
            ).build_transaction({"from": self.address, "gas": 0, "gasPrice": 0})
            if self.execute_safe_internal_transaction(transaction["data"]):
                self.safe_cli_info.owners = self.safe.retrieve_owners()
                self.safe_cli_info.threshold = threshold
                return True
            return False

    def send_custom(
        self,
        to: str,
        value: int,
        data: bytes,
        safe_nonce: Optional[int] = None,
        delegate_call: bool = False,
    ) -> bool:
        if value > 0:
            safe_balance = self.ethereum_client.get_balance(self.address)
            if safe_balance < value:
                raise NotEnoughEtherToSend(safe_balance)
        operation = (
            SafeOperationEnum.DELEGATE_CALL if delegate_call else SafeOperationEnum.CALL
        )
        return self.prepare_and_execute_safe_transaction(
            to, value, data, operation, safe_nonce=safe_nonce
        )

    def send_ether(self, to: str, value: int, **kwargs) -> bool:
        return self.send_custom(to, value, b"", **kwargs)

    def send_erc20(self, to: str, token_address: str, amount: int, **kwargs) -> bool:
        transaction = (
            get_erc20_contract(self.ethereum_client.w3, token_address)
            .functions.transfer(to, amount)
            .build_transaction({"from": self.address, "gas": 0, "gasPrice": 0})
        )
        return self.send_custom(
            token_address, 0, HexBytes(transaction["data"]), **kwargs
        )

    def send_erc721(self, to: str, token_address: str, token_id: int, **kwargs) -> bool:
        transaction = (
            get_erc721_contract(self.ethereum_client.w3, token_address)
            .functions.transferFrom(self.address, to, token_id)
            .build_transaction({"from": self.address, "gas": 0, "gasPrice": 0})
        )
        return self.send_custom(token_address, 0, transaction["data"], **kwargs)

    def change_fallback_handler(self, new_fallback_handler: str) -> bool:
        if new_fallback_handler == self.safe_cli_info.fallback_handler:
            raise SameFallbackHandlerException(new_fallback_handler)
        elif semantic_version.parse(
            self.safe_cli_info.version
        ) < semantic_version.parse("1.1.0"):
            raise FallbackHandlerNotSupportedException()
        elif (
            new_fallback_handler != NULL_ADDRESS
            and not self.ethereum_client.is_contract(new_fallback_handler)
        ):
            raise InvalidFallbackHandlerException(
                f"{new_fallback_handler} address is not a contract"
            )
        else:
            transaction = self.safe_contract.functions.setFallbackHandler(
                new_fallback_handler
            ).build_transaction({"from": self.address, "gas": 0, "gasPrice": 0})
            if self.execute_safe_internal_transaction(transaction["data"]):
                self.safe_cli_info.fallback_handler = new_fallback_handler
                self.safe_cli_info.version = self.safe.retrieve_version()
                return True

    def change_guard(self, guard: str) -> bool:
        if guard == self.safe_cli_info.guard:
            raise SameGuardException(guard)
        elif semantic_version.parse(
            self.safe_cli_info.version
        ) < semantic_version.parse("1.3.0"):
            raise GuardNotSupportedException()
        elif guard != NULL_ADDRESS and not self.ethereum_client.is_contract(guard):
            raise InvalidGuardException(f"{guard} address is not a contract")
        else:
            transaction = self.safe_contract.functions.setGuard(
                guard
            ).build_transaction({"from": self.address, "gas": 0, "gasPrice": 0})
            if self.execute_safe_internal_transaction(transaction["data"]):
                self.safe_cli_info.guard = guard
                self.safe_cli_info.version = self.safe.retrieve_version()
                return True

    def change_master_copy(self, new_master_copy: str) -> bool:
        if new_master_copy == self.safe_cli_info.master_copy:
            raise SameMasterCopyException(new_master_copy)
        else:
            safe_version = self.safe.retrieve_version()
            if semantic_version.parse(safe_version) >= semantic_version.parse("1.3.0"):
                raise SafeVersionNotSupportedException(
                    f"{safe_version} cannot be updated (yet)"
                )

            try:
                Safe(new_master_copy, self.ethereum_client).retrieve_version()
            except BadFunctionCallOutput:
                raise InvalidMasterCopyException(new_master_copy)

            transaction = self.safe_contract_1_1_0.functions.changeMasterCopy(
                new_master_copy
            ).build_transaction({"from": self.address, "gas": 0, "gasPrice": 0})
            if self.execute_safe_internal_transaction(transaction["data"]):
                self.safe_cli_info.master_copy = new_master_copy
                self.safe_cli_info.version = self.safe.retrieve_version()
                return True

    def update_version(self) -> Optional[bool]:
        """
        Update Safe Master Copy and Fallback handler to the last version

        :return:
        """

        safe_version = self.safe.retrieve_version()
        if semantic_version.parse(safe_version) >= semantic_version.parse("1.3.0"):
            raise SafeVersionNotSupportedException(
                f"{safe_version} cannot be updated (yet)"
            )

        if self.is_version_updated():
            raise SafeAlreadyUpdatedException(f"{safe_version} already updated")

        addresses = (
            self.last_safe_contract_address,
            self.last_default_fallback_handler_address,
        )
        if not all(
            self.ethereum_client.is_contract(contract) for contract in addresses
        ):
            raise UpdateAddressesNotValid(
                "Not valid addresses to update Safe", *addresses
            )

        multisend = MultiSend(ethereum_client=self.ethereum_client)
        tx_params = {"from": self.address, "gas": 0, "gasPrice": 0}
        multisend_txs = [
            MultiSendTx(MultiSendOperation.CALL, self.address, 0, data)
            for data in (
                self.safe_contract_1_1_0.functions.changeMasterCopy(
                    self.last_safe_contract_address
                ).build_transaction(tx_params)["data"],
                self.safe_contract_1_1_0.functions.setFallbackHandler(
                    self.last_default_fallback_handler_address
                ).build_transaction(tx_params)["data"],
            )
        ]

        multisend_data = multisend.build_tx_data(multisend_txs)

        if self.prepare_and_execute_safe_transaction(
            multisend.address,
            0,
            multisend_data,
            operation=SafeOperationEnum.DELEGATE_CALL,
        ):
            self.safe_cli_info.master_copy = self.last_safe_contract_address
            self.safe_cli_info.fallback_handler = (
                self.last_default_fallback_handler_address
            )
            self.safe_cli_info.version = self.safe.retrieve_version()

    def update_version_to_l2(
        self, migration_contract_address: ChecksumAddress
    ) -> Optional[bool]:
        """
        Update not L2 Safe to L2, so official UI supports it. Useful when replaying Safes deployed in
        non L2 networks (like mainnet) in L2 networks.
        Only v1.1.1, v1.3.0 and v1.4.1 versions are supported. Also, Safe nonce must be 0.

        :return:
        """

        if not self.ethereum_client.is_contract(migration_contract_address):
            raise InvalidMigrationContractException(
                f"Non L2 to L2 migration contract {migration_contract_address} is not deployed"
            )

        safe_version = self.safe.retrieve_version()
        chain_id = self.ethereum_client.get_chain_id()

        if self.safe.retrieve_nonce() > 0:
            raise InvalidNonceException("Nonce must be 0 for non L2 to L2 migration")

        l2_migration_contract = self.ethereum_client.w3.eth.contract(
            NULL_ADDRESS, abi=safe_to_l2_migration["abi"]
        )
        if safe_version == "1.1.1":
            safe_l2_singleton = safe_deployments["1.3.0"]["GnosisSafeL2"][str(chain_id)]
            fallback_handler = safe_deployments["1.3.0"][
                "CompatibilityFallbackHandler"
            ][str(chain_id)]
            data = HexBytes(
                l2_migration_contract.functions.migrateFromV111(
                    safe_l2_singleton, fallback_handler
                ).build_transaction(get_empty_tx_params())["data"]
            )
        elif safe_version in ("1.3.0", "1.4.1"):
            safe_l2_singleton = safe_deployments[safe_version]["GnosisSafeL2"][
                str(chain_id)
            ]
            fallback_handler = self.safe_cli_info.fallback_handler
            data = HexBytes(
                l2_migration_contract.functions.migrateToL2(
                    safe_l2_singleton
                ).build_transaction(get_empty_tx_params())["data"]
            )
        else:
            raise InvalidMasterCopyException(
                "Current version is not supported to migrate to L2"
            )

        if self.prepare_and_execute_safe_transaction(
            migration_contract_address,
            0,
            data,
            operation=SafeOperationEnum.DELEGATE_CALL,
        ):
            self.safe_cli_info.master_copy = safe_l2_singleton
            self.safe_cli_info.fallback_handler = fallback_handler
            self.safe_cli_info.version = self.safe.retrieve_version()

    def change_threshold(self, threshold: int):
        if threshold == self.safe_cli_info.threshold:
            print_formatted_text(
                HTML(f"<ansired>Threshold is already {threshold}</ansired>")
            )
        elif threshold > len(self.safe_cli_info.owners):
            print_formatted_text(
                HTML(
                    f"<ansired>Threshold={threshold} bigger than number "
                    f"of owners={len(self.safe_cli_info.owners)}</ansired>"
                )
            )
        else:
            transaction = self.safe_contract.functions.changeThreshold(
                threshold
            ).build_transaction({"from": self.address, "gas": 0, "gasPrice": 0})

            if self.execute_safe_internal_transaction(transaction["data"]):
                self.safe_cli_info.threshold = threshold

    def enable_module(self, module_address: str):
        if module_address in self.safe_cli_info.modules:
            print_formatted_text(
                HTML(f"<ansired>Module {module_address} is already enabled</ansired>")
            )
        else:
            transaction = self.safe_contract.functions.enableModule(
                module_address
            ).build_transaction({"from": self.address, "gas": 0, "gasPrice": 0})
            if self.execute_safe_internal_transaction(transaction["data"]):
                self.safe_cli_info.modules = self.safe.retrieve_modules()

    def disable_module(self, module_address: str):
        if module_address not in self.safe_cli_info.modules:
            print_formatted_text(
                HTML(f"<ansired>Module {module_address} is not enabled</ansired>")
            )
        else:
            pos = self.safe_cli_info.modules.index(module_address)
            if pos == 0:
                previous_address = SENTINEL_ADDRESS
            else:
                previous_address = self.safe_cli_info.modules[pos - 1]
            transaction = self.safe_contract.functions.disableModule(
                previous_address, module_address
            ).build_transaction({"from": self.address, "gas": 0, "gasPrice": 0})
            if self.execute_safe_internal_transaction(transaction["data"]):
                self.safe_cli_info.modules = self.safe.retrieve_modules()

    def print_info(self):
        for key, value in dataclasses.asdict(self.safe_cli_info).items():
            print_formatted_text(
                HTML(
                    f"<b><ansigreen>{key.capitalize()}</ansigreen></b>="
                    f"<ansiblue>{value}</ansiblue>"
                )
            )
        if self.ens_domain:
            print_formatted_text(
                HTML(
                    f"<b><ansigreen>Ens domain</ansigreen></b>="
                    f"<ansiblue>{self.ens_domain}</ansiblue>"
                )
            )
        if self.safe_tx_service:
            url = f"{self.safe_tx_service.base_url}/api/v1/safes/{self.address}/transactions/"
            print_formatted_text(
                HTML(
                    f"<b><ansigreen>Safe Tx Service</ansigreen></b>="
                    f"<ansiblue>{url}</ansiblue>"
                )
            )

        if self.etherscan:
            url = f"{self.etherscan.base_url}/address/{self.address}"
            print_formatted_text(
                HTML(
                    f"<b><ansigreen>Etherscan</ansigreen></b>="
                    f"<ansiblue>{url}</ansiblue>"
                )
            )

        if not self.hw_wallet_manager.is_supported_hw_wallet(HwWalletType.LEDGER):
            print_formatted_text(
                HTML(
                    "<b><ansigreen>Ledger</ansigreen></b>="
                    "<ansired>Disabled </ansired> <b>Optional ledger library is not installed, run pip install safe-cli[ledger] </b>"
                )
            )
        else:
            print_formatted_text(
                HTML(
                    "<b><ansigreen>Ledger</ansigreen></b>="
                    "<ansiblue>supported</ansiblue>"
                )
            )

        if not self.hw_wallet_manager.is_supported_hw_wallet(HwWalletType.TREZOR):
            print_formatted_text(
                HTML(
                    "<b><ansigreen>Trezor</ansigreen></b>="
                    "<ansired>Disabled </ansired> <b>Optional trezor library is not installed, run pip install safe-cli[trezor] </b>"
                )
            )
        else:
            print_formatted_text(
                HTML(
                    "<b><ansigreen>Trezor</ansigreen></b>="
                    "<ansiblue>supported</ansiblue>"
                )
            )

        if not self.is_version_updated():
            print_formatted_text(
                HTML(
                    "<ansired>Safe is not updated! You can use <b>update</b> command to update "
                    "the Safe to a newest version</ansired>"
                )
            )

    def get_safe_cli_info(self) -> SafeCliInfo:
        safe = self.safe
        balance_ether = Web3.from_wei(
            self.ethereum_client.get_balance(self.address), "ether"
        )
        safe_info = safe.retrieve_all_info()
        return SafeCliInfo(
            self.address,
            safe_info.nonce,
            safe_info.threshold,
            safe_info.owners,
            safe_info.master_copy,
            safe_info.modules,
            safe_info.fallback_handler,
            safe_info.guard,
            balance_ether,
            safe_info.version,
        )

    def get_threshold(self):
        print_formatted_text(self.safe.retrieve_threshold())

    def get_nonce(self):
        print_formatted_text(self.safe.retrieve_nonce())

    def get_owners(self):
        print_formatted_text(self.safe.retrieve_owners())

    def execute_safe_internal_transaction(self, data: bytes) -> bool:
        return self.prepare_and_execute_safe_transaction(self.address, 0, data)

    def prepare_safe_transaction(
        self,
        to: str,
        value: int,
        data: bytes,
        operation: SafeOperationEnum = SafeOperationEnum.CALL,
        safe_nonce: Optional[int] = None,
    ) -> SafeTx:
        safe_tx = self.safe.build_multisig_tx(
            to, value, data, operation=operation.value, safe_nonce=safe_nonce
        )
        self.sign_transaction(safe_tx)  # Raises exception if it cannot be signed
        return safe_tx

    def prepare_and_execute_safe_transaction(
        self,
        to: str,
        value: int,
        data: bytes,
        operation: SafeOperationEnum = SafeOperationEnum.CALL,
        safe_nonce: Optional[int] = None,
    ) -> bool:
        safe_tx = self.prepare_safe_transaction(
            to, value, data, operation, safe_nonce=safe_nonce
        )
        return self.execute_safe_transaction(safe_tx)

    @require_default_sender  # Throws Exception if default sender not found
    def execute_safe_transaction(self, safe_tx: SafeTx):
        try:
            if self.default_sender:
                call_result = safe_tx.call(self.default_sender.address)
            else:
                call_result = safe_tx.call(self.hw_wallet_manager.sender.address)
            print_formatted_text(HTML(f"Result: <ansigreen>{call_result}</ansigreen>"))
            if yes_or_no_question("Do you want to execute tx " + str(safe_tx)):
                if self.default_sender:
                    tx_hash, tx = safe_tx.execute(
                        self.default_sender.key, eip1559_speed=TxSpeed.NORMAL
                    )
                else:
                    tx_hash, tx = self.hw_wallet_manager.execute_safe_tx(
                        safe_tx, eip1559_speed=TxSpeed.NORMAL
                    )
                self.executed_transactions.append(tx_hash.hex())
                print_formatted_text(
                    HTML(
                        f"<ansigreen>Sent tx with tx-hash {tx_hash.hex()} "
                        f"and safe-nonce {safe_tx.safe_nonce}, waiting for receipt</ansigreen>"
                    )
                )
                tx_receipt = self.ethereum_client.get_transaction_receipt(
                    tx_hash, timeout=120
                )
                if tx_receipt:
                    fees = self.ethereum_client.w3.from_wei(
                        tx_receipt["gasUsed"]
                        * tx_receipt.get("effectiveGasPrice", tx.get("gasPrice", 0)),
                        "ether",
                    )
                    print_formatted_text(
                        HTML(
                            f"<ansigreen>Tx was executed on block-number={tx_receipt['blockNumber']}, fees "
                            f"deducted={fees}</ansigreen>"
                        )
                    )
                    self.safe_cli_info.nonce += 1
                    return True
                else:
                    print_formatted_text(
                        HTML(
                            f"<ansired>Tx with tx-hash {tx_hash.hex()} still not mined</ansired>"
                        )
                    )
        except InvalidInternalTx as invalid_internal_tx:
            print_formatted_text(
                HTML(f"Result: <ansired>InvalidTx - {invalid_internal_tx}</ansired>")
            )
        return False

    # Batch_transactions multisend
    def batch_safe_txs(
        self, safe_nonce: int, safe_txs: Sequence[SafeTx]
    ) -> Optional[SafeTx]:
        """
        Submit signatures to the tx service. It's recommended to be on Safe v1.3.0 to prevent issues
        with `safeTxGas` and gas estimation.

        :return:
        """

        try:
            multisend = MultiSend(ethereum_client=self.ethereum_client)
        except ValueError:
            multisend = None
            print_formatted_text(
                HTML(
                    "<ansired>Multisend contract is not deployed on this network and it's required for "
                    "batching txs</ansired>"
                )
            )

        multisend_txs = []
        for safe_tx in safe_txs:
            # Check if call is already a Multisend call
            inner_txs = MultiSend.from_transaction_data(safe_tx.data)
            if inner_txs:
                multisend_txs.extend(inner_txs)
            else:
                multisend_txs.append(
                    MultiSendTx(
                        MultiSendOperation.CALL, safe_tx.to, safe_tx.value, safe_tx.data
                    )
                )

        if len(multisend_txs) == 1:
            safe_tx.safe_tx_gas = 0
            safe_tx.base_gas = 0
            safe_tx.gas_price = 0
            safe_tx.signatures = b""
            safe_tx.safe_nonce = safe_nonce  # Resend single transaction
        elif multisend:
            safe_tx = SafeTx(
                self.ethereum_client,
                self.address,
                multisend.address,
                0,
                multisend.build_tx_data(multisend_txs),
                SafeOperationEnum.DELEGATE_CALL.value,
                0,
                0,
                0,
                None,
                None,
                safe_nonce=safe_nonce,
            )
        else:
            # Multisend not defined
            return None

        safe_tx = self.sign_transaction(safe_tx)
        if not safe_tx.signatures:
            print_formatted_text(
                HTML("<ansired>At least one owner must be loaded</ansired>")
            )
            return None
        else:
            return safe_tx

    def get_signers(self) -> Tuple[List[LocalAccount], List[HwWallet]]:
        """

        :return: Tuple with eoa signers and hw_wallet signers
        """
        permitted_signers = self.get_permitted_signers()
        threshold = self.safe_cli_info.threshold
        eoa_signers: List[Account] = (
            []
        )  # Some accounts that are not an owner can be loaded
        for account in self.accounts:
            if account.address in permitted_signers:
                eoa_signers.append(account)
                threshold -= 1
                if threshold == 0:
                    break
        # If still pending required signatures continue with ledger owners
        hw_wallet_signers = []
        if threshold > 0 and self.hw_wallet_manager.wallets:
            for hw_wallet in self.hw_wallet_manager.wallets:
                if hw_wallet.address in permitted_signers:
                    hw_wallet_signers.append(hw_wallet)
                    threshold -= 1
                    if threshold == 0:
                        break

        if self.require_all_signatures and threshold > 0:
            raise NotEnoughSignatures(threshold)

        return (eoa_signers, hw_wallet_signers)

    # TODO Set sender so we can save gas in that signature
    def sign_transaction(self, safe_tx: SafeTx) -> SafeTx:
        eoa_signers, hw_wallets_signers = self.get_signers()
        for selected_account in eoa_signers:
            safe_tx.sign(selected_account.key)

        # Sign with ledger
        if len(hw_wallets_signers):
            safe_tx = self.hw_wallet_manager.sign_safe_tx(safe_tx, hw_wallets_signers)

        return safe_tx

    @require_tx_service
    def _require_tx_service_mode(self):
        print_formatted_text(
            HTML(
                "<ansired>First enter tx-service mode using <b>tx-service</b> command</ansired>"
            )
        )

    def get_delegates(self):
        return self._require_tx_service_mode()

    def add_delegate(self, delegate_address: str, label: str, signer_address: str):
        return self._require_tx_service_mode()

    def remove_delegate(self, delegate_address: str, signer_address: str):
        return self._require_tx_service_mode()

    def submit_signatures(self, safe_tx_hash: bytes) -> bool:
        return self._require_tx_service_mode()

    def get_balances(self):
        return self._require_tx_service_mode()

    def get_transaction_history(self):
        return self._require_tx_service_mode()

    def batch_txs(self, safe_nonce: int, safe_tx_hashes: Sequence[bytes]) -> bool:
        return self._require_tx_service_mode()

    def execute_tx(self, safe_tx_hash: Sequence[bytes]) -> bool:
        return self._require_tx_service_mode()

    def get_permitted_signers(self) -> Set[ChecksumAddress]:
        """
        :return: Accounts that can sign a transaction
        """
        return set(self.safe_cli_info.owners)

    def drain(self, to: str):
        # Getting all events related with ERC20 transfers
        last = self.ethereum_client.get_block("latest")["number"]
        token_addresses = get_erc_20_list(self.ethereum_client, self.address, 1, last)
        safe_txs = []
        for token_address in token_addresses:
            balance = self.ethereum_client.erc20.get_balance(
                self.address, token_address
            )
            if balance > 0:
                transaction = (
                    get_erc20_contract(self.ethereum_client.w3, token_address)
                    .functions.transfer(to, balance)
                    .build_transaction({"from": self.address, "gas": 0, "gasPrice": 0})
                )

                safe_tx = self.prepare_safe_transaction(
                    token_address,
                    0,
                    HexBytes(transaction["data"]),
                    SafeOperationEnum.CALL,
                    safe_nonce=None,
                )
                safe_txs.append(safe_tx)

        # Getting ethereum balance
        balance_eth = self.ethereum_client.get_balance(self.address)
        if balance_eth:
            safe_tx = self.prepare_safe_transaction(
                to,
                balance_eth,
                b"",
                SafeOperationEnum.CALL,
                safe_nonce=None,
            )
            safe_txs.append(safe_tx)

        if safe_txs:
            multisend_tx = self.batch_safe_txs(self.get_nonce(), safe_txs)
            if multisend_tx is not None:
                if self.execute_safe_transaction(multisend_tx):
                    print_formatted_text(
                        HTML(
                            "<ansigreen>Transaction to drain account correctly executed</ansigreen>"
                        )
                    )
        else:
            print_formatted_text(
                HTML("<ansigreen>Safe account is currently empty</ansigreen>")
            )

    def remove_proposed_transaction(self, safe_tx_hash: bytes):
        return self._require_tx_service_mode()

    def process_command(self, first_command: str, rest_command: List[str]) -> bool:
        if first_command == "help":
            print_formatted_text("I still cannot help you")
        elif first_command == "refresh":
            print_formatted_text("Reloading Safe information")
            self.refresh_safe_cli_info()

        return False
