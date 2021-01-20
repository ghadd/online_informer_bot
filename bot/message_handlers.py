from database import State
from .utils import *
from .utils.time_helpers import get_in_secs, validate_timeout


def send_menu(bot, msg):
    bot.send_message(
        msg.from_user.id,
        "Menu:",
        reply_markup=menu_markup
    )


def handle_start(bot, msg):
    if User.get_or_none(User.user_id == msg.from_user.id):
        logger.info("User {} is a familiar fella.".format(USER(msg.from_user)))
        message = "Hey! How'ya doing?"
    else:
        logger.info("User {} is a newbie. Adding.".format(USER(msg.from_user)))
        User.insert(
            user_id=msg.from_user.id,
            first_name=msg.from_user.first_name,
            username=msg.from_user.username
        ).execute()
        logger.info("Added user {} to database.".format(USER(msg.from_user)))
        message = "Hey! Welcome, use bla bla bla?"

    bot.send_message(
        msg.from_user.id,
        message,
        reply_markup=menu_markup
    )
    logger.info("Updating user {} state to NORMAL.".format(USER(msg.from_user)))
    User.update_state(msg.from_user, State.NORMAL)


def handle_prompt_user(bot, q, contents, new_state, reply_markup=None):
    logger.info("Prompting user {} to input (mode {}).".format(USER(q.from_user), State.get_value_naming(new_state)))
    bot.send_message(
        q.from_user.id,
        contents,
        reply_markup=reply_markup
    )

    bot.delete_message(
        q.from_user.id,
        q.message.message_id
    )

    User.update_state(q.from_user, new_state)


def handle_add_user(bot, msg):
    try:
        entity = get_working_entity(bot, msg)
    except ValueError as e:
        bot.send_message(
            msg.from_user.id,
            "Sorry, I was not able to find this user."
        )
        logger.warn(e)
        return

    user_w = User.get(User.user_id == msg.from_user.id)
    if list(filter(lambda user_t: user_t.user_id == entity.id, user_w.tracking_users)):
        logger.info("User {} has {} in tracking list already".format(
            USER(msg.from_user),
            USER(entity)
        ))
        bot.send_message(
            msg.from_user.id,
            'This user is in your tracking list already.'
        )
        return

    if len(user_w.tracking_users) >= 5 and not user_w.premium:
        logger.info(
            "User {} without premium membership is attempting to add more than 5 users.".format(USER(msg.from_user)))
        bot.send_message(
            msg.from_user.id,
            'Cannot add more than 5 users in free version.'
        )
        return

    user_t = TrackingUser(entity)
    logger.info("Adding user {} to {}' tracking list.".format(USER(entity), USER(msg.from_user)))
    user_w.tracking_users.append(user_t)
    user_w.save()

    bot.send_message(
        msg.from_user.id,
        'O\'KAY, added <a href="tg://user?id={user_id}">{user_name}</a> for tracking.'.format(
            user_id=entity.id,
            user_name=entity.first_name,
        ),
        parse_mode='HTML'
    )

    logger.info("Updating user {} state to NORMAL.".format(USER(msg.from_user)))
    User.update_state(msg.from_user, State.NORMAL)
    send_menu(bot, msg)


def handle_del_user(bot, msg):
    try:
        entity = get_working_entity(bot, msg)
    except ValueError as e:
        logger.info(e)
        bot.send_message(
            msg.from_user.id,
            "Sorry, I was not able to find this user."
        )
        return

    user_w = User.get(User.user_id == msg.from_user.id)

    if not list(filter(lambda user_t: user_t.user_id == entity.id, user_w.tracking_users)):
        logger.info("User {} is not in tracking list of {}".format(USER(entity), USER(msg.from_user)))
        message = 'User <a href="tg://user?id={user_id}">{user_name}</a> is not in your tracking list.'.format(
            user_id=entity.id,
            user_name=entity.first_name,
        )
    else:
        logger.info("Removing user {} from tracking list of {}".format(USER(entity), USER(msg.from_user)))
        user_w.tracking_users = list(filter(lambda user_t: user_t.user_id != entity.id, user_w.tracking_users))
        user_w.save()
        message = 'Sure, deleted <a href="tg://user?id={user_id}">{user_name}</a> from tracking.'.format(
            user_id=entity.id,
            user_name=entity.first_name,
        )

    bot.send_message(
        msg.from_user.id,
        message,
        parse_mode='HTML'
    )

    logger.info("Updating user {} state to NORMAL.".format(USER(msg.from_user)))
    User.update_state(msg.from_user, State.NORMAL)
    send_menu(bot, msg)


def handle_open_settings(bot, q):
    user_w = User.get(User.user_id == q.from_user.id)
    current_settings = "Current settings:\n" \
                       "Notification timeout: {timeout}\n" \
                       "Premium membership: {premium}" \
        .format(
            timeout=get_labeled_time(user_w.notification_timeout),
            premium="true" if user_w.premium else "false"
        )

    bot.edit_message_text(
        current_settings,
        q.from_user.id,
        q.message.message_id,
        reply_markup=settings_markup
    )
    bot.answer_callback_query(q.id)


def handle_update_info(bot, q):
    user = User.get(User.user_id == q.from_user.id)
    try:
        notify_user(bot, user)
    except ApiTelegramException as e:
        logger.warn(e)
        bot.send_message(
            q.from_user.id,
            "You have no users tracking yet :("
        )

    bot.delete_message(
        q.from_user.id,
        q.message.message_id,
    )
    send_menu(bot, q)


def handle_update_certain_info(bot, msg):
    user = User.get(User.user_id == msg.from_user.id)
    try:
        certain_user = get_working_entity(bot, msg)
        certain_user = list(filter(lambda user_t: user_t.user_id == certain_user.id, user.tracking_users))
        if not certain_user:
            bot.send_message(
                msg.from_user.id,
                "Who the heck is this guy? Please, choose an option from the keyboard, i suggested."
            )
            return
        else:
            certain_user = certain_user[0]

        notify_user(bot, user, certain_record=certain_user)
        User.update_state(msg.from_user, State.NORMAL)
        send_menu(bot, msg)
    except ValueError as e:
        bot.send_message(
            msg.from_user.id,
            "Please, choose an option from the keyboard, i suggested."
        )
        logger.info(e)


def handle_set_timeout(bot, msg):
    timeout = msg.text
    try:
        validate_timeout(timeout)
    except ValueError:
        bot.send_message(
            msg.from_user.id,
            "Invalid format of timeout"
        )
        return

    timeout_in_seconds = get_in_secs(timeout)
    if timeout_in_seconds < MIN_NOTIFICATION_TIMEOUT:
        bot.send_message(
            msg.from_user.id,
            f'Cannot set this this timeout. Minimum value is {get_labeled_time(MIN_NOTIFICATION_TIMEOUT)}'
        )
    else:
        bot.send_message(
            msg.from_user.id,
            f'Setting your timeout to {get_labeled_time(timeout_in_seconds)}.'
        )
        User.update_timeout(msg.from_user, timeout_in_seconds)

    send_menu(bot, msg)
    User.update_state(msg.from_user, State.NORMAL)


def handle_go_back(bot, q):
    bot.edit_message_text(
        "Menu:",
        q.from_user.id,
        q.message.message_id,
        reply_markup=menu_markup
    )

    bot.answer_callback_query(q.id)


def NO_TRACKING_USERS(bot, q):
    bot.send_message(
        q.from_user.id,
        "You have no users tracking yet :("
    )
    bot.delete_message(
        q.from_user.id,
        q.message.message_id
    )
    send_menu(bot, q)
