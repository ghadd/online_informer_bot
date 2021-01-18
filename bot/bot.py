from .message_handlers import *

from client import *
from database import *
from settings import *

import asyncio
import telebot
import time

from telethon.errors import TypeNotFoundError

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
            for user_w in users:
                users_tracking = user_w.users_tracking

                for user_tracking in users_tracking:
                    cl = ClientMonitor(user_tracking.user_id)
                    status = cl.is_online()
                    user_tracking.online_timeline.append(status)

                update_users_tracking(user_w)

            # notifying users
            for user_w in users:
                if (datetime.now() - user_w.last_notified).total_seconds() > user_w.notification_timeout:
                    notify_user(bot, user_w)

            time.sleep(DEFAULT_TIMEOUT)
    except TypeNotFoundError:
        pass

