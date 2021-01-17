from bot.utils import *
from database.tracking_user import TrackingUser
from database.user import *


def handle_start(bot, msg):
    if User.get_or_none(User.user_id == msg.from_user.id):
        bot.send_message(
            msg.from_user.id,
            "Hey! How'ya doing?"
        )
    else:
        User.insert(
            user_id=msg.from_user.id,
            first_name=msg.from_user.first_name
        ).execute()
        bot.send_message(
            msg.from_user.id,
            "Hey! Welcome, use bla bla bla?"
        )


def handle_add_user(bot, msg):
    try:
        entity = get_working_entity(bot, msg)
    except ValueError:
        return

    user = User.get(User.user_id == msg.from_user.id)

    if list(filter(lambda user_t: user_t.id == entity.id, user.users_tracking)):
        bot.send_message(
            msg.from_user.id,
            'This user is in your tracking list already'
        )
        return

    if len(user.users_tracking) >= 5:
        bot.send_message(
            msg.from_user.id,
            'Cannot add more than 5 users in free version.'
        )
        return

    user.users_tracking.append(TrackingUser(entity))
    update_users_tracking(user)

    bot.send_message(
        msg.from_user.id,
        'O\'KAY, added <a href="tg://user?id={user_id}">{user_name}</a> for tracking.'.format(
            user_id=entity.id,
            user_name=entity.first_name,
        ),
        parse_mode='HTML'
    )


def handle_del_user(bot, msg):
    try:
        entity = get_working_entity(bot, msg)
    except ValueError:
        return

    user = User.get(User.user_id == msg.from_user.id)

    if not list(filter(lambda user_t: user_t.user_id == entity.id, user.users_tracking)):
        message = 'User <a href="tg://user?id={user_id}">{user_name}</a> is not in your tracking list.'.format(
            user_id=entity.id,
            user_name=entity.first_name,
        )
    else:
        user.users_tracking = list(filter(lambda user_t: user_t.user_id != entity.id, user.users_tracking))
        update_users_tracking(user)
        message = 'Sure, deleted <a href="tg://user?id={user_id}">{user_name}</a> from tracking.'.format(
            user_id=entity.id,
            user_name=entity.first_name,
        )

    bot.send_message(
        msg.from_user.id,
        message,
        parse_mode='HTML'
    )


def handle_get_info(bot, msg):
    user = User.get(User.user_id == msg.from_user.id)
    try:
        certain_user = get_working_entity(bot, msg)
        notify_user(bot, user, certain_record=certain_user)
    except ValueError:
        notify_user(bot, user)


def handle_set_timeout(bot, msg):
    try:
        timeout = " ".join(msg.text.split()[1:])
    except IndexError:
        bot.send_message(
            msg.from_user.id,
            "Use this as ..."
        )
        return

    timeout_in_seconds = get_in_secs(timeout)
    if timeout_in_seconds:
        if timeout_in_seconds < MIN_NOTIFICATION_TIMEOUT:
            bot.send_message(
                msg.from_user.id,
                f'Cannot set this this timeout. Minimum value is {get_labeled_time(MIN_NOTIFICATION_TIMEOUT)}'
            )
            return
        bot.send_message(
            msg.from_user.id,
            f'Setting your timeout to {get_labeled_time(timeout_in_seconds)}.'
        )
        User.update(
            {
                User.notification_timeout: timeout_in_seconds
            }
        ).where(
            User.user_id == msg.from_user.id
        ).execute()
    else:
        bot.send_message(
            msg.from_user.id,
            'Cannot set value to zero.'
        )


def handle_get_me(bot, msg):
    user = User.get(User.user_id == msg.from_user.id)

    message = ''

    tracking_users = get_track_info(user, simplified=True)
    message += '**Tracking users**: {}\n\n'.format(tracking_users)

    timeout = get_labeled_time(user.notification_timeout)
    message += '**Notification timeout**: {}\n\n'.format(timeout)

    bot.send_message(
        msg.from_user.id,
        message,
        parse_mode='Markdown'
    )
