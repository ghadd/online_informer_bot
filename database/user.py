from datetime import datetime

from peewee import *
from playhouse.sqlite_ext import JSONField

from database.tracking_user import TrackingUser
from settings.config import DATABASE_PATH, MINUTE

db = SqliteDatabase(DATABASE_PATH)

class User(Model):
    user_id = IntegerField()
    first_name = CharField()

    users_tracking = JSONField(json_dumps=TrackingUser.custom_dumps, json_loads=TrackingUser.custom_loads, default=[])
    last_notified = DateTimeField(default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    notification_timeout = IntegerField(default=MINUTE / 10)

    class Meta:
        database = db
