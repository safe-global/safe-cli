#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# reference: (Ethereum Interface) https://medium.com/hackernoon/creating-a-python-ethereum-interface-part-1-4d2e47ea0f4d
# reference: (Safe Code) https://github.com/gnosis/safe-contracts/blob/development/test/gnosisSafeDeploymentViaTx.js
# reference: (Safe Project) https://github.com/gnosis/safe-contracts

# Import Web3 Module

# Import Constant
from core.constants.console_constant import NULL_ADDRESS

# Import Contract Reader
from core.utils.build_contract_reader import ContractReader

class TruffleSafeSetup:
    """ Gnosis Safe Module
    This module will provide the set of functions needed to interact with the Gnosis Safe through the commandline
    """
    def __init__(self, provider, contract_artifacts, logger=''):
        """
        Function Init for the Gnosis Safe Module, that provides de core functions to interact with the contract through
        the gnosis console.
        :param provider:
        :param contract_artifacts:
        :param logger:
        """
        self.name = self.__class__.__name__
        self.provider = provider
        self.build_contract_reader = ContractReader()
        self.logger = logger
        self.contract_artifacts = contract_artifacts

    def setup(self, gnosissafe_instance, proxy_instance):
        """ Setup
        This function will finish the setup the Gnosis Safe Contract through the proxy contract
            :param gnosissafe_instance: Main Gnosis Safe Instance to interact with
            :param proxy_instance: Each proxy you're linking with the master copy of the Gnosis Safe Instance
            :return: Proxy Instance
        """
        try:
            # Setup for GnosisSafe & Proxy Accounts
            account0 = self.provider.eth.accounts[0]
            account1 = self.provider.eth.accounts[1]
            account2 = self.provider.eth.accounts[2]
            list_of_accounts = [account0, account1, account2]

            print('--init safe gnosis setup')
            gnosissafe_instance.functions.setup(list_of_accounts, 1, NULL_ADDRESS, b'', NULL_ADDRESS, NULL_ADDRESS, 0, NULL_ADDRESS).transact({'from': account0})
            print('--init proxy factory setup')
            proxy_instance.functions.setup(list_of_accounts, 1, NULL_ADDRESS, b'', NULL_ADDRESS, NULL_ADDRESS, 0, NULL_ADDRESS).transact({'from': account0})
            return proxy_instance
        except Exception as err:
            print(type(err), err)
        return

    def standard_safe_transaction(self, provider, account_to, account_from_private_key, account_from, ether_value=1):
        """ Standard Safe Transaction
        This function will perform a standard transact operation

            :param provider: current provider
            :param account_to: account from which you are transacting with the current operation
            :param account_from_private_key: key from which you are performing the current operation
            :param account_from: account from which you are sending the transact operation
            :param ether_value: toWei value to be transferred via transaction
            :return: Receipt Tx ()
        """
        try:
            signed_txn = provider.eth.account.signTransaction(
                dict(
                    nonce=provider.eth.getTransactionCount(str(account_from)),
                    gasPrice=provider.eth.gasPrice,
                    gas=100000,
                    to=str(account_to),
                    value=provider.toWei(ether_value, 'ether')
                    ), account_from_private_key
            )
            signed_txn_hash = provider.eth.sendRawTransaction(signed_txn.rawTransaction)
            return signed_txn_hash
        except Exception as err:
            print(err)
        return 'signed_txn_hash'