#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Eth Account Package
from eth_account import Account

# Import Deterministic Ganache Account Information (Address, Private Key)
from core.constants.console_constant import DETERMINISTIC_ACCOUNT_INFORMATION as ganache_data

# Import HexBytes Module
from hexbytes import HexBytes

# Import Constants
from core.constants.console_constant import STRING_DASHES, NULL_ADDRESS

# Import Account Artifacts Module
from core.artifacts.constants.type_artifacts import TypeOfAccount


class AccountsArtifacts:
    """ Account Artifacts
    This class will store all the information regarding account artifacts
    """
    def __init__(self, logger, ethereum_client, silence_flag=False, test_flag=False):
        self.logger = logger
        self.ethereum_client = ethereum_client
        self.silence_flag = silence_flag
        self.test_flag = test_flag
        # convert to ether
        self.account_data = {
            'NULL': {
                'network': TypeOfAccount.LOCAL_ACCOUNT,
                'balance': 0,
                'address': NULL_ADDRESS,
                'private_key': HexBytes('').hex(),
                'instance': None
            }
        }
        if test_flag:
            self._setup_ganache_accounts()
            self._setup_random_accounts()

    def command_view_accounts(self):
        """ Command View Accounts
         This function will show the values currently stored withing he account artifact class
        :return:
        """
        self.logger.info(' ' + STRING_DASHES)
        self.logger.info('| {0:^14} | {1:^44} | {2:^74} | '.format('Account', 'Address', 'Private Key'))
        self.logger.info(' ' + STRING_DASHES)
        for item in self.account_data:
            self.logger.info('| {0:^14} | {1:^44} | {2:^74} |'.format(
                item, self.account_data[item]['address'], str(self.account_data[item]['private_key']))
            )
        self.logger.info(' ' + STRING_DASHES)

    def new_account_entry(self, network, local_account):
        """ New Account Entry
        This function will generate a new entry dictionary for a contract artifact that has been loaded
        :param network:
        :param local_account:
        :return:
        """
        return {
                'network': network, 'balance': self.ethereum_client.w3.eth.getBalance(local_account.address),
                'address': local_account.address, 'private_key': HexBytes(local_account.privateKey).hex(),
                'instance': local_account
        }

    def add_account_artifact(self, address='', private_key='', alias='uAccount', network=TypeOfAccount.LOCAL_ACCOUNT):
        """ Add Account Artifact
        This function will add a new account to the ConsoleAccountArtifacts
            :param address:
            :param private_key:
            :param alias:
            :return:
        """
        local_account = None
        if private_key != '' and address == '':
            try:
                local_account = Account.privateKeyToAccount(HexBytes(private_key))
                self.account_data[(alias + str(len(self.account_data)-1))] = self.new_account_entry(network, local_account)
                return self.account_data
            except Exception as err:
                self.logger.error('Unable to add_account() {0} {1}'.format(type(err), err))
        elif private_key != '' and address != '':
            try:
                local_account = Account.privateKeyToAccount(private_key)
                if local_account.address != address:
                    self.logger.error('Miss Match in generated address via private_key and provided address')
                    raise Exception
            except Exception as err:
                self.logger.error('Unable to add_account() {0} {1}'.format(type(err), err))
            self.account_data[(alias + str(len(self.account_data)-1))] = self.new_account_entry(network, local_account)
            return self.account_data
        else:
            self.logger.error('Not enough values were given to the add_account()')

    def get_local_account(self, private_key, owner_address_list):
        """ Get Local Account
        This function will retrieve a local account to be set as sender in the current contract safe you are loaded
        in. It will compare the list of actual owners vs the generated address being created using a private_key, if
        there is no matching withing the owner_list of the contract an error will be prompted.
        :param private_key:
        :param owner_address_list:
        :return:
        """
        try:
            local_account = Account.privateKeyToAccount(private_key)
            for owner_address in owner_address_list:
                if local_account.address == owner_address:
                    self.logger.debug0('Match found in owner list while checking address generated via private_key')
                    return local_account
        except Exception as err:
            self.logger.debug0('Miss Match in generated account via private_key when '
                               'comparing address in owner list of the contract')
            self.logger.error('Unable to get_local_account() {0} {1}'.format(type(err), err))

    def _setup_random_accounts(self, account_number=10):
        """ Setup Random Accounts
        This function will setup n number of random accounts to interact with during the console execution
        :param account_number:
        :return:
        """
        self.logger.debug0('')
        self.logger.debug0(' | Setup Random Accounts | ')
        self.logger.debug0(STRING_DASHES)
        for index in range(1, account_number, 1):
            local_account = Account.create()
            self.logger.debug0('(+) Random Account with Address {0} '.format(local_account.address))
            self.add_account_artifact(local_account.address, local_account.privateKey, alias='rAccount')
        self.logger.debug0(STRING_DASHES)
        self.logger.debug0(' | [ {0} ] Random Accounts Added | '.format(account_number))

    def _setup_ganache_accounts(self):
        """ Setup Ganache Accounts
        This function will retrieve and setup ten ganache accounts to interact with during the console execution
        :return:
        """
        self.logger.debug0('')
        self.logger.debug0(' | Setup Ganache Accounts  | ')
        self.logger.debug0(STRING_DASHES)
        for index, data in enumerate(ganache_data):
            local_account = Account.privateKeyToAccount(ganache_data[data]['private_key'])
            self.logger.debug0('(+) Ganache Account with Address {0} '.format(local_account.address))
            self.add_account_artifact(local_account.address, local_account.privateKey, alias='gAccount')
        self.logger.debug0(STRING_DASHES)
        self.logger.debug0(' | [ {0} ] Ganache Accounts Added | '.format(len(ganache_data)))
