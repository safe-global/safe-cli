#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class ConsoleInformation:
    def __init__(self):
        self.name = self.__class__.__name__

    @staticmethod
    def command_view_about():
        print('gnosis-cli 0.0.1a prototype')

    @staticmethod
    def command_view_help():
        print('---------' * 10)
        print('Console Command List')
        print('---------' * 10)
        print(' (+) loadContract: --alias= ')
        print('---------' * 10)
        print(' (+) setNetwork: command to set current network')
        print(' (+) setAutofill: Command to set auto fill option')
        print(' (+) setDefaultOwner: Command to set default owner')
        print(' (+) setDefaultOwnerList: Command to set default owner list')
        print('---------' * 10)
        print(' (+) viewNetwork: Command to get current and available network')
        print(' (+) viewAccounts: Command to get available Accounts')
        print(' (+) viewContracts: Command to get available Contracts')
        print(' (+) viewOwnerList: Command to get default owner list')
        print(' (+) viewOwner: Command to get default owner')
        print(' (+) viewPayloads: Command to get available Payloads')
        print('---------' * 10)
        print(' (+) newContract: --address= --abi= | --abi= --bytecode=')
        print(' (+) newAccount: --alias= --address= --private_key=')
        print(' (+) newPayload: Command to create a new payload to be stored, used in call() & transact()')
        print(' (+) newTxPayload: Command to create a new tx payload to be stored')
        print(' (+) quit|close|exit: Command to exit gnosis-cli & contract-cli')