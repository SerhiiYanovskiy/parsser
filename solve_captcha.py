import time
import requests
from config import CAPTCHA_API_KEY, ANTI_CAPTCHA_SERVICE
from color_logger import logger

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
