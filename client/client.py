"""
This file uses telegram user api (based on telethon) in order to monitor users' online status.

Restrictions
    * As a real TG account is used as monitor, if user status is ``last seen recently``, henceforth
    that user denied your access to his/her online status.
"""
from typing import Optional

from telethon.sync import TelegramClient
from telethon.tl.types import UserStatusOnline

from settings.config import API_ID, API_HASH
from settings.logger import get_logger

logger = get_logger(__name__)


class ClientMonitor:
    """
    This class objects are basically telegram user entities, able to check online status of given entities.

    Attributes
    ----------
    entity_qualifier : Optional[str, int]
        any entity identifier, determining the user entity
    """
    def __init__(self, entity_qualifier: Optional[str, int]):
        self.entity_qualifier = entity_qualifier

    @staticmethod
    def get_entity(entity_qualifier):
        with TelegramClient(__file__, API_ID, API_HASH) as client:
            return client.get_entity(entity_qualifier)

    def is_online(self) -> bool:
        """
        Returns
        -------
        True is entity at self.entity_qualifier is online and False otherwise

        Raises
        ------
        ValueError
            When entity is not provided or it is invalid User entity
        """
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
