# Importing Custom Logger & Logging Modules
from core.logger.custom_logger import CustomLogger, DEBUG0
from logging import INFO
import logging

from core.input.console_input_getter import ConsoleInputGetter

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

# Setup Console Input Getter
console_getter = ConsoleInputGetter(logger)


def setinel_helper(address_value, safe_interface):
    """ Sender Helper
    This function send utils
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

def test_get_load_safe():
    load_safe_command = 'loadSafe --address=0x5b1869D9A4C187F2EAa108f3062412ecf0526b24'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_safe_command)

    safe_address = desired_parsed_item_list[0][1][0]

    assert command_argument == 'loadSafe'
    assert safe_address == '0x5b1869D9A4C187F2EAa108f3062412ecf0526b24'


def test_get_load_owner():
    load_safe_command = 'loadOwner --private_key=0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_safe_command)

    private_key = desired_parsed_item_list[0][1][0]

    assert command_argument == 'loadOwner'
    assert private_key == '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'


def test_get_unload_owner():
    unload_safe_command = 'unloadOwner --private_key=0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(unload_safe_command)

    private_key = desired_parsed_item_list[0][1][0]

    assert command_argument == 'unloadOwner'
    assert private_key == '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'


def test_get_is_owner():
    add_owner_safe = 'isOwner --address=0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(add_owner_safe)

    owner_address = desired_parsed_item_list[0][1][0]

    assert command_argument == 'isOwner'
    assert owner_address == '0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0'


def test_get_change_threshold():
    change_threshold_command = 'changeThreshold --uint=2'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(change_threshold_command)

    new_threshold_value = int(desired_parsed_item_list[0][1][0])

    assert command_argument == 'changeThreshold'
    assert new_threshold_value == 2


def test_get_add_owner():
    add_owner_command = 'addOwner --address=0xE11BA2b4D45Eaed5996Cd0823791E0C93114882d'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(add_owner_command)

    new_owner_address = desired_parsed_item_list[0][1][0]

    assert command_argument == 'addOwner'
    assert new_owner_address == '0xE11BA2b4D45Eaed5996Cd0823791E0C93114882d'


def test_get_add_owner_with_threshold():
    add_owner_command = 'addOwnerWithThreshold --address=0xE11BA2b4D45Eaed5996Cd0823791E0C93114882d --uint=2'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(add_owner_command)

    new_owner_address = desired_parsed_item_list[0][1][0]
    new_threshold_value = int(desired_parsed_item_list[1][1][0])

    assert command_argument == 'addOwnerWithThreshold'
    assert new_owner_address == '0xE11BA2b4D45Eaed5996Cd0823791E0C93114882d'
    assert new_threshold_value == 2


def test_get_change_owner():
    swap_owner_command = 'swapOwner --address=0xE11BA2b4D45Eaed5996Cd0823791E0C93114882d --address=0xd03ea8624C8C5987235048901fB614fDcA89b117'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(swap_owner_command)

    old_owner_address = desired_parsed_item_list[0][1][0]
    new_owner_address = desired_parsed_item_list[0][1][1]

    assert command_argument == 'swapOwner'
    assert old_owner_address == '0xE11BA2b4D45Eaed5996Cd0823791E0C93114882d'
    assert new_owner_address == '0xd03ea8624C8C5987235048901fB614fDcA89b117'

def test_get_remove_owner():
    remove_owner_command = 'removeOwner --address=0xd03ea8624C8C5987235048901fB614fDcA89b117'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(remove_owner_command)

    owner_address = desired_parsed_item_list[0][1][0]
    assert command_argument == 'removeOwner'
    assert owner_address == '0xd03ea8624C8C5987235048901fB614fDcA89b117'

def test_get_send_ether():
    return



def test_get_deposit_ether():
    # deposit_ether_command = 'depositEther --private_key=0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d --ether=2'
    # local_account = Account.privateKeyToAccount(desired_parsed_item_list[0][1][0])
    # ethereum_units_amount = desired_parsed_item_list[1:]
    # ether_helper = EtherHelper(logger, network_agent.ethereum_client)
    # amount_value = ether_helper.get_unify_ether_amount(ethereum_units_amount)
    return


def test_get_withdraw_ether():
    return


def test_get_send_token():
    return


def test_get_deposit_token():
    return


def test_get_withdraw_token():
    return

