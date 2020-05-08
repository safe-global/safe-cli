from abc import ABC
from typing import Dict, Optional
from urllib.parse import urljoin

import requests


class BaseAPIException(Exception):
    pass


class BaseAPI(ABC):
    URL_BY_NETWORK: Dict[int, str] = {}

    def __init__(self, network: int):
        self.network = network
        self.url = self.URL_BY_NETWORK[network]

    @classmethod
    def from_network_number(cls, network: int) -> Optional['BaseAPI']:
        if network in cls.URL_BY_NETWORK:
            return cls(network)

    def _get_request(self, url: str) -> requests.Response:
        full_url = urljoin(self.url, url)
        response = requests.get(full_url)
        if not response.ok:
            raise BaseAPI(f'Cannot get balances from {url}')
        return response
