#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Init Scenario ( To have a functional contract to test commands )
from safe_init_scenario_script import gnosis_py_init_scenario, gnosis_py_init_tokens

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

parser.add_argument('--private_key', action='append',
                    dest='private_key_collection',
                    help='This init option will store a list o private keys to be initialize during the Loading Process'
                         'in the Console and they will be converted to LocalAccounts. Those values can be viewed '
                         'through viewAccounts command. Additionally while using the General Contract or Safe Contract'
                         'Consoles, those values can be accessed during contract interaction via alias. '
                         'Example( Ganache Account 0 Alias ): isOwner --address=gAccount0.address', type=str)

parser.add_argument('--version', action='version', version='%(prog)s 0.0.1a')
parser.add_argument('--test', action='store_true',
                    dest='test', default=False,
                    help='This init option will launch the loading of local artifacts such a copy of the gnosis_safe &'
                         'and 10 random local accounts and the 10 default accounts provided by the ganache local '
                         'blockchain.')
parser.add_argument('--safe_address', action='store',
                    dest='safe_address', default='0x',
                    help='This init option, will store the value of the safe address you like to operate with during'
                         ' the execution of the Console. This value can be changed in the Console via '
                         'loadSafe command).',
                    type=str)

try:
    config = configparser.ConfigParser()
    config.read('./gnosis_cli.ini')

    # 'name': init_file['GnosisConsole']['name'],
    # 'version': init_file['GnosisConsole']['version']
    # Retrieve ArgParse values
    results = parser.parse_args()
    init_configuration = {
        'safe_address': results.safe_address,
        'quiet': results.quiet,
        'debug': results.debug,
        'network': results.network,
        'private_key': results.private_key_collection,
        'name': config['DEFAULT']['name'],
        'version': config['DEFAULT']['version']
    }

    # Init Scenario with Random Safe with Setup (Pre-Loaded Contracts)
    pre_loaded_contract_artifacts = None
    pre_loaded_token_artifacts = None
    if results.test:
        # pre_loaded_contract_artifacts = gnosis_py_init_scenario()
        pre_loaded_token_artifacts = gnosis_py_init_tokens('0x5b1869D9A4C187F2EAa108f3062412ecf0526b24')

    # Init GnosisConsoleEngine with current configuration
    gnosis_console_engine = GnosisConsoleEngine(
        init_configuration,
        contract_artifacts=pre_loaded_contract_artifacts,
        token_artifacts=pre_loaded_token_artifacts)

except ConnectionError:
    print('Launch [ "ganache-cli -d" ] command on a new terminal before you try to run the console again!')
except Exception as err:
    print('Uknown Error:', type(err), '\n', err)
