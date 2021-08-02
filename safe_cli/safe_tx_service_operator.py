from typing import Optional

from hexbytes import HexBytes
from prompt_toolkit import HTML, print_formatted_text
from tabulate import tabulate

from gnosis.safe import SafeOperation, SafeTx

from .safe_operator import (AccountNotLoadedException,
                            NonExistingOwnerException, SafeOperator,
                            ServiceNotAvailable)
from .utils import yes_or_no_question


class SafeTxServiceOperator(SafeOperator):
    def __init__(self, address: str, node_url: str):
        super().__init__(address, node_url)
        if not self.safe_tx_service:
            raise ServiceNotAvailable(f'Cannot configure tx service for network {self.network.name}')
        self.require_all_signatures = False  # It doesn't require all signatures to be present to send a tx

    def approve_hash(self, hash_to_approve: HexBytes, sender: str) -> bool:
        raise NotImplementedError('Not supported when using tx service')

    def get_delegates(self):
        delegates = self.safe_tx_service.get_delegates(self.address)
        headers = ['delegate', 'delegator', 'label']
        rows = []
        for delegate in delegates:
            row = [delegate['delegate'], delegate['delegator'], delegate['label']]
            rows.append(row)
        print(tabulate(rows, headers=headers))

    def add_delegate(self, delegate_address: str, label: str, signer_address: str):
        signer_account = [account for account in self.accounts if account.address == signer_address]
        if not signer_account:
            raise AccountNotLoadedException(signer_address)
        elif signer_address not in self.safe_cli_info.owners:
            raise NonExistingOwnerException(signer_address)
        else:
            signer_account = signer_account[0]
            try:
                self.safe_tx_service.add_delegate(self.address, delegate_address, label, signer_account)
                return True
            except IOError:
                return False

    def remove_delegate(self, delegate_address: str, signer_address: str):
        signer_account = [account for account in self.accounts if account.address == signer_address]
        if not signer_account:
            raise AccountNotLoadedException(signer_address)
        elif signer_address not in self.safe_cli_info.owners:
            raise NonExistingOwnerException(signer_address)
        else:
            signer_account = signer_account[0]
            try:
                self.safe_tx_service.remove_delegate(self.address, delegate_address, signer_account)
                return True
            except IOError:
                return False

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
