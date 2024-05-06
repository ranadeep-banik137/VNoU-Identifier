# from modules.face_identifier2 import encode_face
import logging
import os
from modules.face_identifier import encode_face, delete_similar_images
from modules.database import insert_table_data, fetch_table_data_in_tuples, fetch_last_user_id
from modules.data_reader import read_file, convertToBinaryData


def run_app():
    encode_face(fetch_table_data_in_tuples())


def set_log_level():
    logging.getLogger().setLevel(os.getenv('LOG_LEVEL').upper() if os.getenv('LOG_LEVEL') is not None else None or 'INFO')


def populate_database_with_local_config():
    for line in read_file():
        if 'id,name' in line:
            continue
        comma_separated_val = line.split(",")
        print(f'Last user id is {fetch_last_user_id()}')
        insert_table_data(fetch_last_user_id() + 1, convertToBinaryData(f'img/{comma_separated_val[0]}.png'), comma_separated_val[1])


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #populate_database_with_local_config()
    set_log_level()
    run_app()
