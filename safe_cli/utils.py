import os

from gnosis.eth import EthereumClient


# Return a list of address of ERC20 tokens related with the safe_address
# block_step is the number of blocks retrieved for each get until get all blocks between from_block until to_block
def get_erc_20_list(
    ethereum_client: EthereumClient,
    safe_address: str,
    from_block: int,
    to_block: int,
    block_step: int = 500000,
) -> list:
    addresses = set()
    for i in range(from_block, to_block + 1, block_step):
        events = ethereum_client.erc20.get_total_transfer_history(
            from_block=i, to_block=i + (block_step - 1), addresses=[safe_address]
        )
        for event in events:
            if "value" in event["args"]:
                addresses.add(event["address"])

    return addresses


def yes_or_no_question(question: str, default_no: bool = True) -> bool:
    if "PYTEST_CURRENT_TEST" in os.environ:
        return True  # Ignore confirmations when running tests
    choices = " [y/N]: " if default_no else " [Y/n]: "
    default_answer = "n" if default_no else "y"
    reply = str(input(question + choices)).lower().strip() or default_answer
    if reply[0] == "y":
        return True
    if reply[0] == "n":
        return False
    else:
        return False if default_no else True
