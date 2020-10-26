from gnosis.eth.ethereum_client import EthereumNetwork

from .base_api import BaseAPI


class Etherscan(BaseAPI):
    URL_BY_NETWORK = {
        EthereumNetwork.MAINNET: 'https://etherscan.io',
        EthereumNetwork.ROPSTEN: 'https://ropsten.etherscan.io',
        EthereumNetwork.RINKEBY: 'https://rinkeby.etherscan.io',
        EthereumNetwork.GOERLI: 'https://goerli.etherscan.io',
        EthereumNetwork.KOVAN: 'https://kovan.etherscan.io',
    }
