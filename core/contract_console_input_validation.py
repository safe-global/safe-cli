#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Importing Constants
from core.constants.default_values import CONTRACT_ADDRESS_LENGTH, TX_ADDRESS_LENGTH, INFURA_API_KEY_LENGTH, ETHERSCAN_API_KEY_LENGTH

# Importing Re Package
import re

class GnosisConsoleInputValidation:
    """ Gnosis Console Input

    """
    def __init__(self, logger):
        self.name = self.__class__.__name__
        self.logger = logger


    def input_api_key_validation(self, api_key):
        """ Input API Key Validation
        This function will validate the input API Key validation
        :param api_key:
        :return:
        """

        try:
            valid_api_key = re.search('[aA-zZ,0-9]*', api_key).group(0)
            if len(api_key) is INFURA_API_KEY_LENGTH and valid_api_key != '':
                self.logger.info('Infura API Key Detected')
            elif len(api_key) is ETHERSCAN_API_KEY_LENGTH and valid_api_key != '':
                self.logger.info('Etherscan API Key Detected')
            else:
                self.logger.info('No API Key Detected')
        except Exception as err:
            print(err)
        return '-1'

    def input_network_validation(self, network, network_id, network_params):
        """ Input Network Validation
        This function will validate the input network/network id, if both are provided. If network does not support
        network params they will not be validated and a warning will be prompted.
            :param network:
            :param network_id:
            :param network_params:
            :return:
        """
        if network != '':
            if network.lower() == 'ganache':
                self.logger.info('Ganache Network Detected')
                if network_params != {}:
                    self.logger.info('Ganache Param Network Detected')
            elif network.lower() == 'mainnet':
                self.logger.info('Mainnet Network Detected')
            elif network.lower() == 'rinkeby':
                self.logger.info('Rinkeby Network Detected')

        # Todo: Found Network Id's to be evalutated here if the network "name" it's not provided
        elif network_id != -1:
            self.logger.info('Nothing to watch here!')

        # validate the network o network id to launch the provider later.
        # if ganache and not online, launch te current ganache cli with the provided parameters.
        return
