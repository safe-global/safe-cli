#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Import Prompt Tool Packages
from prompt_toolkit.lexers import Lexer

# Import Regex Expresions from Contract Console Constants Package
from core.contract.constants.contract_constants import (
    console_quit_commands, console_method_names, address_param, uint_param, bytecode_param,
    console_commands, console_contract_execution_commands, console_help_commands, console_known_networks, ether_params
)

# Import Re Package
import re

# Color Constants
BASIC_TEXT = 'LightGray'
BASE_HIGHLIGHT_COLOR = 'MidnightBlue'
PARAM_COLOR = 'SlateBlue'
EXIT_COLOR = 'Tomato'
CONTRACT_METHODS_COLOR = 'DarkOrange'
CONSOLE_COMMANDS = 'SaddleBrown'
KNOWN_NETWORKS_COLOR = 'DarkSalmon'
INFORMATION_COLOR = 'LightYellow'

class SyntaxLexer(Lexer):
    """ Syntax Lexer

    """
    @staticmethod
    def __is_valid_argument(regular_expresion, stream):
        """ Is Valid Argument
        This function will try to retrieve a piece of input stream, if group(0) does not raise AttributeError it will
        return True, otherwise False

        :param regular_expresion:
        :param stream:
        :return:
        """
        try:
            re.search(regular_expresion, stream).group(0)
            return True
        except AttributeError:
            return False

    def lex_document(self, document):
        """ Lex Document
        This function will change the color of the document text to fit the proper syntax highlight
        :param document: stream input provided by the console user
        :return: output colored syntax
        """
        # remark: Color Palette
        # colors = list(sorted(NAMED_COLORS, key=NAMED_COLORS.get))

        def get_line(lineno):
            aux_list = []
            for index, word in enumerate(document.lines[lineno].split(' ')):
                current_color = BASIC_TEXT

                if self.__is_valid_argument(console_method_names, word) \
                        or self.__is_valid_argument(console_commands, word):
                    current_color = CONTRACT_METHODS_COLOR

                elif self.__is_valid_argument(console_help_commands, word):
                    current_color = INFORMATION_COLOR

                elif self.__is_valid_argument(console_known_networks, word):
                    current_color = KNOWN_NETWORKS_COLOR

                elif self.__is_valid_argument(address_param, word) \
                        or self.__is_valid_argument(uint_param, word) \
                        or self.__is_valid_argument('--bytecode=', word) \
                        or self.__is_valid_argument('--alias=', word) \
                        or self.__is_valid_argument('--api_key=', word) \
                        or self.__is_valid_argument(ether_params, word) \
                        or self.__is_valid_argument('--private_key=', word):
                    current_color = PARAM_COLOR

                elif self.__is_valid_argument(console_contract_execution_commands, word):
                    current_color = CONSOLE_COMMANDS

                elif self.__is_valid_argument(console_quit_commands, word):
                    current_color = EXIT_COLOR
                aux_list.append((current_color, word + ' '))
            return aux_list
        return get_line
