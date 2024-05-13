import logging
import os
from modules.speech import play_speech

def run_test():
    play_speech('Ranadeep Banik')


def set_log_level():
    logging.getLogger().setLevel(os.getenv('LOG_LEVEL').upper() if os.getenv('LOG_LEVEL') is not None else None or 'INFO')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #populate_database_with_local_config()
    set_log_level()
    run_test()
