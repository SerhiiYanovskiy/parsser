import random
import time
import discum
from exceptions import *
from color_logger import logger
from randomize import randomise
from data import messages
from solve_captcha import solve
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


class MessageSender(discum.Client):
    def __init__(self, *args, **kwargs):
        self.__token = kwargs["token"]
        self.__proxy = kwargs["proxy"]
        logger.debug(f'[MessageSender] Starting with token {kwargs["token"]}')
        super().__init__(*args, **kwargs)
        if not self.checkToken(kwargs['token'])[0]:
            logger.debug(f'[MessageSender] Bad token {kwargs["token"]}')
            raise BadToken
        logger.info(f'[MessageSender] Success start with token {kwargs["token"]}')

    @staticmethod
    def __resp_decode(response) -> dict:
        logger.debug(response.text)
        try:
            return response.json()
        except Exception as e:
            logger.critical(f'[MessageSender] {e.__class__}: {e.args[0]}')
            return None

    def send_message(self, guild_id, member_id, name):
        captcha_key, token, resp = None, None, {}
        response_dm = self.__resp_decode(self.createDM([int(member_id)]))
        channel_id = response_dm.get('id', None)
        logger.debug(f'[MessageSender] Created DM {channel_id}')
        time.sleep(random.randint(*WAIT))
        for _ in range(MAX_RETRY_CAPTCHA_SOLVE):
            resp = self.__resp_decode(self.sendMessage(channel_id, randomise(
                messages.get(guild_id, list(messages.values())[0])).format(user=member_id), captcha_key=captcha_key, token=token))
            if not resp.get('captcha_sitekey', None):
                break
            logger.warning(f'[MessageSender] Captcha required')
            proxy = self.__proxy.replace('http://', '') if self.__proxy else None
            captcha_key = solve(resp['captcha_sitekey'], self._user_agent, self.s.cookies,
                                resp['captcha_rqdata'], proxy=proxy)
            token = resp['captcha_rqtoken']
        else:
            logger.error(f'[MessageSender] Problems with solving captcha')
            return True

        if not resp.get('content', None):
            logger.error(f'[MessageSender] Fail send message to «{name}»')
        else:
            logger.success(f'[MessageSender] Success send message to «{name}»')
