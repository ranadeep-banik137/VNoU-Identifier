from modules.database import fetch_table_data_in_tuples
from constants.db_constansts import query_data


def is_user_already_identified(name):
    bool_value = False
    _id = 0 if name == '' else fetch_table_data_in_tuples('', query_data.ID_FOR_NAME % name)[0][0]
    identification_table_tuple = fetch_table_data_in_tuples('', query_data.ALL_FOR_ID % _id)
    if identification_table_tuple:
        bool_value = True if str(fetch_table_data_in_tuples('', query_data.IS_IDENTIFIED_FOR_ID % _id)[0][0]) == '1' else False
    return bool_value
