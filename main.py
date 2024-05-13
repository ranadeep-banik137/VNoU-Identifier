# from modules.face_identifier2 import encode_face
import logging
import os
from modules.face_identifier import encode_face
from modules.database import insert_table_data, fetch_table_data_in_tuples, fetch_last_user_id
from modules.data_reader import read_file, convertToBinaryData


def run_app():
    encode_face(fetch_table_data_in_tuples())


def set_log_level():
    logging.getLogger().setLevel(os.getenv('LOG_LEVEL').upper() if os.getenv('LOG_LEVEL') is not None else None or 'INFO')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    set_log_level()
    run_app()
