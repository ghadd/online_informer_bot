import os

DAY = 60 * 60 * 24
HOUR = 60 * 60
MINUTE = 60

# consider creating those files
API_ID = os.environ["TG_API_ID"]
API_HASH = os.environ["TG_API_HASH"]
BOT_TOKEN = os.environ["ONLINE_INFORMER_BOT_TOKEN"]

DEFAULT_TIMEOUT = MINUTE / 10
DEFAULT_NOTIFY_TIMEOUT = DAY
MIN_NOTIFICATION_TIMEOUT = HOUR / 2

DATABASE_PATH = os.path.abspath('./database/db.sqlite')

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
TIME_FORMAT = '%H:%M:%S'


def PROPS(cls):
    return [i for i in cls.__dict__.keys() if i[:1] != '_']
