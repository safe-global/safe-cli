#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Importing Constants
from core.constants.console_constant import INFURA_API_KEY_LENGTH, ETHERSCAN_API_KEY_LENGTH

# Importing Re Package
import re

# is_valid_address = r'^(0x)?[0-9a-f]{40}$'
# is_62_valid_address = r'^(0x)?[0-9a-f]{62}$'
# Web3.fromWei(1000000000000000000, 'Gwei')
# Web3.isAddress('0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed')
# Web3.isChecksumAddress('0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed')

class ConsoleInputValidation:
    """ Console Input Validation

    """
    def __init__(self, logger):
        self.name = self.__class__.__name__
        self.logger = logger

    def validate_integer_input(self, param, param_type):
        """ Validate Integer Input

        :param param:
        :param param_type:
        :return:
        """
        # use hex()
        # address payable 160
        # address 256
        if param_type == 'uint8' and param <= 255:
            return True, ''
        elif param_type == 'uint16' and param <= 65535:
            return True, ''
        elif param_type == 'uint32' and param <= 4294967295:
            return True, ''
        elif param_type == 'uint64'and param <= 18446744073709551615:
            return True, ''
        elif param_type == 'uint128'and param <= 340282366920938463463374607431768211455:
            return True, ''
        elif param_type == 'uint160'and param <= 1461501637330902918203684832716283019655932542975:
            return True, ''
        elif param_type == 'uint256'and param <= 115792089237316195423570985008687907853269984665640564039457584007913129639935:
            return True, ''
        return False, 'Not a valid {0} (Does not fit the current type for the function input)'.format(param_type)

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
