import logging
import os
import json
import time
from datetime import datetime
from modules.config_reader import read_config
from modules.database import fetch_table_data_in_tuples
from constants.db_constansts import query_data
from modules.data_reader import make_dir_if_not_exist, get_tuple_index_from_list_matching_column
from modules.data_cache import get_identification_cache, get_frame_cache
from modules.date_time_converter import convert_epoch_to_timestamp

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


def log_transaction(frame_number, user_id, name, model, is_eligible_for_announcement, filename=config['app_default']['log-file-dir']):
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
    user_data = fetch_table_data_in_tuples('', query_data.ALL_USER_DETAILS_FOR_ID % user_id)[0]
    user_identification_data = get_identification_cache()
    match_index = get_tuple_index_from_list_matching_column(tuple_list=user_identification_data, column_val=user_id, column_index=0)
    data = {
        "timestamp": serialize_datetime(current_time),
        "frame_number": frame_number,
        "user_id": user_id,
        "name": name,
        "contact": user_data[3],
        "email": user_data[4],
        "detected_at": serialize_datetime(convert_epoch_to_timestamp(user_identification_data[match_index][1])),
        "total_visit_count": user_identification_data[match_index][3],
        "model": model,
        "is_repeated_user": not is_eligible_for_announcement,
        "name_announced": is_eligible_for_announcement
    }

    # Convert to JSON string
    json_str = json.dumps(data, separators=(',', ':'))

    make_dir_if_not_exist(filename)
    # Append JSON string to the specified text file
    with open(filename, 'a') as file:
        file.write(json_str + '\n')


def log_notification(user_id, name, images, email, email_sent, cc_email, bcc_email, subject, mail_sent_at, filename=config['mail']['log-file-dir']):
    notifications = {
        "id": user_id,
        "name": name,
        "email_mode": 'SMTP',
        "email_sent": email_sent,
        "email_id": email,
        "email_from": str(config['mail']['id']),
        "cc": cc_email,
        "bcc": bcc_email,
        "subject": subject,
        "attachments": set_attachments_in_log(images),
        "email_sent_at": mail_sent_at
    }
    json_str = json.dumps(notifications, separators=(',', ':'))

    make_dir_if_not_exist(filename)
    # Append JSON string to the specified text file
    with open(filename, 'a') as file:
        file.write(json_str + '\n')


def set_attachments_in_log(images):
    image_list = []
    save_img_to_local = config['mail']['save-image-to-local']
    for image_data, image_name in images:
        image = {"image_saved_to_local": 'True' if save_img_to_local else 'False'}
        if save_img_to_local:
            image["image_link"] = f'{config["files"]["save-unknown-image-filepath"]}{image_name}'
            image["image_title"] = image_name
        image_list.append(image)
    return image_list


def log_unknown_notification(frame_number, model, filename=config['app_default']['log-file-dir_unknown']):
    if frame_number > 0:
        current_time = datetime.fromtimestamp(time.time()).strftime(config['app_default']['timestamp-format'])
        frame_cache = get_frame_cache()
        match_index = get_tuple_index_from_list_matching_column(tuple_list=frame_cache, column_val=frame_number, column_index=0)
        is_detected = frame_cache[match_index][1]
        is_saved = frame_cache[match_index][2]
        images = frame_cache[match_index][3]
        if match_index is not None or match_index != '':
            reason = frame_cache[match_index][4]
            match reason:
                case 'INVALID':
                    str_reason = 'Frame Invalid'
                case 'TILT':
                    str_reason = 'Face Tilted'
                case 'BLUR':
                    str_reason = 'Image Blurred'
                case 'SKIP':
                    str_reason = 'Frame Skipped'
                case 'NIL':
                    str_reason = 'No Face Detected'
                case 'UNIDENTIFIED':
                    str_reason = 'Face Not Identified'
                case _:
                    str_reason = 'Valid Frame'
        unknown_notifications = {
            "timestamp": serialize_datetime(current_time),
            "frame_number": frame_number,
            "model": model,
            "is_person_detected": is_detected,
            "is_img_saved_in_local": is_saved,
            "unidentified_reason": str_reason
        }
        if is_saved and images is not None:
            unknown_notifications['image_link'] = f'{images}'
        if str_reason != 'Valid Frame':
            json_str = json.dumps(unknown_notifications, separators=(',', ':'))

            make_dir_if_not_exist(filename)
            # Append JSON string to the specified text file
            with open(filename, 'a') as file:
                file.write(json_str + '\n')
