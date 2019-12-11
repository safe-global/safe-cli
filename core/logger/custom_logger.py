#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Import Logging Packa
from logging import getLoggerClass, addLevelName, NOTSET

# Import Custom Logging Level Constants
from core.logger.constants.custom_verbose_levels import VERBOSE, DEBUG0, FATAL


class CustomLogger(getLoggerClass()):
    """ CustomLogger

     Custom Logging defines additional levels of logging for the logging package

            :param _name
            :param _level
    """
    def __init__(self, _name, _level=NOTSET):
        super().__init__(_name, _level)
        addLevelName(VERBOSE, 'VERBOSE')
        addLevelName(DEBUG0, 'DEBUG0')
        addLevelName(FATAL, 'FATAL')

    def verbose(self, _msg, *args, **kwargs):
        """ Verbose

        Verbose logging message it's thrown in case we enable verbose output of the process.

            :param _msg:
            :param args:
            :param kwargs:
            :return: verbose lvl logging message
        """
        if self.isEnabledFor(VERBOSE):
            self._log(VERBOSE, _msg, args, **kwargs)

    def debug0(self, _msg, *args, **kwargs):
        """ Debug0

        Debug0 logging message it's thrown in case we need a less verbose output of the process, but still want to
        perform debugging.

            :param _msg:
            :param args:
            :param kwargs:
            :return: debug0 lvl logging message
        """
        if self.isEnabledFor(DEBUG0):
            self._log(DEBUG0, _msg, args, **kwargs)

    def fatal(self, _msg, *args, **kwargs):
        """ Fatal

        Fatal logging message it's thrown in case an unexpected Exception it's launched by the application.

            :param _msg:
            :param args:
            :param kwargs:
            :return: fatal lvl logging message
        """
        if self.isEnabledFor(FATAL):
            self._log(DEBUG0, _msg, args, **kwargs)
