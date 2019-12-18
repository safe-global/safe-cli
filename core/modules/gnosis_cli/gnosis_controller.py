#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Temporal Information Artifacts
from core.eth_assets.help_artifacts import InformationArtifacts

# Import ConsoleInputGetter for Testing Purposes
from core.input.console_input_getter import ConsoleInputGetter
from core.input.console_input_handler import ConsoleInputHandler


class GnosisController:
    """ Console Controller
    This class will represent and function as pseudo-controller for the execution of the proper commands
    :param logger:
    :param network_agent:
    :param ethereum_assets:
    :param gnosis_engine:
    """
    def __init__(self, logger, network_agent, ethereum_assets, gnosis_engine):
        self.logger = logger

        # EthereumAssets:
        self.ethereum_assets = ethereum_assets
        self.contracts = self.ethereum_assets.contracts
        self.accounts = self.ethereum_assets.accounts
        self.payloads = self.ethereum_assets.payloads
        self.tokens = self.ethereum_assets.tokens

        self.network_agent = network_agent

        self.console_information = InformationArtifacts(self.logger)

        # Modules
        self.gnosis_engine = gnosis_engine
        self.safe_engine = self.gnosis_engine.safe_engine
        self.contract_engine = self.gnosis_engine.contract_engine

        self.safe_interface = None
        self.contract_interface = None

        self.console_getter = ConsoleInputGetter(self.logger)
        self.console_handler = ConsoleInputHandler()

    def operate(self, desired_parsed_item_list, priority_group, command_argument, argument_list):
        """ Operate With Console
        This function will operate with the gnosis console using the input command/arguments provided by the user
        :param desired_parsed_item_list:
        :param priority_group:
        :param command_argument:
        :param argument_list:
        :return:
        """
        # load console console commands trigger procedures
        self.logger.debug0('(+) [ Operating with General Console ]: ' + command_argument)
        if command_argument == 'loadContract':
            if priority_group == 0:
                contract_alias = self.console_handler.input_handler(
                    command_argument, desired_parsed_item_list, priority_group)
                self.contract_interface = self.contract_engine.run(contract_alias)
        elif command_argument == 'loadSafe':
            if priority_group == 1:
                safe_address = self.console_handler.input_handler(
                    command_argument, desired_parsed_item_list, priority_group)
                self.safe_interface = self.safe_engine.run(safe_address)

        # view console commands procedures
        elif command_argument == 'viewTokens':
            self.tokens.command_view_tokens()
        elif command_argument == 'viewNetwork':
            self.network_agent.view_networks()
        elif command_argument == 'viewContracts':
            self.contracts.command_view_contracts()
        elif command_argument == 'viewAccounts':
            self.accounts.view_accounts()
        elif command_argument == 'viewPayloads':
            self.payloads.command_view_payloads()

        # new console commands trigger procedures
        elif command_argument == 'newAccount':
            self.logger.info('newAccount <Address> or <PK> or <PK + Address>')
        elif command_argument == 'newPayload':
            self.payloads.command_new_payload(command_argument, argument_list)
        elif command_argument == 'newTxPayload':
            self.payloads.command_new_payload(command_argument, argument_list)
        elif command_argument == 'newToken':
            self.tokens.command_new_token(command_argument, argument_list)

        # setter console commands trigger procedures
        elif command_argument == 'setNetwork':
            if priority_group == 1:
                network_name, network_api_key = self.console_handler.input_handler(
                    command_argument, desired_parsed_item_list, priority_group)
                self.network_agent.set_network_provider_endpoint(network_name, network_api_key)
            elif priority_group == 2:
                network_name, network_api_key = self.console_handler.input_handler(
                    command_argument, desired_parsed_item_list, priority_group)
                self.network_agent.set_network_provider_endpoint(network_name, network_api_key)

        # information console commands trigger procedures
        elif command_argument == 'about':
            self.console_information.command_view_about()
        elif command_argument == 'help':
            self.console_information.command_view_general_information()
