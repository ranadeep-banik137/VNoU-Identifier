import datetime
import re
from modules.config_reader import read_config

config = read_config()


def convert_into_epoch(time):
    split_val = re.split('[^\w]', time)
    epoch = datetime.datetime(int(split_val[0]), int(split_val[1]), int(split_val[2]), int(split_val[3]), int(split_val[4]), int(split_val[5])).timestamp()
    return int(epoch)


def convert_epoch_to_timestamp(epoch_time, timestamp_format=config['app_default']['timestamp-format']):
    timestamp = datetime.datetime.fromtimestamp(epoch_time)
    # Format the datetime object to string in the desired format
    formatted_time = timestamp.strftime(timestamp_format)
    return formatted_time
