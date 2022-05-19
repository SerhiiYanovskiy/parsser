import time
import discum
from color_logger import logger
from collections import defaultdict
from exceptions import *
from config import TIMEOUT, WAIT_BETWEEN_REQUESTS
from datetime import datetime
from threading import Thread


class Parser(discum.Client):
    def __init__(self, *args, **kwargs):
        self.__queue = kwargs.pop('queue')
        self.__start_time = datetime.utcnow()
        self.__last_members = defaultdict(set)
        self.__users = list()

        logger.debug(f'[Parser] Starting with token {kwargs["token"]}')
        super().__init__(*args, **kwargs)
        if not self.checkToken(kwargs['token'])[0]:
            logger.debug(f'[Parser] Bad token {kwargs["token"]}')
            raise BadToken
        logger.info(f'[Parser] Success start with token {kwargs["token"]}')

    def __new_members_check(self, guild_id):
        members = self.gateway.session.guild(guild_id).members.copy()
        for member_id, member in zip(members.keys(), members.values()):
            try:
                joined_at = datetime.strptime(member['joined_at'], '%Y-%m-%dT%H:%M:%S+00:00')
            except ValueError:
                joined_at = datetime.strptime(member['joined_at'], '%Y-%m-%dT%H:%M:%S.%f+00:00')

            if joined_at < self.__start_time or member_id in self.__users:
                continue
            self.__users.append(member_id)
            logger.new_member(f'[Parser] New member {member["username"]}#{member["discriminator"]}')
            self.__queue.put((guild_id, member['presence']['user']['id'], member['username']))

    def __close_after_fetching(self, event, guild_id):
        if self.gateway.finishedMemberFetching(guild_id):
            logger.debug(f'[Parser] Success parsed {len(self.gateway.session.guild(guild_id).members)} members in {guild_id}')
            self.gateway.removeCommand({'function': self.__close_after_fetching, 'params': {'guild_id': guild_id}})
            self.gateway.close()
        elif event.event.response['t'] == 'GUILD_MEMBER_LIST_UPDATE':
            try:
                update_members = set(self.gateway.session.guild(guild_id).members)
                new_members = list(update_members - self.__last_members[guild_id])
                if new_members:
                    logger.debug(f'[Parser] Parsed {len(self.gateway.session.guild(guild_id).members)} members in {guild_id}')
                    self.__new_members_check(guild_id)
                self.__last_members[guild_id] = set(self.gateway.session.guild(guild_id).members)
            except KeyError:
                pass

    def __parse_members(self, guild_id, channel_id):
        self.gateway.fetchMembers(guild_id, channel_id, keep="all", wait=WAIT_BETWEEN_REQUESTS)
        self.gateway.command({'function': self.__close_after_fetching, 'params': {'guild_id': guild_id}})
        self.gateway.run(auto_reconnect=True)

    def _parse_members(self, guild_id, channel_id):
        while True:
            self.__last_members[guild_id].clear()
            logger.debug(f'[Parser] Parsing {guild_id}...')
            self.__parse_members(guild_id, channel_id)
            logger.debug(f'[Parser] Wait {TIMEOUT} seconds...')
            time.sleep(TIMEOUT)

    def parse_members(self, channels):
        threads = list()
        for guild_id, channel_id in channels:
            logger.info(f'[Parser] Start member parser for {guild_id}')
            threads.append(Thread(target=self._parse_members, args=(guild_id, channel_id), daemon=True))
            threads[-1].start()

        try:
            [thread.join() for thread in threads]
        except KeyboardInterrupt:
            pass
