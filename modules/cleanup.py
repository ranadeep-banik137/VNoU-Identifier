import logging
import os
from modules.config_reader import read_config
from modules.data_reader import get_file_names, remove_file, make_dir_if_not_exist

config = read_config()


def clean_files(path, delete_files=False):
    if os.path.exists(path):
        files = get_file_names(path)
        for file in files:
            file_path = f'{path}/{file}'
            logging.info(f'Cleaning files {[file in files]} in {path}')
            remove_file(file_path)
            if not delete_files:
                make_dir_if_not_exist(file_path)


def clean_system_cache():
    if config['files']['clear-cache-before-run']:
        clean_files(config['reporting']['path'])
        clean_files('logs')
        clean_files('gui/uploads')
        clean_files('captured', True)
        clean_files('faces')
