from datetime import datetime
from typing import List

from peewee import *
from playhouse.mysql_ext import JSONField

from database.tracking_user import TrackingUser
from settings.config import DATETIME_FORMAT, PROPS, HOUR

# retrieving a database by default path
DB_NAME = "online_informer_db"
DB_USER = "root"
DB_PASS = "fHgw[3D>/62vj~WR"
DB_HOST = "localhost"
DB_PORT = 3306

db = MySQLDatabase(DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)


class State:
    """
    This class is used like a simple enum:
    NORMAL: user is not prompted to do anything special
    ENTITY_INPUT_*: user is prompted to input an entity (either to add, delete of check)
    DATETIME_INOUT: user is prompted to input a timedelta
    """
    NORMAL = 0
    ENTITY_INPUT_ADD = 1
    ENTITY_INPUT_DEL = 2
    ENTITY_INPUT_CHK = 3
    DATETIME_INPUT = 4

    @staticmethod
    def get_value_naming(v):
        props = PROPS(State)
        for prop in props:
            if State().__getattribute__(prop) == v:
                return prop


class User(Model):
    """
    This class is a peewee database model, representing a telegram user.
    Usually objects of this class are referred as ``watcher`` or ``user_w``.

    Attributes
    ----------
    user_id : int
        telegram user id
    first_name : str
        telegram user first name (is Required)
    username : str
        telegram user username (is Optional)
    state : State
        current user's state
    premium : bool
        True if user is a premium user, False otherwise
    tracking_users : List[TrackingUser]
        list of users, current user tracks
    last_notified : datetime.datetime
        the time, user was notified last time
    notification_timeout :
        time difference between two discrete notifications
    """
    user_id = IntegerField()
    first_name = CharField()
    username = CharField(null=True)
    state = IntegerField(default=State.NORMAL)
    premium = BooleanField(default=False)

    tracking_users = JSONField(default=[])
    last_notified = DateTimeField(default=datetime.now().strftime(DATETIME_FORMAT))
    notification_timeout = IntegerField(default=6 * HOUR)

    @staticmethod
    def _set_property(tg_user, prop_name, property_value):
        user = User.get_or_none(User.user_id == tg_user.id)
        if not user:
            raise ValueError("User could not be found.")

        setattr(user, prop_name, property_value)
        user.save()

    @staticmethod
    def _get_property(tg_user, prop_name):
        user = User.get_or_none(User.user_id == tg_user.id)
        if not user:
            raise ValueError("User could not be found.")

        return getattr(user, prop_name)

    """
    Some get/update methods, based on telegram user object
    """

    @staticmethod
    def update_state(tg_user, new_state):
        User._set_property(tg_user, "state", new_state)

    @staticmethod
    def update_timeout(tg_user, new_timeout):
        User._set_property(tg_user, "notification_timeout", new_timeout)

    @staticmethod
    def update_last_notified(tg_user, new_datetime=datetime.now()):
        User._set_property(tg_user, "last_notified", new_datetime)

    @staticmethod
    def get_state(tg_user):
        return User._get_property(tg_user, "state")

    def get_tracking_users(self):
        return [TrackingUser.from_dict(de_dict) for de_dict in self.tracking_users]

    def set_tracking_users(self, tracking_users: List[TrackingUser]):
        self.tracking_users = [user_t.to_dict() for user_t in tracking_users]

    class Meta:
        database = db
