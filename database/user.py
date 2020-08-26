import json
import time
from json import JSONDecodeError

from peewee import *

from settings.config import DATABASE_PATH

db = SqliteDatabase(DATABASE_PATH)


class User(Model):
    user_id = IntegerField()
    first_name = CharField()

    users_tracking = CharField(default="[]")  # json repr of TrackingUser's
    last_notified = IntegerField(default=time.time())  # Unix time
    notification_timeout = IntegerField(default=60 * 60 * 24)  # in secs

    class Meta:
        database = db


class TrackingUser:
    def __init__(self, de_json=""):
        try:
            obj = json.loads(de_json)
            self.user_id = obj['user_id']
            self.first_name = obj['first_name']
            self.online_timeline = obj['online']
        except JSONDecodeError as err:
            raise err

    def json(self):
        return json.dumps(
            {
                "user_id": self.user_id,
                "first_name": self.first_name,
                "online": self.online_timeline
            }
        )
