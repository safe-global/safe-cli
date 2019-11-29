#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Init Scenario ( To have a functional contract to test commands )
from safe_init_scenario_script import gnosis_py_init_scenario

# Import GnosisConsoleEngine Module
from core.console_engine import GnosisConsoleEngine

# Import ConnectionError Exception: (Ganache not loaded)
from requests.exceptions import ConnectionError

# Import ArgParse Module
import argparse

# Define ArgParse Arguments for the GnosisConsoleEngine
parser = argparse.ArgumentParser()
parser.add_argument('--silence', action='store_true',
                    dest='silence', default=False,
                    help='This init option will store the value for the silence param, and subsequently will '
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

try:
    # Retrieve ArgParse values
    results = parser.parse_args()
    init_gnosis_console_configuration = {
        'silence': results.silence,
        'debug': results.debug,
        'network': results.network,
        'private_key': results.private_key_collection
    }

    # Init Scenario with Random Safe with Setup (Pre-Loaded Contracts)
    contract_artifacts_assets = gnosis_py_init_scenario()

    # Init GnosisConsoleEngine with current configuration
    gnosis_console_engine = GnosisConsoleEngine(init_gnosis_console_configuration)

    # Load Contract Artifacts Assets ( Init Safe from Scenario )
    gnosis_console_engine.load_contract_artifacts(contract_artifacts_assets)

    # Run the Gnosis Console
    gnosis_console_engine.run_console_session()

except ConnectionError:
    print('Launch [ "ganache-cli -d" ] command on a new terminal before you try to run the console again!')
except Exception as err:
    print('Uknown Error:', type(err), '\n', err)
