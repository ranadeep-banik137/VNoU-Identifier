import logging
import os
from modules.speech import play_speech
from modules.data_reader import convertToBinaryData, read_file
from modules.database import fetch_last_user_id, populate_users


def run_test():
    play_speech('Ranadeep Banik')


def populate_database_with_local_config():
    for line in read_file():
        if 'id,name' in line:
            continue
        comma_separated_val = line.split(",")
        print(f'Last user id is {fetch_last_user_id()}')
        populate_users(fetch_last_user_id() + 1, convertToBinaryData(f'img/{comma_separated_val[0]}.png'),
                          comma_separated_val[1])


def set_log_level():
    logging.getLogger().setLevel(
        os.getenv('LOG_LEVEL').upper() if os.getenv('LOG_LEVEL') is not None else None or 'INFO')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # populate_database_with_local_config()
    set_log_level()
    run_test()
