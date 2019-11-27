#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class GnosisConsoleInputError(Exception):
    """ GnosisConsoleInputError

    Raised when the Gnosis Console Input is unable to perform proper operations giving an known error
        :param _gnosis_console
        :param _err
        :param _trace
        :return Error Exception Message
    """
    def __init__(self, _gnosis_console, err, _trace, *args):
        self.name = self.__class__.__name__
        self.gnosis_console = _gnosis_console
        self.err = err
        self.trace = _trace
        self.message = '{0}, in  {1} Unable to perform proper operations: [ {2} ]'.format(self.name, _gnosis_console, err)
        super(GnosisConsoleInputError, self).__init__(self.message, err, _gnosis_console, *args)


class GnosisConsoleInputFatalException(Exception):
    """ GnosisConsoleInputFatalException

    Raised when the Network Agent is unable to perform proper operations giving an unknown exception
        :param _gnosis_console
        :param _err
        :param _trace
        :return Fatal Exception Message
    """
    def __init__(self, _gnosis_console, _err, _trace, *args):
        self.name = self.__class__.__name__
        self.gnosis_console = _gnosis_console
        self.err = _err
        self.trace = _trace
        self.message = '{0}, in  {1} Unable to perform proper operations: [ {2} ]'.format(self.name, _gnosis_console, _err)
        super(GnosisConsoleInputFatalException, self).__init__(self.message, _err, _gnosis_console, *args)
