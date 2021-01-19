from telebot.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, User as TgUser

from database import User
from settings import USER

REMOVE = ReplyKeyboardRemove()


def TRACKED_USERS(tg_user: TgUser) -> ReplyKeyboardMarkup:
    """
    This function created a Reply Keyboard markup with identifiers of all users, tg_user is tracking

    Parameters
    ----------
    tg_user : telebot.types.User
        user, whose tracked users are placed to the keyboard markup
    Returns
    -------
    ReplyKeyboardMarkup with user's tracking list entities
    """
    markup = ReplyKeyboardMarkup(row_width=2)
    user_w = User.get(User.user_id == tg_user.id)

    if not user_w.users_tracking:
        raise ValueError("No users tracking for {}".format(USER(tg_user)))

    for user_t in user_w.tracking_users:
        markup.add(user_t.username if user_t.username else str(user_t.user_id))
    
    return markup
