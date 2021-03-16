"""
This file mostly provides functionality for managing and time as a pretty-formatted strings and back

    * _get_in_secs - turns expression like '234' or '7h' or '3m' etc to corresponding number of seconds
    * get_in_secs - turns whole expression with multiple '\\d+[dhms] structures' to total number of seconds of it
    * smart_join - wraps standard join with nullability obliteration
    * get_labeled_time - turns any positive number of seconds to a pretty-formatted string
    * validate_timeout - validated timeout string for processing in get_in_secs
    * get_start_of_day - retrieves current day' 00:00:00 time point
"""

import re
from datetime import datetime, date
from typing import List

from settings import MINUTE, HOUR, DAY


def _get_in_secs(timeout_string: str) -> int:
    """
    Turns timeout string fitting \\d+[dhms] regex to number of seconds
    Parameters
    ----------
    timeout_string : str
        timeout partial string

    Returns
    -------
    corresponding to the timeout string number of seconds
    """
    try:
        return int(timeout_string[:timeout_string.index('s')])
    except ValueError:
        pass

    try:
        return int(timeout_string[:timeout_string.index('m')]) * MINUTE
    except ValueError:
        pass

    try:
        return int(timeout_string[:timeout_string.index('h')]) * HOUR
    except ValueError:
        pass

    try:
        return int(timeout_string[:timeout_string.index('d')]) * DAY
    except ValueError:
        pass

    return 0


def get_in_secs(timeout_string: str) -> int:
    """
    Turns combined timeout to a total sum using _get_in_secs function for each space-separated part of timeout

    Parameters
    ----------
    timeout_string : str
        Combined timeout which must be fitting the regex ``(\\d+[dhms] *)*``

    Returns
    -------
    corresponding to the timeout string number of seconds
    """
    # possible format "1d 2h 35s"
    sep = timeout_string.split()
    res = 0

    for el in sep:
        res += _get_in_secs(el)

    return res


def smart_join(elements: List[str], sep: str) -> str:
    """
    Uses regular join after filtering null elements from the initial list
    Parameters
    ----------
    elements : List[str]
        list of /possibly null/ strings to join
    sep : str
        joining delimiter

    Returns
    -------
    joined string
    """
    # deletes null-objects before regular joining
    elements = list(filter(lambda x: x, elements))
    return sep.join(elements)


def validate_timeout(timeout_string: str) -> None:
    """

    Parameters
    ----------
    timeout_string : str
        string, representing some time

    Raises
    ------
    ValueError
        When the timeout string happened to be invalid
    """
    regex_string = r"(\d+[dhms] *)*"
    regex = re.compile(regex_string)

    match = regex.match(timeout_string)
    if not match.span()[1] == len(timeout_string):
        raise ValueError("Invalid timeout string format")


def get_labeled_time(timeout: int) -> str:
    """
    Turns some amount of seconds to a pretty-formatted string.
    Probably, must've been used datetime.strftime...

    Parameters
    ----------
    timeout : int
        amount of seconds to label

    Returns
    -------
    string, corresponding to given number of seconds
    """
    d = int(timeout // DAY)
    h = int(timeout // HOUR)
    m = int(timeout // MINUTE)
    s = int(timeout)

    # pretty handful recursion comes here, we name the biggest time qualifier and then name everything without it
    if d:
        return smart_join([f'{d} day{"s" if d > 1 else ""}', get_labeled_time(timeout - d * DAY)], ' ')

    if h:
        return smart_join([f'{h} hour{"s" if h > 1 else ""}', get_labeled_time(timeout - h * HOUR)], ' ')

    if m:
        return smart_join([f'{m} minute{"s" if m > 1 else ""}', get_labeled_time(timeout - m * MINUTE)], ' ')

    return f'{s} second{"s" if s > 1 else ""}' if s else ''


def get_start_of_day() -> datetime:
    """
    Returns
    -------
    00:00:00 time point of current day
    """
    start_of_day = datetime.combine(date.today(), datetime.min.time())
    return start_of_day
