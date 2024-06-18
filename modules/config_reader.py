import yaml
import logging


# Read the YAML file
def read_config(config_path='config/config.yml'):
    config = None
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError as err:
        logging.error(f'Config file not found {err}')
    except Exception as e:
        logging.error(f'Config file reading failed {e}')
    return config


# Write the dictionary to a YAML file
def update_config(config_data=''):
    # Example of setting a config_data
    # config_data = {
    #    'database': {
    #       'host': 'localhost',
    #        'port': 3306,
    #        'user': 'your_username',
    #        'password': 'your_password'
    #    }
    # }
    try:
        with open('config.yml', 'w') as file:
            yaml.dump(config_data, file)
    except FileNotFoundError as err:
        logging.error(f'Config file not found {err}')
    except Exception as e:
        logging.error(f'Config file update failed {e}')
