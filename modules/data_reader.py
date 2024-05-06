import os
import shutil


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
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData


def convert_binary_to_img(data, filename):
    with open(filename, "wb") as fh:
        fh.write(data)
    return filename


def remove_file(filename):
    os.remove(filename)


def get_file_names(folder_path=f'{os.getenv("PROJECT_PATH") or ""}img'):
    return [file_name for file_name in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file_name))]
