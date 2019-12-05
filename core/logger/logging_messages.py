#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from core.constants.console_constant import STRING_DASHES


class LoggingMessagesFormatter:
    """ Logging Message Formatter

    """
    def __init__(self):
        self.name = self.__class__.__name__

    def log_error_footer(self, msg='Error.'):
        return self.format_header(msg, '-')

    def log_success_footer(self, msg='Success.'):
        return self.format_header(msg, '-')

    def log_banner(self, msg='Head Banner'):
        return self.format_header(msg, '=')

    @staticmethod
    def format_header(msg, filler=' '):
        """ Format Header
        This function will perform formatting a header like message being prompted in the console
        :return:
        """
        text = ':[ {0} ]:'.format(msg.title())
        return text.center(140, filler)


    def format_error_message(self):
        """ Format Error Messages
        This function will perform formatting a error like message being prompted in the console
        :return:
        """
        return

    def format_warn_message(self):
        """
        This function will perform formatting a warn like message being prompted in the console
        :return:
        """
        return

    def format_success_message(self):
        return

    