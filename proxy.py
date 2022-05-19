import sys
from pathlib import Path
import requests
from threading import Thread, Lock
from color_logger import logger
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


lock = Lock()
script_location = Path(__file__).absolute().parent


def test_proxy(proxy, results):
    try:
        requests.get('https://api.ipify.org?format=json', proxies={
            'http': proxy,
            'https': proxy
        }, timeout=5)
        with lock:
            results.append(proxy)
    except Exception as e:
        with lock:
            logger.debug(f'Bag proxy - {proxy}, {e}')


def test_proxies(_proxies):
    results = []
    logger.debug('Proxies testing start')
    threads = [Thread(target=test_proxy, args=(proxy, results)) for proxy in _proxies]
    [thread.start() for thread in threads]
    [thread.join() for thread in threads]
    logger.info(f'Proxies tested - {len(results)}/{len(_proxies)} valid')
    return results


with open(script_location / PROXY, 'r') as f:
    proxies = test_proxies([i.strip() for i in f.readlines()])


def get_proxy():
    try:
        return proxies.pop()
    except IndexError:
        logger.error('No proxy')
        sys.exit()
