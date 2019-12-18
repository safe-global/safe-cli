#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Temporal Information Artifacts
from core.eth_assets.help_artifacts import InformationArtifacts

# Import ConsoleInputGetter for Testing Purposes
from core.input.console_input_getter import ConsoleInputGetter
from core.input.console_input_handler import ConsoleInputHandler


class ContractController:
    """ Console Controller
    This class will represent and function as pseudo-controller for the execution of the proper commands
    """
    def __init__(self, logger, network_agent, ethereum_assets, gnosis_engine):
        self.logger = logger

        self.ethereum_assets = ethereum_assets
        self.contracts = self.ethereum_assets.contracts
        self.accounts = self.ethereum_assets.accounts
        self.payloads = self.ethereum_assets.payloads
        self.tokens = self.ethereum_assets.tokens
        self.network_agent = network_agent
        self.console_information = InformationArtifacts(self.logger)

        self.gnosis_engine = gnosis_engine
        self.safe_interface = None
        self.contract_interface = None
        self.console_getter = ConsoleInputGetter(self.logger)
        self.console_handler = ConsoleInputHandler()

    def operate_with_contract(self, stream, contract_methods, contract_instance):
        """ Operate With Contract
        This function will retrieve the methods present in the contract_instance
        :param stream: command_argument (method to call) that will trigger the operation
        :param contract_methods: dict with all the avaliable methods retrieved from the abi file
        :param contract_instance: only for eval() so it can be triggered
        :return: if method found, a method from the current contract_cli.log will be triggered, success or
        not depends on the establishing of the proper values.
        """
        try:
            self.logger.debug0('(+) [ Operating with Contract Console ]: ' + stream)
            for item in contract_methods:
                if contract_methods[item]['name'] in stream:
                    splitted_stream = stream.split(' ')
                    address_from = ''
                    # This function Call now longer works, break in compatibility
                    _query, _execute, _queue, _ = self.console_getter.get_input_affix_arguments(splitted_stream)
                    function_name, function_arguments = \
                        self.console_getter.retrieve_contract_data(splitted_stream, contract_methods[item]['arguments'])
                    self.logger.debug0('command: {0} | arguments: {1} | execute_flag: {2} | query_flag: {3} | '.format(
                        function_name, function_arguments, _execute, _queue))

                    if _execute or _queue or _query:
                        if _query:
                            # remark: Call Solver
                            self.logger.info(contract_methods[item]['call'].format(function_arguments, address_from))
                            resolution = eval(contract_methods[item]['call'].format(function_arguments, address_from))
                            self.logger.info(resolution)

                        elif _execute:
                            # remark: Transaction Solver
                            if contract_methods[item]['name'].startswith('get'):
                                self.logger.warn('transact() operation is discourage if you are using a getter method')
                            # if address_from != '':
                                # address_from = '\{\'from\':{0}\}'.format(address_from)

                            self.logger.info(contract_methods[item]['transact'].format(function_arguments, address_from))
                            resolution = eval(contract_methods[item]['transact'].format(function_arguments, address_from))
                            self.logger.info(resolution)
                            # this is the hash to be signed, maybe call for approve dialog, approveHash dialogue,
                            # map functions to be performed by the gnosis_py library

                        elif _queue:
                            # remark: Add to the Batch Solver
                            self.logger.info('(Future Implementation) executeBatch when you are ready to launch '
                                             'the transactions that you queued up!')

                    else:
                        self.logger.warn('--execute, --query or --queue arguments needed in order to properly '
                                         'operate with the current contract_cli.log')

        except Exception as err:
            self.logger.debug0('operate_with_contract() {0}'.format(err))
