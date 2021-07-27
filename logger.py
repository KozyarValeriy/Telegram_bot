import logging
import os

SEP = "\t"  # separator in the log line


def get_logger(name: str) -> logging.Logger:
    """ Function to get logger

    :param name: name of logger (to display in a file),
    :return: Logger
    """
    formatter = logging.Formatter(fmt=SEP.join(["%(asctime)s", "%(levelname)s", "%(funcName)s(%(lineno)d)",
                                                "[pid: %(process)d]", "%(message)s"]),
                                  datefmt="%Y-%m-%d %H:%M:%S")
    logger = logging.getLogger(name)

    level = logging.INFO
    if hasattr(logging, os.getenv("BOT_LOG_LEVEL", "").upper()):
        level = getattr(logging, os.getenv("BOT_LOG_LEVEL", "").upper())
    logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(level)
    logger.addHandler(handler)

    return logger
