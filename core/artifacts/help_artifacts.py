#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Aesthetic Constants
from core.constants.console_constant import STRING_DASHES

# Help Message Constants
LOAD_CONTRACT_MSG = 'loadContract --alias=<Contract Name>'
LOAD_SAFE_MSG = 'loadSafe --address=<Contract Address>'
SET_NETWORK_MSG = 'setNetwork --network=<Network Name> --api_key=<Optional>'

VIEW_NETWORKS_MSG = 'viewNetwork'
VIEW_ACCOUNTS_MSG = 'viewAccounts'
VIEW_CONTRACT_MSG = 'viewContracts'
VIEW_PAYLOADS_MSG = 'viewPayloads'
VIEW_TOKEN_MSG = 'viewTokens'

NEW_CONTRACT_MSG = 'newContract --address=<Contract Address> --abi=<Path to Contract ABI>'
NEW_ACCOUNT_MSG = 'newAccount --private_key=<Account Private Key>'
NEW_PAYLOAD_MSG = 'newPayload'
NEW_PAYLOAD_TX_MSG = 'newPayloadTx'

QUIT_MSG = 'exit|quit|close'

DISCLAIMER_MSG = 'This is a proof of concept software, focused on the design of an interface to interact ' \
                 'directly with a contract safe. Since this in early development, it is not advised to use this ' \
                 'program in a non testing environment such as Mainnet. For now is recommended to use this sofware' \
                 'in Rinkeby or Ganache'

NAME_VERSION_MSG = 'Gnosis-Cli 0.1.0'

SAFE_BANNER = 'Console Safe Commands'
CONTRACT_BANNER_MSG = 'Console Contract Commands'

IS_OWNER_MSG = 'isOwner --address=<Account Address>'
ARE_OWNER_MSG = 'areOwners --address=<Account Address> ... --address=<Account Address>'
GET_OWNER_MSG = 'getOwners'
GET_THRESHOLD_MSG = 'getThreshold'
ADD_OWNER_MSG = 'addOwner --address=<Account Address>'
ADD_OWNERS_MSG = ''
ADD_OWNER_WITH_THRESHOLD_MSG = 'addOwnerWithThreshold --address=<Account Address> --uint=<New Threshold>'

SWAP_OR_CHANGE_OWNER_MSG = 'swapOwner|changeOnwer --address=<Old Account Address> --address=<New Account Address>'
REMOVE_OWNER_MSG = ''
REMOVE_OWNERS_MSG = ''

SEND_ETHER_MSG = ''
DEPOSIT_ETHER_MSG = ''
WITHDRAW_ETHER_MSG = ''

SEND_TOKEN_MSG = ''
DEPOSIT_TOKEN_MSG = ''
WITHDRAW_TOKEN_MSG = ''

NONCE_MSG = ''
CODE_MSG = ''
VERSION = ''

VIEW_SENDER = ''


class InformationArtifacts:
    def __init__(self, logger):
        self.name = self.__class__.__name__
        self.logger = logger

    def command_view_disclaimer(self):
        self.logger.info()

    def command_view_about(self):
        """
        Temporal Function to display current version of the gnosis-cli
        :return:
        """
    def command_view_help(self):
        """
        Temporal Function to display information about the possible functions that can be used in the gnosis-cli
        :return:
        """
        print('---------' * 10)
        print('Console Command List')
        print('---------' * 10)
        print(' (+) loadContract: --alias= ')
        print('---------' * 10)
        print(' (+) setNetwork: command to set current network')

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