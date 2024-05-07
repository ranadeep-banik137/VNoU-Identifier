import os
import logging
from modules.data_reader import get_file_names,convertToBinaryData
from modules.database import insert_table_data,fetch_last_user_id


def transfer_data_to_db_and_delete_original(src_path):
    for file in get_file_names(src_path):
        file_extension = os.path.splitext(file)
        if file_extension is not '':
            name = file.split('-')[0] + ' ' + file.split('-')[1] if '-' in file else file.split('.')[0]
            insert_table_data(fetch_last_user_id() + 1, convertToBinaryData(os.path.join(src_path, file)), name)
            logging.info(f"Inserted data for {name}")
            os.remove(os.path.join(src_path, file))
            logging.info(f'Removed the original file {os.path.join(src_path, file)}')
