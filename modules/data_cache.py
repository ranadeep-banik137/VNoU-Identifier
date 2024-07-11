import base64
import logging
import os
import time
import cv2
import face_recognition as fr
from tqdm import tqdm
from modules.database import fetch_table_data_in_tuples
from modules.data_reader import convert_binary_to_img, remove_file, get_missing_items_from_tuple_list, get_tuple_from_list_matching_column, get_tuple_index_from_list_matching_column, make_dir_if_not_exist, convert_image_url_to_base64
from modules.config_reader import read_config
from modules.date_time_converter import convert_epoch_to_timestamp


# Cached data
config = read_config()
cached_data = None
cache_last_updated = 0
user_id = []
reference_encodings = []
names = []
latest_data = []
identification_data = []
reporting_data = []
total_frame_count = 0
frame_data = []
cache_expiry_secs = int(os.getenv('CACHE_EXPIRATION_IN_SECONDS', config['face_recognition']['cache-expiry']))


def get_data():
    global cached_data
    global cache_last_updated
    # Check if cache is expired or empty
    if time.time() - cache_last_updated > cache_expiry_secs or cached_data is None:
        # Fetch data from the database
        cached_data = fetch_table_data_in_tuples()
        cache_last_updated = time.time()

    return cached_data


def process_db_data():
    global reference_encodings
    global names
    global user_id
    global cached_data
    global cache_last_updated
    if cached_data is None:
        cached_data = fetch_table_data_in_tuples()
        cache_last_updated = time.time()
        user_id, reference_encodings, names = process_encoding(cached_data)
    if time.time() - cache_last_updated > cache_expiry_secs:
        next_update_cache = fetch_table_data_in_tuples()
        missing_elements = get_missing_items_from_tuple_list(cached_data, next_update_cache)
        if missing_elements:
            user_id, reference_encodings, names = process_encoding(missing_elements, 'Encoding missing data files to cache')
            cached_data = next_update_cache
        cache_last_updated = time.time()


def process_encoding(rows, desc='Encoding backend files'):
    logging.info(f'Backing up all files from backend/ Maintenance in progress..')
    with tqdm(total=len(rows), desc=desc, unit="file") as pbar:
        for row in rows:
            _id = row[0]
            name = row[1]
            binary_img = row[2]
            file_path = f'faces/{row[0]}_{name}.jpg'
            make_dir_if_not_exist(file_path)
            image_path = convert_binary_to_img(binary_img, file_path)
            reference_image = fr.load_image_file(image_path)
            rgb_image = cv2.cvtColor(reference_image, cv2.COLOR_BGR2RGB)
            encodings = fr.face_encodings(rgb_image, fr.face_locations(rgb_image))
            if encodings and name.strip() != '' and _id != '':
                user_id.append(_id)
                reference_encodings.append(encodings[0])
                names.append(name)
            if not os.getenv('SAVE_DB_DATA_TO_LOCAL', config['app_default']['save-db-data-to-local']):
                remove_file(image_path)
            pbar.update(1)
    return user_id, reference_encodings, names


def get_cache():
    return user_id, reference_encodings, names


def get_identification_cache():
    return identification_data


def get_reporting_cache():
    return reporting_data


def get_total_app_frames():
    return total_frame_count


def get_frame_cache():
    return frame_data


def update_frame_counts(count):
    global total_frame_count
    total_frame_count = count


def update_user_identification_cache(_id):
    global identification_data
    id_list = get_tuple_from_list_matching_column(tuple_list=identification_data, column_index=0, column_val=_id)
    count = 1
    time_identified = int(time.time())
    valid_till = int(config['face_recognition']['voice-command-expiry']) + time_identified
    if id_list is not None:
        match_index = get_tuple_index_from_list_matching_column(tuple_list=identification_data, column_index=0, column_val=_id)
        count = identification_data[match_index][3] + 1
        valid_till = identification_data[match_index][2]
        logging.debug(f'Cache has identification records for userId: {identification_data[match_index][0]}')
        identification_data.pop(match_index)
        logging.debug(f'Cache removed data for userID: {_id}')
    identification_data.append((_id, time_identified, valid_till, count, (valid_till < time_identified)))
    logging.debug(f'Cache added data for userID: {_id} which is valid till: {convert_epoch_to_timestamp(valid_till)}')
    logging.debug(f'Cache list has data count for {len(identification_data)} records after updating')


def is_user_eligible_for_announcement(_id):
    match_index = get_tuple_index_from_list_matching_column(tuple_list=identification_data, column_index=0, column_val=_id)
    val = True if match_index is None else identification_data[match_index][4]
    logging.debug(f'Data for userID {_id} {"does not have its identification cached. Hence eligible for announcement" if match_index is None else ("has its identification cached. And it is eligible for announcement" if val else "has its identification cached but not eligible for announcement")}')
    return val


def cache_email_reporting_items(_id, name, email_id, is_email_sent, email_sent_at, img_data=[]):
    global reporting_data
    # tup = (_id, name, email_id, email_sent_at, email_count)
    e_list = get_tuple_from_list_matching_column(tuple_list=reporting_data, column_index=0, column_val=_id)
    email_count = 1 if is_email_sent else 0
    # img_file = None Was kept for directly referring the images from repository. Instead, it is now encoded and added in html
    base64_img = convert_image_url_to_base64('https://static8.depositphotos.com/1009634/988/v/450/depositphotos_9883921-stock-illustration-no-user-profile-picture.jpg') # This is blank image to be used as default one if user mail was not sent with any image
    for img_binary, img_name in img_data:
        # img = f'{config["files"]["save-unknown-image-filepath"]}{img_name}'
        # img_file = f'/{img}' if os.path.exists(img) else None
        base64_img = base64.b64encode(img_binary).decode('utf-8')
    if e_list is not None:
        match_index = get_tuple_index_from_list_matching_column(tuple_list=reporting_data, column_index=0, column_val=_id)
        email_count = reporting_data[match_index][4] + 1
        logging.debug(f'Cache has email records for userId: {reporting_data[match_index][0]}')
        reporting_data.pop(match_index)
        logging.debug(f'Email cache removed data for user: {name}')
    reporting_data.append((_id, name, email_id, email_sent_at if is_email_sent else None, email_count, base64_img))
    logging.debug(f'Email cache list has data count for {len(reporting_data)} records after updating')


def cache_frame_data(frame_number, is_detected, is_unknown_img_saved, img_path, reason=''):
    global frame_data
    frame_data.append((frame_number, is_detected, is_unknown_img_saved, img_path, reason))
