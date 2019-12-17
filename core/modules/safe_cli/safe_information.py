#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import LogMessageFormatter: view_functions
from core.logger.log_message_formatter import LogMessageFormatter

# Import Constants: view_fall_back_handler
from core.constants.console_constant import NULL_ADDRESS

# Import HexBytes Module: view_code in hex
from hexbytes import HexBytes


class SafeInformation:
    def __init__(self, logger, network_agent,  safe_interface, safe_sender):
        self.name = self.__class__.__name__
        self.logger = logger

        # SafeInterface:
        self.safe_interface = safe_interface

        # SafeSender: is_sender()
        self.safe_sender = safe_sender

        # NetworkAgent: ethereum_client, w3
        self.network_agent = network_agent

        # EthereumClient: get_balance()
        self.ethereum_client = network_agent.ethereum_client

        # LogFormatter: view_functions()
        self.log_formatter = LogMessageFormatter(self.logger)

    def preview_threshold_owners(self):
        self.view_safe_threshold()
        self.view_safe_owners()

    def preview_version_change(self):
        self.view_master_copy()
        self.view_safe_version()

    def view_information(self):
        """ Command Safe Information
        This function will retrieve and show any pertinent information regarding the current safe
        :return:
        """
        self.log_formatter.log_banner_header('Safe Information')
        self.view_safe_owners()
        # self.command_view_balance()
        self.view_safe_threshold()

        self.log_formatter.log_section_left_side('Safe General Information')
        self.view_safe_name(block_style=False)
        self.view_master_copy(block_style=False)
        self.view_safe_version(block_style=False)
        self.view_proxy_copy(block_style=False)
        self.view_fallback_handler(block_style=False)
        self.view_safe_nonce(block_style=False)

    def view_fallback_handler(self, block_style=True):
        """ Command Fallback Handler
        This function will retrieve and show the fallback handler address value of the safe
        :param block_style:
        :return:
        """
        if block_style:
            self.log_formatter.log_section_left_side('Safe Fallback Handler')
        self.log_formatter.log_data(' (#) Fallback Handler: {0}', NULL_ADDRESS)
        if block_style:
            self.log_formatter.log_dash_splitter()

    def view_proxy_copy(self, block_style=True):
        """ Command Proxy
        This function will retrieve and show the proxy address value of the safe
        :param block_style:
        :return:
        """
        if block_style:
            self.log_formatter.log_section_left_side('Safe Proxy')
        self.log_formatter.log_data(' (#) ProxyCopy: {0}', self.safe_interface.address)
        if block_style:
            self.log_formatter.log_dash_splitter()

    def view_master_copy(self, block_style=True):
        """ Command Master Copy
        This function will retrieve and show the master copy address value of the safe
        :param block_style:
        :return:
        """
        if block_style:
            self.log_formatter.log_section_left_side('Safe MasterCopy')
        self.log_formatter.log_data(' (#) MasterCopy: {0}', self.safe_interface.retrieve_master_copy_address())
        if block_style:
            self.log_formatter.log_dash_splitter()

    def view_safe_nonce(self, block_style=True):
        """ Command Safe Nonce
        This function will retrieve and show the nonce value of the safe
        :param block_style:
        :return:
        """
        if block_style:
            self.log_formatter.log_section_left_side('Safe Nonce')
        self.log_formatter.log_data(' (#) Nonce: {0} ', self.safe_interface.retrieve_nonce())
        if block_style:
            self.log_formatter.log_dash_splitter()

    def view_safe_code(self, block_style=True):
        """ Command Safe Code
        This function will retrieve and show the code value of the safe
        :param block_style:
        :return: code of the safe
        """
        if block_style:
            self.log_formatter.log_section_left_side('Safe Code')
        self.log_formatter.log_data(' (#) Code: {0} ', HexBytes(self.safe_interface.retrieve_code()).hex())
        if block_style:
            self.log_formatter.log_dash_splitter()

    def view_safe_version(self, block_style=True):
        """ Command Safe Version
        This function will retrieve and show the VERSION value of the safe
        :param block_style:
        :return: version of the safe
        """
        if block_style:
            self.log_formatter.log_section_left_side('Safe Version')
        self.log_formatter.log_data(' (#) MasterCopy Version: {0} ', self.safe_interface.retrieve_version())
        if block_style:
            self.log_formatter.log_dash_splitter()

    def view_safe_name(self, block_style=True):
        """ Command Safe Name
        This function will retrieve and show the NAME value of the safe
        :param block_style:
        :return:
        """
        if block_style:
            self.log_formatter.log_section_left_side('Safe Name')
        self.log_formatter.log_data(' (#) MasterCopy Name: {0} ', self.safe_interface.functions.NAME().call())
        if block_style:
            self.log_formatter.log_dash_splitter()

    def view_safe_threshold(self, block_style=True):
        """ Command Safe Get Threshold
        This function will retrieve and show the threshold of the safe
        :param block_style:
        :return:
        """
        if block_style:
            self.log_formatter.log_section_left_side('Safe Threshold')
        self.log_formatter.log_data(' (#) Threshold: {0} ', self.safe_interface.functions.getThreshold().call())
        if block_style:
            self.log_formatter.log_dash_splitter()

    def check_safe_owner(self, owner_address, block_style=True):
        """ Command Safe isOwner
        This function will check if any given owner is part of the safe owners
        :param owner_address:
        :param block_style:
        :return: True if it's a owner, otherwise False
        """
        if block_style:
            self.log_formatter.log_section_left_side('Safe Owners')

        information_data = ' (#) Owner with Address: {0} | isOwner: {1} '.format(
            owner_address, self.safe_interface.retrieve_is_owner(owner_address))
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        if block_style:
            self.log_formatter.log_dash_splitter()

    def check_safe_are_owners(self, owners_list):
        """ Command Safe areOwners
        This function will check if a list of any given owners is part of the safe owners
        :param owners_list:
        :return: True if it's a owner, otherwise False
        """
        self.log_formatter.log_section_left_side('Safe Owners List')
        for owner_address in owners_list:
            self.check_safe_owner(owner_address, block_style=False)
        self.log_formatter.log_dash_splitter()
