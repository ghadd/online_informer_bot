import asyncio
import time

import telebot
from telethon.errors import TypeNotFoundError

from database import State
from .message_handlers import *
from .keyboard_markups import TRACKED_USERS
from .utils import *

logger = get_logger(__name__)
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)


@bot.message_handler(commands=['start'])
def start(msg):
    handle_start(bot, msg)


@bot.callback_query_handler(lambda q: q.data == "add_user")
def prompt_add_user(q):
    handle_prompt_user(bot, q,
                       "Now, send me any identifier for your user. "
                       "It could be UserID or username of user to add to your tracking list.",
                       State.ENTITY_INPUT_ADD)


@bot.message_handler(func=lambda msg: User.get_state(msg.from_user) == State.ENTITY_INPUT_ADD)
def add_user(msg):
    handle_add_user(bot, msg)


@bot.callback_query_handler(lambda q: q.data == "del_user")
def prompt_del_user(q):
    handle_prompt_user(bot, q,
                       "Now, send me any identifier for your user. "
                       "It could be UserID or username of user to delete from your tracking list.",
                       State.ENTITY_INPUT_DEL)


@bot.message_handler(func=lambda msg: User.get_state(msg.from_user) == State.ENTITY_INPUT_DEL)
def del_user(msg):
    handle_del_user(bot, msg)


@bot.callback_query_handler(lambda q: q.data == "settings")
def open_settings(q):
    handle_open_settings(bot, q)


@bot.callback_query_handler(lambda q: q.data == "update")
def update_info(q):
    handle_update_info(bot, q)


@bot.callback_query_handler(lambda q: q.data == "update_certain")
def prompt_update_certain_info(q):
    try:
        tracking_users_markup = TRACKED_USERS(q.from_user)
    except ValueError:
        NO_TRACKING_USERS(bot, q)
        return

    handle_prompt_user(bot, q, "Select a user to see data of.", State.ENTITY_INPUT_CHK, tracking_users_markup)


@bot.message_handler(func=lambda msg: User.get_state(msg.from_user) == State.ENTITY_INPUT_CHK)
def update_certain_info(msg):
    handle_update_certain_info(bot, msg)


@bot.callback_query_handler(lambda q: q.data == "set_timeout")
def prompt_set_timeout(q):
    handle_prompt_user(bot, q, "Enter new timeout.", State.DATETIME_INPUT)


@bot.message_handler(func=lambda msg: User.get_state(msg.from_user) == State.DATETIME_INPUT)
def set_timeout(msg):
    handle_set_timeout(bot, msg)


@bot.callback_query_handler(lambda q: q.data == "go_premium")
def go_premium(q):
    CURRENTLY_UNAVAILABLE(bot, q)


@bot.callback_query_handler(lambda q: q.data == "go_back")
def go_back(q):
    handle_go_back(bot, q)


def updater():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while True:
            # checking users
            users = User.select()
            for user_w in users:
                users_tracking = user_w.tracking_users

                for user_tracking in users_tracking:
                    cl = ClientMonitor(user_tracking.user_id)
                    status = cl.is_online()
                    user_tracking.online_timeline.append(status)

                user_w.save()

            # notifying users
            for user_w in users:
                if (datetime.now() - user_w.last_notified).total_seconds() > user_w.notification_timeout:
                    try:
                        notify_user(bot, user_w)
                    except ApiTelegramException as e:
                        pass

            time.sleep(DEFAULT_TIMEOUT)
    except TypeNotFoundError:
        pass
