#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Web3 Package
from web3 import Web3

# Import HexBytes Package
from hexbytes import HexBytes

# Import Json ABIReader Package
from core.utils.build_contract_reader import ContractReader

class ContractInterface:
    def __init__(self, provider):
        self.provider = provider
        self.build_contract_reader = ContractReader()

    # Todo: rename or something the contract_to_point
    # def get_artifacts(self, contract_data, contract_address=None, contract_to_point=None):
    #     """ Get Artifacts
    #
    #     This function will return a contract instance, contract abi, contract bytecode and contract address depending
    #     on the input provided by the user. If te user gives just the .json file, the bytecode will be retrieve and a new
    #     instance for the contract will be generated in the blockchain so it can be interacted with.
    #
    #     :param contract_address:
    #     :param contract_abi:
    #     :return: contract_instance, contract_abi, contract_bytecode, contract_address
    #     """
    #     if contract_address is not None:
    #         contract_abi, contract_bytecode = self.build_contract_reader.read_from(contract_data)
    #         contract_instance = self.provider.eth.contract(abi=contract_abi, address=contract_address)
    #         return {
    #             'instance': contract_instance,
    #             'abi': contract_abi,
    #             'bytecode': contract_bytecode,
    #             'address': Web3.toChecksumAddress(contract_address)
    #         }
    #
    #     contract_abi, contract_bytecode = self.build_contract_reader.read_from(contract_data)
    #     contract_instance = self.provider.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
    #
    #     if contract_to_point is not None:
    #         # Submit the transaction that deploys the new contract into the blockchain
    #         tx_hash = contract_instance.constructor(contract_to_point).transact({'from': self.provider.eth.accounts[0]})
    #         # Wait for the transaction to be mined, and get the transaction receipt
    #         tx_receipt = self.provider.eth.waitForTransactionReceipt(tx_hash)
    #     else:
    #         # Submit the transaction that deploys the new contract into the blockchain
    #         tx_hash = contract_instance.constructor().transact({'from': self.provider.eth.accounts[0]})
    #         # Wait for the transaction to be mined, and get the transaction receipt
    #         tx_receipt = self.provider.eth.waitForTransactionReceipt(tx_hash)
    #     return {
    #         'instance': contract_instance,
    #         'abi': contract_abi,
    #         'bytecode': contract_bytecode,
    #         'address': Web3.toChecksumAddress(tx_receipt.contractAddress)
    #     }

    def map_contract_methods(self, contract_instance):
        """ Map Contract functions
        This function will map Events, Functions ( call , transact ), make distintions beetwen them? no input automatic query like function
        input but not output + doble Mayus name Event, otherwise functions with input,output transact it's required
        :param contract_instance:
        :return:
        """
        item_name = ''
        item_input = ''
        contract_methods = {}
        try:
            # Retrieve methods presents in the provided abi file
            for index, item in enumerate(contract_instance.functions.__dict__['abi']):
                try:
                    item_name = item['name']
                except KeyError:
                    continue
                try:
                    item_input = item['inputs']
                except KeyError:
                    item_input = ''
                try:
                    # <>

                    metadata_arguments = []
                    metadata_information = []
                    stream_input = ''
                    if len(item_input) >= 1:
                        for data_index, data in enumerate(item_input):
                            metadata_information.append({data_index: str(data['type']) + ' ' + str(data['name'])})
                            metadata_arguments.append({data_index: str(data['type'])})
                            stream_input += '{' + str(data_index) + '},'

                        contract_methods[index] = {
                            'name': item_name,
                            'arguments': metadata_arguments,
                            'argument_block': stream_input[:-1],
                            'metadata': metadata_information,
                            'call': 'contract_instance.functions.{0}('.format(item_name) + '{0}).call({1})',
                            'transact': 'contract_instance.functions.{0}('.format(item_name) + '{0}).transact({1})',
                        }
                    else:
                        contract_methods[index] = {
                            'name': item_name,
                            'arguments': metadata_arguments,
                            'argument_block': stream_input,
                            'metadata': metadata_information,
                            'call': 'contract_instance.functions.{0}('.format(item_name) + '{0}).call({1})',
                            'transact': 'contract_instance.functions.{0}('.format(item_name) + '{0}).transact({1})',
                        }
                except Exception as err:
                    print(type(err), err)
            return contract_methods
        except Exception as err:
            print(err)
