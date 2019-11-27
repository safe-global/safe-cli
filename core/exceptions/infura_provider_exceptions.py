#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class InfuraProviderError(Exception):
    """ InfuraProviderError

    Raised when the infura Provider is unable to perform proper operations to the EndPoint giving an known error
        :param _provider_name
        :param _err
        :param _trace
        :return Error Exception Message
    """
    def __init__(self, _provider_name, _network, _err, _trace, *args):
        self.name = self.__class__.__name__
        self.provider_name = _provider_name
        self.err = _err
        self.trace = _trace
        self.message = '{0}, in {1} Unable to perform proper operations to the EndPoint: [ {2} ]'.format(self.name, _provider_name, _err)
        super(InfuraProviderError, self).__init__(self.message, _err, _provider_name, *args)


class InfuraProviderFatalException(Exception):
    """ InfuraProviderFatalException

    Raised when the infura Provider is unable to perform proper operations to the EndPoint giving an unknown exception
        :param _provider_name
        :param _err
        :param _trace
        :return Fatal Exception Message
    """
    def __init__(self, _provider_name, _err, _trace, *args):
        self.name = self.__class__.__name__
        self.provider_name = _provider_name
        self.err = _err
        self.trace = _trace
        self.message = '{0}, in {1} Unable to perform proper operations with the EndPoint: [ {2} ]'.format(self.name, _provider_name, _err)
        super(InfuraProviderFatalException, self).__init__(self.message, _err, _provider_name, *args)

