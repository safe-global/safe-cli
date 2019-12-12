# from core.console_input_getter import ConsoleInputGetter
# command_argument = 'dummyCommand'
# argument_list = ['--address=']
# argument_list1 = ['--alias=a', '--coco=1', '--coco=2', '--address=3', 'bytecode=12412341234143141241']
# argument_list0 = ['--alias=a', '--address=1', '--address=2', '--address=3']
# argument_list2 = ['--address=0x1', '--gas=5', '--gas=1', '--gas=2', '--address=0x2', '--bytecode=12412341234143141241']
# argument_list3 = ['--address=0x1', '--address=0x5', '--gas=1', '--gas=2', '--address=0x2', '--bytecode=12412341234143141241']
# ConsoleInputGetter().get_gnosis_input_command_argument('dummyCommand', argument_list2)

# query_execTransaction_not_enough_args = 'execTransaction --queue --address=0x00000000000000000000000000000000 --address=0x00000000000000000000000000000001 --address=0x00000000000000000000000000000002'
# execute_swap_owner = 'swapOwner --address=0x00000000000000000000000000000000 --address=0x00000000000000000000000000000001 --address=0x00000000000000000000000000000002 --from=0x00000000000000000000000000000003 --execute'
# query_is_owner = 'isOwner --address=0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1 --query'
# query_get_owners = 'getOwners --query'

import pytest

# Importing Custom Logger & Logging Modules
from core.logger.custom_logger import CustomLogger, DEBUG0
from logging import INFO
import logging

from core.console_controller import ConsoleController
from core.artifacts.token_artifacts import TokenArtifacts
from core.artifacts.data_artifacts import DataArtifacts
from core.artifacts.contract_artifacts import ContractArtifacts
from core.artifacts.payload_artifacts import PayloadArtifacts
from core.artifacts.account_artifacts import AccountsArtifacts
from core.net.network_agent import NetworkAgent
from core.input.console_input_getter import ConsoleInputGetter
from core.contract.safe_commands import ConsoleSafeCommands
from core.artifacts.utils.ether_helper import EtherHelper
from hexbytes import HexBytes



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

# Setup Contract Payloads
payload_artifacts = PayloadArtifacts(logger)
# Setup Contract Artifacts
contract_artifacts = ContractArtifacts(logger)
# Setup EthereumClient
network_agent = NetworkAgent(logger)
# Setup Console Input Getter
console_getter = ConsoleInputGetter(logger)
# Setup Console Account Artifacts
account_artifacts = AccountsArtifacts(logger, network_agent.get_ethereum_client(), False)
# Setup Console Token
token_artifacts = TokenArtifacts(logger)
# Setup DataArtifacts
data_artifacts = DataArtifacts(
    logger, account_artifacts, payload_artifacts,
    token_artifacts, contract_artifacts
)


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

from eth_account import Account
from gnosis.eth.ethereum_client import EthereumClient
from gnosis.safe.tests.utils import deploy_safe


def test_load_safe():
    load_safe_command = 'loadSafe --address=0x5b1869D9A4C187F2EAa108f3062412ecf0526b24'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_safe_command)
    tmp_address = desired_parsed_item_list[0][1][0]
    console_safe = ConsoleSafeCommands(tmp_address, logger, data_artifacts, network_agent)

    # Assert if the current Safe was properly setup
    assert console_safe.safe_operator.address == '0x5b1869D9A4C187F2EAa108f3062412ecf0526b24'
    assert console_safe.safe_operator.retrieve_threshold() == 1
    assert console_safe.safe_operator.retrieve_version() == '1.1.0'
    assert console_safe.safe_operator.retrieve_owners() == ['0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1',
                                                            '0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0',
                                                            '0x22d491Bde2303f2f43325b2108D26f1eAbA1e32b']


def test_load_safe_owner():
    load_safe_command = 'loadSafe --address=0x5b1869D9A4C187F2EAa108f3062412ecf0526b24'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_safe_command)
    tmp_address = desired_parsed_item_list[0][1][0]
    console_safe = ConsoleSafeCommands(tmp_address, logger, data_artifacts, network_agent)

    # ------------------------------------------------------------------------------------------------------------------
    load_safe_command = 'loadOwner --private_key=0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_safe_command)
    private_key = desired_parsed_item_list[0][1][0]

    local_owner = account_artifacts.get_local_account(str(private_key), console_safe.safe_operator.retrieve_owners())
    if local_owner in console_safe.local_owner_account_list:
        logger.error('Local Owner Already in local_owner_account_list')
    else:
        console_safe.local_owner_account_list.append(local_owner)

    console_safe.command_safe_information()
    console_safe.setup_sender()

    assert console_safe.sender_private_key == '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    assert console_safe.sender_address == '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'


def test_unload_safe_owner():
    # LOAD SAFE
    # ------------------------------------------------------------------------------------------------------------------
    load_safe_command = 'loadSafe --address=0x5b1869D9A4C187F2EAa108f3062412ecf0526b24'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_safe_command)
    tmp_address = desired_parsed_item_list[0][1][0]
    console_safe = ConsoleSafeCommands(tmp_address, logger, data_artifacts, network_agent)

    # LOAD OWNER
    # ------------------------------------------------------------------------------------------------------------------
    load_owner_safe = 'loadOwner --private_key=0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_owner_safe)
    private_key = desired_parsed_item_list[0][1][0]

    local_owner = account_artifacts.get_local_account(str(private_key), console_safe.safe_operator.retrieve_owners())
    if local_owner in console_safe.local_owner_account_list:
        logger.error('Local Owner Already in local_owner_account_list')
    else:
        console_safe.local_owner_account_list.append(local_owner)
    console_safe.setup_sender()

    # Assert the new loaded owner, and the variables that are affected by it
    assert len(console_safe.local_owner_account_list) == 1
    assert console_safe.sender_address == '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'
    assert console_safe.sender_private_key == '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    assert console_safe.sender_address == console_safe.local_owner_account_list[0].address
    assert console_safe.sender_private_key == HexBytes(console_safe.local_owner_account_list[0].privateKey).hex()

    # UNLOAD OWNER
    # ------------------------------------------------------------------------------------------------------------------
    unload_safe_command = 'unloadOwner --private_key=0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(unload_safe_command)
    private_key = desired_parsed_item_list[0][1][0]

    local_owner = account_artifacts.get_local_account(private_key, console_safe.safe_operator.retrieve_owners())

    if local_owner in console_safe.local_owner_account_list:
        for local_owner_account in console_safe.local_owner_account_list:
            if local_owner_account == local_owner:
                console_safe.local_owner_account_list.remove(local_owner)
        console_safe.setup_sender()
    else:
        logger.error('Local Account generated via Private Key it is not Loaded')

    # Assert current loaded owner, length of local_accounts should be 0 and the values for private_key/address for the
    # sender should be None
    assert len(console_safe.local_owner_account_list) == 0
    assert console_safe.sender_private_key is None
    assert console_safe.sender_address is None


def test_is_owner():
    load_safe_command = 'loadSafe --address=0x5b1869D9A4C187F2EAa108f3062412ecf0526b24'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_safe_command)
    tmp_address = desired_parsed_item_list[0][1][0]
    console_safe = ConsoleSafeCommands(tmp_address, logger, data_artifacts, network_agent)

    # ------------------------------------------------------------------------------------------------------------------
    add_owner_safe = 'isOwner --address=0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(add_owner_safe)

    address_value = desired_parsed_item_list[0][1][0]
    console_safe.command_safe_is_owner(address_value)

    # Assert values used in the command, called the command anyways to validate proper functioning
    assert console_safe.safe_operator.retrieve_owners() == ['0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1',
                                                            '0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0',
                                                            '0x22d491Bde2303f2f43325b2108D26f1eAbA1e32b']
    assert (console_safe.safe_operator.retrieve_is_owner('0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0'))


def test_change_threshold():
    # LOAD SAFE
    # ------------------------------------------------------------------------------------------------------------------
    load_safe_command = 'loadSafe --address=0x5b1869D9A4C187F2EAa108f3062412ecf0526b24'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_safe_command)
    tmp_address = desired_parsed_item_list[0][1][0]
    console_safe = ConsoleSafeCommands(tmp_address, logger, data_artifacts, network_agent)

    # LOAD OWNER
    # ------------------------------------------------------------------------------------------------------------------
    load_fst_owner_command = 'loadOwner --private_key=0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_fst_owner_command)
    private_key = desired_parsed_item_list[0][1][0]

    local_owner = account_artifacts.get_local_account(str(private_key), console_safe.safe_operator.retrieve_owners())
    if local_owner in console_safe.local_owner_account_list:
        logger.error('Local Owner Already in local_owner_account_list')
    else:
        console_safe.local_owner_account_list.append(local_owner)
    console_safe.setup_sender()

    # Assert current loaded owner, length of local_accounts should be 1 and the values for private_key/address the fst
    # loaded user in the test
    assert len(console_safe.local_owner_account_list) == 1
    assert console_safe.sender_private_key in '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    assert console_safe.sender_address in '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'

    # CHANGE THRESHOLD
    # ------------------------------------------------------------------------------------------------------------------
    change_threshold_command = 'changeThreshold --uint=2'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(change_threshold_command)
    uint_value = desired_parsed_item_list[0][1][0]
    console_safe.command_safe_change_threshold(int(uint_value))
    # ------------------------------------------------------------------------------------------------------------------

    assert console_safe.safe_operator.retrieve_threshold() == 2

    # LOAD ANOTHER OWNER
    # ------------------------------------------------------------------------------------------------------------------
    load_snd_owner_command = 'loadOwner --private_key=0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_snd_owner_command)
    private_key = desired_parsed_item_list[0][1][0]

    local_owner = account_artifacts.get_local_account(str(private_key), console_safe.safe_operator.retrieve_owners())
    if local_owner in console_safe.local_owner_account_list:
        logger.error('Local Owner Already in local_owner_account_list')
    else:
        console_safe.local_owner_account_list.append(local_owner)
    console_safe.setup_sender()

    # Assert current loaded owner, length of local_accounts should be 2 and the values for private_key/address the snd
    # loaded user in the test
    assert len(console_safe.local_owner_account_list) == 2
    assert console_safe.sender_private_key in '0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1'
    assert console_safe.sender_address in '0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0'

    # REVERT CHANGE THRESHOLD
    # ------------------------------------------------------------------------------------------------------------------
    change_threshold_command = 'changeThreshold --uint=1'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(change_threshold_command)
    uint_value = desired_parsed_item_list[0][1][0]
    console_safe.command_safe_change_threshold(int(uint_value))

    assert console_safe.safe_operator.retrieve_threshold() == 1

    # UNLOAD OWNER
    # ------------------------------------------------------------------------------------------------------------------
    unload_owner_command = 'unloadOwner --private_key=0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(unload_owner_command)
    private_key = desired_parsed_item_list[0][1][0]

    local_owner = account_artifacts.get_local_account(private_key, console_safe.safe_operator.retrieve_owners())

    if local_owner in console_safe.local_owner_account_list:
        for local_owner_account in console_safe.local_owner_account_list:
            if local_owner_account == local_owner:
                console_safe.local_owner_account_list.remove(local_owner)
        console_safe.setup_sender()
    else:
        logger.error('Local Account generated via Private Key it is not Loaded')

    # Assert current loaded owner, length of local_accounts should be 1 and the values for private_key/address the fst
    # loaded user in the test
    assert len(console_safe.local_owner_account_list) == 1
    assert console_safe.sender_private_key in '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    assert console_safe.sender_address in '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'


def test_add_owner():
    # LOAD SAFE
    # ------------------------------------------------------------------------------------------------------------------
    load_safe_command = 'loadSafe --address=0x5b1869D9A4C187F2EAa108f3062412ecf0526b24'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_safe_command)
    tmp_address = desired_parsed_item_list[0][1][0]
    console_safe = ConsoleSafeCommands(tmp_address, logger, data_artifacts, network_agent)

    # LOAD OWNER
    # ------------------------------------------------------------------------------------------------------------------
    load_owner_command = 'loadOwner --private_key=0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_owner_command)
    private_key = desired_parsed_item_list[0][1][0]

    local_owner = account_artifacts.get_local_account(str(private_key), console_safe.safe_operator.retrieve_owners())
    if local_owner in console_safe.local_owner_account_list:
        logger.error('Local Owner Already in local_owner_account_list')
    else:
        console_safe.local_owner_account_list.append(local_owner)
    console_safe.setup_sender()

    # Assert current loaded owner, length of local_accounts should be 1 and the values for private_key/address the fst
    # loaded user in the test
    assert len(console_safe.local_owner_account_list) == 1
    assert console_safe.sender_private_key in '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    assert console_safe.sender_address in '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'

    # ADD OWNER
    # ------------------------------------------------------------------------------------------------------------------
    add_owner_command = 'addOwner --address=0xE11BA2b4D45Eaed5996Cd0823791E0C93114882d'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(add_owner_command)

    address_value = desired_parsed_item_list[0][1][0]
    console_safe.command_safe_add_owner_threshold(address_value)

    assert len(console_safe.safe_operator.retrieve_owners()) == 4
    assert console_safe.safe_operator.retrieve_is_owner(address_value)
    assert console_safe.sender_private_key in '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    assert console_safe.sender_address in '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'

def test_swap_owner():
    # LOAD SAFE
    # ------------------------------------------------------------------------------------------------------------------
    load_safe_command = 'loadSafe --address=0x5b1869D9A4C187F2EAa108f3062412ecf0526b24'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_safe_command)
    tmp_address = desired_parsed_item_list[0][1][0]
    console_safe = ConsoleSafeCommands(tmp_address, logger, data_artifacts, network_agent)

    # LOAD OWNER
    # ------------------------------------------------------------------------------------------------------------------
    load_fst_owner_command = 'loadOwner --private_key=0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_fst_owner_command)
    private_key = desired_parsed_item_list[0][1][0]

    local_owner = account_artifacts.get_local_account(str(private_key), console_safe.safe_operator.retrieve_owners())
    if local_owner in console_safe.local_owner_account_list:
        logger.error('Local Owner Already in local_owner_account_list')
    else:
        console_safe.local_owner_account_list.append(local_owner)
    console_safe.setup_sender()

    # Assert current loaded owner, length of local_accounts should be 1 and the values for private_key/address the fst
    # loaded user in the test
    assert len(console_safe.local_owner_account_list) == 1
    assert console_safe.sender_private_key in '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    assert console_safe.sender_address in '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'

    # LOAD ANOTHER OWNER
    # ------------------------------------------------------------------------------------------------------------------
    load_snd_owner_command = 'loadOwner --private_key=0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_snd_owner_command)
    private_key = desired_parsed_item_list[0][1][0]

    local_owner = account_artifacts.get_local_account(str(private_key), console_safe.safe_operator.retrieve_owners())
    if local_owner in console_safe.local_owner_account_list:
        logger.error('Local Owner Already in local_owner_account_list')
    else:
        console_safe.local_owner_account_list.append(local_owner)
    console_safe.setup_sender()

    # Assert current loaded owner, length of local_accounts should be 2 and the values for private_key/address the snd
    # loaded user in the test
    assert len(console_safe.local_owner_account_list) == 2
    assert console_safe.sender_private_key in '0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1'
    assert console_safe.sender_address in '0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0'

    # SWAP OWNER
    # ------------------------------------------------------------------------------------------------------------------
    swap_owner_command = 'swapOwner --address=0xE11BA2b4D45Eaed5996Cd0823791E0C93114882d --address=0xd03ea8624C8C5987235048901fB614fDcA89b117'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(swap_owner_command)

    address_value_to = desired_parsed_item_list[0][1][0]
    address_new_value = desired_parsed_item_list[0][1][1]
    previous_owner = setinel_helper(address_value_to, console_safe)
    console_safe.command_safe_swap_owner(previous_owner, address_value_to, address_new_value)

    assert console_safe.safe_operator.retrieve_is_owner(address_new_value)
    assert len(console_safe.safe_operator.retrieve_owners()) == 4
    assert console_safe.safe_operator.retrieve_threshold() == 2


def test_remove_owner():
    # LOAD SAFE
    # ------------------------------------------------------------------------------------------------------------------
    load_safe_command = 'loadSafe --address=0x5b1869D9A4C187F2EAa108f3062412ecf0526b24'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_safe_command)
    tmp_address = desired_parsed_item_list[0][1][0]
    console_safe = ConsoleSafeCommands(tmp_address, logger, data_artifacts, network_agent)

    # LOAD OWNER
    # ------------------------------------------------------------------------------------------------------------------
    load_fst_owner_command = 'loadOwner --private_key=0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_fst_owner_command)
    private_key = desired_parsed_item_list[0][1][0]

    local_owner = account_artifacts.get_local_account(str(private_key), console_safe.safe_operator.retrieve_owners())
    if local_owner in console_safe.local_owner_account_list:
        logger.error('Local Owner Already in local_owner_account_list')
    else:
        console_safe.local_owner_account_list.append(local_owner)
    console_safe.setup_sender()

    # Assert current loaded owner, length of local_accounts should be 1 and the values for private_key/address the fst
    # loaded user in the test
    assert len(console_safe.local_owner_account_list) == 1
    assert console_safe.sender_private_key in '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    assert console_safe.sender_address in '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'

    # LOAD ANOTHER OWNER
    # ------------------------------------------------------------------------------------------------------------------
    load_snd_owner_command = 'loadOwner --private_key=0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_snd_owner_command)
    private_key = desired_parsed_item_list[0][1][0]

    local_owner = account_artifacts.get_local_account(str(private_key), console_safe.safe_operator.retrieve_owners())
    if local_owner in console_safe.local_owner_account_list:
        logger.error('Local Owner Already in local_owner_account_list')
    else:
        console_safe.local_owner_account_list.append(local_owner)
    console_safe.setup_sender()

    # Assert current loaded owner, length of local_accounts should be 2 and the values for private_key/address the snd
    # loaded user in the test
    assert len(console_safe.local_owner_account_list) == 2
    assert console_safe.sender_private_key in '0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1'
    assert console_safe.sender_address in '0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0'

    # REMOVE OWNER
    # ------------------------------------------------------------------------------------------------------------------
    add_owner_safe = 'removeOwner --address=0xd03ea8624C8C5987235048901fB614fDcA89b117'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(add_owner_safe)

    address_value_to = desired_parsed_item_list[0][1][0]
    previous_owner = setinel_helper(address_value_to, console_safe)
    console_safe.command_safe_remove_owner(previous_owner, address_value_to)

    assert not console_safe.safe_operator.retrieve_is_owner(address_value_to)
    assert len(console_safe.safe_operator.retrieve_owners()) == 3
    assert console_safe.safe_operator.retrieve_threshold() == 1

def test_deposit_ether():
    # LOAD SAFE
    # ------------------------------------------------------------------------------------------------------------------
    load_safe_command = 'loadSafe --address=0x5b1869D9A4C187F2EAa108f3062412ecf0526b24'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_safe_command)
    tmp_address = desired_parsed_item_list[0][1][0]
    console_safe = ConsoleSafeCommands(tmp_address, logger, data_artifacts, network_agent)

    # LOAD OWNER
    # ------------------------------------------------------------------------------------------------------------------
    load_fst_owner_command = 'loadOwner --private_key=0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_fst_owner_command)
    private_key = desired_parsed_item_list[0][1][0]

    local_owner = account_artifacts.get_local_account(str(private_key), console_safe.safe_operator.retrieve_owners())
    if local_owner in console_safe.local_owner_account_list:
        logger.error('Local Owner Already in local_owner_account_list')
    else:
        console_safe.local_owner_account_list.append(local_owner)
    console_safe.setup_sender()

    # Assert current loaded owner, length of local_accounts should be 1 and the values for private_key/address the fst
    # loaded user in the test
    assert len(console_safe.local_owner_account_list) == 1
    assert console_safe.sender_private_key in '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    assert console_safe.sender_address in '0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1'

    # SEND ETHER TO THE SAFE
    # ------------------------------------------------------------------------------------------------------------------
    deposit_ether_command = 'depositEther --private_key=0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d --ether=2'
    local_account = Account.privateKeyToAccount(desired_parsed_item_list[0][1][0])
    ethereum_units_amount = desired_parsed_item_list[1:]
    ether_helper = EtherHelper(logger, network_agent.ethereum_client)
    amount_value = ether_helper.get_unify_ether_amount(ethereum_units_amount)
    console_safe.command_deposit_ether_raw(amount_value, local_account)

    #assert network_agent.ethereum_client.w3.eth.getBalance(console_safe.safe_operator.address) == network_agent.ethereum_client.w3.toWei('2', 'ether')


# def test_withdraw_ether():
#     address_value_to = desired_parsed_item_list[0][1][0]
#     ethereum_units_amount = desired_parsed_item_list[1:]
#     ether_helper = EtherHelper(self.logger, self.network_agent.ethereum_client)
#     amount_value = ether_helper.get_unify_ether_amount(ethereum_units_amount)
#     self.logger.debug0('Total Amount: {0} Wei'.format(amount_value))
#     safe_interface.command_withdraw_ether_raw(amount_value, address_value_to)
#     return

# def test_deposit_token():
#     return
#
# def test_withdraw_token():
#     return
