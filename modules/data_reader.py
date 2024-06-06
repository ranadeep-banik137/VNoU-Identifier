import os
import shutil
import logging
import time


def read_file(filename=f'{os.getenv("PROJECT_PATH") or ""}data/database.csv'):
    f = open(filename, "r")
    return f.read().splitlines()


def add_entry_to_file(entry, src=f'{os.getenv("PROJECT_PATH") or ""}data/database.csv',
                      bkp_dest=f'{os.getenv("PROJECT_PATH") or ".."}/data/database_bkp.csv', is_backup_needed=True):
    if is_backup_needed:
        shutil.copyfile(src, bkp_dest)
    f = open(src, "a+")
    f.write(entry)


def get_available_image(index):
    try:
        f = open(f'{os.getenv("PROJECT_PATH") or ""}img/{index}.png', "r")
        return f'{os.getenv("PROJECT_PATH") or ""}img/{index}.png'
    except Exception as err:
        return f'{os.getenv("PROJECT_PATH") or ""}img/{index}.jpg'


def convertToBinaryData(filename):
    # Convert digital data to binary format
    logging.info(f'Converting the img in location: {filename} to binary')
    with open(filename, 'rb') as file:
        binary_data = file.read()
    return binary_data


def convert_binary_to_img(data, filename):
    with open(filename, "wb") as fh:
        fh.write(data)
    return filename


def remove_file(filename):
    os.remove(filename)


def get_file_names(folder_path=f'{os.getenv("PROJECT_PATH") or ""}img'):
    return [file_name for file_name in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file_name))]


def is_img_file(file_path):
    flag = False
    if os.path.basename(file_path) in ['.jpg', '.jpeg', '.png', '.img']:
        flag = True
    return flag


def wait_until_file_is_ready(file, retry=5):
    while retry != 0:
        if os.path.exists(file):
            is_file_ready = False
            while not is_file_ready:
                initial_size = os.path.getsize(file)
                time.sleep(10)
                current_size = os.path.getsize(file)
                if initial_size == current_size:
                    is_file_ready = True
                    retry = 0
        else:
            retry = retry - 1
