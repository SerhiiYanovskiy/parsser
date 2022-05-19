import time
import requests
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


SERVICES = [
    'https://api.capmonster.cloud',
    'https://api.anti-captcha.com'
]


def solve(captcha_site_key, user_agent, cookies=None, data="", proxy=None):
    if ANTI_CAPTCHA_SERVICE in (0, 1):
        return solve_anti_captcha(captcha_site_key, user_agent, cookies, data, proxy)


def solve_anti_captcha(captcha_site_key, user_agent, cookies=None, __data="", proxy=None):
    if cookies is None:
        cookies = dict()
    logger.debug('[Captcha Solver] Start solving captcha')
    data = {
        "clientKey": CAPTCHA_API_KEY,
        "task":
            {
                "type": "HCaptchaTask" if proxy else 'HCaptchaTaskProxyless',
                "websiteURL": 'https://discord.com/channels/@me',
                "websiteKey": captcha_site_key,
                "data": __data,
                "cookies": ';'.join(f'{name}={value}' for name, value in zip(cookies.keys(), cookies.values())),
                "userAgent": user_agent
            }
    }
    if proxy:
        (login, password), (address, port) = [i.split(':') for i in proxy.split('@')]
        _proxy = {"proxyType": "http",
                  "proxyAddress": address,
                  "proxyPort": int(port),
                  "proxyLogin": login,
                  "proxyPassword": password}
        data['task'] = {**data['task'], **_proxy}
    r = requests.post(f'{SERVICES[ANTI_CAPTCHA_SERVICE]}/createTask', json=data)
    logger.debug(r.json())
    logger.info(f'[Captcha Solver] Id of captcha {r.json()["taskId"]}')
    return __get_result(r.json()['taskId'])


def __get_result(task_id):
    logger.debug('[Captcha Solver] Wait result of captcha')
    time.sleep(15)
    for _ in range(12):
        r = requests.get(f'{SERVICES[ANTI_CAPTCHA_SERVICE]}/getTaskResult',
                         json={"clientKey": CAPTCHA_API_KEY, "taskId": task_id})
        logger.debug(r.json())
        if r.json().get('status') == 'ready':
            logger.success('[Captcha Solver] Captcha solved')
            return r.json()['solution']['gRecaptchaResponse']
        else:
            logger.info(f'[Captcha Solver] Captcha not ready')
        time.sleep(5)
