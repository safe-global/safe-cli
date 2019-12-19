#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import HTML for defining the prompt style
from prompt_toolkit import HTML

# Import Console Artifacts

# Import PromptToolkit Package
from prompt_toolkit import PromptSession
from prompt_toolkit.shortcuts import yes_no_dialog

# Importing Custom Logger & Logging Modules
from core.logger.custom_logger import CustomLogger, DEBUG0
from logging import INFO
import logging

# Import TypeOfConsole Enum
from core.constants.console_constant import TypeOfConsole

# Import EtherHelper for unifying ether amount quantities

# Import Console Components
from core.modules.safe_cli.components.safe_interface import SafeInterface
from core.modules.safe_cli.components.safe_configuration import SafeConfiguration
from core.modules.safe_cli.safe_controller import SafeController

# Import LogMessageFormatter: view_functions
from core.logger.log_message_formatter import LogMessageFormatter

# Import Completer & SyntaxLexer
from core.modules.safe_cli.prompt_components.safe_lexer import SafeLexer
from core.modules.safe_cli.prompt_components.safe_completer import SafeCompleter

from core.input.console_input_getter import ConsoleInputGetter

EXIT_DIALOG_TITLE = 'Exiting Safe ({0})'
EXIT_DIALOG_MSG = 'All data regarding loaded owners & sender configuration will be lost, ' \
                  'Are you sure you want to exit the {0}?'
SAFE_ENGINE_LOG = './log/safe_cli.log'


class SafeEngine:
    """ SafeEngine
    This class will run the safe prompt and interact with components via command line
    :param network_agent:
    :param ethereum_assets:
    :param gnosis_manager:
    """
    def __init__(self, network_agent, ethereum_assets, gnosis_manager):
        self.name = self.__class__.__name__

        # GnosisManager: update state
        self.gnosis_manager = gnosis_manager

        self.safe_interface = None
        self.safe_controller = None
        self.safe_address = None

        # Configure Logger Here
        self.ethereum_assets = ethereum_assets

        # Custom Logger Init Configuration: Default Values
        self.logging_lvl = DEBUG0
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

    # def _setup_console_init(self, configuration):
    #     """ Setup Console Safe Configuration
    #
    #     :param configuration:
    #     :return:
    #     """
    #     if configuration['safe'] is not None:
    #         if self.network_agent.ethereum_client.w3.isAddress(configuration['safe']):
    #             try:
    #                 self.log_formatter.log_entry_message('Entering Safe Console')
    #                 if configuration['private_key'] is not None:
    #                     self.logger.debug0(configuration['private_key'])
    #                     for private_key_owner in configuration['private_key']:
    #                         self.safe_sender.load_owner(private_key_owner)
    #                 # self.run()
    #             except Exception as err:
    #                 self.logger.error('{0}'.format(self.name))
    #                 self.logger.error(err)

    def run(self, safe_address):
        """ Run Safe Console
        This function will run the safe console
        :return:
        """
        try:
            self.safe_interface = SafeInterface(self.logger, self.network_agent,
                                                safe_address, self.safe_configuration,
                                                self.ethereum_assets)
            self.safe_address = self.safe_interface.safe_instance.address
            prompt_toolbar = self.safe_interface.safe_sender.get_toolbar_text()
            prompt_refresh_interval = 0.5
            prompt_text = self.get_prompt_text(affix_stream='safe-cli', stream='Safe (' + self.safe_address + ')')
            prompt_session = PromptSession(completer=SafeCompleter(), lexer=SafeLexer())
            self.gnosis_manager.active_prompt = TypeOfConsole.SAFE_CONSOLE
            self.safe_controller = SafeController(self.logger, self.network_agent,
                                                  self.safe_interface, self.ethereum_assets)
            while True:
                try:
                    stream = prompt_session.prompt(message=prompt_text,
                                                   bottom_toolbar=prompt_toolbar,
                                                   refresh_interval=prompt_refresh_interval)

                    desired_parsed_item_list, priority_group, command_argument, argument_list = \
                        self.getter.get_gnosis_input_command_argument(stream)
                    self.safe_controller.operate(desired_parsed_item_list, priority_group,
                                                 command_argument, argument_list)

                    self._exit(command_argument, argument_list)
                except KeyboardInterrupt:
                    # remark: Control-C pressed. Try again.
                    continue
                except EOFError:
                    self.gnosis_manager.active_prompt = TypeOfConsole.GNOSIS_CONSOLE
                    # remark: Control-D pressed.
                    break
        except Exception as err:
            self.logger.error(err)

    def _exit(self, command_argument, argument_list):
        """ _Exit
        This function will exit the current prompt
        :param command_argument:
        :param argument_list:
        :return:
        """
        _, _, _, _now = self.getter.get_input_affix_arguments(argument_list)
        if (command_argument == 'close') or (command_argument == 'quit') or (command_argument == 'exit'):
            if not _now:
                result = yes_no_dialog(title=EXIT_DIALOG_TITLE.format(self.safe_address),
                                       text=EXIT_DIALOG_MSG.format(TypeOfConsole.SAFE_CONSOLE.value)).run()
                if result:
                    self.active_session = TypeOfConsole.GNOSIS_CONSOLE
                    raise EOFError
            elif _now:
                self.active_session = TypeOfConsole.GNOSIS_CONSOLE
                raise EOFError

    @staticmethod
    def get_prompt_text(affix_stream='', stream=''):
        """ Get Prompt Text
        This function will generate the string that will be shown as the prompt text
        :param affix_stream:
        :param stream:
        :return:
        """
        return HTML('<ansiblue>[ </ansiblue><strong>./%s</strong><ansiblue> ]'
                    '[ </ansiblue><strong>%s</strong><ansiblue> ]: </ansiblue>' % (affix_stream, stream))
