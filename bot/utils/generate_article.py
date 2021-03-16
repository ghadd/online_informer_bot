"""
This file provides chart & article generation tools for representing user' online activity.

    * get_doughnut_chart_url - generates doughnut online vs. offline representation chart
    * get_radar_chart_url - generates radar chart with 24 peripheral nodes corresponding to 24 hours
    * generate_article - generates a telegra.ph article with all tracking list users overlook
    * generate_personalized_article - generates a telegra.ph article with one-user detailed overlook
"""

import json

# jinja2 felt like an obvious choice, having ability to build up HTML articles with telegraph
from jinja2 import Template
from quickchart import QuickChart
from telegraph import Telegraph

from settings import *
from .online_helpers import *

logger = logger.get_logger(__name__)


def get_doughnut_chart_url(user_w: User, user_t: TrackingUser, whole_day: bool = False) -> str:
    """
    This function generates a chart, representing users online vs offline,
    using quickchart.io API with configuration, based on
    template `/bot/utils/assets/doughnut_chart_config` based on user_t online timeline
    for last ``user_w.notification_timeout`` if ``whole_day`` is ``False`` or last 24hrs if it is ``True``.

    Parameters
    ----------
    user_w : user.User
        User, which properties i.e. notification timeout and user_t online timeline are considered as factors
        for the chart data. user_t must be a part of user.get_tracking_users() list.
    user_t : user.TrackingUser
        Tracking user, whose online timeline list is being monitored and transposed to chart data.
    whole_day : bool
        if True, chart will contain data, based on user_t last 24hrs activity, otherwise, it'll be defaulted
        to `user_w.notification_timeout`.

    Returns
    -------
    str:
        URL for doughnut chart image which can be downloaded or embedded anywhere.
    """
    logger.info("Generating doughnut chart for {}(id:{}) about {}(id:{}), whole_day={}".format(user_w.first_name,
                                                                                               user_w.user_id,
                                                                                               user_t.first_name,
                                                                                               user_t.user_id,
                                                                                               whole_day))
    chart_config_template = Template(open("./bot/utils/assets/doughnut_chart_config.jinja2").read())

    # [online seconds, offline seconds]
    data = [*get_online_offline(user_w, user_t, whole_day)]
    total_string = get_labeled_time(sum(data))

    qc = QuickChart()
    qc.config = chart_config_template.render(data_string=json.dumps(data), total_string=json.dumps(total_string))

    return qc.get_url()


def get_radar_chart_url(user_t: TrackingUser) -> str:
    """
    Creates a radar chart based on whole day user_t activity, having values from 0 to 1 for each of 24 rays.

    Parameters
    ----------
    user_t: user.TrackingUser
        Tracking user, whose data is being displayed on the resulting graph.

    Returns
    -------
    URL for radar chart image which can be downloaded or embedded anywhere.
    """
    logger.info("Generating radar chart about {}(id:{})".format(user_t.first_name, user_t.user_id))
    chart_config_template = Template(open("./bot/utils/assets/radar_chart_config.jinja2").read())

    # creating labels from 00:00:00 to 23:00:00 with 1 hour step
    start_of_day = get_start_of_day()
    labels = [(start_of_day + timedelta(hours=i)).strftime(TIME_FORMAT) for i in range(0, 24)]

    # getting array of records since start of the day
    records = get_whole_day_records(user_t)
    # number of records per hour
    chunk = int(HOUR // DEFAULT_TIMEOUT)

    # now, transferring boolean data to integer data, so it can be summed
    int_records = [int(rec) for rec in records]
    # and managing percentage of online time for each hour (for example having 3 records for hour
    # stored in list [1, 1, 0] would lead to 0.66 as online part of the whole hour (40 minutes))
    data = [sum(int_records[chunk * i:chunk * (i + 1)]) / chunk for i in range(24)]

    qc = QuickChart()
    qc.config = chart_config_template.render(labels=json.dumps(labels), data_string=json.dumps(data))

    url = qc.get_url()
    return url


def generate_article(user_w: User) -> str:
    """
    This function creates a ``Telegra.ph`` article, based on user_w tracking list, so that the article
    fits doughnut charts for each tracked by user_w user.

    Parameters
    ----------
    user_w : user.User
        User model, which tracking list is being processed and shown up in the article.

    Returns
    -------
    URL for generated bulk ``telegra.ph`` article
    """
    telegraph = Telegraph()
    page_template_contents = open("./bot/utils/assets/telegraph_page.jinja2").read()
    page_template = Template(page_template_contents)

    telegraph.create_account(short_name='Online Informer')

    page_contents = page_template.render(
        user_w=user_w,
        get_image_url=get_doughnut_chart_url,
        number_of_users_tracking=len(user_w.get_tracking_users())
    )
    response = telegraph.create_page(
        f'{user_w.first_name}({user_w.user_id}) Tracking list',
        html_content=page_contents
    )

    return 'https://telegra.ph/{}'.format(response['path'])


def generate_personalized_article(user_w: User, user_t: TrackingUser) -> str:
    """
    This function creates a Telegra.ph personalized article based on user_t online timeline
    from user_w tracking list.

    Parameters
    ----------
    user_w : user.User
        User model, from which user_t online timeline is taken (timelines are not unified for different
        `watchers`).

    user_t : user.TrackingUser
        Tracking User, whose data is being represented in multiple charts on a single article.

    Returns
    -------
    URL for generated personalized ``telegra.ph`` article
    """
    telegraph = Telegraph()
    page_template = Template(open("./bot/utils/assets/telegraph_page_personalized.jinja2").read())

    telegraph.create_account(short_name='Online Informer')

    online, offline = get_online_offline(user_w, user_t)
    total = online + offline

    # letting the jinja render charts while rendering the article template
    page_contents = page_template.render(user_w=user_w, user_t=user_t, get_doughnut_chart_url=get_doughnut_chart_url,
                                         get_radar_chart_url=get_radar_chart_url, online=online,
                                         online_time=get_labeled_time(online), total_time=get_labeled_time(total), )
    response = telegraph.create_page(
        f'Info about {user_t.first_name}\' online',
        html_content=page_contents
    )

    return 'https://telegra.ph/{}'.format(response['path'])
