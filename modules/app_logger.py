import logging
import os
import json
from modules.config_reader import read_config
from datetime import datetime
from modules.database import fetch_table_data_in_tuples
from constants.db_constansts import query_data
from modules.data_reader import make_dir_if_not_exist

config = read_config()


def serialize_datetime(obj):
    """Serialize datetime object to ISO format."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")


def set_log_handler(formatter=logging.Formatter(config['app_default']['log-formatter'])):
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.setLevel(os.getenv('LOG_LEVEL', config['app_default']['log-level']).upper())
    logger.addHandler(stream_handler)


def log_transaction(frame_number, name, model, filename=config['app_default']['log-file-dir']):
    """
    Log a transaction as a JSON object in a text file.

    Parameters:
    - timestamp (str): Current timestamp in ISO format.
    - frame_number (int): Frame number.
    - user_id (str): User ID.
    - name (str): Name.
    - contact (str): Contact information.
    - email (str): Email address.
    - detected_at (str): Timestamp when detected in ISO format.
    - total_visit_count (int): Total visit count.
    - model (str): face recognition model.
    - filename (str): File name to append (default: 'transactions.txt').
    """
    # Create JSON object
    data = {
        "timestamp": datetime.now().isoformat(),
        "frame-number": frame_number,
        "user_id": get_element(name, 'user_id'),
        "Name": name,
        "contact": get_element(name, 'contact'),
        "email": '',
        "detected_at": serialize_datetime(get_element(name, 'detected_at')),
        "total_visit_count": get_element(name, 'total_visit_count'),
        "model": model
    }

    # Convert to JSON string
    json_str = json.dumps(data, separators=(',', ':'))

    make_dir_if_not_exist(filename)
    # Append JSON string to the specified text file
    with open(filename, 'a') as file:
        file.write(json_str + '\n')


def get_element(name, element):
    _id = fetch_table_data_in_tuples('', query_data.ID_FOR_NAME % name)[0][0]
    match element:
        case 'user_id':
            return _id
        case 'contact':
            return fetch_table_data_in_tuples('', query_data.CONTACT_FOR_ID % _id)[0][0]
        case 'detected_at':
            return fetch_table_data_in_tuples('', query_data.TIME_IDENTIFIED_FOR_ID % _id)[0][0]
        case 'total_visit_count':
            return fetch_table_data_in_tuples('', query_data.VISIT_COUNT_FOR_ID % _id)[0][0]
        case _:
            return None
