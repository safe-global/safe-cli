from typing import Optional

from hexbytes import HexBytes
from prompt_toolkit import HTML, print_formatted_text

from gnosis.safe import SafeOperation, SafeTx

from .safe_operator import SafeOperator, ServiceNotAvailable
from .utils import yes_or_no_question


class SafeTxServiceOperator(SafeOperator):
    def __init__(self, address: str, node_url: str):
        super().__init__(address, node_url)
        if not self.safe_tx_service:
            raise ServiceNotAvailable(f'Cannot configure tx service for network {self.network.name}')
        self.require_all_signatures = False  # It doesn't require all signatures to be present to send a tx

    def approve_hash(self, hash_to_approve: HexBytes, sender: str) -> bool:
        raise NotImplementedError('Not supported when using tx service')

    def execute_safe_transaction(self, to: str, value: int, data: bytes,
                                 operation: SafeOperation = SafeOperation.CALL,
                                 safe_nonce: Optional[int] = None) -> bool:
        safe_tx = self.prepare_safe_transaction(to, value, data, operation, safe_nonce=safe_nonce)
        return self.post_transaction_to_tx_service(safe_tx)

    def post_transaction_to_tx_service(self, safe_tx: SafeTx) -> bool:
        if yes_or_no_question('Do you want to execute tx ' + str(safe_tx)):
            self.safe_tx_service.post_transaction(self.address, safe_tx)
            print_formatted_text(HTML(f'<ansigreen>Tx with safe-tx-hash <b>{safe_tx.safe_tx_hash.hex()}</b> was sent '
                                      f'to Gnosis Safe Transaction service</ansigreen>'))
            return True
        return False
