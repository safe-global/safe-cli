import json
from itertools import chain
from typing import Any, Dict, Optional, Sequence, Set, Union

from colorama import Fore, Style
from eth_account.messages import defunct_hash_message
from eth_account.signers.local import LocalAccount
from eth_typing import ChecksumAddress
from hexbytes import HexBytes
from prompt_toolkit import HTML, print_formatted_text
from safe_eth.eth.contracts import get_erc20_contract
from safe_eth.eth.eip712 import eip712_encode_hash
from safe_eth.safe import SafeOperationEnum, SafeTx
from safe_eth.safe.api import SafeAPIException
from safe_eth.safe.api.transaction_service_api.transaction_service_messages import (
    get_remove_transaction_message,
)
from safe_eth.safe.multi_send import MultiSend, MultiSendOperation, MultiSendTx
from safe_eth.safe.safe_signature import SafeSignature
from safe_eth.safe.signatures import signature_to_bytes
from safe_eth.util.util import to_0x_hex_str
from tabulate import tabulate

from ..utils import get_input, yes_or_no_question
from . import SafeServiceNotAvailable
from .exceptions import AccountNotLoadedException, NonExistingOwnerException
from .hw_wallets.hw_wallet import HwWallet
from .safe_operator import SafeOperator


class SafeTxServiceOperator(SafeOperator):
    def __init__(self, address: str, node_url: str):
        super().__init__(address, node_url)
        if not self.safe_tx_service:
            raise SafeServiceNotAvailable(
                f"Cannot configure tx service for network {self.network.name}"
            )
        self.require_all_signatures = (
            False  # It doesn't require all signatures to be present to send a tx
        )

    def approve_hash(self, hash_to_approve: HexBytes, sender: str) -> bool:
        raise NotImplementedError("Not supported when using tx service")

    def sign_message(
        self,
        eip712_message_path: Optional[str] = None,
    ) -> bool:
        if eip712_message_path:
            try:
                message = json.load(open(eip712_message_path, "r"))
                message_hash = eip712_encode_hash(message)
            except ValueError:
                raise ValueError
        else:
            print_formatted_text("EIP191 message to sign:")
            message = get_input()
            message_hash = defunct_hash_message(text=message)

        safe_message_hash = self.safe.get_message_hash(message_hash)
        eoa_signers, hw_wallet_signers = self.get_signers()
        # Safe transaction service just accept one signer to create a message
        signature = b""
        if eoa_signers:
            signature_dict = eoa_signers[0].unsafe_sign_hash(safe_message_hash)
            signature = signature_to_bytes(
                signature_dict["v"], signature_dict["r"], signature_dict["s"]
            )

        elif hw_wallet_signers:
            signature = SafeSignature.export_signatures(
                self.hw_wallet_manager.sign_message(
                    safe_message_hash, [hw_wallet_signers[0]]
                )
            )
        else:
            print_formatted_text(
                HTML("<ansired>At least one owner must be loaded</ansired>")
            )

        if self.safe_tx_service.post_message(self.address, message, signature):
            print_formatted_text(
                HTML(
                    f"<ansigreen>Message  with safe-message-hash {to_0x_hex_str(safe_message_hash)} was correctly created on Safe Transaction Service</ansigreen>"
                )
            )
            return True
        else:
            print_formatted_text(
                HTML(
                    "<ansired>Something went wrong creating message on Safe Transaction Service</ansired>"
                )
            )
            return False

    def confirm_message(self, safe_message_hash: bytes, sender: ChecksumAddress):
        # GET message
        try:
            safe_message = self.safe_tx_service.get_message(safe_message_hash)
        except SafeAPIException:
            print_formatted_text(
                HTML(
                    f"<ansired>Message with hash {to_0x_hex_str(safe_message_hash)} does not exist</ansired>"
                )
            )
        if not yes_or_no_question(
            f"Message: {safe_message['message']} \n Do you want to sign the following message?:"
        ):
            return False

        signer = self.search_account(sender)
        if not signer:
            print_formatted_text(
                HTML(f"<ansired>Owner with address {sender} was not loaded</ansired>")
            )

        if isinstance(signer, LocalAccount):
            signature = signer.unsafe_sign_hash(safe_message_hash).signature
        else:
            signature = SafeSignature.export_signatures(
                self.hw_wallet_manager.sign_message(safe_message_hash, [signer])
            )

        try:
            self.safe_tx_service.post_message_signature(safe_message_hash, signature)
        except SafeAPIException as e:
            print_formatted_text(
                HTML(f"<ansired>Message wasn't confirmed due an error: {e}</ansired>")
            )
            return False
        print_formatted_text(
            HTML(
                f"<ansigreen>Message with safe-message-hash {to_0x_hex_str(safe_message_hash)} was correctly confirmed on Safe Transaction Service</ansigreen>"
            )
        )
        return True

    def get_delegates(self):
        delegates = self.safe_tx_service.get_delegates(self.address)
        headers = ["delegate", "delegator", "label"]
        rows = []
        for delegate in delegates:
            row = [delegate["delegate"], delegate["delegator"], delegate["label"]]
            rows.append(row)
        print(tabulate(rows, headers=headers))
        return rows

    def add_delegate(self, delegate_address: str, label: str, signer_address: str):
        signer_account = [
            account for account in self.accounts if account.address == signer_address
        ]
        if not signer_account:
            raise AccountNotLoadedException(signer_address)
        elif signer_address not in self.safe_cli_info.owners:
            raise NonExistingOwnerException(signer_address)
        else:
            signer_account = signer_account[0]
            try:
                hash_to_sign = self.safe_tx_service.create_delegate_message_hash(
                    delegate_address
                )
                signature = signer_account.unsafe_sign_hash(hash_to_sign)
                self.safe_tx_service.add_delegate(
                    delegate_address,
                    signer_account.address,
                    label,
                    signature.signature,
                    safe_address=self.address,
                )
                return True
            except SafeAPIException:
                return False

    def remove_delegate(self, delegate_address: str, signer_address: str):
        signer_account = [
            account for account in self.accounts if account.address == signer_address
        ]
        if not signer_account:
            raise AccountNotLoadedException(signer_address)
        elif signer_address not in self.safe_cli_info.owners:
            raise NonExistingOwnerException(signer_address)
        else:
            signer_account = signer_account[0]
            try:
                hash_to_sign = self.safe_tx_service.create_delegate_message_hash(
                    delegate_address
                )
                signature = signer_account.unsafe_sign_hash(hash_to_sign)
                self.safe_tx_service.remove_delegate(
                    delegate_address,
                    signer_account.address,
                    signature.signature,
                    safe_address=self.address,
                )
                return True
            except SafeAPIException:
                return False

    def submit_signatures(self, safe_tx_hash: bytes) -> bool:
        """
        Submit signatures to the tx service

        :return:
        """

        safe_tx, tx_hash = self.safe_tx_service.get_safe_transaction(safe_tx_hash)
        safe_tx.signatures = b""  # Don't post again existing signatures
        if tx_hash:
            print_formatted_text(
                HTML(
                    f"<ansired>Tx with safe-tx-hash {to_0x_hex_str(safe_tx_hash)} "
                    f"has already been executed on {to_0x_hex_str(tx_hash)}</ansired>"
                )
            )
        else:
            safe_tx = self.sign_transaction(safe_tx)
            if safe_tx.signers:
                self.safe_tx_service.post_signatures(safe_tx_hash, safe_tx.signatures)
                print_formatted_text(
                    HTML(
                        f"<ansigreen>{len(safe_tx.signers)} signatures were submitted to the tx service</ansigreen>"
                    )
                )
                return True
            else:
                print_formatted_text(
                    HTML(
                        "<ansired>Cannot generate signatures as there were no suitable signers</ansired>"
                    )
                )
        return False

    def batch_txs(self, safe_nonce: int, safe_tx_hashes: Sequence[bytes]) -> bool:
        """
        Submit signatures to the tx service. It's recommended to be on Safe v1.3.0 to prevent issues
        with `safeTxGas` and gas estimation.

        :return:
        """

        try:
            multisend = MultiSend(ethereum_client=self.ethereum_client)
        except ValueError:
            print_formatted_text(
                HTML(
                    "<ansired>Multisend contract is not deployed on this network and it's required for "
                    "batching txs</ansired>"
                )
            )

        multisend_txs = []
        for safe_tx_hash in safe_tx_hashes:
            safe_tx, _ = self.safe_tx_service.get_safe_transaction(safe_tx_hash)
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

        if len(multisend_txs) > 1:
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
            safe_tx.safe_tx_gas = 0
            safe_tx.base_gas = 0
            safe_tx.gas_price = 0
            safe_tx.signatures = b""
            safe_tx.safe_nonce = safe_nonce  # Resend single transaction
        safe_tx = self.sign_transaction(safe_tx)
        if not safe_tx.signatures:
            print_formatted_text(
                HTML("<ansired>At least one owner must be loaded</ansired>")
            )
            return False
        else:
            return self.post_transaction_to_tx_service(safe_tx)

    def execute_tx(self, safe_tx_hash: Sequence[bytes]) -> bool:
        """
        Submit transaction on the tx-service to blockchain

        :return:
        """
        safe_tx, tx_hash = self.safe_tx_service.get_safe_transaction(safe_tx_hash)
        if tx_hash:
            print_formatted_text(
                HTML(
                    f"<ansired>Tx with safe-tx-hash {to_0x_hex_str(safe_tx_hash)} "
                    f"has already been executed on {to_0x_hex_str(tx_hash)}</ansired>"
                )
            )
        elif len(safe_tx.signers) < self.safe_cli_info.threshold:
            print_formatted_text(
                HTML(
                    f"<ansired>Number of signatures {len(safe_tx.signers)} "
                    f"must reach the threshold {self.safe_cli_info.threshold}</ansired>"
                )
            )
        else:
            if executed := self.execute_safe_transaction(safe_tx):
                self.refresh_safe_cli_info()
            return executed

    def get_balances(self):
        balances = self.safe_tx_service.get_balances(self.address)
        headers = ["name", "balance", "symbol", "decimals", "tokenAddress"]
        rows = []
        for balance in balances:
            if balance["tokenAddress"]:  # Token
                row = [
                    balance["token"]["name"],
                    f"{int(balance['balance']) / 10 ** int(balance['token']['decimals']):.5f}",
                    balance["token"]["symbol"],
                    balance["token"]["decimals"],
                    balance["tokenAddress"],
                ]
            else:  # Ether
                row = [
                    "ETHER",
                    f"{int(balance['balance']) / 10 ** 18:.5f}",
                    "Ξ",
                    18,
                    "",
                ]
            rows.append(row)
        print(tabulate(rows, headers=headers))
        return rows

    def get_transaction_history(self):
        transactions = self.safe_tx_service.get_transactions(self.address)
        headers = ["nonce", "to", "value", "transactionHash", "safeTxHash"]
        rows = []
        last_executed_tx = False
        for transaction in transactions:
            row = [transaction[header] for header in headers]
            data_decoded: Dict[str, Any] = transaction.get("dataDecoded")
            if data_decoded:
                row.append(self.safe_tx_service.data_decoded_to_text(data_decoded))
            if transaction["transactionHash"]:
                if not transaction["isSuccessful"]:
                    # Transaction failed
                    row[0] = Fore.RED + str(row[0])
                else:
                    row[0] = Fore.GREEN + str(
                        row[0]
                    )  # For executed transactions we use green
                    if not last_executed_tx:
                        row[0] = Style.BRIGHT + row[0]
                        last_executed_tx = True
            else:
                row[0] = Fore.YELLOW + str(
                    row[0]
                )  # For non executed transactions we use yellow

            row[0] = Style.RESET_ALL + row[0]  # Reset all just in case
            rows.append(row)

        headers.append("dataDecoded")
        headers[0] = Style.BRIGHT + headers[0]
        print(tabulate(rows, headers=headers))
        return rows

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
        return self.post_transaction_to_tx_service(safe_tx)

    def post_transaction_to_tx_service(self, safe_tx: SafeTx) -> bool:
        if not yes_or_no_question(
            f"Do you want to send the tx with safe-tx-hash={to_0x_hex_str(safe_tx.safe_tx_hash)} to Safe Transaction Service (it will not be executed) "
            + str(safe_tx)
        ):
            return False

        self.safe_tx_service.post_transaction(safe_tx)
        print_formatted_text(
            HTML(
                f"<ansigreen>Tx with safe-tx-hash={to_0x_hex_str(safe_tx.safe_tx_hash)} was sent to Safe Transaction service</ansigreen>"
            )
        )
        return True

    def get_permitted_signers(self) -> Set[ChecksumAddress]:
        """
        :return: Owners and delegates, as they also can sign a transaction for the tx service
        """
        owners = super().get_permitted_signers()
        owners.update(
            [
                row["delegate"]
                for row in self.safe_tx_service.get_delegates(self.address)
            ]
        )
        return owners

    # Function that sends all assets to an account (to)
    def drain(self, to: ChecksumAddress):
        balances = self.safe_tx_service.get_balances(self.address)
        safe_txs = []
        safe_tx = None
        for balance in balances:
            amount = int(balance["balance"])
            if balance["tokenAddress"] is None:  # Then is ether
                if amount != 0:
                    safe_tx = self.prepare_safe_transaction(
                        to,
                        amount,
                        b"",
                        SafeOperationEnum.CALL,
                        safe_nonce=None,
                    )
            else:
                transaction = (
                    get_erc20_contract(self.ethereum_client.w3, balance["tokenAddress"])
                    .functions.transfer(to, amount)
                    .build_transaction({"from": self.address, "gas": 0, "gasPrice": 0})
                )
                safe_tx = self.prepare_safe_transaction(
                    balance["tokenAddress"],
                    0,
                    HexBytes(transaction["data"]),
                    SafeOperationEnum.CALL,
                    safe_nonce=None,
                )
            if safe_tx:
                safe_txs.append(safe_tx)
        if len(safe_txs) > 0:
            multisend_tx = self.batch_safe_txs(safe_tx.safe_nonce, safe_txs)
            if multisend_tx is not None:
                self.post_transaction_to_tx_service(multisend_tx)
                print_formatted_text(
                    HTML(
                        "<ansigreen>Transaction to drain account correctly created</ansigreen>"
                    )
                )
        else:
            print_formatted_text(
                HTML("<ansigreen>Safe account is currently empty</ansigreen>")
            )

    def search_account(
        self, address: ChecksumAddress
    ) -> Optional[Union[LocalAccount, HwWallet]]:
        """
        Search the provided address between loaded owners

        :param address:
        :return: LocalAccount or HwWallet of the provided address
        """
        for account in chain(self.accounts, self.hw_wallet_manager.wallets):
            if account.address == address:
                return account

    def remove_proposed_transaction(self, safe_tx_hash: bytes):
        eip712_message = get_remove_transaction_message(
            self.address, safe_tx_hash, self.ethereum_client.get_chain_id()
        )
        message_hash = eip712_encode_hash(eip712_message)
        try:
            safe_tx, _ = self.safe_tx_service.get_safe_transaction(safe_tx_hash)
            signer = self.search_account(safe_tx.proposer)
            if not signer:
                print_formatted_text(
                    HTML(
                        f"<ansired>The proposer with address: {safe_tx.proposer} was not loaded</ansired>"
                    )
                )
                return False

            if isinstance(signer, LocalAccount):
                signature = signer.unsafe_sign_hash(message_hash).signature
            else:
                signature = self.hw_wallet_manager.sign_eip712(
                    eip712_message, [signer]
                )[0].signature

            if len(safe_tx.signers) >= self.safe.retrieve_threshold():
                print_formatted_text(
                    HTML(
                        "<ansired>The transaction has all the required signatures to be executed!!!\n"
                        "This means that the transaction can be executed by a 3rd party monitoring your Safe even after removal!\n"
                        f"Make sure you execute a transaction with nonce {safe_tx.safe_nonce} to void the current transaction"
                        "</ansired>"
                    )
                )

            if not yes_or_no_question(
                f"Do you want to remove the tx with safe-tx-hash={to_0x_hex_str(safe_tx.safe_tx_hash)}"
            ):
                return False

            self.safe_tx_service.delete_transaction(
                to_0x_hex_str(safe_tx_hash), to_0x_hex_str(signature)
            )
            print_formatted_text(
                HTML(
                    f"<ansigreen>Transaction {to_0x_hex_str(safe_tx_hash)} was removed correctly</ansigreen>"
                )
            )
            return True
        except SafeAPIException as e:
            print_formatted_text(
                HTML(f"<ansired>Transaction wasn't removed due an error: {e}</ansired>")
            )
            return False
