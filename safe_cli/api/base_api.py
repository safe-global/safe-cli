from abc import ABC
from typing import Dict, Optional
from urllib.parse import urljoin

import requests

from gnosis.eth.ethereum_client import EthereumNetwork


class BaseAPIException(Exception):
    pass


class BaseAPI(ABC):
    URL_BY_NETWORK: Dict[EthereumNetwork, str] = {}

    def __init__(self, network: EthereumNetwork):
        self.network = network
        self.base_url = self.URL_BY_NETWORK[network]

    @classmethod
    def from_network_number(cls, network: int) -> Optional["BaseAPI"]:
        ethereum_network = EthereumNetwork(network)
        if ethereum_network in cls.URL_BY_NETWORK:
            return cls(ethereum_network)

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
