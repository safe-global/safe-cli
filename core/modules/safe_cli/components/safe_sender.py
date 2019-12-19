#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import HexBytes Module: Signatures
from hexbytes import HexBytes

# Exceptions: _add, _remove operations
from core.modules.safe_cli.exceptions.safe_sender_exceptions import SafeSenderNotFound, SafeSenderAlreadyLoaded, SafeSenderNotEnoughSigners

# Import LogMessageFormatter: view_functions()
from core.logger.log_message_formatter import LogMessageFormatter

# Import HTML for defining the prompt style
from prompt_toolkit import HTML


# Import EtherHelper
from core.eth_assets.helper.ether_helper import EtherHelper

# Constants
MARK = 'X'
UN_MARK = ' '


class SafeSender:
    """ SafeSender
    This class will perform the logic needed to manage the main sender for the safe-cli operations
    :param logger:
    :param network_agent:
    :param safe_interface:
    :param ethereum_assets:
    """
    def __init__(self, logger, network_agent, safe_interface, ethereum_assets):
        self.name = self.__class__.__name__
        self.logger = logger

        # SafeInterface:
        self.safe_interface = safe_interface
        # SafeInterface: safe_instance
        self.safe_instance = self.safe_interface.safe_instance
        # SafeInterface: safe class gnosis-py
        self.safe_operator = self.safe_interface.safe_operator

        # Sender list
        self.sender_account_list = []

        # Current sender
        self.sender_private_key = None
        self.sender_address = None

        # NetworkAgent: ethereum_client
        self.network_agent = network_agent

        # EthereumClient: get_balance()
        self.ethereum_client = network_agent.ethereum_client

        # Accounts: get_local_account()
        self.accounts = ethereum_assets.accounts

        # LogFormatter: view_functions()
        self.log_formatter = LogMessageFormatter(self.logger)

        # EtherHelper: balance with ether units
        self.ether_helper = EtherHelper(self.logger, self.ethereum_client)

    def is_sender(self, sender_address):
        """ Is_Sender
        This function wil return MARK if current address
        :param sender_address:
        :return: If True MARK else UN_MARK
        """
        if sender_address == self.sender_address:
            return MARK
        return UN_MARK

    def is_sender_loaded(self, sender_address):
        """ Is_Sender_Loaded
        This function will return MARK if current address within the sender_account_list
        :param sender_address:
        :return: If True MARK else UN_MARK
        """
        for sender in self.sender_account_list:
            if sender_address == sender.address:
                return MARK
        return UN_MARK

    # Just Show from here, mark loaded ones
    def view_safe_owners(self):
        """ Command Safe Get Owners
        This function will retrieve and show the get owners of the safe
        :return:
        """
        self.log_formatter.log_section_left_side('Safe Owner Data')
        for owner_index, owner in enumerate(self.safe_instance.functions.getOwners().call()):
            information_data = ' (#) Owner {0} | Address: {1} | Sender: [{2}] | Balance: {3} '.format(
                owner_index, owner, self.is_sender(owner), self.ethereum_client.w3.eth.getBalance(owner))
            self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.log_formatter.log_dash_splitter()

    def view_owners(self):
        """ View_Owners
        This function will retrieve and show the owners within the safe-cli, marking the sender with and "[X]" and if it's
        currently loaded with another "[X]"
        :return:
        """
        self.log_formatter.log_section_left_side('Loaded Owner Data')
        for owner_index, owner in enumerate(self.sender_account_list):
            information_data = ' (#) Owner {0} | Address: {1} | Sender: [{2}] | Balance: {3} '.format(
                owner_index, owner.address, self.is_sender(owner.address),
                self.ethereum_client.w3.eth.getBalance(owner.address))
            self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.log_formatter.log_dash_splitter()

    def view_sender(self):
        """ View_Sender
        This function will retrieve and show the sender value of the safe
        :return:
        """
        self.log_formatter.log_section_left_side('Safe Sender')
        self.log_formatter.log_data(' (#) Address: {0}', self.sender_address)
        self.log_formatter.log_data(' (#) Private Key: {0}', self.sender_private_key)
        self.log_formatter.log_dash_splitter()

    def _setup_sender(self, msg_header='Setup Sender'):
        """ Setup_Sender
        This functions will find the best fit owner to be the sender of the transactions, the moment the user
        loads a viable owner account
        :return:
        """
        # List to store ether for each loaded owner and find the one with the max balance ether
        sender_stored_ether = []

        # Only establish the sender if len() equals to 1 or more
        if len(self.sender_account_list) >= 1:
            for index, sender in enumerate(self.sender_account_list):
                sender_ether = self.ethereum_client.w3.eth.getBalance(sender.address)
                sender_stored_ether.append(sender_ether)

            # Select the sender with the max ether balance
            max_balance_sender_index = sender_stored_ether.index(max(sender_stored_ether))

            # Setup sender_address via index
            self.sender_address = self.sender_account_list[max_balance_sender_index].address
            # Setup sender_private_key
            self.sender_private_key = HexBytes(self.sender_account_list[max_balance_sender_index].privateKey).hex()

            # Prompt results of sender setup
            self.log_formatter.log_section_left_side(msg_header)
            self.log_formatter.log_data(' (#) Address: {0}', self.sender_address)
            self.log_formatter.log_data(' (#) Balance: {0}', self.ethereum_client.w3.eth.getBalance(self.sender_address))
            self.log_formatter.log_dash_splitter()

    def _update_sender(self, msg_header='Update Sender'):
        """ Update_Sender
        This function will update the current sender_address/sender_private_key
        :param msg_header:
        :return:
        """
        # Since the sender has to be valid, might as well reset the values to default and setup again
        # this way we avoid the search for a valid sender to be removed.
        self._reset_sender()
        self._setup_sender(msg_header)

    def _reset_sender(self):
        """ Reset_Sender
        This function will reset the current sender_address/sender_private_key
        :return:
        """
        self.sender_address = None
        self.sender_private_key = None

    def _add_sender(self, sender_account):
        """ Add_Sender
        This function will add a sender to the sender_account_list
        :param sender_account:
        :return:
        """
        if (sender_account is not None) and (sender_account in self.sender_account_list):
            raise SafeSenderAlreadyLoaded

        elif sender_account is not None:
            self.sender_account_list.append(sender_account)
            self.logger.debug0('[ Safe Sender ]: New sender account added {0}'.format(self.sender_account_list))

            # Add new element account to EthereumAssets.Accounts
            self.accounts.add_account_artifact(
                sender_account.address, sender_account.privateKey, alias='safeOwner_')
            self.logger.debug0('[ Safe Sender ]: Current senders {0}'.format(self.sender_account_list))
            return True
        else:
            raise SafeSenderNotFound(None)

    def _remove_sender(self, sender_account):
        """ Remove_Sender
        This function will remove a sender from the sender_account_list
        :param sender_account:
        :return: True otherwise raise SafeSenderNotFound
        """
        if (sender_account is not None) and (sender_account in self.sender_account_list):
            for stored_sender in self.sender_account_list:
                # Found Match
                if stored_sender == sender_account:
                    self.logger.debug0('[ Safe Sender ]: Removing sender account {0} from sender_account_list'.format(
                        sender_account))

                    # Remove new element account to EthereumAssets.accounts
                    # todo: implement remove element from EthereumAssets.Accounts
                    self.sender_account_list.remove(sender_account)
            self.logger.debug0('[ Safe Sender ]: Current senders {0}'.format(self.sender_account_list))
            return True
        else:
            raise SafeSenderNotFound(None)

    def unload_owner_via_address(self, sender_address):
        """ Unload_Owner_Via_Address
        This function will remove a sender from the sender_account_list via address
        :param sender_address:
        """
        try:
            for sender in self.sender_account_list:
                if sender.address == sender_address:

                    # If the remove is a success, setup sender again as planned
                    if self._remove_sender(sender):
                        self._update_sender()

            self.logger.debug0('[ Safe Sender ]: Current senders {0}'.format(self.sender_account_list))
        except SafeSenderNotFound as err:
            self.logger.error(err.message)
        except Exception as err:
            self.logger.error(err)

    def are_enough_signatures_loaded(self):
        """ Are_Enough_Signatures_Loaded
        This function eval if the current operation is in disposition to be executed, evaluating the number of threshold
        limiting the execution of operations vs de current lenght of the list of account_local
        :return:
        """
        if self.safe_operator.retrieve_threshold() <= len(self.sender_account_list):
            return True
        # self.logger.warn('Not Enough Signatures Loaded/Stored in sender_accounts_list')
        raise SafeSenderNotEnoughSigners(None)

    def load_owner(self, private_key):
        """ Load_Owner
        This function will load a sender using a private_key
        :param private_key:
        :return:
        """
        try:
            self.logger.debug0('[ Safe Sender ]: Loading new sender {0}'.format(HexBytes(private_key).hex()))
            new_sender = self.accounts.get_local_verified_account(
                HexBytes(private_key).hex(), self.safe_operator.retrieve_owners())

            # If the add is a success, setup sender again as planned
            if self._add_sender(new_sender):
                self._setup_sender()

        except SafeSenderNotFound as err:
            self.logger.error(err.message)
        except SafeSenderAlreadyLoaded as err:
            self.logger.error(err.message)
        except Exception as err:
            self.logger.error(err)

    def unload_owner(self, private_key):
        """ Unload_Owner
        This funtion will unload a sender using the private_key
        :param private_key:
        :return:
        """
        try:
            self.logger.debug0('[ Safe Sender ]: Unloading old sender {0}'.format(HexBytes(private_key).hex()))
            old_sender = self.accounts.get_local_verified_account(
                HexBytes(private_key).hex(), self.safe_operator.retrieve_owners())

            # If the remove is a success, setup sender again as planned
            if self._remove_sender(old_sender):
                self._update_sender()

        except SafeSenderNotFound:
            self.logger.error('[ Safe Sender ]: Sender is not part of the safe owners')
        except Exception as err:
            self.logger.error(err)

    def get_toolbar_text(self):
        """ Get Toolbar Text
        This function will return the data for the toolbar displaying the current sender
        :return:
        """
        amount = 0
        if (self.sender_address is not None) and (self.sender_private_key is not None):
            text_badge, tmp_amount = self.ether_helper.get_simplified_balance(self.sender_address)
            amount = '{0} {1}'.format(str(tmp_amount), text_badge)
        return HTML(' [ <strong>Sender:</strong> %s'
                    ' | <strong>PK:</strong> %s'
                    ' | <strong>Balance:</strong> %s ]' % (self.sender_address, self.sender_private_key, amount))
