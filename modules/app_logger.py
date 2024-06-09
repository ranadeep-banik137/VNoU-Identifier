import logging
import os
from modules.config_reader import read_config


config = read_config()


def set_log_handler(formatter=logging.Formatter(config['app_default']['log-formatter'])):
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.setLevel(os.getenv('LOG_LEVEL', config['app_default']['log-level']).upper())
    logger.addHandler(stream_handler)
