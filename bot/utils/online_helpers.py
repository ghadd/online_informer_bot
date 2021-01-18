from datetime import datetime

from bot.utils import get_start_of_day
from settings import DEFAULT_TIMEOUT, DAY


def get_online_offline(user_w, user_t, whole_day=False):
    if whole_day:
        records = get_whole_day_records(user_t)
    else:
        n_records = int(user_w.notification_timeout / DEFAULT_TIMEOUT)
        records = user_t.online_timeline[-n_records:]

    online = records.count(True) * DEFAULT_TIMEOUT
    offline = len(records) * DEFAULT_TIMEOUT - online

    return online, offline


def get_whole_day_records(user_t):
    # getting the info for each hour && filling missing with zeros
    start_of_day = get_start_of_day()
    time_since_start_of_day = datetime.now() - start_of_day
    max_n_of_records = int(time_since_start_of_day.total_seconds() / DEFAULT_TIMEOUT)
    max_n_of_day_records = int(DAY // DEFAULT_TIMEOUT)
    records = user_t.online_timeline[-max_n_of_records:]

    records = records + [False for i in range(max_n_of_day_records - len(records))]
    return records