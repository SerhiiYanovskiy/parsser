import logging
import datetime
import os
import logging

CONSOLE_LOGGING_LVL = logging.DEBUG
FILE_LOGGING_LVL = logging.DEBUG


# Chance of letter replace
# Value must be between 0 and 1
# For disable randomize text set -1
CHANCE = -1

# File with accounts
# Account format can be viewed in README.txt
ACCOUNTS = 'data/accounts.txt'
PROXY = 'data/proxy.txt'
MESSAGES = 'data/messages.txt'

SAVE_LOG_TO_FILE = False

# If you like set date of log in name add {}
# Example:
#   log_{}.log - file with date
#   log.log - file without date
LOGS_FILE = 'log_{}.log'

# Wait before send message
# (min, max)
WAIT = (0, 1)

# Wait after request for get data
WAIT_BETWEEN_REQUESTS = 1

# Seconds between sending a message from 1 account
SECONDS = 10

# Timeout between parsing members
TIMEOUT = 1

# Count of workers
THREADS = 2

# Api Key for solve captcha
CAPTCHA_API_KEY = 'c67e6c0e8e7cdc90e50d2c257f2e061f'

# Number of attempts to solve captcha
MAX_RETRY_CAPTCHA_SOLVE = 5

# Number of attempts to send the message
MAX_TRY_SEND_MESSAGE = 3

# 0 - https://capmonster.cloud/
# 1 - http://anti-captcha.com/
ANTI_CAPTCHA_SERVICE = 1



logging.SUCCESS = 25
logging.addLevelName(logging.SUCCESS, 'SUCCESS')
logging.NEW_MEMBER = 26
logging.addLevelName(logging.NEW_MEMBER, 'NEW_MEMBER')


class CustomFormatter(logging.Formatter):
    grey = '\033[90m'
    blue = '\033[94m'
    yellow = '\033[93m'
    red = '\033[91m'
    bold_red = '\033[41m'
    green = '\033[92m'
    new_member = '\033[95m'
    reset = '\033[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.SUCCESS: self.green + self.fmt + self.reset,
            logging.NEW_MEMBER: self.new_member + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

fmt = '%(asctime)s | %(message)s'

stdout_handler = logging.StreamHandler()
stdout_handler.setLevel(CONSOLE_LOGGING_LVL)
stdout_handler.setFormatter(CustomFormatter(fmt))
logger.addHandler(stdout_handler)

setattr(logger, 'success', lambda message, *args: logger._log(logging.SUCCESS, message, args))
setattr(logger, 'new_member', lambda message, *args: logger._log(logging.NEW_MEMBER, message, args))


if SAVE_LOG_TO_FILE:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = logging.FileHandler('logs/'+LOGS_FILE.format(datetime.datetime.now().strftime('%Y_%m_%d-%H-%M-%S')))
    file_handler.setLevel(FILE_LOGGING_LVL)
    file_handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(file_handler)

