#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class SafeSenderNotEnoughSigners(Exception):
    """ SafeSenderNotEnoughSigners
    Raised when the SafeSender is unable to perform proper operations while trying to remove a sender
    :param console_type
    :param _err
    :param _trace
    :return SafeSenderNotFound Exception Message
    """
    def __init__(self, console_type, _err, _trace, *args):
        self.name = self.__class__.__name__
        self.console_type = console_type
        self.err = _err
        self.trace = _trace
        self.message = '{0}, in  {1} Unable to perform proper operations: [ {2} ]'.format(self.name, console_type, _err)
        super(SafeSenderNotEnoughSigners, self).__init__(self.message, _err, console_type, *args)


class SafeSenderNotFound(Exception):
    """ SafeSenderNotFound
    Raised when the SafeSender is unable to perform proper operations while trying to remove a sender
    :param console_type
    :param _err
    :param _trace
    :return SafeSenderNotFound Exception Message
    """
    def __init__(self, console_type, _err, _trace, *args):
        self.name = self.__class__.__name__
        self.console_type = console_type
        self.err = _err
        self.trace = _trace
        self.message = '{0}, in  {1} Unable to perform proper operations: [ {2} ]'.format(self.name, console_type, _err)
        super(SafeSenderNotFound, self).__init__(self.message, _err, console_type, *args)


class SafeSenderAlreadyLoaded(Exception):
    """ InvalidSafeSenderPrivateKey
    Raised when the SafeSender is unable to perform proper operations while trying to find a address match in the owners
    :param console_type
    :param _err
    :param _trace
    :return Fatal Exception Message
    """
    def __init__(self, console_type, _err, _trace, *args):
        self.name = self.__class__.__name__
        self.console_type = console_type
        self.err = _err
        self.trace = _trace
        self.message = '{0}, in  {1} Unable to perform proper operations: [ {2} ]'.format(self.name, console_type, _err)
        super(SafeSenderAlreadyLoaded, self).__init__(self.message, _err, console_type, *args)
