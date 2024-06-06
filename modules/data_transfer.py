import os
import logging
from modules.data_reader import get_file_names,convertToBinaryData, wait_until_file_is_ready
from modules.database import populate_users


def transfer_data_to_db_and_delete_original(src_path):
    for file in get_file_names(src_path):
        wait_until_file_is_ready(file)
        logging.info(f'Found new image file got uploaded with filename: {file}')
        file_extension = os.path.splitext(file)
        if file_extension is not '':
            name = file.split('-')[0] + ' ' + file.split('-')[1] if '-' in file else file.split('.')[0]
            populate_users(convertToBinaryData(os.path.join(src_path, file)), name)
            logging.info(f"Inserted data for {name}")
            os.remove(os.path.join(src_path, file))
            logging.info(f'Removed the original file {os.path.join(src_path, file)}')
