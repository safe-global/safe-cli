# Importing Custom Logger & Logging Modules
from core.logger.custom_logger import CustomLogger
from logging import INFO
import logging

from core.net.network_agent import NetworkAgent


# ----------------------------------------------------------------------------------------------------------------------
# Setting Up Components
# ----------------------------------------------------------------------------------------------------------------------
logging_lvl = INFO
logger = CustomLogger(__name__, logging_lvl)
formatter = logging.Formatter(fmt='%(asctime)s - [ %(levelname)s ]: %(message)s',
                              datefmt='%I:%M:%S %p')

# Custom Logger Console Configuration: Console Init Configuration
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(level=logging_lvl)

# Custom Logger Console/File Handler Configuration
logger.addHandler(console_handler)

# Setup Console Input Getter
network_agent = NetworkAgent(logger)


def test_set_network_ganache():
    network_name = 'ganache'
    assert network_agent.network == network_name
    assert network_agent.get_current_node_endpoint() == 'http://localhost:8545'
    assert network_agent.ethereum_client.w3.isConnected()


def test_set_network_rinkeby():
    api_key = 'b3fa360a82cd459e8f1b459b3cf9127c'
    network_name = 'rinkeby'
    network_agent.set_network_provider_endpoint(network_name, api_key)

    assert network_agent.network == network_name
    assert network_agent.get_current_node_endpoint() == 'https://rinkeby.infura.io/v3/b3fa360a82cd459e8f1b459b3cf9127c'
    assert network_agent.ethereum_client.w3.isConnected()


def test_set_network_mainnet():
    api_key = 'b3fa360a82cd459e8f1b459b3cf9127c'
    network_name = 'mainnet'
    network_agent.set_network_provider_endpoint(network_name, api_key)

    assert network_agent.network == network_name
    assert network_agent.get_current_node_endpoint() == 'https://mainnet.infura.io/v3/b3fa360a82cd459e8f1b459b3cf9127c'
    assert network_agent.ethereum_client.w3.isConnected()

# def test_set_network_ropsten():
#     network_name = 'ropsten'
#     api_key = ''