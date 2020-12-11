from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests

from gnosis.eth.ethereum_client import EthereumNetwork
from gnosis.safe import SafeTx

from .base_api import BaseAPI


class TransactionService(BaseAPI):
    URL_BY_NETWORK = {
        EthereumNetwork.MAINNET: 'https://safe-transaction.mainnet.gnosis.io',
        EthereumNetwork.RINKEBY: 'https://safe-transaction.rinkeby.gnosis.io',
        EthereumNetwork.GOERLI: 'https://safe-transaction.goerli.gnosis.io/',
        EthereumNetwork.XDAI: 'https://safe-transaction.xdai.gnosis.io/',
        EthereumNetwork.VOLTA: 'https://safe-transaction.volta.gnosis.io/',
        EthereumNetwork.ENERGY_WEB_CHAIN: 'https://safe-transaction.ewc.gnosis.io/',

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
            raise BaseAPI(f'Cannot get balances: {response.content}')
        else:
            return response.json()

    def get_transactions(self, safe_address: str) -> List[Dict[str, Any]]:
        response = self._get_request(f'/api/v1/safes/{safe_address}/multisig-transactions/')
        if not response.ok:
            raise BaseAPI(f'Cannot get transactions: {response.content}')
        else:
            return response.json().get('results', [])

    def post_transaction(self, safe_address: str, safe_tx: SafeTx):
        url = urljoin(self.base_url, f'/api/v1/safes/{safe_address}/multisig-transactions/')
        random_account = '0x1b95E981F808192Dc5cdCF92ef589f9CBe6891C4'
        sender = safe_tx.sorted_signers[0] if safe_tx.sorted_signers else random_account
        data = {
            'to': safe_tx.to,
            'value': safe_tx.value,
            'data': safe_tx.data.hex() if safe_tx.data else None,
            'operation': safe_tx.operation,
            'gasToken': safe_tx.gas_token,
            'safeTxGas': safe_tx.safe_tx_gas,
            'baseGas': safe_tx.base_gas,
            'gasPrice': safe_tx.gas_price,
            'refundReceiver': safe_tx.refund_receiver,
            'nonce': safe_tx.safe_nonce,
            'contractTransactionHash': safe_tx.safe_tx_hash.hex(),
            'sender': sender,
            'signature': safe_tx.signatures.hex() if safe_tx.signatures else None,
            'origin': 'Safe-CLI'
        }
        response = requests.post(url, json=data)
        if not response.ok:
            raise BaseAPI(f'Error posting transaction: {response.content}')
