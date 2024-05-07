import os

from modules.data_transfer import transfer_data_to_db_and_delete_original
from watchdog.events import FileSystemEventHandler
from modules.data_reader import convertToBinaryData, get_file_names, remove_file


class ImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        src_path = os.getenv("GUI_PATH") or "gui/uploads"
        if not event.is_directory:
            try :
                print(get_file_names(src_path))
                transfer_data_to_db_and_delete_original(src_path)
            except Exception as e:
                print('flow break')
                transfer_data_to_db_and_delete_original(src_path)

