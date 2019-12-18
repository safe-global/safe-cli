# Importing Custom Logger & Logging Modules
from core.logger.custom_logger import CustomLogger
from logging import INFO
import logging

from core.eth_assets.components.accounts import Accounts
from core.eth_assets.components.tokens import Tokens
from core.eth_assets.ethereum_assets import EthereumAssets
from core.input.console_input_getter import ConsoleInputGetter
from core.modules.safe_cli import ConsoleSafeCommands
from core.net.network_agent import NetworkAgent
from test.utils.scenario_script import deploy_gnosis_safe_v1_1_0, deploy_uxi_tokens, deploy_gnosis_safe_v1_1_1

# ----------------------------------------------------------------------------------------------------------------------
# Setting Up Components
# ----------------------------------------------------------------------------------------------------------------------
logging_lvl = INFO
logger = CustomLogger(__name__, INFO)
formatter = logging.Formatter(fmt='%(asctime)s - [ %(levelname)s ]: %(message)s',
                              datefmt='%I:%M:%S %p')
# Custom Logger Console Configuration: Console Init Configuration
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(level=logging_lvl)
# Custom Logger Console/File Handler Configuration
logger.addHandler(console_handler)

network_agent = NetworkAgent(logger)
# Setup Console Input Getter
console_getter = ConsoleInputGetter(logger)
# Setup Console Account Artifacts
account_artifacts = Accounts(logger, network_agent.get_ethereum_client(), False)
# Setup Console Token
token_artifacts = Tokens(logger, network_agent.ethereum_client)
# Setup DataArtifacts
data_artifacts = EthereumAssets(logger, account_artifacts, None, token_artifacts, None)
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# Setting Up Scenario
# ----------------------------------------------------------------------------------------------------------------------
safe_address = deploy_gnosis_safe_v1_1_0()
new_master_copy_address = deploy_gnosis_safe_v1_1_1()
token_address = deploy_uxi_tokens(safe_address)
# ----------------------------------------------------------------------------------------------------------------------

# Constants for the Current Test
legit_safe_owner = '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
un_legit_safe_owner = '0x5f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'

def test_load_legit_safe_owner():
    # Load Safe
    console_safe = ConsoleSafeCommands(safe_address, logger, data_artifacts, network_agent)

    # Load Owner
    private_key = '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    local_owner = account_artifacts.get_local_verified_account(private_key, console_safe.safe_operator.retrieve_owners())

    if local_owner in console_safe.local_owner_account_list:
        logger.error('Local Owner Already in local_owner_account_list')
    else:
        console_safe.local_owner_account_list.append(local_owner)
    console_safe.setup_sender()

    assert console_safe.sender_private_key == '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    assert console_safe.sender_address == '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'


def test_load_un_legit_safe_owner():
    # Load Safe
    console_safe = ConsoleSafeCommands(safe_address, logger, data_artifacts, network_agent)

    # Load Owner
    private_key = '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    local_owner = account_artifacts.get_local_verified_account(private_key, console_safe.safe_operator.retrieve_owners())

    if local_owner in console_safe.local_owner_account_list:
        logger.error('Local Owner Already in local_owner_account_list')
    else:
        console_safe.local_owner_account_list.append(local_owner)
    console_safe.setup_sender()

    assert console_safe.sender_private_key == '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    assert console_safe.sender_address == '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'




