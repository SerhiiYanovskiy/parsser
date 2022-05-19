import random
import sys
import time
from parser import Parser
from message_sender import MessageSender
from exceptions import BadToken
from on_join import OnJoin
from multiprocessing import Queue, Process, Manager
from data import parse_accounts, message_accounts, del_token
from color_logger import logger
from threading import Thread
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



def __return_client(_message_senders, client):
    logger.debug(f'[Worker] Account will return to the queue in {SECONDS} seconds')
    time.sleep(SECONDS)
    _message_senders.put(client)
    logger.debug(f'[Worker] Account returned to the queue')


def worker(_queue, _message_senders):
    while True:
        try:
            data = _queue.get()
            is_no_tokens = False
            for _ in range(MAX_TRY_SEND_MESSAGE):
                client = _message_senders.get()
                try:
                    message_sender = MessageSender(token=client['token'], log=False, proxy=client['proxy'])
                    time.sleep(random.randint(*WAIT))
                    is_send_message = message_sender.send_message(*data)
                    if is_send_message:
                        if del_token(client['token']):
                            is_no_tokens = True
                    else:
                        Thread(target=__return_client, args=(_message_senders, client)).start()
                    break
                except BadToken:
                    if del_token(client['token']):
                        is_no_tokens = True
                        break
            if is_no_tokens:
                break
        except KeyboardInterrupt:
            break


def start_parser(_token, _proxy, _channels, _queue):
    try:
        if _channels:
            _parser = Parser(token=_token, log=False, proxy=_proxy, queue=_queue)
            _parser.parse_members(_channels)
        else:
            _on_join = OnJoin(token=_token, log=False, proxy=_proxy, queue=_queue)
            _on_join.start_on_join_parser()
    except BadToken:
        del_token(_token)


if __name__ == '__main__':
    queue = Queue()
    manager = Manager()
    message_senders = Queue()
    parsers = []

    if not parse_accounts or not message_accounts:
        logger.critical(f'No {"parser" if not parse_accounts else "message"} accounts')
        sys.exit()

    from proxy import get_proxy

    for token, is_use_proxy in message_accounts:
        message_senders.put({'proxy': get_proxy() if int(is_use_proxy) else None, 'token': token})

    for token, is_use_proxy, channels in parse_accounts:
        parsers.append(Process(target=start_parser, args=(token, get_proxy() if int(is_use_proxy) else None,
                                                          channels, queue), daemon=True))
        parsers[-1].start()

    threads = [Process(target=worker, args=(queue, message_senders), daemon=True) for worker_id in range(THREADS)]
    for thread in threads:
        logger.info(f'[Worker] Started')
        thread.start()

    try:
        while True:
            if not all(map(lambda x: x.is_alive(), threads)) or not any(map(lambda x: x.is_alive(), parsers)):
                break
    except KeyboardInterrupt:
        pass
