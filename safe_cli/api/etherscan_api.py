from gnosis.eth.ethereum_client import EthereumNetwork

from .base_api import BaseAPI


class EtherscanApi(BaseAPI):
    URL_BY_NETWORK = {
        EthereumNetwork.MAINNET: "https://etherscan.io",
        EthereumNetwork.RINKEBY: "https://rinkeby.etherscan.io",
        EthereumNetwork.ROPSTEN: "https://ropsten.etherscan.io",
        EthereumNetwork.GOERLI: "https://goerli.etherscan.io",
        EthereumNetwork.KOVAN: "https://kovan.etherscan.io",
        EthereumNetwork.BINANCE: "https://bscscan.com",
        EthereumNetwork.MATIC: "https://polygonscan.com",
        EthereumNetwork.OPTIMISTIC: "https://optimistic.etherscan.io",
    }
