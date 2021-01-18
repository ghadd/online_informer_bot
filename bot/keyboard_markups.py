from telebot.types import ReplyKeyboardRemove, ReplyKeyboardMarkup

from database import User

REMOVE = ReplyKeyboardRemove()


def TRACKED_USERS(tg_user):
    markup = ReplyKeyboardMarkup(row_width=2)
    user_w = User.get(User.user_id == tg_user.id)

    if not user_w.users_tracking:
        raise ValueError

    for user_t in user_w.users_tracking:
        markup.add(user_t.first_name)

    return markup
