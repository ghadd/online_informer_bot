"""
This file provides a basic logger support

    * get_logger - returns a logger which pipes to /tmp/online_informer_bot.log and console.
"""

import logging


def get_logger(name: str) -> logging.Logger:
    """
    Parameters
    ----------
    name : str
        logger name (usually is __name__)

    Returns
    -------
    a basing logger with file and console sinks.
    """
    logger = logging.Logger(name, level=logging.DEBUG)

    file_handler = logging.FileHandler('/tmp/online_informer_bot.log')
    stream_handler = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
