from typing import Optional

from hexbytes import HexBytes
from prompt_toolkit import HTML, print_formatted_text

from gnosis.eth.constants import NULL_ADDRESS
from gnosis.safe import InvalidInternalTx, SafeOperation, SafeTx

from safe_cli.utils import yes_or_no_question

from .safe_operator import SafeOperator, SafeServiceNotAvailable


class SafeRelayOperator(SafeOperator):
    def __init__(self, address: str, node_url: str, gas_token: Optional[str] = None):
        super().__init__(address, node_url)
        self.gas_token = gas_token or NULL_ADDRESS
        if not self.safe_relay_service:
            raise SafeServiceNotAvailable(
                f"Cannot configure relay service for network {self.network.name}"
            )

    def approve_hash(self, hash_to_approve: HexBytes, sender: str) -> bool:
        raise NotImplementedError("Not supported when using relay")

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
        return self.post_transaction_to_relay_service(safe_tx)

    def post_transaction_to_relay_service(self, safe_tx: SafeTx) -> bool:
        safe_tx.gas_token = self.gas_token
        estimation = self.safe_relay_service.get_estimation(self.address, safe_tx)
        safe_tx.base_gas = estimation["baseGas"]
        safe_tx.safe_tx_gas = estimation["safeTxGas"]
        safe_tx.gas_price = estimation["gasPrice"]
        last_used_nonce: Optional[int] = estimation["lastUsedNonce"]
        safe_tx.safe_nonce = 0 if last_used_nonce is None else last_used_nonce + 1
        safe_tx.refund_receiver = estimation["refundReceiver"] or NULL_ADDRESS
        safe_tx.signatures = b""  # Sign transaction again
        self.sign_transaction(safe_tx)
        if yes_or_no_question("Do you want to execute tx " + str(safe_tx)):
            try:
                call_result = safe_tx.call(self.default_sender.address)
                print_formatted_text(
                    HTML(f"Result: <ansigreen>{call_result}</ansigreen>")
                )
                transaction_data = self.safe_relay_service.send_transaction(
                    self.address, safe_tx
                )
                tx_hash = transaction_data["txHash"]
                print_formatted_text(
                    HTML(
                        f"<ansigreen>Gnosis Safe Relay has queued transaction with "
                        f"transaction-hash <b>{tx_hash}</b></ansigreen>"
                    )
                )
                return True
            except InvalidInternalTx as invalid_internal_tx:
                print_formatted_text(
                    HTML(
                        f"Result: <ansired>InvalidTx - {invalid_internal_tx}</ansired>"
                    )
                )
        return False
