import json

from settings.config import *


def get_image_link(labels, data):
    data = {
        'labels': labels,
        'datasets': [
            {
                'label': 'Online',
                'data': data,
                'fill': FILL,
                'borderColor': BORDER_COLOR
            }
        ]
    }

    params = {
        'c': json.dumps({
            'type': TYPE,
            'data': data
        }),
        'bkg': BG_COLOR
    }

    link = CHART_API_POINT
    for param in params:
        link += f'{param}={params[param]}&'

    return link
