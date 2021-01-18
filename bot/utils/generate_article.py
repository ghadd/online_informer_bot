import json
from datetime import timedelta

from jinja2 import Template
from quickchart import QuickChart
from telegraph import Telegraph

from settings import *
from .time_helpers import *
from .online_helpers import *


def get_doughnut_chart_url(user_w, user_t, whole_day=False):
    chart_config_template = Template(open("./bot/utils/assets/doughnut_chart_config.jinja2").read())

    data = [*get_online_offline(user_w, user_t, whole_day)]
    total_string = get_labeled_time(sum(data))

    qc = QuickChart()
    qc.config = chart_config_template.render(data_string=json.dumps(data), total_string=json.dumps(total_string))

    return qc.get_url()


def get_radar_chart_url(user_t):
    chart_config_template = Template(open("./bot/utils/assets/radar_chart_config.jinja2").read())

    start_of_day = get_start_of_day()
    labels = [(start_of_day + timedelta(hours=i)).strftime(TIME_FORMAT) for i in range(0, 24)]

    records = get_whole_day_records(user_t)
    chunk = int(HOUR // DEFAULT_TIMEOUT)

    int_records = [int(rec) for rec in records]
    data = [sum(int_records[chunk * i:chunk * (i + 1)]) / chunk for i in range(24)]

    qc = QuickChart()
    qc.config = chart_config_template.render(labels=json.dumps(labels), data_string=json.dumps(data))

    url = qc.get_url()
    return url


def generate_article(user_w):
    telegraph = Telegraph()
    page_template = Template(open("./bot/utils/assets/telegraph_page.jinja2").read())

    telegraph.create_account(short_name='Online Informer')

    response = telegraph.create_page(
        f'{user_w.first_name}({user_w.user_id}) Tracking list',
        html_content=page_template.render(user_w=user_w, get_image_url=get_doughnut_chart_url)
    )

    return 'https://telegra.ph/{}'.format(response['path'])


def generate_personalized_article(user_w, user_t):
    telegraph = Telegraph()
    page_template = Template(open("./bot/utils/assets/telegraph_page_personalized.jinja2").read())

    telegraph.create_account(short_name='Online Informer')

    online, offline = get_online_offline(user_w, user_t)
    total = online + offline

    response = telegraph.create_page(
        f'Info about {user_t.first_name}\' online',
        html_content=page_template.render(user_w=user_w, user_t=user_t,
                                          get_doughnut_chart_url=get_doughnut_chart_url,
                                          get_radar_chart_url=get_radar_chart_url,
                                          online=online,
                                          online_time=get_labeled_time(online),
                                          total_time=get_labeled_time(total),
                                          )
    )

    return 'https://telegra.ph/{}'.format(response['path'])
