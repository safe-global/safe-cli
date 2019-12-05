#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Json Package
import json

# Import Os Package
import os

# Constants
STRING_DASHES = '----------' * 14


class ContractReader:
    """ Build Contract Reader
    This class will provide functionality for the extraction of the abi and bytecode for any given contract
    """
    def __init__(self, logger=None):
        self.name = self.__class__.__name__
        self.logger = logger

    @staticmethod
    def read_from(file_path):
        """ Read From
        This method will read the json file provided within the current file_path, and return in it's found the abi
        and the bytecode for the current contract.
        :param file_path: path to the build files of the current contract
        :return: contract_abi, contract_bytecode
        """
        contract_abi = {}
        contract_bytecode = {}
        contract_name = os.path.basename(file_path)[:-5]
        try:
            print(STRING_DASHES)
            print(' | Reading ABI File from path {current_path}  | '.format(current_path=file_path))
            with open(file_path) as f:
                json_data = json.load(f)

            try:
                contract_abi = json_data["abi"]
                print(' | {contract_name} ABI has been found within the file path provided for the current contract | '.format(contract_name=contract_name))
            except KeyError:
                print('Unable to Retrieve ABI from .json build')
                pass

            try:
                contract_bytecode = json_data["bytecode"]
                print(' | {contract_name} Bytecode has been found within the file path provided for the current contract | '.format(contract_name=contract_name))
            except KeyError:
                print(' | Unable to Retrieve Bytecode from .json build | ')
                pass
            return contract_abi, contract_bytecode, contract_name
        except Exception as err:
            print('[ FATAL Contract Reader ]: {error}'.format(error=err))


