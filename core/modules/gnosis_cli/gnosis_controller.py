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
    """
    def __init__(self, logger, network_agent, data_artifact, console_engine):
        self.logger = logger

        self.data_artifact = data_artifact
        self.contract_artifacts = self.data_artifact.contract_artifacts
        self.account_artifacts = self.data_artifact.account_artifacts
        self.payload_artifacts = self.data_artifact.payload_artifacts
        self.token_artifacts = self.data_artifact.token_artifacts
        self.network_agent = network_agent
        self.console_information = InformationArtifacts(self.logger)

        self.console_engine = console_engine
        self.safe_interface = None
        self.contract_interface = None
        self.console_getter = ConsoleInputGetter(self.logger)
        self.console_handler = ConsoleInputHandler(self.logger, self.data_artifact)

    def operate_with_console(self, desired_parsed_item_list, priority_group, command_argument, argument_list):
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
                self.contract_interface = self.console_engine.run_contract_console(contract_alias)
        elif command_argument == 'loadSafe':
            if priority_group == 1:
                safe_address = self.console_handler.input_handler(
                    command_argument, desired_parsed_item_list, priority_group)
                self.safe_interface = self.console_engine.run_safe_console(safe_address)

        # view console commands procedures
        elif command_argument == 'viewTokens':
            self.token_artifacts.command_view_tokens()
        elif command_argument == 'viewNetwork':
            self.network_agent.command_view_networks()
        elif command_argument == 'viewContracts':
            self.contract_artifacts.command_view_contracts()
        elif command_argument == 'viewAccounts':
            self.account_artifacts.command_view_accounts()
        elif command_argument == 'viewPayloads':
            self.payload_artifacts.command_view_payloads()

        # new console commands trigger procedures
        elif command_argument == 'newAccount':
            self.logger.info('newAccount <Address> or <PK> or <PK + Address>')
        elif command_argument == 'newPayload':
            self.payload_artifacts.command_new_payload(command_argument, argument_list)
        elif command_argument == 'newTxPayload':
            self.payload_artifacts.command_new_payload(command_argument, argument_list)
        elif command_argument == 'newToken':
            self.token_artifacts.command_new_token(command_argument, argument_list)

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
