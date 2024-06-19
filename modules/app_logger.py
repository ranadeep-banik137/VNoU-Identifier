import logging
import os
import json
import time
from datetime import datetime
from modules.config_reader import read_config
from modules.database import fetch_table_data_in_tuples
from constants.db_constansts import query_data
from modules.data_reader import make_dir_if_not_exist, fetch_first_element_in_tuple

config = read_config()


# Define a filter to exclude specific loggers or messages
class InfoFilter(logging.Filter):
    def filter(self, record):
        # Filter out messages from comtypes.client._code_cache logger
        return not record.getMessage().startswith('INFO:comtypes.client._code_cache')


def serialize_datetime(obj):
    """Serialize datetime string or object to ISO format."""
    if obj == '' or obj is None:
        return ''
    elif isinstance(obj, str):
        try:
            # Parse the string into a datetime object
            dt_obj = datetime.strptime(obj, '%Y-%m-%d %H:%M:%S')
            # Return ISO formatted datetime string
            return dt_obj.isoformat()
        except ValueError:
            raise ValueError(f"Cannot parse datetime string: {obj}")
    elif isinstance(obj, datetime):
        # Return ISO formatted datetime string for datetime object
        return obj.isoformat()
    else:
        raise TypeError("Unsupported type for serialization")


def set_log_handler(formatter=logging.Formatter(config['app_default']['log-formatter'])):
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addFilter(InfoFilter())
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
    current_time = datetime.fromtimestamp(time.time()).strftime(config['app_default']['timestamp-format'])
    data = {
        "timestamp": serialize_datetime(current_time),
        "frame-number": frame_number,
        "user_id": get_element(name, 'user_id'),
        "name": name,
        "contact": get_element(name, 'contact'),
        "email": get_element(name, 'email'),
        "detected_at": serialize_datetime(current_time if get_element(name, 'detected_at') == '' else get_element(name, 'detected_at')),
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
    _id = fetch_first_element_in_tuple(fetch_table_data_in_tuples('', query_data.ID_FOR_NAME % name))
    match element:
        case 'user_id':
            return 0 if _id is None else _id
        case 'contact':
            contact = fetch_first_element_in_tuple(fetch_table_data_in_tuples('', query_data.CONTACT_FOR_ID % _id))
            return '' if contact is None else contact
        case 'detected_at':
            detected_at = fetch_first_element_in_tuple(fetch_table_data_in_tuples('', query_data.TIME_IDENTIFIED_FOR_ID % _id))
            return '' if detected_at is None else detected_at
        case 'total_visit_count':
            visit_count = fetch_first_element_in_tuple(fetch_table_data_in_tuples('', query_data.VISIT_COUNT_FOR_ID % _id))
            return 0 if visit_count is None else visit_count
        case _:  # Email yet to be inserted
            return None
