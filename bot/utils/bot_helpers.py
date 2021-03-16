"""
This file corresponds to lower level handlers for user bot-user interaction and mostly
provides notification and data-collection functionality.

    * get_track_info - return response string for incoming update query
    * notify_user - sends a generated track info to the destination user and handles possible errors
    * get_working_entity - processes message text as an TG entity object and returns it if it's type.User
    * CURRENTLY_UNAVAILABLE - tool for temporary implementation absence notifications
"""

from datetime import datetime
from typing import Optional

import telethon
from telebot import TeleBot
from telebot.apihelper import ApiTelegramException
from telebot.types import Message
from telethon.hints import Entity

from bot.inline_markups import *
from bot.keyboard_markups import *
from bot.utils.generate_article import generate_article, generate_personalized_article
from client import ClientMonitor
from database import User, TrackingUser
from settings.logger import *

logger = get_logger(__name__)


def get_track_info(user: User, certain_record: Optional[TrackingUser] = None) -> str:
    """
    Function that generates an article depending on user query i.e. bulk update (article about multiple users)
    or personalized update (enhanced article about a single user) and creates a response message string.

    Parameters
    ----------
    user : user.User
        model of a user, which tracking user(s) info is displayed on the article.
    certain_record : user.TrackingUser, optional
        model of a tracking user, which is being displayed. (If provided - personalized article is being generated)

    Returns
    -------
    str
        string response for user (watching), containing article about users' (tracking) online status.
    """

    # if no users to tracking - return empty response, which throws a Telegram API Exception later on
    # which leads to sending a corresponding message while handling it
    if not user.get_tracking_users():
        logger.warning(f'{user.first_name}({user.user_id}) has no one to track')
        return ""

    logger.info(f'Gathering track info for {user.first_name}({user.user_id}).')
    # if certain record (a single tracking user) is provided - generate personalized article
    # template: bot/utils/assets/telegraph_page_personalized.jinja2
    if certain_record:
        logger.info("Creating a personalized article for {}(id:{}) about {}(id:{})".
                    format(user.first_name, user.user_id, certain_record.first_name, certain_record.user_id))
        article_link = generate_personalized_article(user, certain_record)
        return "Check {}' info out here: {}".format(certain_record.first_name, article_link)

    # otherwise - generate an overview for each tracking user in the same article
    # template: bot/utils/assets/telegraph_page.jinja2
    else:
        logger.info("Creating a bulk article for {}(id:{})".format(user.first_name, user.user_id))
        article_link = generate_article(user)
        return "Check your query results out here: {}".format(article_link)


def notify_user(bot: TeleBot, user: User, certain_record: Optional[TrackingUser] = None) -> None:
    """
    This method uses bot object to notify provided user about his tracking list or a single user if
    certain_record is provided. May be user both in manual updates and timeout-based updates.

    Parameters
    ----------
    bot : telebot.TeleBot
        Bot object, the sender in notification transaction.
    user : user.User
        User model, the receiver in notification transaction and provider of tracking_users data.
    certain_record : user.TrackingUser
        TrackingUser model (must be part of user.users_tracking list if provided) which is then
        being displayed in personalized article.

    Raises
    ------
    telebot.apihelper.ApiTelegramException
        When user does not have any users tracking and get_track_info returns an empty string
    """
    try:
        # getting query response
        track_info = get_track_info(user, certain_record=certain_record)
        # this one throws ApiTelegramException if track_info is empty
        # reply markup is set to remove, as we dont want it to be opened after we got the personalized result
        bot.send_message(
            user.user_id,
            track_info,
            reply_markup=REMOVE,
            parse_mode='Markdown'
        )
    except ApiTelegramException as e:
        # re-raising to handle in higher level handle functions
        raise e

    logger.info(f'Performing notification for {user.first_name}({user.user_id}) done.')

    # if user was checking overall stats about tracking users, count the current time as last_notified
    if not certain_record:
        user.last_notified = datetime.now()
        user.save()


def get_working_entity(bot: TeleBot, msg: Message) -> Entity:
    """
    This function perceives a message, received by bot as some kind of valid telegram entity identifier
    i.e. username or id and return an Entity object corresponding to it. Usually must be bind with previous
    state assignments for correct usage.

    Parameters
    ----------
    bot : telebot.TeleBot
        Bot object, which receives a provided message and need to process it as a entity.
    msg : telebot.types.Message
        Incoming telegram message, involving some entity identifier inside of its text

    Returns
    -------
    telethon.hints.Entity
        telegram entity object

    Examples
    --------
    Imaging you having to get a user entity for some processing after clicking one of your menu buttons.
    In order to process incoming message correctly, it is worth adding some user states enum. In our case
    user.State provides us with things like ``ENTITY_INPUT_ADD``, which refers to the fact, that the very next
    message from user must contain an entity identifier, corresponding to wanted functionality - Adding the
    user to the tracking list in our case. So, after clicking on button and sending a prompt so enter an entity,
    we set our user state to the corresponding one and than matching the handler respectively (``handle_add_user``
    in our case).

    Raises
    ------
    ValueError
        When a non-user entity was provided in message text.
    """
    entity_qualifier = msg.text

    entity = ClientMonitor.get_entity(entity_qualifier)
    # Entity is a shortcut for [types.User, types.Chat, types.Channel], so we must guarantee that the
    # provided one is types.User
    if not isinstance(entity, telethon.types.User):
        bot.send_message(
            msg.from_user.id,
            'I was not able to find this user.'
        )
        raise ValueError(f'Got non-user entity `{entity_qualifier}`')
    return entity


def CURRENTLY_UNAVAILABLE(bot: TeleBot, user_id: int) -> None:
    """
    This method is used as a macro for not implemented parts of the code.

    Parameters
    ----------
    bot : telebot.TeleBot
        bot object, handling the issue
    user_id :
        telegram ID of user, receiving the `Unimplemented` error
    """
    bot.send_message(
        user_id,
        "This feature is currently unavailable",
        reply_markup=menu_markup
    )
