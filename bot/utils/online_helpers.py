"""
This file provides functionality, handling online status computations and collecting.

    * get_whole_day_records - gets user' online records from start to the end of the day
    * get_online_offline - get the (online, offline) tuple of corresponding time values in seconds
"""

from datetime import timedelta
from typing import Tuple, List

from database import User, TrackingUser
from settings import DEFAULT_TIMEOUT
from .time_helpers import *


def get_whole_day_records(user_t: TrackingUser) -> List[bool]:
    """
    This function gets user_t online records from start to the end of the day.

    Examples
    --------
    Imagine it's 9:20AM and user_t has a first record set on 1:00AM. This means that we consider periods
    from the midnight to 1:00AM (as we have no clue about user_t status on that time) and 9:20AM to next midnight
    (as that time if is future and user could not possibly be online in that period).

    Parameters
    ----------
    user_t : user.TrackingUser
        Tracking user, whose online timeline is being analyzed.

    Returns
    -------
    List of online status records from the start to the end of the day.
    """
    # getting the info for each hour available
    start_of_day = get_start_of_day()
    time_since_start_of_day = datetime.now() - start_of_day
    max_n_of_records = int(time_since_start_of_day.total_seconds() / DEFAULT_TIMEOUT)
    max_n_of_day_records = int(DAY // DEFAULT_TIMEOUT)
    records = user_t.online_timeline[-max_n_of_records:]

    # calculating and filling possible gaps with ``False``s
    missing_front = int((datetime.now()
                         - timedelta(seconds=DEFAULT_TIMEOUT * len(records))
                         - get_start_of_day()).total_seconds() // DEFAULT_TIMEOUT)
    missing_back = max_n_of_day_records - missing_front - len(records)

    records = [False] * missing_front + records + [False] * missing_back
    return records


def get_online_offline(user_w: User, user_t: TrackingUser, whole_day: bool = False) -> Tuple[int, int]:
    """
    Analyzes user_t online timeline, involving the fact, user_t is in user_w tracking list.

    Parameters
    ----------
    user_w : user.User
        User, which tracking list contains user_t.
    user_t : user.TrackingUser
        Tracking user, whose online timeline is being analyzed.
    whole_day : bool
        If True, collects records for the whole day, filling possible front & back gaps,
        otherwise uses user_w.notification_timeout as a time bound.

    Returns
    -------
    Tuple (seconds online, seconds offline)
    """
    if whole_day:
        records = get_whole_day_records(user_t)
    else:
        # if whole_day is false, we are getting records, bounded by user_w.notification_timeout
        n_records = int(user_w.notification_timeout // DEFAULT_TIMEOUT)
        records = user_t.online_timeline[-n_records:]

    online = records.count(True) * int(DEFAULT_TIMEOUT)
    offline = len(records) * DEFAULT_TIMEOUT - online

    return online, offline
