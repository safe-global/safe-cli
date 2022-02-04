from abc import ABC
from typing import Dict, Optional
from urllib.parse import urljoin

import requests

from gnosis.eth.ethereum_client import EthereumClient, EthereumNetwork


class BaseAPIException(Exception):
    pass


class BaseAPI(ABC):
    URL_BY_NETWORK: Dict[EthereumNetwork, str] = {}

    def __init__(self, ethereum_client: EthereumClient, network: EthereumNetwork):
        self.ethereum_client = ethereum_client
        self.network = network
        self.base_url = self.URL_BY_NETWORK[network]

    @classmethod
    def from_ethereum_client(
        cls, ethereum_client: EthereumClient
    ) -> Optional["BaseAPI"]:
        ethereum_network = ethereum_client.get_network()
        if ethereum_network in cls.URL_BY_NETWORK:
            return cls(ethereum_client, ethereum_network)

    def _get_request(self, url: str) -> requests.Response:
        full_url = urljoin(self.base_url, url)
        return requests.get(full_url)

    def _post_request(self, url: str, payload: Dict) -> requests.Response:
        full_url = urljoin(self.base_url, url)
        return requests.post(
            full_url, json=payload, headers={"Content-type": "application/json"}
        )

    def _delete_request(self, url: str, payload: Dict) -> requests.Response:
        full_url = urljoin(self.base_url, url)
        return requests.delete(
            full_url, json=payload, headers={"Content-type": "application/json"}
        )
