import logging


def get_logger(name):
    logger = logging.Logger(name, level=logging.DEBUG)

    file_handler = logging.FileHandler('/tmp/online_informer_bot.log')
    stream_handler = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


def USER(tg_user):
    return "{}(id:{})".format(tg_user.first_name, tg_user.id)


def LOG_HANDLE_MESSAGE(logger, msg):
    logger.info("Handling request from {user}: {text}".format(
        user=USER(msg.from_user),
        text=msg.text
    ))


def LOG_HANDLE_CALLBACK_QUERY(logger, q):
    logger.info("Handling request from {user}: {text}".format(
        user=USER(q.from_user),
        text=q.data
    ))
