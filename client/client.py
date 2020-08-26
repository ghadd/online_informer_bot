from telethon.sync import TelegramClient
from telethon.tl.types import UserStatusOnline

from settings.config import API_ID, API_HASH
from settings.logger import get_logger

logger = get_logger(__name__)


def is_online(username="", user_id=0):
    with TelegramClient(__file__, API_ID, API_HASH) as client:
        user = None

        if username:
            try:
                user = client.get_entity(username)
            except ValueError:
                logger.error(f'User with username `{username}` cannot be found.')
        else:
            try:
                user = client.get_entity(user_id)
            except ValueError:
                logger.error(f'User with id `{user_id}` cannot be found.')

        if user:
            return isinstance(user.status, UserStatusOnline)


def get_entity(entity_id):
    with TelegramClient(__file__, API_ID, API_HASH) as client:
        entity = client.get_entity(entity_id)
        return entity
