#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Importing Custom Logger & Logging Modules
from core.logger.custom_logger import CustomLogger
from logging import INFO
import logging

# Import Socket Exceptions
from core.utils.net.exceptions import NetworkAgentFatalException

# Import Socket Module
import socket

class NetworkAgent:
    """ Network Agent

    Code Reference: https://stackoverflow.com/questions/3764291/checking-network-connection
    This class will establish the current state of the connectivity to internet for the system in case it's needed.
    """
    def __init__(self, logging_lvl=INFO):
        self.name = self.__class__.__name__
        self.logger = CustomLogger(self.name, logging_lvl)

        # CustomLogger Format Definition
        formatter = logging.Formatter(fmt='%(asctime)s - [%(levelname)s]: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

        # Custom Logger File Configuration: File Init Configuration
        file_handler = logging.FileHandler('./log/network_agent.log', 'w')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level=logging_lvl)

        # Custom Logger Console Configuration: Console Init Configuration
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level=logging_lvl)

        # Custom Logger Console/File Handler Configuration
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self.address = '8.8.8.8'
        self.port = 53
        self.timeout = 3

    def network_status(self):
        """ Network Status

        This Function will check the availability of the network connection
            :return True if there is internet connectivity otherwise False
        """
        try:
            socket.setdefaulttimeout(self.timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self.address, self.port))
            self.logger.info('{0}: '.format(self.name))
            return True
        except socket.error:
            return False
        except Exception as err:
            # Empty param should be trace for further debugging in case it's needed
            self.logger.fatal('{0}: {1}'.format(self.name, err))
            raise NetworkAgentFatalException(self.name, err, '')
