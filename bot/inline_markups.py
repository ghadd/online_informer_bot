from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

add_user_button = InlineKeyboardButton("Add tracking user", callback_data='add_user')
del_user_button = InlineKeyboardButton("Delete tracking user", callback_data='del_user')
settings_button = InlineKeyboardButton("Settings", callback_data='settings')
update_button = InlineKeyboardButton("Update", callback_data='update')
update_certain_button = InlineKeyboardButton("Update certain user", callback_data='update_certain')

menu_markup = InlineKeyboardMarkup()
menu_markup\
    .row(add_user_button, del_user_button)\
    .row(update_button, update_certain_button)\
    .row(settings_button)

set_timeout_button = InlineKeyboardButton("Set timeout", callback_data='set_timeout')
go_premium_button = InlineKeyboardButton("Go premium", callback_data='go_premium')
go_back_button = InlineKeyboardButton("Back to menu", callback_data='go_back')

settings_markup = InlineKeyboardMarkup()
settings_markup.row(set_timeout_button)
settings_markup.row(go_premium_button)
settings_markup.row(go_back_button)
