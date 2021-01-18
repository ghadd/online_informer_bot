import re
from datetime import timedelta

import requests
import telethon
from telebot.apihelper import ApiTelegramException

from client import ClientMonitor
from database.user import *
from settings.logger import *
from .chart import *
from .inline_markups import *
from .keyboard_markups import *

logger = get_logger(__name__)


def get_track_info(user, certain_record=None):
    if not user.users_tracking:
        f'{user.first_name}({user.user_id}) has no one to track'
        return ""
    logger.info(f'Gathering track info for {user.first_name}({user.user_id}).')

    users_tracking = user.users_tracking
    info = ''

    if certain_record:
        logger.info(f'Info for {user.first_name}({user.user_id}) is being gathered about {certain_record.first_name}'
                    f'({certain_record.id}).')
        users_tracking = filter(lambda x: x.user_id == certain_record.id, user.users_tracking)

    for user_t in users_tracking:
        n_records = int(user.notification_timeout / DEFAULT_TIMEOUT)
        records = user_t.online_timeline[-n_records:]
        online = records.count(True) * DEFAULT_TIMEOUT
        total = len(records) * DEFAULT_TIMEOUT  # in secs

        online_status = f'was online for {get_labeled_time(online)}' if online else 'was not online'
        info += f'{user_t.first_name} in last {get_labeled_time(total)} {online_status}\n'

    return f'`{info}`'


def send_photo_chart(bot, user, certain_record):
    users_tracking = list(filter(lambda x: x.user_id == certain_record.id, user.users_tracking))

    if users_tracking:
        user_t = users_tracking[0]
    else:
        return

    logger.info(f'Maintaining data for building chart about {certain_record.first_name}({certain_record.id}).')
    n_records = int(user.notification_timeout / DEFAULT_TIMEOUT)
    online_int = [int(rec) for rec in user_t.online_timeline[-n_records:]]
    chunk = int(HOUR / DEFAULT_TIMEOUT)
    data = [sum(online_int[i:i + chunk]) * DEFAULT_TIMEOUT / HOUR for i in range(0, len(online_int), chunk)]
    labels = [(datetime.now() - timedelta(hours=i)).strftime('%H:%M:%S') for i in range(len(data))][::-1]

    photo_url = get_image_link(labels, data)
    response = requests.get(photo_url)

    logger.info(f'Downloading chart about {certain_record.first_name}({certain_record.id}) '
                f'to file {CHART_BLANK.format(user.user_id, certain_record.id)}.')
    file = open(CHART_BLANK.format(user.user_id, certain_record.id), "wb")
    file.write(response.content)
    file.close()

    logger.info(f'Sending chart about {certain_record.first_name}({certain_record.id}) '
                f'to {user.first_name}({user.user_id}).')
    bot.send_photo(
        user.user_id,
        open(CHART_BLANK.format(user.user_id, certain_record.id), "rb"),
        caption=f'{certain_record.first_name} stats.'
    )


def notify_user(bot, user, certain_record=None):
    try:
        bot.send_message(
            user.user_id,
            get_track_info(user, certain_record=certain_record),
            reply_markup=REMOVE,
            parse_mode='Markdown'
        )
    except ApiTelegramException as e:
        raise e

    logger.info(f'Performing notification for {user.first_name}({user.user_id}) done.')

    if certain_record:
        send_photo_chart(bot, user, certain_record)
    else:
        user.last_notified = datetime.now()
        user.save()


def get_working_entity(bot, msg):
    entity_qualifier = msg.text

    entity = ClientMonitor.get_entity(entity_qualifier)
    if not isinstance(entity, telethon.types.User):
        bot.send_message(
            msg.from_user.id,
            'I was not able to find this user.'
        )
        User.set_state(msg.from_user, State.NORMAL)
        raise ValueError(f'Got non-user entity `{entity_qualifier}`')
    return entity


def CURRENTLY_UNAVAILABLE(bot, user_id):
    bot.send_message(
        user_id,
        "This feature is currently unavailable",
        reply_markup=menu_markup
    )


def _get_in_secs(timeout):
    # turns expression like '234' or '7h' or '3m' etc to corresponding number of seconds
    try:
        return int(timeout)
    except ValueError:
        pass

    try:
        return int(timeout[:timeout.index('m')]) * MINUTE
    except ValueError:
        pass

    try:
        return int(timeout[:timeout.index('h')]) * HOUR
    except ValueError:
        pass

    try:
        return int(timeout[:timeout.index('d')]) * DAY
    except ValueError:
        pass

    return 0


def get_in_secs(timeout):
    # possible format "1d 2h 35s"
    sep = timeout.split()
    res = 0

    for el in sep:
        res += _get_in_secs(el)

    return res


def smart_join(sep, elements):
    # deletes null-objects before regular joining
    elements = list(filter(lambda x: x, elements))
    return sep.join(elements)


def get_labeled_time(timeout):
    d = timeout // DAY
    h = (timeout - d * DAY) // HOUR
    m = (timeout - d * DAY - h * HOUR) // MINUTE
    s = (timeout - d * DAY - h * HOUR - m * MINUTE)

    if d:
        return smart_join(', ', [f'{d} day{"s" if d > 1 else ""}', get_labeled_time(timeout - d * DAY)])

    if h:
        return smart_join(', ', [f'{h} hour{"s" if h > 1 else ""}', get_labeled_time(timeout - h * HOUR)])

    if m:
        return smart_join(', ', [f'{m} minute{"s" if m > 1 else ""}', get_labeled_time(timeout - m * MINUTE)])

    return f'{timeout} second{"s" if s > 1 else ""}' if timeout else ''


def validate_timeout(timeout_string):
    regex_string = r"(\d+[dhms] *)*"
    regex = re.compile(regex_string)

    match = regex.match(timeout_string)
    if not match.span()[1] == len(timeout_string):
        raise ValueError("Invalid timeout string format")
