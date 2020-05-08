from typing import Any, Dict, List

from .base_api import BaseAPI


class TransactionService(BaseAPI):
    URL_BY_NETWORK = {
        1: 'https://safe-transaction.mainnet.gnosis.io',
        # 3:
        4: 'https://safe-transaction.rinkeby.gnosis.io',
        # 5:
        # 42
    }

    def get_balances(self, safe_address: str) -> List[Dict[str, Any]]:
        response = self._get_request(f'/api/v1/safes/{safe_address}/balances/')
        if not response.ok:
            raise BaseAPI(f'Cannot get balances from {url}')
        else:
            return response.json()

    def get_transactions(self, safe_address: str) -> List[Dict[str, Any]]:
        response = self._get_request(f'/api/v1/safes/{safe_address}/transactions/')
        if not response.ok:
            raise BaseAPI(f'Cannot get balances from {url}')
        else:
            return response.json().get('results', [])
