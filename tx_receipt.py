# Importing Custom Logger & Logging Modules
from core.logger.custom_logger import CustomLogger, DEBUG0
import logging
from core.input.console_input_getter import ConsoleInputGetter
from gnosis.eth.ethereum_client import EthereumClient
from attributedict.collections import AttributeDict
from hexbytes import HexBytes
from enum import Enum

class TypeOfTokens(Enum):
    ERC20 = 'ERC20'
    ERC721 = 'ERC721'


send_ether_amount = 'sendEther --address=0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e --ether=1000 --ether=2 --gwei=10'

logging_lvl = DEBUG0
logger = CustomLogger(__name__, logging_lvl)

# CustomLogger Format Definition: Output Init Configuration
formatter = logging.Formatter(fmt='[ %(levelname)s ]: %(message)s')

# Custom Logger Console Configuration: Console Init Configuration
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(level=logging_lvl)
