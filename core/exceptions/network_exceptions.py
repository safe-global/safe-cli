#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class NetworkAgentSocketError(Exception):
    """ NetworkAgentSocketError

    Raised when the Network Agent is unable to perform proper operations to the EndPoint giving an known error
        :param _network_agent
        :param _err
        :param _trace
        :return Error Exception Message
    """
    def __init__(self, _network_agent, err, _trace, *args):
        self.name = self.__class__.__name__
        self.network_agent = _network_agent
        self.err = err
        self.trace = _trace
        self.message = '{0}, in  {1} Unable to perform proper operations to the EndPoint: [ {2} ]'.format(self.name, _network_agent, err)
        super(NetworkAgentSocketError, self).__init__(self.message, err, _network_agent, *args)


class NetworkAgentFatalException(Exception):
    """ NetworkAgentFaltaException

    Raised when the Network Agent is unable to perform proper operations to the EndPoint giving an unknown exception
        :param _network_agent
        :param _err
        :param _trace
        :return Fatal Exception Message
    """
    def __init__(self, _network_agent, _err, _trace, *args):
        self.name = self.__class__.__name__
        self.network_agent = _network_agent
        self.err = _err
        self.trace = _trace
        self.message = '{0}, in  {1} Unable to perform proper operations with the EndPoint: [ {2} ]'.format(self.name, _network_agent, _err)
        super(NetworkAgentFatalException, self).__init__(self.message, _err, _network_agent, *args)

