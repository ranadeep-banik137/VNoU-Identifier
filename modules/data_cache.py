import logging
import os
import time
import face_recognition as fr
from tqdm import tqdm
from modules.database import fetch_table_data_in_tuples
from modules.data_reader import convert_binary_to_img, remove_file, get_missing_items_from_tuple_list
from modules.config_reader import read_config


# Cached data
config = read_config()
cached_data = None
cache_last_updated = 0
reference_encodings = []
names = []
latest_data = []
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
    global cached_data
    global cache_last_updated
    if cached_data is None:
        cached_data = fetch_table_data_in_tuples()
        cache_last_updated = time.time()
        reference_encodings, names = process_encoding(cached_data)
    if time.time() - cache_last_updated > cache_expiry_secs:
        missing_elements = get_missing_items_from_tuple_list(cached_data, fetch_table_data_in_tuples())
        if missing_elements:
            reference_encodings, names = process_encoding(missing_elements, 'Encoding missing data files to cache')
        cache_last_updated = time.time()

    return reference_encodings, names


def process_encoding(rows, desc='Encoding backend files'):
    logging.info(f'Backing up all files from backend/ Maintenance in progress..')
    with tqdm(total=len(rows), desc=desc, unit="file") as pbar:
        for row in get_data():
            name = row[1]
            binary_img = row[2]
            image_path = convert_binary_to_img(binary_img, f'{os.getenv("PROJECT_PATH") or ""}data/test{row[0]}.jpg')
            reference_image = fr.load_image_file(image_path)
            encoding = fr.face_encodings(reference_image)
            if encoding and name.strip() != '':
                reference_encodings.append(encoding[0])
                names.append(name)
            remove_file(image_path)
            pbar.update(1)
    return reference_encodings, names
