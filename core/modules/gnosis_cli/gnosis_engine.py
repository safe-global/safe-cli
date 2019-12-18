#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import HTML for defining the prompt style
from prompt_toolkit import HTML

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

# Import Completer & SyntaxLexer
from core.modules.safe_cli.prompt_components.safe_lexer import SafeLexer
from core.modules.safe_cli.prompt_components.safe_completer import SafeCompleter

# Import LogMessageFormatter: view_functions
from core.logger.log_message_formatter import LogMessageFormatter

# Import Completer & SyntaxLexer
from core.modules.safe_cli.prompt_components.safe_lexer import SafeLexer
from core.modules.safe_cli.prompt_components.safe_completer import SafeCompleter

from core.input.console_input_getter import ConsoleInputGetter
from core.modules.gnosis_cli.gnosis_controller import GnosisController

EXIT_DIALOG_TITLE = 'Exiting ({0})'
EXIT_DIALOG_MSG = 'All data regarding accounts, tokens, contracts & payloads will be lost, ' \
                  'Are you sure you want to exit the {0}?'
SAFE_ENGINE_LOG = './log/safe_cli.log'


class GnosisEngine:
    def __init__(self, network_agent, ethereum_assets, gnosis_manager, engine_modules):
        self.name = self.__class__.__name__

        self.gnosis_manager = gnosis_manager
        self.gnosis_controller = None
        self.network_agent = network_agent
        self.ethereum_client = network_agent.ethereum_client

        self.ethereum_assests = ethereum_assets

        # Custom Logger Init Configuration: Default Values
        self.logging_lvl = INFO
        self.logger = CustomLogger(self.name, self.logging_lvl)
        self._setup_logger()

        self.getter = ConsoleInputGetter(self.logger)

        self.safe_engine = engine_modules['safe']
        self.contract_engine = engine_modules['contract']
        # self.relay_engine = engine_modules['relay']

    def _setup_logger(self):
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

    def run(self):
        """ Run
        This function will launch the gnosis-cli
        """
        try:
            prompt_text = self.get_prompt_text(affix_stream='gnosis-cli')
            prompt_session = PromptSession(completer=SafeCompleter(), lexer=SafeLexer())
            self.gnosis_controller = GnosisController(self.logger, self.network_agent, self.ethereum_assests, self)
            while True:
                try:
                    stream = prompt_session.prompt(message=prompt_text)
                    desired_parsed_item_list, priority_group, command_argument, argument_list = \
                        self.getter.get_gnosis_input_command_argument(stream)

                    self.gnosis_controller.operate(desired_parsed_item_list, priority_group,
                                                   command_argument, argument_list)
                    self._exit(command_argument, argument_list)
                except KeyboardInterrupt:
                    # remark: Control-C pressed. Try again.
                    continue
                except EOFError:
                    # remark: Control-D pressed.
                    break
        except Exception as err:
            self.logger.error(err)

    def _exit(self, command_argument, argument_list):
        _, _, _, _now = self.getter.get_input_affix_arguments(argument_list)
        if (command_argument == 'close') or (command_argument == 'quit') or (command_argument == 'exit'):
            if not _now:
                result = yes_no_dialog(title=EXIT_DIALOG_TITLE.format(TypeOfConsole.GNOSIS_CONSOLE.value),
                                       text=EXIT_DIALOG_MSG.format(TypeOfConsole.GNOSIS_CONSOLE.value)).run()
                if result:
                    raise EOFError
            elif _now:
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
