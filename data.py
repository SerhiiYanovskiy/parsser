from pathlib import Path
from color_logger import logger
from collections import defaultdict
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


script_location = Path(__file__).absolute().parent


with open(script_location / ACCOUNTS, 'r') as f:
    parse_accounts, message_accounts = [], []
    for account in [[i for i in line.strip().split(':') if i] for line in f.readlines() if line]:
        if account:
            (parse_accounts if int(account[0]) else message_accounts).append(account[1:])
    result = defaultdict(list)
    for i in parse_accounts:
        if len(i) > 2:
            result[i[0]].append(i[2:])
    parse_accounts = {i[0]: [i[0], i[1], result[i[0]]] for i in parse_accounts}.values()

with open(script_location / MESSAGES, 'r') as f:
    messages = {}
    for line in f.readlines():
        data = line.strip().split(':', 1)
        messages[data[0]] = data[1]


def del_token(token):
    global parse_accounts
    global message_accounts
    parse_accounts = list(filter(lambda x: x[0] != token, parse_accounts))
    message_accounts = list(filter(lambda x: x[0] != token, message_accounts))
    with open(script_location / ACCOUNTS, 'w') as file:
        for account_data in parse_accounts:
            if account_data[2]:
                for additional_data in account_data[2]:
                    file.write(f'1:{":".join(account_data[:2]+additional_data)}\n')
            else:
                file.write(f'1:{":".join(account_data[:2])}\n')
        [file.write(f'0:{":".join(i)}\n') for i in message_accounts]
    with open(script_location / 'bad_tokens.txt', 'a+') as file:
        file.write(f'{token}\n')
    if not parse_accounts or not message_accounts:
        logger.critical(f'No {"parser" if not parse_accounts else "message"} accounts')
        return True
