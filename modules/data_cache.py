import os
import time
import face_recognition as fr
from modules.database import fetch_table_data_in_tuples
from modules.data_reader import convert_binary_to_img, remove_file

# Cached data
cached_data = None
cache_last_updated = 0
reference_encodings = []
names = []
cache_expiry_secs = int(os.getenv('CACHE_EXPIRATION_IN_SECONDS', 10800))


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
    global cache_last_updated
    if time.time() - cache_last_updated > cache_expiry_secs or cached_data is None:
        for row in get_data():
            name = row[1]
            binary_img = row[2]
            image_path = convert_binary_to_img(binary_img, f'{os.getenv("PROJECT_PATH") or ""}data/test{row[0]}.jpg')
            reference_image = fr.load_image_file(image_path)
            encoding = fr.face_encodings(reference_image)
            if encoding:
                reference_encodings.append(encoding[0])
                names.append(name)
            remove_file(image_path)
        cache_last_updated = time.time()

    return reference_encodings, names
