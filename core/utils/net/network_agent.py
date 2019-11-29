#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Importing Custom Logger & Logging Modules
from core.logger.custom_logger import CustomLogger
from logging import INFO
import logging

# Import Socket Exceptions
from core.utils.net.exceptions.network_exceptions import (NetworkAgentFatalException, NetworkAgentSocketError)

# Import Socket Module
import socket
from core.constants.console_constant import API_KEY_DICT
from gnosis.eth.ethereum_client import EthereumClient


DEFAULT_INFURA_API_KEY =  'b3fa360a82cd459e8f1b459b3cf9127c'
DEFAULT_ETHERSCAN_API_KEY = 'A1T1PKJXZJC1T4RJZK4ZMZH4JEYTUGAA6G'

class NetworkAgent:
    """ Network Agent

    Code Reference: https://stackoverflow.com/questions/3764291/checking-network-connection
    This class will establish the current state of the connectivity to internet for the system in case it's needed.
    """
    def __init__(self, logger, network='ganache', api_key=None):
        self.name = self.__class__.__name__
        self.logger = logger
        self.network = network

        # Default Polling Address Settings: Used for checking internet availability
        self.polling_address = '8.8.8.8'
        self.polling_port = 53
        self.polling_timeout = 3

        # Default Ethereum Node Endpoint for the EthereumClient
        self.default_node_endpoint = 'http://localhost:8545'

        if self.network_status():
            self.set_network_provider_endpoint(network, api_key)

    def _setup_new_provider(self, node_url):
        tmp_client = EthereumClient(ethereum_node_url=node_url)
        if tmp_client.w3.isConnected():
            self.ethereum_client = tmp_client
            self.logger.info('{0} Successfully retrieved a valid connection to {1} '.format(self.name, node_url))
        else:
            self.logger.error('{0} Unable to retrieve a valid connection to {1} '.format(self.name, node_url))

    def view_network_information(self):
        self.logger.info('To Be Implemented')

    def set_network_provider_endpoint(self, network, api_key=None):
        """ Set Network

        :param network:
        :param api_key:
        :return:
        """
        if network == 'mainnet':
            mainnet_node_url = '{0}{1}'.format('https://mainnet.infura.io/v3/', api_key)
            if api_key is not None:
                self._setup_new_provider(mainnet_node_url)
                self.network = 'mainnet'
            else:
                self.logger.error('Infura API KEY needed, {0} Unable to retrieve a valid connection to {1} '.format(self.name, mainnet_node_url))

        elif network == 'ropsten':
            ropsten_node_url = '{0}{1}'.format('https://ropsten.node.url/', api_key)
            if api_key is not None:
                self._setup_new_provider(ropsten_node_url)
                self.network = 'ropsten'
            else:
                self.logger.error('API KEY needed, {0} Unable to retrieve a valid connection to {1} '.format(self.name, ropsten_node_url))

        elif network == 'rinkeby':
            rinkeby_node_url = '{0}{1}'.format('https://rinkeby.infura.io/v3/', api_key)
            if api_key is not None:
                self._setup_new_provider(rinkeby_node_url)
                self.network = 'rinkeby'
            else:
                self.logger.error('API KEY needed, {0} Unable to retrieve a valid connection to {1} '.format(self.name, rinkeby_node_url))
        elif network == 'ganache':
            self._setup_new_provider('http://localhost:8545')
            self.network = 'ganache'

    def network_status(self):
        """ Network Status

        This Function will check the availability of the network connection
            :return True if there is internet connectivity otherwise False
        """
        try:
            socket.setdefaulttimeout(self.polling_timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self.polling_address, self.polling_port))
            self.logger.debug0('{0}: Internet is On!!'.format(self.name))
            return True
        except socket.error:
            return False
        except Exception as err:
            # Empty param should be trace for further debugging in case it's needed
            self.logger.debug0('{0}: Something went really wrong:\n{1}'.format(self.name, err))
            raise NetworkAgentFatalException(self.name, err, '')
