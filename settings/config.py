import os

DAY = 60 * 60 * 24
HOUR = 60 * 60
MINUTE = 60

# consider creating those files
API_ID = int(open('./settings/.api_id', 'r').read())
API_HASH = open('./settings/.api_hash', 'r').read()
BOT_TOKEN = open('./settings/.bot_token', 'r').read()

DEFAULT_TIMEOUT = MINUTE / 2
DEFAULT_NOTIFY_TIMEOUT = DAY
MIN_NOTIFICATION_TIMEOUT = HOUR / 2

DATABASE_PATH = os.path.abspath('./database/db.sqlite')

CHART_API_POINT = 'https://quickchart.io/chart?'
TYPE = 'line'
FILL = False
BORDER_COLOR = 'green'
BG_COLOR = 'white'

CHART_BLANK = './temp/{}-{}.png'
