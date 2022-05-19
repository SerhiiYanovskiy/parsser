import random
import time
import discum
from exceptions import *
from color_logger import logger
from randomize import randomise
from config import WAIT, MAX_RETRY_CAPTCHA_SOLVE
from data import messages
from solve_captcha import solve


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
