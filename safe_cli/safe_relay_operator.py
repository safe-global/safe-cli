from typing import Optional

from prompt_toolkit import HTML, print_formatted_text

from gnosis.safe import SafeOperation

from safe_cli.api.gnosis_relay import RelayService

from .safe_operator import (NotEnoughEtherToSend, SafeOperator,
                            ServiceNotAvailable)


class SafeRelayOperator(SafeOperator):
    def __init__(self, address: str, node_url: str):
        super().__init__(address, node_url)
        self.safe_relay_service = RelayService.from_network_number(self.network.value)

    def send_custom(self, to: str, value: int, data: bytes, safe_nonce: Optional[int] = None,
                    delegate_call: bool = False) -> bool:
        if value > 0:
            safe_balance = self.ethereum_client.get_balance(self.address)
            if safe_balance < value:
                raise NotEnoughEtherToSend(safe_balance)
        operation = SafeOperation.DELEGATE_CALL if delegate_call else SafeOperation.CALL
        return self.post_transaction_to_relay_service(to, value, data, operation)

    def post_transaction_to_relay_service(self, to: str, value: int, data: bytes,
                                          operation: SafeOperation = SafeOperation.CALL,
                                          gas_token: Optional[str] = None):
        if not self.safe_relay_service:
            raise ServiceNotAvailable(self.network.name)

        safe_tx = self.safe.build_multisig_tx(to, value, data, operation=operation.value, gas_token=gas_token)
        estimation = self.safe_relay_service.get_estimation(self.address, safe_tx)
        safe_tx.base_gas = estimation['baseGas']
        safe_tx.safe_tx_gas = estimation['safeTxGas']
        safe_tx.gas_price = estimation['gasPrice']
        safe_tx.safe_nonce = estimation['lastUsedNonce'] + 1
        safe_tx.refund_receiver = estimation['refundReceiver']
        safe_tx.gas_token = gas_token
        self.sign_transaction(safe_tx)
        transaction_data = self.safe_relay_service.send_transaction(self.address, safe_tx)
        tx_hash = transaction_data['txHash']
        print_formatted_text(HTML(f'<ansigreen>Gnosis Safe Relay has queued transaction with '
                                  f'transaction-hash <b>{tx_hash}</b></ansigreen>'))
