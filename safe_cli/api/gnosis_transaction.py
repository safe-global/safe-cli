from typing import Any, Dict, List, Optional

from .base_api import BaseAPI


class TransactionService(BaseAPI):
    URL_BY_NETWORK = {
        1: 'https://safe-transaction.mainnet.gnosis.io',
        # 3:
        4: 'https://safe-transaction.rinkeby.gnosis.io',
        # 5:
        # 42
    }

    def data_decoded_to_text(self, data_decoded: Dict[str, Any]) -> Optional[str]:
        """
        Decoded data decoded to text
        :param data_decoded:
        :return:
        """
        if not data_decoded:
            return None

        method = data_decoded['method']
        parameters = data_decoded.get('parameters', [])
        text = ''
        for parameter in parameters:  # Multisend or executeTransaction from another Safe
            if 'decodedValue' in parameter:
                text += (method + ':\n - ' + '\n - '.join([self.data_decoded_to_text(decoded_value.get('decodedData',
                                                                                                       {}))
                                                           for decoded_value in parameter.get('decodedValue', {})])
                         + '\n')
        if text:
            return text.strip()
        else:
            return (method + ': '
                    + ','.join([str(parameter['value'])
                                for parameter in parameters]))

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
