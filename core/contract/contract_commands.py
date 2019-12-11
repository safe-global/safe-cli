#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class ConsoleContractCommands:
    """ Console Contract Commands
    This function will provide dynamic access to the function  contracts using the abi
    """
    def __init__(self):
        self.name = self.__class__.__name__

    @staticmethod
    def to_method_artifact(name, arguments, argument_block, metadata):
        """ To Struct Method Artifacts
        This function will return a properly structured method artifact for contract_method dictionary

        :param name:
        :param arguments:
        :param argument_block:
        :param metadata:
        :return:
        """
        # todo: add {} ? to the function call reference
        return {
            'name': name,
            'arguments': arguments,
            'argument_block': argument_block,
            'metadata': metadata,
            'call': 'contract_instance.functions.{0}('.format(name) + '{0}).call({1})',
            'transact': 'contract_instance.functions.{0}('.format(name) + '{0}).transact({1})',
        }

    def map_contract_methods(self, contract_instance):
        """ Map Contract functions
        This function will map Events, Functions ( call , transact ), make distintions beetwen them? no input automatic
        query like function input but not output + doble Mayus name Event, otherwise functions with input,output
        transact it's required

        :param contract_instance: current contract instance used in the console
        :return: dictionary with the methods of the current instance provided
        """
        contract_methods = {}
        try:
            # Retrieve methods presents in the provided abi file
            for index, item in enumerate(contract_instance.functions.__dict__['abi']):
                method_arguments = []
                method_metadata = []
                stream_argument_input = ''

                try:
                    method_name = item['name']
                except KeyError:
                    # Here, it's ignored to be able to fully parse the keys of the abi
                    continue
                try:
                    method_inputs = item['inputs']
                except KeyError:
                    method_inputs = ''

                if len(method_inputs) >= 1:
                    for method_index, method_data in enumerate(method_inputs):
                        method_metadata.append({
                            method_index: str(method_data['type']) + ' ' + str(method_data['name'])
                        })
                        method_arguments.append({method_index: str(method_data['type'])})
                        stream_argument_input += '{' + str(method_index) + '},'

                    # Remove extra comma from the stream_argument_input[:-1] to fit the proper function input pattern
                    contract_methods[index] = self.to_method_artifact(
                        method_name, method_arguments, stream_argument_input[:-1], method_metadata
                    )
                else:
                    # No method input, so no removal needed here
                    contract_methods[index] = self.to_method_artifact(
                        method_name, method_arguments, stream_argument_input, method_metadata
                    )
            return contract_methods
        except Exception as err:
            print(type(err), err)
