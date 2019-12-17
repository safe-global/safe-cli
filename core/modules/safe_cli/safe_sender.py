#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import HexBytes Module: Signatures
from hexbytes import HexBytes

# Exceptions: _add, _remove operations
from core.modules.safe_cli.exceptions.safe_sender_exceptions import SafeSenderNotFound, SafeSenderAlreadyLoaded, SafeSenderNotEnoughSigners

# Import LogMessageFormatter: view_functions
from core.logger.log_message_formatter import LogMessageFormatter

# Constants
MARK = 'X'
UN_MARK = ' '


class SafeSender:
    def __init__(self, logger, safe_interface, network_agent, ethereum_assets):
        self.name = self.__class__.__name__
        self.logger = logger

        # SafeInterface: safe_instance
        self.safe_interface = safe_interface

        # Sender list
        self.sender_account_list = []

        # Current sender
        self.sender_private_key = None
        self.sender_address = None

        # Network Agent: ethereum_client
        self.network_agent = network_agent

        # EthereumClient: get_balance()
        self.ethereum_client = network_agent.ethereum_client

        # Account Artifacts: get_local_account()
        self.account_artifacts = ethereum_assets.account_artifacts

        # view functions
        self.log_formatter = LogMessageFormatter(self.logger)

    def is_sender(self, address):
        if address == self.sender_address:
            return MARK
        return UN_MARK

    def is_sender_loaded(self, address):
        for sender in self.sender_account_list:
            if address == sender.address:
                return MARK
        return UN_MARK

    # Just Show from here, mark loaded ones
    def view_safe_owners(self):
        """ Command Safe Get Owners
        This function will retrieve and show the get owners of the safe
        :return:
        """
        self.log_formatter.log_section_left_side('Safe Owner Data')
        for owner_index, owner in enumerate(self.safe_interface.functions.getOwners().call()):
            information_data = ' (#) Owner {0} | Address: {1} | Sender: [{2}] | Balance: {3} '.format(
                owner_index, owner, self._is_sender(owner), self.ethereum_client.w3.eth.getBalance(owner))
            self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.log_formatter.log_dash_splitter()

    def view_owners(self):
        """ Command Safe Get Owners
        This function will retrieve and show the loaded owners of the safe
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
        """ Command View Default Sender
        This function will retrieve and show the sender value of the safe
        :return:
        """
        self.log_formatter.log_section_left_side('Safe Sender')
        self.log_formatter.log_data(' (#) Address: {0}', self.sender_address)
        self.log_formatter.log_data(' (#) Private Key: {0}', self.sender_private_key)
        self.log_formatter.log_dash_splitter()

    def _setup_sender(self, msg_header='Setup Sender'):
        """ Setup Sender
        This functions will find the best fit owner to be the sender of the transactions, the moment the user
        loads a viable owner account
        :return:
        """
        # List to store ether for each loaded owner and find the one with the max balance ether
        sender_stored_ether = []

        # Prompt header
        self.log_formatter.log_section_left_side('Setup Sender Based On Ether')

        # Only establish the sender if len() equals 1
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
        # Since the sender has to be valid, might as well reset the values to default and setup again
        # this way we avoid the search for a valid sender to be removed.
        self._reset_sender()
        self._setup_sender(msg_header)

    def _reset_sender(self):
        self.sender_address = None
        self.sender_private_key = None

    def _add_sender(self, sender_account):
        if (sender_account is not None) and (sender_account in self.sender_account_list):
            raise SafeSenderAlreadyLoaded

        elif sender_account is not None:
            self.sender_account_list.append(sender_account)
            self.logger.debug0('[ Safe Sender ]: New sender account added {0}'.format(self.sender_account_list))

            # Add new element account to EthereumAssets.Accounts
            self.account_artifacts.add_account_artifact(
                sender_account.address, sender_account.private_key, alias='safeOwner_')
            self.logger.debug0('[ Safe Sender ]: Current Senders {0}'.format(self.sender_account_list))
            return True
        else:
            raise SafeSenderNotFound

    def _remove_sender(self, sender_account):

        if (sender_account is not None) and (sender_account in self.sender_account_list):
            for stored_sender in self.sender_account_list:
                # Found Match
                if stored_sender == sender_account:
                    self.logger.debug0('[ Safe Sender ]: Removing sender account {0} from sender_account_list'.format(
                        sender_account))

                    # Remove new element account to EthereumAssets.Accounts
                    # todo: implement remove element from EthereumAssets.Accounts
                    self.sender_account_list.remove(sender_account)
            self.logger.debug0('[ Safe Sender ]: Current Senders {0}'.format(self.sender_account_list))
            return True
        else:
            raise SafeSenderNotFound

    def are_enough_signatures_loaded(self):
        """ Are Enough Signatures Loaded
        This funcion eval if the current operation is in disposition to be executed, evaluating the number of threshold
        limiting the execution of operations vs de current lenght of the list of account_local
        :return:
        """
        if self.safe_interface.retrieve_threshold() == self.sender_account_list:
            return True
        self.logger.warn('Not Enough Signatures Loaded/Stored in local_accounts_list')
        raise SafeSenderNotEnoughSigners

    def load_owner(self, private_key):
        try:
            self.logger.debug0('[ Safe Sender ]: Loading new Sender {0}'.format(HexBytes(private_key).hex()))
            new_sender = self.account_artifacts.get_local_account(
                HexBytes(private_key).hex(), self.safe_interface.retrieve_owners())

            # If the add is a success, setup sender again as planned
            if self._add_sender(new_sender):
                self._setup_sender()

        except SafeSenderNotFound:
            self.logger.error('[ Safe Sender ]: Sender is not part of the safe owners, Unable to properly loadOwner')
        except SafeSenderAlreadyLoaded:
            self.logger.error('[ Safe Sender ]: Sender already in sender_account_list')
        except Exception as err:
            self.logger.error(err)

    def unload_owner(self, private_key):
        try:
            self.logger.debug0('[ Safe Sender ]: Loading new Sender {0}'.format(HexBytes(private_key).hex()))
            old_sender = self.account_artifacts.get_local_account(
                HexBytes(private_key).hex(), self.safe_interface.retrieve_owners())

            # If the remove is a success, setup sender again as planned
            if self._remove_sender(old_sender):
                self._update_sender()

        except SafeSenderNotFound:
            self.logger.error('[ Safe Sender ]: Sender is not part of the safe owners')
        except Exception as err:
            self.logger.error(err)

    # Sender Data so it should be here
    def set_toolbar_text(self, sender_address=None, sender_private_key=None):
        """ Get Toolbar Text

        :param sender_address:
        :param sender_private_key:
        :return:
        """
        amount = 0
        if (sender_address is not None) and (sender_private_key is not None):
            balance = self.network_agent.ethereum_client.w3.eth.getBalance(sender_address)
            wei_amount = self.ether_helper.get_unify_ether_amount([('--wei', [balance])])
            text_badge, tmp_amount = self.ether_helper.get_proper_ether_amount(wei_amount)
            amount = '{0} {1}'.format(str(tmp_amount), text_badge)
        return HTML(' [ <strong>Sender:</strong> %s'
                    ' | <strong>PK:</strong> %s'
                    ' | <strong>Balance:</strong> %s ]' % (sender_address, sender_private_key, amount))