#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Console Constants
from core.constants.console_constant import NULL_ADDRESS

# Import GnosisConsoleEngine Module
from core.console_engine import GnosisConsoleEngine

# Import ConnectionError Exception: (Ganache not loaded)
from requests.exceptions import ConnectionError

# Import ArgParse Module
import argparse

# Import ConfigParser Module
import configparser

# Define ArgParse Arguments for the GnosisConsoleEngine
parser = argparse.ArgumentParser()
parser.add_argument('--quiet', action='store_true',
                    dest='quiet', default=False,
                    help='This init option will store the value for the quiet param, and subsequently will '
                         'disable/hide the Loading Process in the Console. (By default, it will be set to False).')
parser.add_argument('--debug', action='store_true',
                    dest='debug', default=False,
                    help='This init option will store the value for the debug param, and subsequently will enable the '
                         'Debug Output Mode in the Console. (By default, it will be set to False).')

parser.add_argument('--network', action='store',
                    dest='network', default='ganache',
                    help='This init option, will store the value of the network you like to operate with during the '
                         'execution of the Console. This value can be changed in the Console via setNetwork command, '
                         'also it can be viewed through viewNetworks command. (By default, it will be set to ganache).',
                    type=str)
parser.add_argument('--private_key', action='append', default=[],
                    dest='private_key_collection',
                    help='This init option will store a list o private keys to be initialize during the Loading Process'
                         'in the Console and they will be converted to LocalAccounts. Those values can be viewed '
                         'through viewAccounts command. Additionally while using the General Contract or Safe Contract'
                         'Consoles, those values can be accessed during contract interaction via alias. '
                         'Example( Ganache Account 0 Alias ): isOwner --address=gAccount0.address', type=str)
parser.add_argument('--api_key', action='store', default=None, dest='api_key', help='', type=str)
parser.add_argument('--safe', action='store',
                    dest='safe_address', default=None,
                    help='This init option, will store the value of the safe address you like to operate with during'
                         ' the execution of the Console. This value can be changed in the Console via '
                         'loadSafe command).', type=str)
parser.add_argument('--contract', action='store', dest='contract_address', default=None,
                    help='', type=str)
parser.add_argument('--erc20', action='append',
                    dest='erc20_collection', default=[],
                    help='This init option, will store the values of the erc20 token addresses you like to operate with'
                         ' during the execution of the Console.', type=str)
parser.add_argument('--erc721', action='append',
                    dest='erc721_collection', default=[],
                    help='This init option, will store the values of the erc721 token addresses you like to operate '
                         'with during the execution of the Console.', type=str)
parser.add_argument('--test', action='store_true',
                    dest='test', default=False,
                    help='This init option will launch the loading 10 random local accounts and '
                         'the 10 default local accounts provided by the ganache'
                         'blockchain.')
parser.add_argument('--version', action='version', version='%(prog)s 0.0.1a')

try:
    config = configparser.ConfigParser()
    config.read('./gnosis_cli.ini')

    # Retrieve ArgParse values
    results = parser.parse_args()
    init_configuration = {
        'quiet': results.quiet,
        'debug': results.debug,
        'network': results.network,
        'private_key': results.private_key_collection,
        'api_key': results.api_key,
        'safe': results.safe_address,
        'erc20': results.erc20_collection,
        'erc721': results.erc721_collection,
        'test': results.test,
        'name': config['DEFAULT']['name'],
        'version': config['DEFAULT']['version']
    }

    # Init GnosisConsoleEngine with current configuration
    gnosis_console_engine = GnosisConsoleEngine(init_configuration)

except ConnectionError:
    print('Launch [ "ganache-cli -d" ] command or setup [ network + api_key ] before you try to run the console again!')
except Exception as err:
    print('Uknown Error:', type(err), '\n', err)
