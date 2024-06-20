import time
import logging
import os
from modules.data_reader import get_file_names, wait_until_file_is_ready, convertToBinaryData
from modules.app_logger import set_log_handler
from modules.database import populate_users
from modules.config_reader import read_config, clear_yaml_file


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    set_log_handler()
    path = "gui/uploads/"  # Use your actual path here
    yaml_file = 'details.yml'
    while True:
        files = get_file_names(path)
        # logging.info('No files' if not len(files) > 0 else there are files found in {path}')
        if len(files) > 0 and yaml_file in files:
            logging.info(f'Image files and {yaml_file} file found in {path}')
            time.sleep(2)
            for file in files:
                wait_until_file_is_ready(file)
                file_name, file_extension = os.path.splitext(file)
                if file_extension is not '' and 'VNoU' in file_name:
                    base_config = read_config(f'{path}{yaml_file}')
                    file_config = base_config[file_name]
                    first_name = str(file_config['first_name'])
                    middle_name = str(file_config['middle_Name'])
                    last_name = str(file_config['last_Name'])
                    name = f"{first_name} {'' if middle_name.strip() == '' else middle_name + ' '}{last_name}"
                    contact = str(file_config['phone'])
                    email = str(file_config['email'])
                    populate_users(convertToBinaryData(os.path.join(path, file)), name, contact, email, '', '', '', '')
                    logging.info(f"Inserted data for {name}")
                    os.remove(os.path.join(path, file))
                    logging.info(f'Removed the original file {os.path.join(path, file)}')
                else:
                    if file_name == 'details':
                        logging.debug(f'{yaml_file} ignored for uploading')
                    else:
                        logging.error(f'File {file} is corrupted. Waiting for the file to be written successfully')
                    continue
            logging.debug('Clearing the details data')
            clear_yaml_file(f'{path}{yaml_file}')
