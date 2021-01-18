import re
from datetime import datetime, date

from settings import MINUTE, HOUR, DAY


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
    d = int(timeout // DAY)
    h = int(timeout // HOUR)
    m = int(timeout // MINUTE)
    s = int(timeout)

    if d:
        return smart_join(' ', [f'{d} day{"s" if d > 1 else ""}', get_labeled_time(timeout - d * DAY)])

    if h:
        return smart_join(' ', [f'{h} hour{"s" if h > 1 else ""}', get_labeled_time(timeout - h * HOUR)])

    if m:
        return smart_join(' ', [f'{m} minute{"s" if m > 1 else ""}', get_labeled_time(timeout - m * MINUTE)])

    return f'{s} second{"s" if s > 1 else ""}' if s else ''


def validate_timeout(timeout_string):
    regex_string = r"(\d+[dhms] *)*"
    regex = re.compile(regex_string)

    match = regex.match(timeout_string)
    if not match.span()[1] == len(timeout_string):
        raise ValueError("Invalid timeout string format")


def get_start_of_day():
    start_of_day = datetime.combine(date.today(), datetime.min.time())
    return start_of_day