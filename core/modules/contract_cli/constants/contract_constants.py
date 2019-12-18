#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import HTML Module
from prompt_toolkit.formatted_text import HTML

# simple_function_operand = '((--address=)(0x([aA-zZ,0-9]{62}|[aA-zZ,0-9]{40}))?)|((--uint=)([0-9]{0,})?)|(--queue)?(--execute)?'
console_method_names = 'isOwner|getOwners|getThreshold|addOwner|swapOwner|removeOwner|changeThreshold|sendEther' \
                       '|sendToken|VERSION|NAME|code|nonce|addOwnerWithThreshold|viewSender|loadOwner' \
                       '|loadMultipleOwners|removeMultipleOwners|unloadOwner|updateSafe|depositEther|' \
                       'withdrawEther|depositToken|withdrawToken|sendToken|viewOwners|viewGas|setBaseGas|' \
                       'setSafeTxGas|setAutoExecute|setAutoFillTokenDecimals'

console_commands = 'viewNetwork|viewAccounts|viewContracts|newPayload|newTxPayload|newAccount|newContract|' \
                   'setNetwork|setDefaultSender|loadContract|loadSafe|viewPayloads|viewTokens|newTokens|' \
                   'viewSender|viewBalance'
console_quit_commands = 'exit|quit|close'
console_help_commands = 'help|about|info'
console_known_networks = 'ropsten|mainnet|ganache|rinkeby'
console_contract_execution_commands = '--queue|--execute|--query'
address_param = '--address=(0x[aA-zZ,0-9]{40,62})?'
bytecode_param = '--bytecode='
uint_param = '--uint=([0-9]{0,})?'
ether_params = '--ether=|--miliether=|--microether=|--wei=|--Kwei=|--Mwei=|--Gwei='

arg_keywords = [
    '--address=', '--uint=', '--ether=', '--miliether=', '--microether=', '--wei=', '--Kwei=',
    '--Mwei=', '--Gwei=', '--query', '--execute', '--queue', '--alias=', '--bytecode=', '--token=', '--amount=',
    '--address_to='
    ]

function_name = [
    'isOwner', 'getOwners', 'swapOwners', 'removeOwner', 'addOwner', 'addOwnersWithThreshold', 'changeOwner'
    'getThreshold', 'changeThreshold', 'sendEther', 'sendToken', 'viewAccounts', 'viewContract', 'viewTokens',
    'viewPayloads', 'viewSender', 'loadOwner', 'loadMultipleOwners', 'removeMultipleOwners', 'unloadOwner',
    'unloadMultipleOwners', 'viewBalance', 'depositEther', 'depositToken', 'withdrawEther', 'withdrawToken',
    'setAutoFillTokenDecimals', 'viewOwners', 'viewGas','setBaseGas', 'setSafeTxGas', 'setAutoExecute'
]

function_params = {
    'isOwner': 'address',
    'areOwners': 'address',
    'getOwners': '_',
    'swapOwners': 'address ,address ,address',
    'addOwner': 'address, uint',
    'removeOwner': 'address, address',
    'getThreshold': '_',
    'changeThreshold': 'uint',
    'sendEther': 'address to, bytecode data',
    'sendToken': 'address',
    'NAME': '_',
    'VERSION': '_',
    'viewAccounts': '_',
    'viewPayloads': '_',
    'viewSender': '_',
    'viewTokens': '_',
    'viewBalance': '_',
    'loadMultipleOwners': '_',
    'loadOwner': '_',
    'unloadOwner': '_',
    'removeMultipleOwners': '_',
    'depositEther': '_',
    'depositToken': '_',
    'withdrawToken': '_',
    'withdrawEther': '_',
    'setAutoFillTokenDecimals': '_',
    'setAutoExecute': '_',
    'viewOwners': '_',
    'setSafeTxGas': '_',
    'setBaseGas': '_',
    'viewGas': '_'
}

function_parms_color = {
    'address': 'ansimagenta',
    'address, address': 'ansimagenta',
    'address ,address ,address': 'ansimagenta',
    'uint': 'ansiyellow',
    'uint, address ,address': 'ansimagenta',
    'address, uint': 'ansimagenta',
    'address to, bytecode data': 'ansimagenta',
    'bytecode': 'ansimagenta',
    '_': 'ansired',
}

meta_arguments = {
    '--address=': HTML('Argument <ansired>--address</ansired> alpha-numeric value of <u>40</u> to <u>64</u>'),
    '--uint256=': HTML('Argument <ansired>--uint256</ansired> integer value from <u>0</u> to <u>2^256-1</u>.'),
}

meta = {
    'isOwner': HTML('Command <ansired>isOwner</ansired> will check if account <u>address</u> is a valid owner.'),
    'getOwners': HTML('Command <ansired>getOwners</ansired> will return a list of valid <u>address</u> account owners.'),
    'swapOwners': HTML('Command <ansired>swapOwners</ansired> will change a old account <u>address</u> for the new one provided.'),
    'addOwner': HTML('Command <ansired>swapOwners</ansired> will add a new owner account <u>address</u>.'),
    'removeOwner': HTML('Command <ansired>removeOwner</ansired> will remove a old account <u>address</u> from the owners list.'),
    'getThreshold': HTML('Command <ansired>getThreshold</ansired> will return the current <u>uint</u> threshold.'),
    'changeThreshold': HTML('Command <ansired>changeThreshold</ansired> will change the current threshold <u>uint</u> for the one provided.'),
    'sendEther': HTML('Command <ansired>sendEther</ansired> will send Ether/Wei to a valid account <u>address</u>.'),
    'sendToken': HTML('Command <ansired>sendToken</ansired> will send Token to a valid account <u>address</u>.'),
    'NAME': HTML('Command <ansired>NAME</ansired> will show current name of the <u>contract_cli.log</u>.'),
    'VERSION': HTML('Command <ansired>VERSION</ansired>  will show current version of the <u>contract_cli.log</u>.'),
}
