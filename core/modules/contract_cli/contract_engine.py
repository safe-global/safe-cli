#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import HTML for defining the prompt style

# Import Console Artifacts

# Import PromptToolkit Package

# Importing Custom Logger & Logging Modules
from core.logger.custom_logger import CustomLogger
from logging import INFO
import logging

# Import TypeOfConsole Enum

# Import EtherHelper for unifying ether amount quantities

# Import Console Components
from core.modules.safe_cli.components.safe_configuration import SafeConfiguration

# Import LogMessageFormatter: view_functions
from core.logger.log_message_formatter import LogMessageFormatter

# Import Completer & SyntaxLexer

from core.input.console_input_getter import ConsoleInputGetter

EXIT_DIALOG_TITLE = 'Exiting Safe ({0})'
EXIT_DIALOG_MSG = 'All data regarding loaded owners & sender configuration will be lost, ' \
                  'Are you sure you want to exit the {0}?'
SAFE_ENGINE_LOG = './log/safe_cli.log'


class ContractEngine:
    def __init__(self, network_agent, ethereum_assets, gnosis_manager):
        self.name = self.__class__.__name__

        # GnosisManager: update state
        self.gnosis_manager = gnosis_manager

        self.contract_interface = None
        self.contract_controller = None
        self.contract_address = None

        # Configure Logger Here
        self.ethereum_assets = ethereum_assets

        # Custom Logger Init Configuration: Default Values
        self.logging_lvl = INFO
        self.logger = CustomLogger(self.name, self.logging_lvl)
        self._setup_logger()

        # LogMessageFormatter: view_functions()
        self.log_formatter = LogMessageFormatter(self.logger)

        self.network_agent = network_agent
        self.ethereum_client = network_agent.ethereum_client

        # Finish setup on components for the safe_cli
        # SafeConfiguration:
        self.safe_configuration = SafeConfiguration(self.logger)

        self.getter = ConsoleInputGetter(self.logger)

    def _setup_logger(self):
        """ Setup_Logger
        This function will configure the custom logger outputs and format
        """
        # CustomLogger: Format Definition: Output Init Configuration
        formatter = logging.Formatter(fmt='%(asctime)s - [ %(levelname)s ]: %(message)s',
                                      datefmt='%I:%M:%S %p')
        detailed_formatter = logging.Formatter(fmt='%(asctime)s - [ %(levelname)s ]: %(message)s',
                                               datefmt='%m/%d/%Y %I:%M:%S %p')

        # CustomLogger: File Configuration: File Init Configuration
        file_handler = logging.FileHandler(SAFE_ENGINE_LOG, 'w')
        file_handler.setFormatter(detailed_formatter)
        file_handler.setLevel(level=self.logging_lvl)

        # CustomLogger: Console Configuration: Console Init Configuration
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level=self.logging_lvl)

        # CustomLogger: Console/File Handler Configuration
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def run(self, contract_alias=None):
        """ Run Contract Console
        This function will run the contract_cli.log console
        :param contract_alias:
        :return:
        """
        try:
            self.log_formatter.log_entry_message('Entering Contract Console')
            # set_title('Contract Console')
            # self.contract_interface = self.data_artifacts.retrive_from_stored_values(
            #     contract_alias, 'instance', 'contract_cli.log')
            # self.logger.debug0('Contract Instance {0} Loaded'.format(self.contract_interface))
            # self.contract_methods = ConsoleContractCommands().map_contract_methods(self.contract_interface)
            # self.active_session = TypeOfConsole.CONTRACT_CONSOLE
            # self.run(
            #     prompt_text=self.get_prompt_text(affix_stream='contract_cli.log-cli', stream=contract_alias))
        except KeyError as err:
            self.logger.error(err)

    # def _setup_console_contract_configuration(self, configuration):
    #     """ Setup Console Contract Configuration
    #     This function will load contract_cli.log eth_assets for the console to have access to
    #     :param configuration:
    #     :return:
    #     """
    #     if configuration['abi'] and configuration['contract_cli.log']:
    #         self.logger.debug0(configuration['contract_cli.log'])
    #         self.logger.debug0(configuration['abi'])
    #
    #         for contract_index, contract_abi in enumerate(configuration['abi']):
    #             contract_address = configuration['contract_cli.log'][contract_index]
    #             contract_abi, contract_bytecode, contract_name = self.contract_reader.read_from(contract_abi)
    #
    #             contract_instance = self.network_agent.ethereum_client.w3.eth.contract(
    #                 abi=contract_abi, address=contract_address)
    #
    #             self.contract_artifacts.add_contract_artifact(
    #                 contract_name, contract_instance, contract_abi, contract_bytecode, contract_address, contract_name)
    #
    #     elif configuration['abi'] and not configuration['contract_cli.log']:
    #         for contract_abi in configuration['abi']:
    #             contract_abi, contract_bytecode, contract_name = self.contract_reader.read_from(contract_abi)
    #             self.contract_artifacts.add_contract_artifact(
    #                 contract_name, None, contract_abi, contract_bytecode, None, contract_name)


