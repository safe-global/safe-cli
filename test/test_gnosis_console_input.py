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

def test_load_safe():
    load_safe_command = 'loadSafe --address=0x5b1869D9A4C187F2EAa108f3062412ecf0526b24'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_safe_command)
    tmp_address = desired_parsed_item_list[0][1][0]
    console_safe = ConsoleSafeCommands(tmp_address, logger, data_artifacts, network_agent)


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
    logger.debug0('[ Signature Value ]: {0} {1}'.format(str(private_key), console_safe.safe_operator.retrieve_owners()))
    local_owner = account_artifacts.get_local_account(str(private_key), console_safe.safe_operator.retrieve_owners())
    if local_owner in console_safe.local_owner_account_list:
        logger.error('Local Owner Already in local_owner_account_list')
    else:
        console_safe.local_owner_account_list.append(local_owner)
        logger.debug0('[ Local Account Added ]: {0}'.format(console_safe.local_owner_account_list))
    console_safe.setup_sender()


def test_unload_safe_owner():
    load_safe_command = 'loadSafe --address=0x5b1869D9A4C187F2EAa108f3062412ecf0526b24'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_safe_command)
    tmp_address = desired_parsed_item_list[0][1][0]
    console_safe = ConsoleSafeCommands(tmp_address, logger, data_artifacts, network_agent)

    # ------------------------------------------------------------------------------------------------------------------
    load_owner_safe = 'loadOwner --private_key=0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_owner_safe)
    private_key = desired_parsed_item_list[0][1][0]
    logger.debug0('[ Signature Value ]: {0} {1}'.format(str(private_key), console_safe.safe_operator.retrieve_owners()))
    local_owner = account_artifacts.get_local_account(str(private_key), console_safe.safe_operator.retrieve_owners())
    if local_owner in console_safe.local_owner_account_list:
        logger.error('Local Owner Already in local_owner_account_list')
    else:
        console_safe.local_owner_account_list.append(local_owner)
        logger.debug0('[ Local Account Added ]: {0}'.format(console_safe.local_owner_account_list))
    console_safe.setup_sender()

    # bug: when only there is one in the list, the variables need to be put to None
    # ------------------------------------------------------------------------------------------------------------------
    load_owner_safe = 'loadOwner --private_key=0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_owner_safe)
    private_key = desired_parsed_item_list[0][1][0]
    logger.debug0('[ Signature Value ]: {0} {1}'.format(str(private_key), console_safe.safe_operator.retrieve_owners()))
    local_owner = account_artifacts.get_local_account(str(private_key), console_safe.safe_operator.retrieve_owners())
    if local_owner in console_safe.local_owner_account_list:
        logger.error('Local Owner Already in local_owner_account_list')
    else:
        console_safe.local_owner_account_list.append(local_owner)
        logger.debug0('[ Local Account Added ]: {0}'.format(console_safe.local_owner_account_list))
    console_safe.setup_sender()

    # ------------------------------------------------------------------------------------------------------------------
    unload_safe_command = 'unloadOwner --private_key=0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(unload_safe_command)
    private_key = desired_parsed_item_list[0][1][0]
    logger.debug0('[ Signature Value ]: {0} {1}'.format(str(private_key), console_safe.safe_operator.retrieve_owners()))
    local_owner = account_artifacts.get_local_account(private_key, console_safe.safe_operator.retrieve_owners())

    if local_owner in console_safe.local_owner_account_list:
        for local_owner_account in console_safe.local_owner_account_list:
            if local_owner_account == local_owner:
                logger.debug0('REMOVING LOCAL ACCOUNT')
                console_safe.local_owner_account_list.remove(local_owner)

        console_safe.setup_sender()
        logger.debug0('[ Local Account Subs ]: {0}'.format(console_safe.local_owner_account_list))
    else:
        logger.error('Local Account generated via Private Key it is not Loaded')


def test_change_threshold():
    load_safe_command = 'loadSafe --address=0x5b1869D9A4C187F2EAa108f3062412ecf0526b24'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_safe_command)
    tmp_address = desired_parsed_item_list[0][1][0]
    console_safe = ConsoleSafeCommands(tmp_address, logger, data_artifacts, network_agent)

    # ------------------------------------------------------------------------------------------------------------------
    load_owner_safe = 'loadOwner --private_key=0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(load_owner_safe)
    private_key = desired_parsed_item_list[0][1][0]
    logger.debug0('[ Signature Value ]: {0} {1}'.format(str(private_key), console_safe.safe_operator.retrieve_owners()))
    local_owner = account_artifacts.get_local_account(str(private_key), console_safe.safe_operator.retrieve_owners())
    if local_owner in console_safe.local_owner_account_list:
        logger.error('Local Owner Already in local_owner_account_list')
    else:
        console_safe.local_owner_account_list.append(local_owner)
        logger.debug0('[ Local Account Added ]: {0}'.format(console_safe.local_owner_account_list))
    console_safe.setup_sender()

    # ------------------------------------------------------------------------------------------------------------------
    change_owner = 'changeThreshold --uint=2'
    desired_parsed_item_list, priority_group, command_argument, argument_list = \
        console_getter.get_gnosis_input_command_argument(change_owner)
    uint_value = desired_parsed_item_list[0][1][0]
    console_safe.command_safe_change_threshold(int(uint_value))