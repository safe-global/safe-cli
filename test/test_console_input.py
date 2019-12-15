# Importing Custom Logger & Logging Modules
from core.logger.custom_logger import CustomLogger, DEBUG0
from logging import INFO
import logging

from eth_account import Account
from core.artifacts.utils.ether_helper import EtherHelper
from core.input.console_input_getter import ConsoleInputGetter
from core.net.network_agent import NetworkAgent
from core.input.console_input_handler import ConsoleInputHandler

# ----------------------------------------------------------------------------------------------------------------------
# Setting Up Components
# ----------------------------------------------------------------------------------------------------------------------
logging_lvl = INFO
logger = CustomLogger(__name__, logging_lvl)
formatter = logging.Formatter(fmt='%(asctime)s - [ %(levelname)s ]: %(message)s',
                              datefmt='%I:%M:%S %p')

# Custom Logger Console Configuration: Console Init Configuration
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(level=logging_lvl)

# Custom Logger Console/File Handler Configuration
logger.addHandler(console_handler)

# Setup Console Input Getter
console_getter = ConsoleInputGetter(logger)

# Setup Console Network Agent
network_agent = NetworkAgent(logger)
console_handler = ConsoleInputHandler(logger)


def test_get_load_safe():
    load_safe_command = 'loadSafe --address=0x5b1869D9A4C187F2EAa108f3062412ecf0526b24'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_safe_command)

    safe_address = console_handler.input_handler(command_argument, desired_parsed_item_list, priority_group)

    assert command_argument == 'loadSafe'
    assert safe_address == '0x5b1869D9A4C187F2EAa108f3062412ecf0526b24'


def test_get_load_owner():
    load_safe_command = 'loadOwner --private_key=0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_safe_command)

    private_key = console_handler.input_handler(command_argument, desired_parsed_item_list, priority_group)

    assert command_argument == 'loadOwner'
    assert private_key == '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'


def test_get_unload_owner():
    unload_safe_command = 'unloadOwner --private_key=0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(unload_safe_command)

    private_key = console_handler.input_handler(command_argument, desired_parsed_item_list, priority_group)

    assert command_argument == 'unloadOwner'
    assert private_key == '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'


def test_get_is_owner():
    add_owner_safe = 'isOwner --address=0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(add_owner_safe)

    owner_address = console_handler.input_handler(command_argument, desired_parsed_item_list, priority_group)

    assert command_argument == 'isOwner'
    assert owner_address == '0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0'


def test_get_change_threshold():
    change_threshold_command = 'changeThreshold --value=2'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(change_threshold_command)

    new_threshold_value = console_handler.input_handler(command_argument, desired_parsed_item_list, priority_group)

    assert command_argument == 'changeThreshold'
    assert new_threshold_value == 2


def test_get_add_owner():
    add_owner_command = 'addOwner --address=0xE11BA2b4D45Eaed5996Cd0823791E0C93114882d'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(add_owner_command)

    new_owner_address = console_handler.input_handler(command_argument, desired_parsed_item_list, priority_group)

    assert command_argument == 'addOwner'
    assert new_owner_address == '0xE11BA2b4D45Eaed5996Cd0823791E0C93114882d'


def test_get_add_owner_with_threshold():
    add_owner_command = 'addOwnerWithThreshold --address=0xE11BA2b4D45Eaed5996Cd0823791E0C93114882d --value=2'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(add_owner_command)

    new_owner_address, new_threshold_value = console_handler.input_handler(
        command_argument, desired_parsed_item_list, priority_group)

    assert command_argument == 'addOwnerWithThreshold'
    assert new_owner_address == '0xE11BA2b4D45Eaed5996Cd0823791E0C93114882d'
    assert new_threshold_value == 2


def test_get_change_owner():
    swap_owner_command = 'swapOwner --address=0xE11BA2b4D45Eaed5996Cd0823791E0C93114882d ' \
                         '--address=0xd03ea8624C8C5987235048901fB614fDcA89b117'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(swap_owner_command)

    old_owner_address, new_owner_address = console_handler.input_handler(
        command_argument, desired_parsed_item_list, priority_group)

    assert command_argument == 'swapOwner'
    assert old_owner_address == '0xE11BA2b4D45Eaed5996Cd0823791E0C93114882d'
    assert new_owner_address == '0xd03ea8624C8C5987235048901fB614fDcA89b117'


def test_get_remove_owner():
    remove_owner_command = 'removeOwner --address=0xd03ea8624C8C5987235048901fB614fDcA89b117'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(remove_owner_command)

    old_owner_address = console_handler.input_handler(command_argument, desired_parsed_item_list, priority_group)

    assert command_argument == 'removeOwner'
    assert old_owner_address == '0xd03ea8624C8C5987235048901fB614fDcA89b117'


def test_get_send_ether():
    send_ether_command = 'sendEther --address_to=0xD833215cBcc3f914bD1C9ece3EE7BF8B14f841bb ' \
                         '--private_key=0xb0057716d5917badaf911b193b12b910811c1497b5bada8d7711f758981c3773 --ether=1'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(send_ether_command)

    address_to, private_key, ether_amounts = console_handler.input_handler(
                        command_argument, desired_parsed_item_list, priority_group)
    local_account = Account.privateKeyToAccount(private_key)
    ether_helper = EtherHelper(logger, network_agent.ethereum_client)
    amount_value = ether_helper.get_unify_ether_amount(ether_amounts)

    expected_amount_value = ether_helper.get_unify_ether_amount([('--ether', [1])])

    assert command_argument == 'sendEther'
    assert address_to == '0xD833215cBcc3f914bD1C9ece3EE7BF8B14f841bb'
    assert local_account.privateKey.hex() == '0xb0057716d5917badaf911b193b12b910811c1497b5bada8d7711f758981c3773'
    assert amount_value == expected_amount_value


def test_get_deposit_ether():
    deposit_ether_command = 'depositEther ' \
                            '--private_key=0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d --ether=2'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(deposit_ether_command)

    private_key, ether_amounts = console_handler.input_handler(command_argument, desired_parsed_item_list, priority_group)
    local_account = Account.privateKeyToAccount(private_key)
    ether_helper = EtherHelper(logger, network_agent.ethereum_client)
    amount_value = ether_helper.get_unify_ether_amount(ether_amounts)
    expected_amount_value = ether_helper.get_unify_ether_amount([('--ether', [2])])

    assert command_argument == 'depositEther'
    assert local_account.privateKey.hex() == '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    assert amount_value == expected_amount_value


def test_get_withdraw_ether():
    withdraw_ether_command = 'withdrawEther --address_to=0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0 --ether=2'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(withdraw_ether_command)

    address_to, ether_amounts = console_handler.input_handler(command_argument, desired_parsed_item_list, priority_group)
    ether_helper = EtherHelper(logger, network_agent.ethereum_client)
    amount_value = ether_helper.get_unify_ether_amount(ether_amounts)
    expected_amount_value = ether_helper.get_unify_ether_amount([('--ether', [2])])

    assert command_argument == 'withdrawEther'
    assert address_to == '0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0'
    assert amount_value == expected_amount_value


def test_get_send_token():
    send_token_command = 'sendToken --token=0x2D8BE6BF0baA74e0A907016679CaE9190e80dD0A ' \
                         '--address_to=0x5b1869D9A4C187F2EAa108f3062412ecf0526b24 --amount=1 ' \
                         '--private_key=0x6370fd033278c143179d81c5526140625662b8daa446c22ee2d73db3707e620c'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(send_token_command)

    token_address, address_to, token_amount, private_key = console_handler.input_handler(
        command_argument, desired_parsed_item_list, priority_group)
    local_account = Account.privateKeyToAccount(private_key)

    expected_token_amount = 1
    assert command_argument == 'sendToken'
    assert token_address == '0x2D8BE6BF0baA74e0A907016679CaE9190e80dD0A'
    assert address_to == '0x5b1869D9A4C187F2EAa108f3062412ecf0526b24'
    assert local_account.privateKey.hex() == '0x6370fd033278c143179d81c5526140625662b8daa446c22ee2d73db3707e620c'
    assert int(token_amount) == expected_token_amount


def test_get_deposit_token():
    deposit_token_command = 'depositToken ' \
                            '--token=0x2D8BE6BF0baA74e0A907016679CaE9190e80dD0A --amount=1 ' \
                            '--private_key=0x6370fd033278c143179d81c5526140625662b8daa446c22ee2d73db3707e620c'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(deposit_token_command)

    token_address, token_amount, private_key = console_handler.input_handler(
        command_argument, desired_parsed_item_list, priority_group)
    local_account = Account.privateKeyToAccount(desired_parsed_item_list[2][1][0])

    expected_token_amount = 1
    assert command_argument == 'depositToken'
    assert token_address == '0x2D8BE6BF0baA74e0A907016679CaE9190e80dD0A'
    assert local_account.privateKey.hex() == '0x6370fd033278c143179d81c5526140625662b8daa446c22ee2d73db3707e620c'
    assert int(token_amount) == expected_token_amount


def test_get_withdraw_token():
    withdraw_token_command = 'withdrawToken ' \
                             '--token=0x2D8BE6BF0baA74e0A907016679CaE9190e80dD0A ' \
                             '--address_to=0x22d491Bde2303f2f43325b2108D26f1eAbA1e32b --amount=1'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(withdraw_token_command)

    token_address, address_to, token_amount = console_handler.input_handler(
        command_argument, desired_parsed_item_list, priority_group)
    expected_token_amount = 1

    assert command_argument == 'withdrawToken'
    assert token_address == '0x2D8BE6BF0baA74e0A907016679CaE9190e80dD0A'
    assert address_to == '0x22d491Bde2303f2f43325b2108D26f1eAbA1e32b'
    assert int(token_amount) == expected_token_amount



