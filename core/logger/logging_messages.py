#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from core.constants.console_constant import STRING_DASHES


class LoggingMessagesFormatter:
    """ Logging Message Formatter

    """
    def __init__(self, logger):
        self.name = self.__class__.__name__
        self.logger = logger

    def log_error_footer(self, msg='Error.'):
        self.logger.error(self.format_header(msg, '-'))

    def log_footer(self, msg='Success.'):
        self.logger.debug0(self.format_header(msg, '-'))

    def log_banner(self, msg='Head Banner'):
        self.logger.debug0(self.format_header(msg, '='))

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
