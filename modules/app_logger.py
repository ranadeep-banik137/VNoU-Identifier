import logging
import os


def set_log_handler(formatter=logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')):
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.setLevel(os.getenv('LOG_LEVEL').upper() if os.getenv('LOG_LEVEL') is not None else None or 'INFO')
    logger.addHandler(stream_handler)
