#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import EtherHelper
from core.eth_assets.helper.ether_helper import EtherHelper

# Import Log Formatter: Receipts, Headers
from core.logger.log_message_formatter import LogMessageFormatter


# Import Gnosis-Py Modules
from gnosis.safe.safe import Safe

from gnosis.eth.contracts import (
    get_safe_V1_0_0_contract, get_safe_V0_0_1_contract,
)


class SafeInterface:
    """ Console Safe Commands
    This class will perform the command call to the different eth_assets and the class methods
    """
    def __init__(self, logger, network_agent, safe_address):
        self.logger = logger

        # NetworkAgent: ethereum_client
        self.network_agent = network_agent

        # EthereumClient: w3
        self.ethereum_client = network_agent.ethereum_client

        # Safe interface
        self.safe_interface = self._safe_interface_resolver(safe_address)

        # Setup: LogFormatter
        self.log_formatter = LogMessageFormatter(self.logger)

    def _safe_interface_resolver(self, safe_address):
        """ Setup Safe Resolver
        This function based on the retrieve version, it will launch the proper instance for the safe
        :param safe_address:
        :return:
        """
        safe_interface = Safe(safe_address, self.ethereum_client)
        safe_version = safe_interface.retrieve_version()

        if safe_version == '1.1.0':
            self.log_formatter.log_section_left_side('Safe Version 1.1.0 Found')
            return safe_interface.get_contract()
        elif safe_version == '1.0.0':
            self.log_formatter.log_section_left_side('Safe Version 1.0.0 Found')
            return get_safe_V1_0_0_contract(self.ethereum_client.w3, safe_address)
        else:
            self.log_formatter.log_section_left_side('Safe Version 0.0.1 Found')
            return get_safe_V0_0_1_contract(self.ethereum_client.w3, safe_address)
