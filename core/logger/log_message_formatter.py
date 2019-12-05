#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from core.constants.console_constant import STRING_DASHES


class LogMessageFormatter:
    """ Logging Message Formatter

    """
    def __init__(self, logger):
        self.name = self.__class__.__name__
        self.logger = logger

    def log_error_footer(self, msg='Error.'):
        message = self.header_block(msg, '-')
        self.logger.error(message)

    def log_header(self, msg='Success.'):
        message = self.header_block(msg, '-')
        self.logger.info(message)

    def log_banner_header(self, msg='Head Banner'):
        message = self.header_block(msg, '=')
        self.logger.info(' ' + message)

    def log_entry_message(self, msg='Entry Message'):
        self.logger.info(' ' + STRING_DASHES)
        self.logger.info('|{0}|'.format(self.header_block(msg=msg, filler=' ')))
        self.logger.info(' ' + STRING_DASHES)

    def log_console_information(self, msg='Informational Title', information=['Some Information']):
        # message = self.header_block(msg, '-')
        # self.logger.info(message)
        # for information_item in information:
        #     information_message = '| {0}{1}|'.format(,len(information_message))
        #     self.logger.info()
        # self.logger.info(STRING_DASHES)
        return

    @staticmethod
    def header_block(msg, filler=' ', str_count=140):
        """ Format Header
        This function will perform formatting a header like message being prompted in the console
        :return:
        """
        text = ':[ {0} ]:'.format(msg.title())
        return text.center(str_count, filler)
