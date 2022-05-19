import sys
from pathlib import Path
import requests
from threading import Thread, Lock
from color_logger import logger
from config import PROXY

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
