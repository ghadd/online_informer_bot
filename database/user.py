from datetime import datetime

from peewee import *
from playhouse.sqlite_ext import JSONField

from database.tracking_user import TrackingUser
from settings.config import DATABASE_PATH, MINUTE

db = SqliteDatabase(DATABASE_PATH)


class State:
    NORMAL = 0
    ENTITY_INPUT_ADD = 1
    ENTITY_INPUT_DEL = 2
    ENTITY_INPUT_CHK = 3
    DATETIME_INPUT = 4


class User(Model):
    user_id = IntegerField()
    first_name = CharField()
    state = IntegerField(default=State.NORMAL)
    premium = BooleanField(default=False)

    users_tracking = JSONField(json_dumps=TrackingUser.custom_dumps, json_loads=TrackingUser.custom_loads, default=[])
    last_notified = DateTimeField(default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
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