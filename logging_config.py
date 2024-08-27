import sys
import logging


LOG_LEVEL = logging.DEBUG

# Logging settings
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

# Logging to file
file_handler = logging.FileHandler('hamster.log', mode='w')
file_handler.setLevel(LOG_LEVEL)
file_formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s -  %(threadName)s - %(message)s',
                                   datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Logging to console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(LOG_LEVEL)
console_formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s -  %(threadName)s - %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)
