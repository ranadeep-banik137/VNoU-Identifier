from modules.face_identifier import encode_face
from modules.app_logger import set_log_handler


def run_app():
    encode_face()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    set_log_handler()
    run_app()
