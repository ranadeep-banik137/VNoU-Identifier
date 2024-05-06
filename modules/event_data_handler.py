import os
import logging
from watchdog.events import FileSystemEventHandler
from modules.database import insert_table_data, fetch_table_data_in_tuples, fetch_last_user_id
from modules.data_reader import convertToBinaryData, get_file_names, remove_file


class ImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            file_name = os.path.basename(event.src_path)
            name = file_name.split('-')[0] + ' ' + file_name.split('-')[1] if '-' in file_name else file_name.split('.')[0]

            insert_table_data(fetch_last_user_id() + 1, convertToBinaryData(event.src_path), name)
            logging.info(f"Inserted data for {name}")
            os.remove(event.src_path)
            logging.info(f'Removed the original file {event.src_path}')
