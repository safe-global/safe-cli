#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Contract Reader Module
from core.eth_assets.helper.contract_reader import ContractReader

# Import Console Commands Module
from core.modules.contract_cli.contract_commands import ConsoleContractCommands

# Import Handlers of the Console

from core.input.console_input_getter import ConsoleInputGetter
from core.net.network_agent import NetworkAgent

# Import HTML for defining the prompt style
from prompt_toolkit import HTML
from prompt_toolkit.shortcuts import set_title



# Import Console Artifacts
from core.eth_assets.assets_engine import AssetsEngine
from core.eth_assets.contracts import ContractArtifacts
from core.eth_assets.payloads import Payloads
from core.eth_assets.accounts import Accounts
from core.eth_assets.tokens import Tokens
from core.eth_assets.help_artifacts import InformationArtifacts

# Import PromptToolkit Package
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import PromptSession
from prompt_toolkit.shortcuts import yes_no_dialog

# Importing Custom Logger & Logging Modules
from core.logger.custom_logger import CustomLogger, DEBUG0
from logging import INFO
import logging

# Import TypeOfConsole Enum
from core.constants.console_constant import TypeOfConsole

# Import EtherHelper for unifying ether amount quantities
from core.eth_assets.helper.ether_helper import EtherHelper

# Import Console Components
from core.modules.safe_cli.safe_sender import SafeSender
from core.modules.safe_cli.safe_interface import SafeInterface
from core.modules.safe_cli.safe_information import SafeInformation
from core.modules.safe_cli.safe_management import SafeManagement
from core.modules.safe_cli.safe_ether import SafeEther
from core.modules.safe_cli.safe_token import SafeToken
from core.modules.safe_cli.safe_transaction import SafeTransaction
from core.modules.safe_cli.safe_configuration import SafeConfiguration
from core.modules.safe_cli.safe_controller import SafeController

# Import LogMessageFormatter: view_functions
from core.logger.log_message_formatter import LogMessageFormatter


# Import Completer & SyntaxLexer
from core.modules.safe_cli.prompt_components.safe_lexer import SafeLexer
from core.modules.safe_cli.prompt_components.safe_completer import SafeCompleter

class SafeEngine:
    def __init__(self, network_agent, ethereum_assets, safe_address, gnosis_manager):
        self.name = self.__class__.__name__
        self.gnosis_manager = gnosis_manager

        # Configure Logger Here
        self.ethereum_assets = ethereum_assets
        self.safe_address = safe_address

        # Custom Logger Init Configuration: Default Values
        self.logging_lvl = INFO
        self.logger = CustomLogger(self.name, self.logging_lvl)

        # CustomLogger Format Definition: Output Init Configuration
        formatter = logging.Formatter(fmt='%(asctime)s - [ %(levelname)s ]: %(message)s',
                                      datefmt='%I:%M:%S %p')
        detailed_formatter = logging.Formatter(fmt='%(asctime)s - [ %(levelname)s ]: %(message)s',
                                               datefmt='%m/%d/%Y %I:%M:%S %p')

        # Custom Logger File Configuration: File Init Configuration
        file_handler = logging.FileHandler('./log/safe_cli.log', 'w')
        file_handler.setFormatter(detailed_formatter)
        file_handler.setLevel(level=self.logging_lvl)

        # Custom Logger Console Configuration: Console Init Configuration
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level=self.logging_lvl)

        # Custom Logger Console/File Handler Configuration
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # view functions
        self.log_formatter = LogMessageFormatter(self.logger)

        self.network_agent = network_agent
        self.ethereum_client = network_agent.ethereum_client

        self.safe_configuration = SafeConfiguration(self.logger)

        self.safe_interface = SafeInterface(self.logger, self.network_agent,
                                            self.safe_address, self.ethereum_assets)
        self.safe_sender = SafeSender(self.logger, self.safe_interface,
                                      self.network_agent, self.ethereum_assets)

        self.safe_information = SafeInformation(self.logger, self.network_agent,
                                                self.safe_interface, self.safe_sender)

        self.safe_transaction = SafeTransaction(self.logger, self.network_agent,
                                                self.safe_interface, self.safe_sender,
                                                self.safe_configuration)
        self.safe_ether = SafeEther(self.logger, self.safe_interface, self.safe_transaction)

        self.safe_token = SafeToken(self.logger, self.network_agent,
                                    self.safe_interface, self.safe_transaction,
                                    self.safe_configuration, self.ethereum_assets)

        self.safe_management = SafeManagement(self.logger, self.safe_interface,
                                              self.safe_transaction, self.safe_configuration,
                                              self.safe_sender)

        self.safe_prompt_config = {
            'prompt': self._get_prompt_text(affix_stream='safe-cli', stream='Safe (' + safe_address + ')'),
            'lexer': SafeLexer(),
            'completer': SafeCompleter(),
            'style': None
        }

    def _setup_console_init(self, configuration):
        """ Setup Console Safe Configuration

        :param configuration:
        :return:
        """
        if configuration['safe'] is not None:
            if self.network_agent.ethereum_client.w3.isAddress(configuration['safe']):
                try:
                    self.log_formatter.log_entry_message('Entering Safe Console')
                    if configuration['private_key'] is not None:
                        self.logger.debug0(configuration['private_key'])
                        for private_key_owner in configuration['private_key']:
                            self.safe_sender.load_owner(private_key_owner)
                    self.run()
                except Exception as err:
                    self.logger.error('{0}'.format(self.name))
                    self.logger.error(err)

    def run(self):
        """ Run Safe Console
        This function will run the safe console
        :return:
        """
        try:
            # Update gnosis manager active prompt
            self.gnosis_manager.active_prompt = TypeOfConsole.SAFE_CONSOLE
            return PromptSession(completer=self.safe_prompt_config['completer'], lexer=self.safe_prompt_config['lexer'])
        except Exception as err:
            self.logger.error(err)




    def _get_prompt_text(self, affix_stream='', stream=''):
        """ Get Prompt Text
        This function will generate the string that will be shown as the prompt text
        :param affix_stream:
        :param stream:
        :return:
        """
        return HTML('<ansiblue>[ </ansiblue><strong>./%s</strong><ansiblue> ]'
                    '[ </ansiblue><strong>%s</strong><ansiblue> ]: </ansiblue>' % (affix_stream, stream))