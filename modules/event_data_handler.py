import os
import logging
import time
from modules.data_transfer import transfer_data_to_db_from_ui
from watchdog.events import FileSystemEventHandler
from modules.data_reader import convertToBinaryData, get_file_names, remove_file


class ImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        src_path = os.getenv("GUI_PATH") or "gui/uploads"
        if not event.is_directory:
            try:

                print(get_file_names(src_path))
                transfer_data_to_db_from_ui()
            except Exception as e:
                logging.error('Flow break')
                transfer_data_to_db_from_ui()
