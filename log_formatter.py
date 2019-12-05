
from core.logger.logging_messages import LoggingMessagesFormatter

# Importing Custom Logger & Logging Modules
from core.logger.custom_logger import CustomLogger, DEBUG0
import logging
from logging import INFO


logging_lvl = DEBUG0
logger = CustomLogger(__name__, INFO)

# CustomLogger Format Definition: Output Init Configuration
formatter = logging.Formatter(fmt='[ %(levelname)s ]: %(message)s')

# Custom Logger Console Configuration: Console Init Configuration
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(level=logging_lvl)

logging_msg_formatter = LoggingMessagesFormatter()
print(logging_msg_formatter.log_banner())
print(logging_msg_formatter.log_error_footer())
print(logging_msg_formatter.log_success_footer())
