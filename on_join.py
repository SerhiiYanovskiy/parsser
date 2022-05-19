import discum
from color_logger import logger
from collections import defaultdict
from exceptions import *
from datetime import datetime


class OnJoin(discum.Client):
    def __init__(self, *args, **kwargs):
        self.__queue = kwargs.pop('queue')
        self.__start_time = datetime.utcnow()
        self.__last_members = defaultdict(set)
        self.__users = list()

        logger.debug(f'[OnJoin] Starting with token {kwargs["token"]}')
        super().__init__(*args, **kwargs)
        if not self.checkToken(kwargs['token'])[0]:
            logger.debug(f'[OnJoin] Bad token {kwargs["token"]}')
            raise BadToken
        logger.info(f'[OnJoin] Success start with token {kwargs["token"]}')

    def __new_data(self, resp):
        if resp.event.message:
            message = resp.parsed.auto()
            if message['type'] == 'guild_member_joined':
                logger.new_member(f'[Parser] New member {message["author"]["username"]}#{message["author"]["discriminator"]}')
                self.__queue.put((message['guild_id'], message['author']['id'], message['author']['username']))

    def start_on_join_parser(self):
        logger.debug('[OnJoin] Waiting for new members...')
        self.gateway.command({'function': self.__new_data})
        self.gateway.run(auto_reconnect=True)
