import datetime
import re

def convert_into_epoch(time):
    split_val = re.split('[^\w]', time)
    epoch = datetime.datetime(int(split_val[0]), int(split_val[1]), int(split_val[2]), int(split_val[3]), int(split_val[4]), int(split_val[5])).timestamp()
    return int(epoch)
