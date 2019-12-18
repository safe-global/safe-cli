#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Log Formatter: Receipts, Headers
from core.logger.log_message_formatter import LogMessageFormatter

# Import Gnosis-Py Modules
from gnosis.safe.safe import Safe

from gnosis.eth.contracts import (
    get_safe_V1_0_0_contract, get_safe_V0_0_1_contract,
)

# Import Console Components
from core.modules.safe_cli.components.safe_sender import SafeSender
from core.modules.safe_cli.components.safe_information import SafeInformation
from core.modules.safe_cli.components.safe_management import SafeManagement
from core.modules.safe_cli.components.safe_ether import SafeEther
from core.modules.safe_cli.components.safe_token import SafeToken
from core.modules.safe_cli.components.safe_transaction import SafeTransaction


class SafeInterface:
    """ Console Safe Commands
    This class will perform the command call to the different eth_assets and the class methods
    """
    def __init__(self, logger, network_agent, safe_address, safe_configuration, ethereum_assets):
        self.logger = logger

        # NetworkAgent: ethereum_client
        self.network_agent = network_agent

        # EthereumClient: w3
        self.ethereum_client = network_agent.ethereum_client

        # Safe Interface
        self.ethereum_assets = ethereum_assets

        # Setup: LogFormatter
        self.log_formatter = LogMessageFormatter(self.logger)

        # SafeInterface:
        self.safe_operator, self.safe_instance = self._safe_interface_resolver(safe_address)
        # SafeConfiguration: configuration
        self.safe_configuration = safe_configuration
        # SafeSender: sender
        self.safe_sender = SafeSender(self.logger, self.network_agent, self, self.ethereum_assets)
        # SafeInformation: view_functions()
        self.safe_information = SafeInformation(self.logger, self.network_agent, self, self.safe_sender)
        # SafeTransaction: safe_ether, safe_token, safe_management
        self.safe_transaction = SafeTransaction(self.logger, self.network_agent, self, self.safe_configuration)
        # SafeEther:
        self.safe_ether = SafeEther(self.logger, self.network_agent, self, self.safe_configuration)
        # SafeToken:
        self.safe_token = SafeToken(self.logger, self.network_agent, self, self.safe_configuration, self.ethereum_assets)
        # SafeManagement:
        self.safe_management = SafeManagement(self.logger, self, self.ethereum_assets)

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
            return safe_interface, safe_interface.get_contract()
        elif safe_version == '1.0.0':
            self.log_formatter.log_section_left_side('Safe Version 1.0.0 Found')
            return safe_interface, get_safe_V1_0_0_contract(self.ethereum_client.w3, safe_address)
        else:
            self.log_formatter.log_section_left_side('Safe Version 0.0.1 Found')
            return safe_interface, get_safe_V0_0_1_contract(self.ethereum_client.w3, safe_address)
