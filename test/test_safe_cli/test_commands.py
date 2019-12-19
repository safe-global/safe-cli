# Importing Custom Logger & Logging Modules
from core.logger.custom_logger import CustomLogger
from logging import INFO
import logging

from hexbytes import HexBytes
from eth_account import Account

from core.eth_assets.components.accounts import Accounts
from core.eth_assets.components.contracts import Contracts
from core.eth_assets.components.payloads import Payloads
from core.eth_assets.components.tokens import Tokens

from core.eth_assets.ethereum_assets import EthereumAssets
from core.input.console_input_getter import ConsoleInputGetter

from core.eth_assets.helper.ether_helper import EtherHelper
from core.net.network_agent import NetworkAgent
from test.utils.scenario_script import deploy_gnosis_safe_v1_1_0, deploy_uxi_tokens, deploy_gnosis_safe_v1_1_1


def setinel_helper(address_value, safe_interface):
    """ Sender Helper
    This function send helper
    :param address_value:
    :param safe_interface:
    :return:
    """
    previous_owner = '0x' + ('0' * 39) + '1'
    logger.info('[ Current Owner with Address to be Removed ]: {0}'.format(str(address_value)))
    logger.info('[ Current Local Account Owners ]: {0}'.format(safe_interface.safe_operator.retrieve_owners()))
    for index, owner_address in enumerate(safe_interface.safe_operator.retrieve_owners()):
        if address_value == owner_address:
            logger.info('[ Found Owner in Owners ]: {0} with Index {1}'.format(owner_address, index))
            try:
                sentinel_index = (index - 1)
                logger.info('[ SENTINEL Address Index ]: {0}'.format(sentinel_index))
                if index != 0:
                    current_owner_list = safe_interface.safe_operator.retrieve_owners()
                    previous_owner = current_owner_list[(index - 1)]

                logger.info('[ Found PreviousOwner on the list ]: {0}'.format(previous_owner))
                return previous_owner
            except IndexError:
                logger.error('Sentinel Address not found, returning NULLADDRESS')


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

# NetworkAgent:
network_agent = NetworkAgent(logger)
# InputGetter:
getter = ConsoleInputGetter(logger)
# Accounts:
accounts = Accounts(logger, network_agent.ethereum_client, False)
# Tokens:
tokens = Tokens(logger, network_agent.ethereum_client)
# EthereumAssets:
ethereum_assets = EthereumAssets(logger, accounts, None, tokens, None)
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# Setting Up Scenario
# ----------------------------------------------------------------------------------------------------------------------
safe_address = deploy_gnosis_safe_v1_1_0()
new_master_copy_address = deploy_gnosis_safe_v1_1_1()
token_address = deploy_uxi_tokens(safe_address)
# ----------------------------------------------------------------------------------------------------------------------


def test_load_safe():
    console_safe = ConsoleSafeCommands(safe_address, logger, ethereum_assets, network_agent)

    # Assert if the current Safe was properly setup
    assert console_safe.safe_operator.address == safe_address
    assert console_safe.safe_operator.retrieve_threshold() == 1
    assert console_safe.safe_operator.retrieve_version() == '1.1.0'
    assert console_safe.safe_operator.retrieve_owners() == ['0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1']



def test_add_owner():
    # Load Safe
    console_safe = ConsoleSafeCommands(safe_address, logger, ethereum_assets, network_agent)

    # Load Owner
    owner_private_key_safe = '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    console_safe.command_load_owner(owner_private_key_safe)

    # Assert the new loaded owner, and the variables that are affected by it
    assert len(console_safe.local_owner_account_list) == 1
    assert console_safe.sender_private_key == '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    assert console_safe.sender_address == '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'
    assert console_safe.sender_address == console_safe.local_owner_account_list[0].address
    assert console_safe.sender_private_key == HexBytes(console_safe.local_owner_account_list[0].privateKey).hex()

    # Add New Owner
    new_owner_address = '0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0'
    console_safe.command_safe_add_owner_threshold(new_owner_address, _execute=True)

    assert len(console_safe.safe_operator.retrieve_owners()) == 2
    assert console_safe.safe_operator.retrieve_is_owner(new_owner_address)


def test_change_threshold():
    # Load Safe
    console_safe = ConsoleSafeCommands(safe_address, logger, ethereum_assets, network_agent)

    # Load Fst Owner
    fst_private_key = '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    console_safe.command_load_owner(fst_private_key)

    # Assert current loaded owner, length of local_accounts should be 1 and the values for private_key/address the fst
    # loaded user in the test
    assert len(console_safe.local_owner_account_list) == 1
    assert console_safe.sender_private_key == '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    assert console_safe.sender_address == '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'

    # Load Snd Owner
    snd_private_key = '0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1'
    console_safe.command_load_owner(snd_private_key)

    # Assert current loaded owner, length of local_accounts should be 2 and the values for private_key/address the snd
    # loaded user in the test
    assert len(console_safe.local_owner_account_list) == 2
    assert console_safe.sender_private_key == '0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1'
    assert console_safe.sender_address == '0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0'

    # Revert Threshold to 1
    new_threshold = 1
    console_safe.command_safe_change_threshold(new_threshold, _execute=True)

    assert console_safe.safe_operator.retrieve_threshold() == new_threshold


def test_swap_owner():
    # Load Safe
    console_safe = ConsoleSafeCommands(safe_address, logger, ethereum_assets, network_agent)

    # Load Fst Owner
    fst_private_key = '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    console_safe.command_load_owner(fst_private_key)

    # Assert current loaded owner, length of local_accounts should be 1 and the values for private_key/address the fst
    # loaded user in the test
    assert len(console_safe.local_owner_account_list) == 1
    assert console_safe.sender_private_key == '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    assert console_safe.sender_address == '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'

    # Load Snd Owner
    snd_private_key = '0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1'
    console_safe.command_load_owner(snd_private_key)

    # Assert current loaded owner, length of local_accounts should be 2 and the values for private_key/address the snd
    # loaded user in the test
    assert len(console_safe.local_owner_account_list) == 2
    assert console_safe.sender_private_key == '0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1'
    assert console_safe.sender_address == '0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0'

    # Swap Owner
    address_value_to = '0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0'
    address_new_value = '0x22d491Bde2303f2f43325b2108D26f1eAbA1e32b'
    previous_owner = setinel_helper(address_value_to, console_safe)
    console_safe.command_safe_swap_owner(previous_owner, address_value_to, address_new_value, _execute=True)

    assert console_safe.safe_operator.retrieve_is_owner(address_new_value)
    assert len(console_safe.safe_operator.retrieve_owners()) == 2
    assert console_safe.safe_operator.retrieve_threshold() == 1


def test_remove_owner():
    # Load Safe
    console_safe = ConsoleSafeCommands(safe_address, logger, ethereum_assets, network_agent)

    # Load Fst Owner
    fst_private_key = '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    console_safe.command_load_owner(fst_private_key)

    # Assert current loaded owner, length of local_accounts should be 1 and the values for private_key/address the fst
    # loaded user in the test
    assert len(console_safe.local_owner_account_list) == 1
    assert console_safe.sender_private_key == '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    assert console_safe.sender_address == '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'

    # Remove Owner
    address_value_to = '0x22d491Bde2303f2f43325b2108D26f1eAbA1e32b'
    previous_owner = setinel_helper(address_value_to, console_safe)
    console_safe.command_safe_remove_owner(previous_owner, address_value_to, _execute=True)

    assert not console_safe.safe_operator.retrieve_is_owner(address_value_to)
    assert len(console_safe.safe_operator.retrieve_owners()) == 1
    assert console_safe.safe_operator.retrieve_threshold() == 1


def test_deposit_ether():
    # Load Safe
    console_safe = ConsoleSafeCommands(safe_address, logger, ethereum_assets, network_agent)

    # Load Fst Owner
    fst_private_key = '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    console_safe.command_load_owner(fst_private_key)

    # Assert current loaded owner, length of local_accounts should be 1 and the values for private_key/address the fst
    # loaded user in the test
    assert len(console_safe.local_owner_account_list) == 1
    assert console_safe.sender_private_key == '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    assert console_safe.sender_address == '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'

    # Deposit Ether in Safe
    previous_balance = network_agent.ethereum_client.w3.eth.getBalance(console_safe.safe_operator.address)

    local_account = Account.privateKeyToAccount(fst_private_key)
    ether_helper = EtherHelper(logger, network_agent.get_ethereum_client())
    amount_value = ether_helper.get_unify_ether_amount([('--ether', [2])])

    previous_user_balance = network_agent.ethereum_client.w3.eth.getBalance(local_account.address)
    console_safe.command_deposit_ether(amount_value, local_account, _execute=True)

    current_balance = network_agent.ethereum_client.w3.eth.getBalance(console_safe.safe_operator.address)
    current_user_balance = network_agent.ethereum_client.w3.eth.getBalance(local_account.address)

    assert current_balance == (previous_balance + amount_value)
    assert current_user_balance != previous_user_balance


def test_withdraw_ether():
    # Load Safe
    console_safe = ConsoleSafeCommands(safe_address, logger, ethereum_assets, network_agent)

    # Load Fst Owner
    fst_private_key = '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    console_safe.command_load_owner(fst_private_key)

    # Assert current loaded owner, length of local_accounts should be 1 and the values for private_key/address the fst
    # loaded user in the test
    assert len(console_safe.local_owner_account_list) == 1
    assert console_safe.sender_private_key == '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    assert console_safe.sender_address == '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'

    # Withdraw Ether from Safe
    address_value_to = '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'
    previous_balance = network_agent.ethereum_client.w3.eth.getBalance(console_safe.safe_operator.address)
    previous_user_balance = network_agent.ethereum_client.w3.eth.getBalance(address_value_to)

    address_value_to = '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'
    ether_helper = EtherHelper(logger, network_agent.get_ethereum_client())
    amount_value = ether_helper.get_unify_ether_amount([('--ether', [2])])
    console_safe.command_withdraw_ether(amount_value, address_value_to, _execute=True)

    current_balance = network_agent.ethereum_client.w3.eth.getBalance(console_safe.safe_operator.address)
    current_user_balance = network_agent.ethereum_client.w3.eth.getBalance(address_value_to)

    assert current_balance == (previous_balance - amount_value)
    assert current_user_balance != previous_user_balance


def test_deposit_token():
    token_amount = 1
    address_to = '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'

    # Load Safe
    console_safe = ConsoleSafeCommands(safe_address, logger, ethereum_assets, network_agent)
    previous_safe_token_balance = network_agent.ethereum_client.erc20.get_balance(console_safe.safe_operator.address, token_address)
    previous_user_token_balance = network_agent.ethereum_client.erc20.get_balance(address_to, token_address)

    # Load Fst Owner
    fst_private_key = '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    console_safe.command_load_owner(fst_private_key)
    local_owner = Account.privateKeyToAccount(fst_private_key)

    # Assert current loaded owner, length of local_accounts should be 1 and the values for private_key/address the fst
    # loaded user in the test
    assert len(console_safe.local_owner_account_list) == 1
    assert console_safe.sender_private_key == '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    assert console_safe.sender_address == '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'

    # Deposit Token in Safe
    console_safe.command_deposit_token(token_address, token_amount, local_owner, _execute=True)
    current_safe_token_balance = network_agent.ethereum_client.erc20.get_balance(console_safe.safe_operator.address, token_address)
    current_user_token_balance = network_agent.ethereum_client.erc20.get_balance(address_to, token_address)

    assert current_safe_token_balance == (previous_safe_token_balance + token_amount)
    assert current_user_token_balance == (previous_user_token_balance - token_amount)


def test_withdraw_token():
    # Load Safe
    console_safe = ConsoleSafeCommands(safe_address, logger, ethereum_assets, network_agent)

    # Load Fst Owner
    fst_private_key = '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    console_safe.command_load_owner(fst_private_key)

    # Assert current loaded owner, length of local_accounts should be 1 and the values for private_key/address the fst
    # loaded user in the test
    assert len(console_safe.local_owner_account_list) == 1
    assert console_safe.sender_private_key == '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    assert console_safe.sender_address == '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'

    # Withdraw Token in Safe
    token_amount = 1
    address_to = '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'
    previous_safe_token_balance = network_agent.ethereum_client.erc20.get_balance(safe_address, token_address)
    previous_user_token_balance = network_agent.ethereum_client.erc20.get_balance(address_to, token_address)

    console_safe.command_withdraw_token(address_to, token_address, token_amount, _execute=True)

    current_safe_token_balance = network_agent.ethereum_client.erc20.get_balance(safe_address, token_address)
    current_user_token_balance = network_agent.ethereum_client.erc20.get_balance(address_to, token_address)

    assert current_user_token_balance == (previous_user_token_balance + token_amount)
    assert current_safe_token_balance == (previous_safe_token_balance - token_amount)


def test_change_master_copy():
    # Load Safe
    console_safe = ConsoleSafeCommands(safe_address, logger, ethereum_assets, network_agent)

    # Load Owner
    owner_private_key_safe = '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    console_safe.command_load_owner(owner_private_key_safe)

    # Assert the new loaded owner, and the variables that are affected by it
    assert len(console_safe.local_owner_account_list) == 1
    assert console_safe.sender_private_key == '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    assert console_safe.sender_address == '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'
    assert console_safe.sender_address == console_safe.local_owner_account_list[0].address
    assert console_safe.sender_private_key == HexBytes(console_safe.local_owner_account_list[0].privateKey).hex()

    # updateSafe
    console_safe.command_safe_change_version(new_master_copy_address, _execute=True)

    assert console_safe.safe_operator.retrieve_master_copy_address() == new_master_copy_address
    # assert console_safe.safe_operator.retrieve_version() == '1.1.1'
