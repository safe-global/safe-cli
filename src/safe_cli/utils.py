import os
from typing import List, Optional

from eth_typing import ChecksumAddress
from prompt_toolkit import HTML, print_formatted_text

from gnosis.eth import EthereumClient
from gnosis.safe.api import TransactionServiceApi


def get_erc_20_list(
    ethereum_client: EthereumClient,
    safe_address: str,
    from_block: int,
    to_block: int,
    block_step: int = 500000,
) -> list:
    """

    :param ethereum_client:
    :param safe_address:
    :param from_block:
    :param to_block:
    :param block_step: is the number of blocks retrieved for each get until get all blocks between from_block until to_block
    :return: a list of address of ERC20 tokens related with the safe_address
    """
    addresses = set()
    for i in range(from_block, to_block + 1, block_step):
        events = ethereum_client.erc20.get_total_transfer_history(
            from_block=i, to_block=i + (block_step - 1), addresses=[safe_address]
        )
        for event in events:
            if "value" in event["args"]:
                addresses.add(event["address"])

    return addresses


def get_input(*args, **kwargs):
    return input(*args, **kwargs)


def yes_or_no_question(question: str, default_no: bool = True) -> bool:
    if "PYTEST_CURRENT_TEST" in os.environ:
        return True  # Ignore confirmations when running tests

    choices = " [y/N]: " if default_no else " [Y/n]: "
    default_answer = "n" if default_no else "y"
    reply = str(get_input(question + choices)).lower().strip() or default_answer
    if reply[0] == "y":
        return True
    if reply[0] == "n":
        return False
    else:
        return False if default_no else True


def choose_option_from_list(
    question: str, options: List, default_option: int = 0
) -> Optional[int]:
    if "PYTEST_CURRENT_TEST" in os.environ:
        return default_option  # Ignore confirmations when running tests
    number_options = len(options)
    for number_option, option in enumerate(options):
        print_formatted_text(HTML(f"{number_option} - <b>{option}</b> "))
    choices = f" [0-{number_options - 1}] default {default_option}: "
    reply = str(get_input(question + choices)).lower().strip() or str(default_option)
    try:
        option = int(reply)
    except ValueError:
        print_formatted_text(HTML("<ansired> Option must be an integer </ansired>"))
        return None

    if option not in range(0, number_options):
        print_formatted_text(
            HTML(
                f"<ansired> {option} is not between [0-{number_options - 1}] </ansired>"
            )
        )
        return None

    return option


def get_safe_from_owner(
    owner: ChecksumAddress, node_url: str
) -> Optional[ChecksumAddress]:
    """
    Show a list of Safe to chose between them and return the selected one.
    :param owner:
    :param node_url:
    :return: Safe address of a selected Safe
    """
    ethereum_client = EthereumClient(node_url)
    safe_tx_service = TransactionServiceApi.from_ethereum_client(ethereum_client)
    safes = safe_tx_service.get_safes_for_owner(owner)
    if safes:
        option = choose_option_from_list(
            "Select the Safe to initialize the safe-cli", safes
        )
        if option is not None:
            return safes[option]
    else:
        raise ValueError(f"No safe was found for the specified owner {owner}")
