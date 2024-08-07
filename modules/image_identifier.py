import threading
import cv2
import os
import time
import logging
from modules.data_transfer import transfer_data_to_database
from modules.face_readers import detect_face_angle_for_face, detect_blurry_variance, recognize_faces, detect_face_locations
from modules.speech import play_speech
from modules.data_cache import process_db_data, get_cache
from modules.config_reader import read_config
from modules.app_logger import log_transaction
from modules.triggers import trigger_mail
from modules.db_miscellaneous import update_timer_for_user_in_background, update_valid_till_for_expired, is_user_already_identified
from modules.file_handler import capture_face_img, delete_similar_images, capture_face_img_with_face_marked

config = read_config()
event_thread = threading.Event()
reference_encodings = []
names = []
user_ids = []


def run_face_recognition():
    global reference_encodings
    global names
    face_config = config['face_recognition']
    input_video_src = str(os.getenv('CAMERA_INDEX', face_config['camera-index']))
    cap = cv2.VideoCapture(input_video_src if not input_video_src.isdigit() else int(input_video_src))
    logging.info(
        f'CAMERA_INDEX is set as {"default Web Cam/Camera Source" if input_video_src == 0 else "link " + str(input_video_src)}')

    process_every_n_frames = int(
        os.getenv('FRAME_RATE_RANGE',
                  face_config['frame-rate-range']))  # Adjust this value to balance performance and accuracy
    logging.info(f'Frames will be skipped every {process_every_n_frames} seconds')
    frame_count = 0
    frame_fail_count = 0
    process_db_data()
    while True:
        test_time = get_test_time()
        # transfer_data_to_database()
        transfer_thread = threading.Thread(target=transfer_data_to_database)
        transfer_thread.start()
        transfer_thread.join()
        logging.info(f'It took {(test_time - get_test_time())} seconds on first thread to transfer data to DB')
        threading.Thread(target=process_db_data()).start()
        logging.info(f'It took {(test_time - get_test_time())} seconds on second thread to process data from DB')
        user_ids, reference_encodings, names = get_cache()
        logging.info(f'It took {(test_time - get_test_time())} seconds to process data from cache')
        # threading.Thread(target=update_valid_till_for_expired).start()
        logging.info(f'It took {(test_time - get_test_time())} seconds update DB on valid till expired')
        ret, frame = cap.read()
        frame_count += 1
        if frame_count % process_every_n_frames != 0:
            logging.warning(f'Index frame {frame_count} skipped')
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue
        if ret:
            face_detect_model = os.getenv('FACE_RECOGNITION_MODEL', face_config['face-recognition-model'])
            face_locations = detect_face_locations(frame, face_detect_model)
            logging.debug(f'It took {(test_time - get_test_time())} seconds to detect model')
            if len(face_locations) > 0:
                if detect_blurry_variance(frame):
                    logging.info('The frame is blurred. Retrying with next frame')
                    logging.debug(f'It took {(test_time - get_test_time())} seconds to detect blurriness')
                    continue
                if detect_face_angle_for_face(frame):
                    logging.info('The face seems tilted. Retrying for frontal detection')
                    logging.debug(f'It took {(test_time - get_test_time())} seconds to detect angle of face')
                    continue
                face_match_index_list = recognize_faces(frame, face_locations, reference_encodings, face_detect_model)
                logging.debug(f'It took {(test_time - get_test_time())} seconds to match faces')
                for (match_found, match_index), face in zip(face_match_index_list, face_locations):
                    if match_found and not detect_blurry_variance(face):
                        user_id = user_ids[match_index]
                        name = names[match_index]
                        logging.info(f"Face identified as: {name}")
                        is_identified = is_user_already_identified(name)
                        if not is_identified:
                            speech_thread = threading.Thread(target=play_speech, args=(name,))
                            mail_thread = threading.Thread(target=trigger_mail, args=(user_id, name, [capture_face_img_with_face_marked(frame, name, face_locations)]))
                            speech_thread.start()
                            logging.debug(f'It took {(test_time - get_test_time())} seconds after starting speech thread')
                            mail_thread.start()
                            logging.debug(f'It took {(test_time - get_test_time())} seconds after starting mail thread')
                            speech_thread.join()
                            mail_thread.join()
                        timer_thread = threading.Thread(target=update_timer_for_user_in_background, args=(name,))
                        log_thread = threading.Thread(target=log_transaction,
                                                      args=(frame_count, user_id, name, face_detect_model, is_identified,))
                        logging.debug(f'It took {(test_time - get_test_time())} seconds after completing both threads')
                        event_thread.set()
                        timer_thread.start()
                        log_thread.start()
                        logging.debug(f'It took {(test_time - get_test_time())} seconds after completing all threads')
                        continue
                    else:
                        if os.getenv('SAVE_UNKNOWN_FACE_IMAGE', face_config['capture-unknown-face']):
                            capture_face_img(frame)
            else:
                logging.info('No face detected')
                continue

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            frame_fail_count += 1
            if frame_fail_count > int(os.getenv('FRAME_MAX_RESET_COUNT', face_config['frame-max-reset-seconds'])):
                time.sleep(0.5)  # Wait for 1 second
                logging.error(f'Frame loading timed out after {frame_fail_count} seconds')
                break
            logging.warning('Frame not loaded correctly. Loading next frame..')
            continue
        threading.Thread(target=delete_similar_images, args=(config['files']['save-unknown-image-filepath'],)).start()
    cap.release()


def get_test_time():
    return int(time.time())
