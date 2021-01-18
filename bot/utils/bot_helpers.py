from datetime import timedelta

import requests
import telethon
from telebot.apihelper import ApiTelegramException

from bot.utils.generate_article import generate_article, generate_personalized_article
from client import ClientMonitor
from database.user import *
from settings.logger import *
from bot.inline_markups import *
from bot.keyboard_markups import *

logger = get_logger(__name__)


def get_track_info(user, certain_record=None):
    if not user.users_tracking:
        logger.info(f'{user.first_name}({user.user_id}) has no one to track')
        return ""

    logger.info(f'Gathering track info for {user.first_name}({user.user_id}).')

    if certain_record:
        article_link = generate_personalized_article(user, certain_record)
        return "Check {}' info out here: {}".format(certain_record.first_name, article_link)
    else:
        article_link = generate_article(user)
        return "Check your query results out here: {}".format(article_link)


def notify_user(bot, user, certain_record=None):
    try:
        bot.send_message(
            user.user_id,
            get_track_info(user, certain_record=certain_record),
            reply_markup=REMOVE,
            parse_mode='Markdown'
        )
    except ApiTelegramException as e:
        raise e

    logger.info(f'Performing notification for {user.first_name}({user.user_id}) done.')

    if not certain_record:
        user.last_notified = datetime.now()
        user.save()


def get_working_entity(bot, msg):
    entity_qualifier = msg.text

    entity = ClientMonitor.get_entity(entity_qualifier)
    if not isinstance(entity, telethon.types.User):
        bot.send_message(
            msg.from_user.id,
            'I was not able to find this user.'
        )
        User.set_state(msg.from_user, State.NORMAL)
        raise ValueError(f'Got non-user entity `{entity_qualifier}`')
    return entity


def CURRENTLY_UNAVAILABLE(bot, user_id):
    bot.send_message(
        user_id,
        "This feature is currently unavailable",
        reply_markup=menu_markup
    )
