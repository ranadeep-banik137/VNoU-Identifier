from modules.face_identifier import encode_face
from modules.database import insert_table_data, fetch_table_data_in_tuples, fetch_last_user_id
from modules.app_logger import set_log_handler


def run_app():
    encode_face(fetch_table_data_in_tuples())


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    set_log_handler()
    run_app()
