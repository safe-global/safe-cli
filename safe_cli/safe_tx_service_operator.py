from typing import Optional

from gnosis.safe import SafeOperation

from .safe_operator import (NotEnoughEtherToSend, SafeOperator,
                            ServiceNotAvailable)

class SafeTxServiceOperator(SafeOperator):
    def send_custom(self, to: str, value: int, data: bytes, safe_nonce: Optional[int] = None,
                    delegate_call: bool = False) -> bool:
        if value > 0:
            safe_balance = self.ethereum_client.get_balance(self.address)
            if safe_balance < value:
                raise NotEnoughEtherToSend(safe_balance)
        operation = SafeOperation.DELEGATE_CALL if delegate_call else SafeOperation.CALL
        return self.post_transaction_to_tx_service(to, value, data, operation, safe_nonce=safe_nonce)

    def post_transaction_to_tx_service(self, to: str, value: int, data: bytes,
                                       operation: SafeOperation = SafeOperation.CALL,
                                       safe_nonce: Optional[int] = None):
        if not self.safe_tx_service:
            raise ServiceNotAvailable(self.network.name)

        safe_tx = self.safe.build_multisig_tx(to, value, data, operation=operation.value, safe_nonce=safe_nonce)
        for account in self.accounts:
            safe_tx.sign(account.key)  # Raises exception if it cannot be signed
        self.safe_tx_service.post_transaction(self.address, safe_tx)
