#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Aesthetic Constants
from core.constants.console_constant import STRING_DASHES

# Help Message Constants
# ----------------------------------------------------------------------------------------------------------------------
LOAD_CONTRACT_MSG = 'loadContract --alias=<Contract Name>'
LOAD_CONTRACT_COMMAND_MSG = 'This command will prompt the user with the options to create a new contract_cli entrie ' \
                            'in the console (To Be Implemented).'
LOAD_SAFE_MSG = 'loadSafe --address=<Contract Address>'
LOAD_SAFE_COMMAND_MSG = 'This command will sync with the --address that has been provided by de user to operate ' \
                        'directly with the owned safe.'
# ----------------------------------------------------------------------------------------------------------------------
SET_NETWORK_MSG = 'setNetwork --network=<Network Name> --api_key=<Optional>'
SET_NETWORK_COMMAND_MSG = 'This command will trigger the configuration of the' \
                          ' current network environment for the gnosis-cli.'
# ----------------------------------------------------------------------------------------------------------------------
VIEW_NETWORKS_MSG = 'viewNetwork'
VIEW_NETWORKS_COMMAND_MSG = 'This command will show the current network that gnosis-cli is currently connected to'
VIEW_ACCOUNTS_MSG = 'viewAccounts'
VIEW_ACCOUNTS_COMMAND_MSG = 'This function will show the current status of the accounts the user has pre/loaded.'
VIEW_CONTRACT_MSG = 'viewContracts'
VIEW_CONTRACT_COMMAND_MSG = 'This command will show the current status of the contracts the user has pre/loaded.'
VIEW_PAYLOADS_MSG = 'viewPayloads'
VIEW_PAYLOADS_COMMAND_MSG = 'This command will show the current status of the payloads the user has pre/loaded.'
VIEW_TOKENS_MSG = 'viewTokens'
VIEW_TOKENS_COMMAND_MSG = 'This command will show the current status of the tokens the user has pre/loaded.'
# ----------------------------------------------------------------------------------------------------------------------
NEW_CONTRACT_MSG = 'newContract --address=<Contract Address> --abi=<Path to Contract ABI>'
NEW_CONTRACT_COMMAND_MSG = 'This command will trigger the creation of a new contract_cli artifact withing the gnosis-cli.'
NEW_ACCOUNT_MSG = 'newAccount --private_key=<Account Private Key>'
NEW_ACCOUNT_COMMAND_MSG = 'This command will trigger the creation of a new account artifact withing the gnosis-cli.'
NEW_PAYLOAD_MSG = 'newPayload'
NEW_PAYLOAD_COMMAND_MSG = 'This command will trigger the creation of a new payload artifact withing the gnosis-cli.'
NEW_PAYLOAD_TX_MSG = 'newPayloadTx'
NEW_PAYLOAD_TX_COMMAND_MSG = 'This command will trigger the creation of' \
                             ' a new payload_tx artifact withing the gnosis-cli.'
NEW_TOKEN_MSG = 'newToken --address=<Token Address> --abi=<Path to Contract ABI>'
NEW_TOKEN_COMMAND_MSG = 'This command will trigger the creation of a new token artifact withing the gnosis-cli.'
# ----------------------------------------------------------------------------------------------------------------------
QUIT_MSG = 'exit|quit|close'
QUIT_COMMAND_MSG = 'This command will trigger the exit of the gnosis-cli/safe-cli/contract_cli-cli'
# ----------------------------------------------------------------------------------------------------------------------
DISCLAIMER_MSG_0 = 'This is a proof of concept software under the MIT License, focused ' \
                   'on the design of an interface, to directly interact with the'
DISCLAIMER_MSG_1 = 'gnosis safe. Since this in early development, it is not advised, ' \
                   'to use this prototype console in a non testing environment, such'
DISCLAIMER_MSG_2 = 'as Mainnet or Ropsten. For now, is only recommended to use this ' \
                   'sofware in testing networks such as Rinkeby or Ganache.'
# ----------------------------------------------------------------------------------------------------------------------
SAFE_BANNER_MSG = 'Console Safe Commands'
CONTRACT_BANNER_MSG = 'Console Contract Commands'
TITLE_MSG = 'Gnosis-Cli 0.1.0'
# ----------------------------------------------------------------------------------------------------------------------
LOAD_OWNER_MSG = 'loadOwner --address=<Owner Address>'
LOAD_OWNER_COMMAND_MSG = 'This command will trigger the method responsable for the loading of an acepted owner ' \
                         'of the safe.'
UNLOAD_OWNER_MSG = 'unloadOwner --address=<Owner Address>'
UNLOAD_OWNER_COMMAND_MSG = 'This command will trigger the method responsable for unloading a owner of the safe-cli.'
NONCE_MSG = 'Nonce'
NONCE_COMMAND_MSG = 'This command will trigger the retrieval of the current nonce value for the safe-cli.'
CODE_MSG = 'code'
CODE_COMMAND_MSG = 'This command will trigger the retrieval of the current code value for the safe-cli.'
VERSION_MSG = 'VERSION'
VERSION_COMMAND_MSG = 'This command will trigger the retrieval of the current version value for the safe-cli.'
VIEW_SENDER_MSG = 'viewSender'
VIEW_SENDER_COMMAND_MSG = 'This command will trigger the visualization of the current selected sender in the safe-cli'
UPDATE_SAFE_MSG = 'updateSafe --address=<New MasterCopy Address>'
UPDATE_SAFE_COMMAND_MSG = 'This command will trigger the update of the MasterCopy Address in the safe-cli.'
IS_OWNER_MSG = 'isOwner --address=<Account Address>'
IS_OWNER_COMMAND_MSG = 'This commmand will trigger the evaluation of the address that is been provided by user.'
ARE_OWNER_MSG = 'areOwners --address=<Account Address> ... --address=<Account Address>'
ARE_OWNERS_COMMAND_MSG = 'This command will trigger the method isOwner for each address provided by in the user input.'
GET_OWNER_MSG = 'getOwners'
GET_OWNER_COMMAND_MSG = 'This command will trigger the method getOwner within the loaded contract_cli in the safe-cli.'
GET_THRESHOLD_MSG = 'getThreshold'
GET_THRESHOLD_COMMAND_MSG = 'This command will trigger the method getThreshold' \
                            ' within the loaded contract_cli in the safe-cli.'
ADD_OWNER_MSG = 'addOwner --address=<Account Address>'
ADD_OWNER_COMMAND_MSG = 'This function will trigger de insertion of a new owner within the actual network ' \
                        'in the safe-cli.'
ADD_OWNERS_MSG = 'addOwners --address=<Old Account Address> ... --address=<N-Old Account Address>'
ADD_OWNERS_COMMAND_MSG = 'This command will trigger the method addOwner for each address provided by in the user input.'
ADD_OWNER_WITH_THRESHOLD_MSG = 'addOwnerWithThreshold --address=<Account Address> --uint=<New Threshold>'
ADD_OWNER_WITH_THRESHOLD_COMMAND_MSG = 'This command will trigger the transaction method responsable for adding a new' \
                                       'user to the safe-cli.'
SWAP_OR_CHANGE_OWNER_MSG = 'swapOwner|changeOnwer --address=<Old Account Address> --address=<New Account Address>'
SWAP_OR_CHANGE_OWNER_COMMAND_MSG = 'This command will trigger the transaction method responsable for changing a old' \
                                   ' owner for a new one in the safe-cli.'
REMOVE_OWNER_MSG = 'removeOwner --address=<Old Account Address>'
REMOVE_OWNER_COMMAND_MSG = 'This command will trigger the transaction method responsable for the deletion of old' \
                           ' owner via account address in the safe-cli.'
REMOVE_OWNERS_MSG = 'removeOwners --address=<Old Account Address> ... --address=<N-Old Account Address>'
REMOVE_OWNERS_COMMAND_MSG = 'This command will trigger the transaction method responsable for the removal of one' \
                            ' or more --address provided via user input.'
# ----------------------------------------------------------------------------------------------------------------------
SEND_ETHER_MSG = 'sendEther --address=<Address To> --private_key=<Private Key from>' \
                 ' --ether=(supported from --wei to --tether)'
SEND_ETHER_COMMAND_MSG = 'This command will trigger the trasaction method to' \
                         ' make a send ether procedure between two parties'
DEPOSIT_ETHER_MSG = 'depositEther --private_key=<Private Key from> --ether=(supported from --wei to --tether)'
DEPOSIT_ETHER_COMMAND_MSG = 'This command will trigger the transaction method to make a deposit of ether in the safe' \
                            ' that is currently loaded in the safe-cli'
WITHDRAW_ETHER_MSG = 'withdrawEther --address=<Address To>  --ether=(supported from --wei to --tether)'
WITHDRAW_ETHER_COMMAND_MSG = 'This command will trigger the transaction method to make a withdraw of ether in the' \
                             ' safe that is currently loaded in the safe-cli.'
# ----------------------------------------------------------------------------------------------------------------------
SEND_TOKEN_MSG = 'sendToken --address=<Token Address> --address=<Address To>' \
                 ' --amount<> --private_key=<From User Private Key>'
SEND_TOKEN_COMMAND_MSG = 'This command will trigger the transaction method to make a send procedure between to parties.'
DEPOSIT_TOKEN_MSG = 'depositToken --address=<Token Address> --amount<> --private_key=<From User Private Key>'
DEPOSIT_TOKEN_COMMAND_MSG = 'This command will trigger the transaction method to make a deposit of tokens in the safe' \
                            ' that is currently loaded in the safe-cli.'
WITHDRAW_TOKEN_MSG = 'withdrawToken --address=<Token Address> --address=<Address To> --amount<Token Amount>'
WITHDRAW_TOKEN_COMMAND_MSG = 'This command will trigger the transaction method to make a withdraw of tokens in the' \
                             ' safe that is currently loaded in the safe-cli.'
# ----------------------------------------------------------------------------------------------------------------------


class InformationArtifacts:
    def __init__(self, logger):
        self.name = self.__class__.__name__
        self.logger = logger

    def command_view_disclaimer(self):
        header_data = '-:[ {0} ]:-'.format('Disclaimer')
        self.logger.info(' {0}{1}'.format(header_data, '-' * (140 - len(header_data))))
        self.logger.info('| {0}{1}|'.format(DISCLAIMER_MSG_0, ' ' * (140 - len(DISCLAIMER_MSG_0) - 1)))
        self.logger.info('| {0}{1}|'.format(DISCLAIMER_MSG_1, ' ' * (140 - len(DISCLAIMER_MSG_1) - 1)))
        self.logger.info('| {0}{1}|'.format(DISCLAIMER_MSG_2, ' ' * (140 - len(DISCLAIMER_MSG_2) - 1)))
        self.logger.info(' ' + STRING_DASHES)

    def command_view_about(self):
        """
        Temporal Function to display current version of the gnosis-cli
        :return:
        """
        header_data = '-:[ {0} ]:-'.format('About')
        self.logger.info(' {0}{1}'.format(header_data, '-' * (140 - len(header_data))))

        self.logger.info(' ' + STRING_DASHES)

    def command_view_general_information(self):
        """
        Temporal Function to display information about the possible functions that can be used in the gnosis-cli
        :return:
        """
        header_data = '-:[ {0} ]:-'.format(TITLE_MSG)
        self.logger.info(' {0}{1}'.format(header_data, '-' * (140 - len(header_data))))

        # INFO: loadContract
        information_data = ' (#) {0}'.format(LOAD_CONTRACT_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(LOAD_CONTRACT_COMMAND_MSG, ' ' * (140 - len(LOAD_CONTRACT_COMMAND_MSG) - 5)))

        # INFO: loadSafe
        information_data = ' (#) {0}'.format(LOAD_SAFE_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(LOAD_SAFE_COMMAND_MSG, ' ' * (140 - len(LOAD_SAFE_COMMAND_MSG) - 5)))

        # INFO: setNetwork
        information_data = ' (#) {0}'.format(SET_NETWORK_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(SET_NETWORK_COMMAND_MSG, ' ' * (140 - len(SET_NETWORK_COMMAND_MSG) - 5)))

        # INFO: viewNetworks
        information_data = ' (#) {0}'.format(VIEW_NETWORKS_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(VIEW_NETWORKS_COMMAND_MSG, ' ' * (140 - len(VIEW_NETWORKS_COMMAND_MSG) - 5)))

        # INFO: viewAccounts
        information_data = ' (#) {0}'.format(VIEW_ACCOUNTS_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(VIEW_ACCOUNTS_COMMAND_MSG, ' ' * (140 - len(VIEW_ACCOUNTS_COMMAND_MSG) - 5)))

        # INFO: viewContracts
        information_data = ' (#) {0}'.format(VIEW_CONTRACT_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(VIEW_CONTRACT_COMMAND_MSG, ' ' * (140 - len(VIEW_CONTRACT_COMMAND_MSG) - 5)))

        # INFO: viewTokens
        information_data = ' (#) {0}'.format(VIEW_TOKENS_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(VIEW_TOKENS_COMMAND_MSG, ' ' * (140 - len(VIEW_TOKENS_COMMAND_MSG) - 5)))

        # INFO: newContract
        information_data = ' (#) {0}'.format(NEW_CONTRACT_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(NEW_CONTRACT_COMMAND_MSG, ' ' * (140 - len(NEW_CONTRACT_COMMAND_MSG) - 5)))

        # INFO: newAccount
        information_data = ' (#) {0}'.format(NEW_ACCOUNT_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(NEW_ACCOUNT_COMMAND_MSG, ' ' * (140 - len(NEW_ACCOUNT_COMMAND_MSG) - 5)))

        # INFO: newPayload
        information_data = ' (#) {0}'.format(NEW_PAYLOAD_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(NEW_PAYLOAD_COMMAND_MSG, ' ' * (140 - len(NEW_PAYLOAD_COMMAND_MSG) - 5)))

        # INFO: newPayloadTx
        information_data = ' (#) {0}'.format(NEW_PAYLOAD_TX_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(NEW_PAYLOAD_TX_COMMAND_MSG, ' ' * (140 - len(NEW_PAYLOAD_TX_COMMAND_MSG) - 5)))

        # INFO: newToken
        information_data = ' (#) {0}'.format(NEW_TOKEN_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(NEW_TOKEN_COMMAND_MSG, ' ' * (140 - len(NEW_TOKEN_COMMAND_MSG) - 5)))

        # INFO: exit
        information_data = ' (#) {0}'.format(QUIT_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(QUIT_COMMAND_MSG, ' ' * (140 - len(QUIT_COMMAND_MSG) - 5)))

        self.logger.info(' ' + STRING_DASHES)

    def command_view_safe_information(self):
        """
        Temporal Function to display information about the possible functions that can be used in the gnosis-cli
        :return:
        """
        header_data = '-:[ {0} ]:-'.format(SAFE_BANNER_MSG)
        self.logger.info(' {0}{1}'.format(header_data, '-' * (140 - len(header_data))))

        # INFO: loadOwner
        information_data = ' (#) {0}'.format(LOAD_OWNER_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(LOAD_OWNER_COMMAND_MSG, ' ' * (140 - len(LOAD_OWNER_COMMAND_MSG) - 5)))

        # INFO: unloadOwner
        information_data = ' (#) {0}'.format(UNLOAD_OWNER_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(UNLOAD_OWNER_COMMAND_MSG, ' ' * (140 - len(UNLOAD_OWNER_COMMAND_MSG) - 5)))

        # INFO: nonce
        information_data = ' (#) {0}'.format(NONCE_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(NONCE_COMMAND_MSG, ' ' * (140 - len(NONCE_COMMAND_MSG) - 5)))

        # INFO: code
        information_data = ' (#) {0}'.format(CODE_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(CODE_COMMAND_MSG, ' ' * (140 - len(CODE_COMMAND_MSG) - 5)))

        # INFO: version
        information_data = ' (#) {0}'.format(VERSION_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(VERSION_COMMAND_MSG, ' ' * (140 - len(VERSION_COMMAND_MSG) - 5)))

        self.logger.info(' ' + STRING_DASHES)

        # INFO: viewSender
        information_data = ' (#) {0}'.format(VIEW_SENDER_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(VIEW_SENDER_COMMAND_MSG, ' ' * (140 - len(VIEW_SENDER_COMMAND_MSG) - 5)))

        # INFO: updateSafe
        information_data = ' (#) {0}'.format(UPDATE_SAFE_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(UPDATE_SAFE_COMMAND_MSG, ' ' * (140 - len(UPDATE_SAFE_COMMAND_MSG) - 5)))

        self.logger.info(' ' + STRING_DASHES)

        # INFO: isOwner
        information_data = ' (#) {0}'.format(IS_OWNER_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(IS_OWNER_COMMAND_MSG, ' ' * (140 - len(IS_OWNER_COMMAND_MSG) - 5)))

        # INFO: areOwners
        information_data = ' (#) {0}'.format(ARE_OWNER_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(ARE_OWNERS_COMMAND_MSG, ' ' * (140 - len(ARE_OWNERS_COMMAND_MSG) - 5)))

        # INFO: getOwners
        information_data = ' (#) {0}'.format(GET_OWNER_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(GET_OWNER_COMMAND_MSG, ' ' * (140 - len(GET_OWNER_COMMAND_MSG) - 5)))

        # INFO: getThreshold
        information_data = ' (#) {0}'.format(GET_THRESHOLD_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(GET_THRESHOLD_COMMAND_MSG, ' ' * (140 - len(GET_THRESHOLD_COMMAND_MSG) - 5)))

        # INFO: addOwner
        information_data = ' (#) {0}'.format(ADD_OWNER_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(ADD_OWNER_COMMAND_MSG, ' ' * (140 - len(ADD_OWNER_COMMAND_MSG) - 5)))

        # INFO: addOwners
        information_data = ' (#) {0}'.format(ADD_OWNERS_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(ADD_OWNERS_COMMAND_MSG, ' ' * (140 - len(ADD_OWNERS_COMMAND_MSG) - 5)))

        # INFO: addOwnerWithThreshold
        information_data = ' (#) {0}'.format(ADD_OWNER_WITH_THRESHOLD_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(ADD_OWNER_WITH_THRESHOLD_COMMAND_MSG, ' ' * (140 - len(ADD_OWNER_WITH_THRESHOLD_COMMAND_MSG) - 5)))

        # INFO: changeOwner/swapOwner
        information_data = ' (#) {0}'.format(SWAP_OR_CHANGE_OWNER_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(SWAP_OR_CHANGE_OWNER_COMMAND_MSG, ' ' * (140 - len(SWAP_OR_CHANGE_OWNER_COMMAND_MSG) - 5)))

        # INFO: removeOwner
        information_data = ' (#) {0}'.format(REMOVE_OWNER_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(REMOVE_OWNER_COMMAND_MSG, ' ' * (140 - len(REMOVE_OWNER_COMMAND_MSG) - 5)))

        # INFO: removeOwners
        information_data = ' (#) {0}'.format(REMOVE_OWNERS_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(REMOVE_OWNERS_COMMAND_MSG, ' ' * (140 - len(REMOVE_OWNERS_COMMAND_MSG) - 5)))

        # INFO: sendEther
        information_data = ' (#) {0}'.format(SEND_ETHER_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(SEND_ETHER_COMMAND_MSG, ' ' * (140 - len(SEND_ETHER_COMMAND_MSG) - 5)))

        # INFO: depositEther
        information_data = ' (#) {0}'.format(DEPOSIT_ETHER_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(DEPOSIT_ETHER_COMMAND_MSG, ' ' * (140 - len(DEPOSIT_ETHER_COMMAND_MSG) - 5)))

        # INFO: withdrawEther
        information_data = ' (#) {0}'.format(WITHDRAW_ETHER_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(WITHDRAW_ETHER_COMMAND_MSG, ' ' * (140 - len(WITHDRAW_ETHER_COMMAND_MSG) - 5)))

        # INFO: sendToken
        information_data = ' (#) {0}'.format(SEND_TOKEN_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(SEND_TOKEN_COMMAND_MSG, ' ' * (140 - len(SEND_TOKEN_COMMAND_MSG) - 5)))

        # INFO: depositToken
        information_data = ' (#) {0}'.format(DEPOSIT_TOKEN_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(DEPOSIT_TOKEN_COMMAND_MSG, ' ' * (140 - len(DEPOSIT_TOKEN_COMMAND_MSG) - 5)))

        # INFO: withdrawToken
        information_data = ' (#) {0}'.format(WITHDRAW_TOKEN_MSG)
        self.logger.info('| {0}{1}|'.format(information_data, ' ' * (140 - len(information_data) - 1)))
        self.logger.info('|   - {0}{1}|'.format(WITHDRAW_TOKEN_COMMAND_MSG, ' ' * (140 - len(WITHDRAW_TOKEN_COMMAND_MSG) - 5)))

        self.logger.info(' ' + STRING_DASHES)

