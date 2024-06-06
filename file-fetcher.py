import time
import logging
import os
from modules.data_reader import get_file_names, wait_until_file_is_ready, convertToBinaryData
from modules.app_logger import set_log_handler
from modules.database import populate_users


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    set_log_handler()
    path = "gui/uploads/"  # Use your actual path here
    while True:
        files = get_file_names(path)
        logging.info('No files' if not len(files) > 0 else f'there are files found in {path}')
        if len(files) > 0:
            time.sleep(2)
            for file in files:
                wait_until_file_is_ready(file)
                file_name, file_extension = os.path.splitext(file)
                if file_extension is not '' and '-' in file_name:
                    name = file_name.split('-')[0] + ' ' + file_name.split('-')[1] if '-' in file_name else file_name.split('.')[0]
                    populate_users(convertToBinaryData(os.path.join(path, file)), name)
                    logging.info(f"Inserted data for {name}")
                    os.remove(os.path.join(path, file))
                    logging.info(f'Removed the original file {os.path.join(path, file)}')
                else:
                    logging.error(f'File {file} is corrupted. Waiting for the file to be written successfully')
                    continue
