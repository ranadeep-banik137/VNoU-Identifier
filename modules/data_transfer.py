import time
import logging
import os
from modules.data_reader import get_file_names_excluding_file, wait_until_file_is_ready, convertToBinaryData
from modules.database import populate_users
from modules.config_reader import read_config


def transfer_data_to_database():
    path = "gui/uploads/"  # Use your actual path here
    yaml_file = 'details.yml'
    files = get_file_names_excluding_file(path, yaml_file)
    # logging.info('No files' if not len(files) > 0 else there are files found in {path}')
    if len(files) > 0:
        logging.info(f'Image files and {yaml_file} file found in {path}')
        time.sleep(2)
        for file in files:
            wait_until_file_is_ready(file)
            file_name, file_extension = os.path.splitext(file)
            if file_extension != '' and 'VNoU' in file_name:
                base_config = read_config(f'{path}{yaml_file}')
                try:
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
                except KeyError as error:
                    logging.error(f'Config key not found {error}')
                except Exception as e:
                    logging.error(f'Exception occured {e}')
            else:
                if file_name == 'details':
                    logging.debug(f'{yaml_file} ignored for uploading')
                else:
                    logging.error(f'File {file} is corrupted. Waiting for the file to be written successfully')


def transfer_data_to_db_from_ui():
    path = "gui/uploads/"  # Use your actual path here
    yaml_file = 'details.yml'
    while True:
        files = get_file_names_excluding_file(path, yaml_file)
        # logging.info('No files' if not len(files) > 0 else there are files found in {path}')
        if len(files) > 0:
            logging.info(f'Image files and {yaml_file} file found in {path}')
            time.sleep(2)
            for file in files:
                wait_until_file_is_ready(file)
                file_name, file_extension = os.path.splitext(file)
                if file_extension != '' and 'VNoU' in file_name:
                    base_config = read_config(f'{path}{yaml_file}')
                    try:
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
                    except KeyError as error:
                        logging.error(f'Config key not found {error}')
                    except Exception as e:
                        logging.error(f'Exception occured {e}')
                else:
                    if file_name == 'details':
                        logging.debug(f'{yaml_file} ignored for uploading')
                    else:
                        logging.error(f'File {file} is corrupted. Waiting for the file to be written successfully')
                    continue
