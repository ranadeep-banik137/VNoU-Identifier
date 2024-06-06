import yaml


# Read the YAML file
def read_config(config_path='data/config.yml'):
    config = None
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
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
    with open('config.yml', 'w') as file:
        yaml.dump(config_data, file)
