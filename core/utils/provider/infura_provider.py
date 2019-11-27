#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import API Key
from core.constants.api_keys import api_key_dict

# Import Web3 Module

# Importing Custom Logger & Logging Modules
from core.logger.custom_logger import CustomLogger
from logging import INFO
import logging

class InfuraProvider:
    def __init__(self, network, api_key='', logging_lvl=INFO):
        self.name = self.__class__.__name__
        self.api_key = self.__get_api_key(api_key)
        self.port = ''
        self.network_name = network
        self.address = self.__get_network(network)
        self.uri = '{0}{1}'.format(self.address, self.api_key)

        self.logger = CustomLogger(self.name, logging_lvl)

        # CustomLogger Format Definition
        formatter = logging.Formatter(fmt='%(asctime)s - [%(levelname)s]: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

        # Custom Logger File Configuration: File Init Configuration
        file_handler = logging.FileHandler('./log/gnosis_console/gnosis_console_input.log', 'w')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level=logging_lvl)

        # Custom Logger Console Configuration: Console Init Configuration
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level=logging_lvl)

        # Custom Logger Console/File Handler Configuration
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self._properties = {
            'name': self.name,
            'api_key': self.api_key,
            'port': self.port,
            'address': self.address,
            'uri': self.uri
        }

    def __getitem__(self, _key):
        if _key == 'properties':
            return self._properties
        return self._properties[_key]

    def __get_network(self, network):
        """ Get Network

        :param network:
        :return:
        """
        if network == 'mainnet':
            return 'https://mainnet.infura.io/v3/'
        return 'https://rinkeby.infura.io/v3/'

    def __get_api_key(self, _api_key):
        """ Get API Key
        This function retrieves a valid API Key from constant files in case no one was provided
        :param _api_key:
        :return:
        """
        if _api_key == '':
            return api_key_dict['API_KEY']['infura']['0']
        return _api_key