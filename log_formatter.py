
from core.logger.logging_messages import LoggingMessagesFormatter

# Importing Custom Logger & Logging Modules
from core.logger.custom_logger import CustomLogger, DEBUG0
import logging


logging_lvl = DEBUG0
logger = CustomLogger(__name__, logging_lvl)

# CustomLogger Format Definition: Output Init Configuration
formatter = logging.Formatter(fmt='[ %(levelname)s ]: %(message)s')

# Custom Logger Console Configuration: Console Init Configuration
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(level=logging_lvl)

logging_msg_formatter = LoggingMessagesFormatter(logger)
# logging_msg_formatter.log_banner()
#logging_msg_formatter.log_error_footer()
logging_msg_formatter.log_footer()
