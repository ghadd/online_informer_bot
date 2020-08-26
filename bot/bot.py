import asyncio

import telebot
from telethon.errors import TypeNotFoundError

from bot.message_handlers import *
from bot.utils import *
from client import client
from database.user import *
from settings.config import *
from settings.logger import get_logger

logger = get_logger(__name__)
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)


@bot.message_handler(commands=['start'])
def start(msg):
    handle_start(bot, msg)


@bot.message_handler(commands=['add_user'])
def add_user(msg):
    handle_add_user(bot, msg)


@bot.message_handler(commands=['del_user'])
def del_user(msg):
    handle_del_user(bot, msg)


@bot.message_handler(commands=['get_info'])
def get_info(msg):
    handle_get_info(bot, msg)


@bot.message_handler(commands=['set_timeout'])
def set_timeout(msg):
    handle_set_timeout(bot, msg)


@bot.message_handler(commands=['get_me'])
def get_me(msg):
    handle_get_me(bot, msg)


def updater():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while True:
            # checking users
            users = User.select()
            for user in users:
                users_tracking_loaded = json.loads(user.users_tracking)
                users_tracking = [TrackingUser(u) for u in users_tracking_loaded]

                for i in range(len(users_tracking)):
                    status = client.is_online(users_tracking[i].user_id)
                    users_tracking[i].online_timeline.append(status)

                update_users_tracking(user, users_tracking)

            # notifying users
            for user in users:
                if time.time() - user.last_notified > user.notification_timeout:
                    notify_user(bot, user)

            time.sleep(DEFAULT_TIMEOUT)
    except TypeNotFoundError:
        pass

