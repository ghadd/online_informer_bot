from datetime import datetime

from peewee import *
from playhouse.sqlite_ext import JSONField

from database.tracking_user import TrackingUser
from settings.config import DATABASE_PATH, MINUTE, DATETIME_FORMAT

# retrieving a database by default path
db = SqliteDatabase(DATABASE_PATH)


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


class User(Model):
    """
    This class is a peewee database model, representing a telegram user.
    Usually objects of this class are referred as ``watcher`` or ``user_w``.

    Attributes
    ----------
    user_id : int
        telegram user id
    first_name : str:
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

    tracking_users = JSONField(json_dumps=TrackingUser.custom_dumps, json_loads=TrackingUser.custom_loads, default=[])
    last_notified = DateTimeField(default=datetime.now().strftime(DATETIME_FORMAT))
    notification_timeout = IntegerField(default=MINUTE / 10)

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

    class Meta:
        database = db