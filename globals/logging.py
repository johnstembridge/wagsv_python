import logging
from logging.handlers import RotatingFileHandler
from globals import config


def log_init():
    # initialize the log handler
    log_path = config.get('locations')['logs'] + '/error.log'
    log_handler = RotatingFileHandler(log_path, maxBytes=1000000, backupCount=1)

    # set the log handler level
    log_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")

    log_handler.setFormatter(formatter)
    return log_handler

