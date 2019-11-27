#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Eth Account Package
from eth_account import Account

# Import Deterministic Ganache Account Information (Address, Private Key)
from core.constants.ganache_constants import DETERMINISTIC_ACCOUNT_INFORMATION as ganache_data

# Import HexBytes Package
from hexbytes import HexBytes

class ConsoleSessionAccounts:
    """ ConsoleSessionAccounts

    """
    def __init__(self):
        self.account_data = {'NULL': {'address': '0x' + '0' * 40, 'private_key': HexBytes('')}}
        self._setup_ganache_accounts()
        self._setup_random_accounts()
        # todo: web3.eth.getBalance(address)

    def add_account(self, address, private_key='', alias='uAccount'):
        """ Add Account

        :param address:
        :param private_key:
        :param alias:
        :return:
        """
        if private_key != '':
            tmp_account = Account.from_key(private_key)
            self.account_data[alias + str(len(self.account_data)-1)] = {'address': tmp_account.address, 'private_key': tmp_account.privateKey}
            return self.account_data
        else:   # Todo: Validate Address
            self.account_data[alias + str(len(self.account_data)-1)] = {'address': address, 'private_key': HexBytes(private_key)}
            return self.account_data

    def _setup_random_accounts(self, account_number=10):
        """ Setup Random Accounts

        :param account_number:
        :return:
        """
        for index in range(1, account_number, 1):
            tmp_account = Account.create()
            self.account_data['rAccount' + str(index - 1)] = {'address': tmp_account.address, 'private_key': tmp_account.privateKey}
        return self.account_data

    def _setup_ganache_accounts(self):
        """ Setup Ganache Accounts

        :return:
        """
        for index, data in enumerate(ganache_data):
            tmp_account = Account.privateKeyToAccount(ganache_data[data]['private_key'])
            self.account_data['gAccount' + str(index)] = {'address': tmp_account.address, 'private_key': tmp_account.privateKey}

    def get_account_data(self, stream):
        """ Get Account Data

        :param stream:
        :return:
        """
        for item in self.account_data:
            if stream.startswith(item):
                key = stream.split('.')[1]
                print(stream, item, self.account_data[item][key])
                return self.account_data[item][key]