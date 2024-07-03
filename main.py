from modules.face_identifier import run_face_recognition
from modules.database import create_table, update_table
from modules.app_logger import set_log_handler
from constants.db_constansts import create_table_queries, update_data


def run_app():
    run_face_recognition()


def initiate_data_tables():
    # create_trigger() # Commented as we are not utilizing the trigger in AWS RDS and logic has been changes In tag 2.0
    create_table(create_table_queries.USERS)
    create_table(create_table_queries.IDENTIFICATION_RECORDS)
    update_table(update_data.RESET_VISIT_COUNT % 0)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    try:
        initiate_data_tables()
        set_log_handler()
        run_app()
    except KeyboardInterrupt:
        print('TODO')
