#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Contract Reader Module

# Import Console Commands Module

# Import Handlers of the Console
from core.input.console_input_getter import ConsoleInputGetter
from core.net.network_agent import NetworkAgent

# Import HTML for defining the prompt style
from prompt_toolkit import HTML

# Import Console Artifacts
from core.eth_assets.ethereum_assets import EthereumAssets
from core.eth_assets.components.contracts import Contracts
from core.eth_assets.components.payloads import Payloads
from core.eth_assets.components.accounts import Accounts
from core.eth_assets.components.tokens import Tokens

from core.eth_assets.help_artifacts import InformationArtifacts

# Importing Custom Logger & Logging Modules
from core.logger.custom_logger import CustomLogger, DEBUG0
from logging import INFO
import logging

# Import TypeOfConsole Enum
from core.constants.console_constant import TypeOfConsole

# Import LogFileManager & LogMessageFormatter
from core.logger.log_file_manager import LogFileManager
from core.logger.log_message_formatter import LogMessageFormatter

# Import GnosisEngine, SafeEngine ContractEngine: run()
from core.modules.gnosis_cli.gnosis_engine import GnosisEngine
from core.modules.safe_cli.safe_engine import SafeEngine
from core.modules.contract_cli.contract_engine import ContractEngine

# Gnosis Manager Log
GNOSIS_MANAGER_LOG = './log/gnosis_manager.log'


class GnosisManager:
    """ Gnosis Console Engine
    This class will perform the core activities for the modules, access to ethereum_assets, and launch capability for
    safe-cli via "loadSafe --address=0x0*40" or contract-cli "loadContract --name=ContractName"
    :param configuration:
    """
    def __init__(self, configuration):
        self.name = self.__class__.__name__
        self.prompt_text = configuration['name']
        # Setup the console files logs if does not exists
        LogFileManager().create_log_files()

        # TypeOfConsole:
        self.active_prompt = TypeOfConsole.GNOSIS_CONSOLE

        # GnosisEngine:
        self.gnosis_engine = None
        # SafeEngine:
        self.safe_engine = None
        # ContractEngine:
        self.contract_engine = None

        # Custom Logger: init
        self.logging_lvl = INFO
        if configuration['debug']:
            self.logging_lvl = DEBUG0

        self.logger = CustomLogger(self.name, self.logging_lvl)
        self._setup_logger()

        # InformationArtifacts: view_disclaimer()
        self.console_information = InformationArtifacts(self.logger)
        self.console_information.command_view_disclaimer()

        # Setup NetworkAgent: setup ethereum network provider
        self.network_agent = NetworkAgent(self.logger, configuration['network'], configuration['api_key'])
        # EthereumClient:
        self.ethereum_client = self.network_agent.ethereum_client

        # Setup: Log Formatter
        self.log_formatter = LogMessageFormatter(self.logger)

        # Setup Console Input Getter
        self.console_getter = ConsoleInputGetter(self.logger)

        # Accounts:
        self.accounts = Accounts(self.logger, self.ethereum_client)
        # Tokens:
        self.tokens = Tokens(self.logger, self.ethereum_client)
        # Payloads:
        self.payloads = Payloads(self.logger)
        # Contracts:
        self.contracts = Contracts(self.logger)

        # Setup EthereumAssets: shared object
        self.ethereum_assets = EthereumAssets(self.logger, self.accounts, self.payloads, self.tokens, self.contracts)

        # Engines: init
        self._init_modules()

    def _init_modules(self):
        """ Init_Modules
        This function will init the modules so it can be passed to the gnosis_engine to launch later
        """
        # SafeEngine: init
        self.safe_engine = SafeEngine(self.network_agent, self.ethereum_assets, self)

        # ContractEngine: init
        self.contract_engine = ContractEngine(self.network_agent, self.ethereum_assets, self)

        # Engine Modules
        engine_modules = {
            'safe': self.safe_engine,
            'contract': self.contract_engine
        }

        # GnosisEngine: init
        self.gnosis_engine = GnosisEngine(self.network_agent, self.ethereum_assets, self, engine_modules)

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
        file_handler = logging.FileHandler(GNOSIS_MANAGER_LOG, 'w')
        file_handler.setFormatter(detailed_formatter)
        file_handler.setLevel(level=self.logging_lvl)

        # CustomLogger: Console Configuration: Console Init Configuration
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level=self.logging_lvl)

        # CustomLogger: Console/File Handler Configuration
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def start(self):
        """ Start
        This function will start the gnosis_manager
        """
        try:
            self.gnosis_engine.run()
        except Exception as err:
            self.logger.error(err)
