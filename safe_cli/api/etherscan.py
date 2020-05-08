from .base_api import BaseAPI


class Etherscan(BaseAPI):
    URL_BY_NETWORK = {
        1: 'https://etherscan.io',
        3: 'https://ropsten.etherscan.io',
        4: 'https://rinkeby.etherscan.io',
        5: 'https://goerli.etherscan.io',
        42: 'https://kovan.etherscan.io',
    }
