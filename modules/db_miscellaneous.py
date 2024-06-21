import os
import time
import logging
from datetime import datetime
from modules.database import fetch_table_data_in_tuples, populate_identification_record, update_table, fetch_table_data
from constants.db_constansts import query_data, update_data, Tables
from modules.config_reader import read_config
from modules.date_time_converter import convert_into_epoch

config = read_config()


def is_user_already_identified(name):
    bool_value = False
    _id = 0 if name == '' else fetch_table_data_in_tuples('', query_data.ID_FOR_NAME % name)[0][0]
    identification_table_tuple = fetch_table_data_in_tuples('', query_data.ALL_FOR_ID % _id)
    if identification_table_tuple:
        bool_value = True if str(fetch_table_data_in_tuples('', query_data.IS_IDENTIFIED_FOR_ID % _id)[0][0]) == '1' else False
    return bool_value


def update_timer_for_user_in_background(name, valid_for_seconds=int(
        os.getenv('VOICE_EXPIRY_SECONDS', config['face_recognition']['voice-command-expiry']))):
    current_time = time.time()
    timestamp = datetime.fromtimestamp(current_time).strftime(config['app_default']['timestamp-format'])
    valid_till_timestamp = datetime.fromtimestamp(int(current_time) + valid_for_seconds).strftime(
        config['app_default']['timestamp-format'])
    _id = fetch_table_data_in_tuples('', query_data.ID_FOR_NAME % name)[0][0]
    table_data = fetch_table_data_in_tuples('', query_data.VISIT_COUNT_FOR_ID % _id)
    visit_count = 0
    id_found = False
    if len(table_data) > 0:
        visit_count = int(table_data[0][0])
        id_found = True
    if not id_found:
        populate_identification_record(_id, True, timestamp, valid_till_timestamp, (visit_count + 1))
        logging.debug(f'User {name} has no record in identification_record table and has been created now')
    elif not int(current_time) <= convert_into_epoch(
            str(fetch_table_data_in_tuples('', query_data.VALID_TILL_FOR_ID % _id)[0][0])):
        update_table(update_data.UPDATE_ALL_TIMESTAMPS_WITH_IDENTIFIER % (
            0, valid_till_timestamp, timestamp, (visit_count + 1), _id))
        logging.debug(f'User {name} updated valid till date and visit count in identification records table')
    else:
        update_table(update_data.UPDATE_VISIT_COUNT % (timestamp, (visit_count + 1), _id))
        logging.debug(f'User {name} updated visit count in identification records table')


def update_valid_till_for_expired():
    try:
        header, rows = fetch_table_data(Tables.IDENTIFICATION_RECORDS)
        for row in rows:
            update_table(update_data.UPDATE_BOOL_FOR_ID % (
                0 if int(time.time()) >= convert_into_epoch(str(row[3])) else 1, int(row[0])))
    except Exception as err:
        logging.error(err)
