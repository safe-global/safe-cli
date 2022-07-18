from typing import Any, Dict, Optional, Sequence, Set

from colorama import Fore, Style
from hexbytes import HexBytes
from prompt_toolkit import HTML, print_formatted_text
from tabulate import tabulate

from gnosis.eth.contracts import get_erc20_contract
from gnosis.safe import SafeOperation, SafeTx
from gnosis.safe.multi_send import MultiSend, MultiSendOperation, MultiSendTx

from safe_cli.api.base_api import BaseAPIException
from safe_cli.utils import yes_or_no_question

from .safe_operator import (
    AccountNotLoadedException,
    NonExistingOwnerException,
    SafeOperator,
    SafeServiceNotAvailable,
)


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

    def get_delegates(self):
        delegates = self.safe_tx_service.get_delegates(self.address)
        headers = ["delegate", "delegator", "label"]
        rows = []
        for delegate in delegates:
            row = [delegate["delegate"], delegate["delegator"], delegate["label"]]
            rows.append(row)
        print(tabulate(rows, headers=headers))

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
                self.safe_tx_service.add_delegate(
                    self.address, delegate_address, label, signer_account
                )
                return True
            except BaseAPIException:
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
                self.safe_tx_service.remove_delegate(
                    self.address, delegate_address, signer_account
                )
                return True
            except BaseAPIException:
                return False

    def submit_signatures(self, safe_tx_hash: bytes) -> bool:
        """
        Submit signatures to the tx service

        :return:
        """

        safe_tx, tx_hash = self.safe_tx_service.get_safe_transaction(safe_tx_hash)
        if tx_hash:
            print_formatted_text(
                HTML(
                    f"<ansired>Tx with safe-tx-hash {safe_tx_hash.hex()} "
                    f"has already been executed on {tx_hash.hex()}</ansired>"
                )
            )
        else:
            owners = self.get_permitted_signers()
            for account in self.accounts:
                if account.address in owners:
                    safe_tx.sign(account.key)

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
                SafeOperation.DELEGATE_CALL.value,
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
                    f"<ansired>Tx with safe-tx-hash {safe_tx_hash.hex()} "
                    f"has already been executed on {tx_hash.hex()}</ansired>"
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
            return self.execute_safe_transaction(safe_tx)

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
            if transaction["transactionHash"] and transaction["isSuccessful"]:
                row[0] = Fore.GREEN + str(
                    row[0]
                )  # For executed transactions we use green
                if not last_executed_tx:
                    row[0] = Style.BRIGHT + row[0]
                    last_executed_tx = True
            elif transaction["transactionHash"]:
                row[0] = Fore.RED + str(row[0])  # For transactions failed
            else:
                row[0] = Fore.YELLOW + str(
                    row[0]
                )  # For non executed transactions we use yellow

            row[0] = Style.RESET_ALL + row[0]  # Reset all just in case
            rows.append(row)

        headers.append("dataDecoded")
        headers[0] = Style.BRIGHT + headers[0]
        print(tabulate(rows, headers=headers))

    def prepare_and_execute_safe_transaction(
        self,
        to: str,
        value: int,
        data: bytes,
        operation: SafeOperation = SafeOperation.CALL,
        safe_nonce: Optional[int] = None,
    ) -> bool:
        safe_tx = self.prepare_safe_transaction(
            to, value, data, operation, safe_nonce=safe_nonce
        )
        return self.post_transaction_to_tx_service(safe_tx)

    def post_transaction_to_tx_service(self, safe_tx: SafeTx) -> bool:
        if yes_or_no_question(
            "Do you want to send the tx to Gnosis Safe Transaction Service (it will not be executed) "
            + str(safe_tx)
        ):
            self.safe_tx_service.post_transaction(self.address, safe_tx)
            print_formatted_text(
                HTML(
                    "<ansigreen>Tx was sent to Gnosis Safe Transaction service</ansigreen>"
                )
            )
            return True
        return False

    def get_permitted_signers(self) -> Set[str]:
        owners = super().get_permitted_signers()
        owners.update(
            [
                row["delegate"]
                for row in self.safe_tx_service.get_delegates(self.address)
            ]
        )
        return owners

    # Function that sends all assets to an account (to)
    def drain(self, to: str):
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
                        SafeOperation.CALL,
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
                    SafeOperation.CALL,
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
