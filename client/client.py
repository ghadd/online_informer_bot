from telethon.sync import TelegramClient
from telethon.tl.types import UserStatusOnline

from settings.config import API_ID, API_HASH
from settings.logger import get_logger

logger = get_logger(__name__)


class ClientMonitor:
    def __init__(self, entity_qualifier):
        self.entity_qualifier = entity_qualifier

    @staticmethod
    def get_entity(entity_qualifier):
        with TelegramClient(__file__, API_ID, API_HASH) as client:
            return client.get_entity(entity_qualifier)

    def is_online(self):
        with TelegramClient(__file__, API_ID, API_HASH) as client:
            user = None

            if not self.entity_qualifier:
                raise ValueError("No entity qualifier provided.")

            try:
                user = client.get_entity(self.entity_qualifier)
            except ValueError:
                logger.error(f'User with entity qualifier `{self.entity_qualifier}` cannot be found.')

            if user:
                return isinstance(user.status, UserStatusOnline)
