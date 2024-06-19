import threading
import cv2
import os
import time
import logging
from modules.face_readers import detect_face_angle_for_face, detect_blurry_variance, recognize_faces, detect_face_locations
from modules.speech import play_speech
from modules.data_cache import process_db_data
from modules.config_reader import read_config
from modules.app_logger import log_transaction
from modules.triggers import trigger_mail
from modules.db_miscellaneous import update_timer_for_user_in_background, update_valid_till_for_expired
from modules.file_handler import capture_face_img, delete_similar_images

config = read_config()
event_thread = threading.Event()


def run_face_recognition():
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
    while True:
        reference_encodings, names = process_db_data()
        update_valid_till_for_expired()
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
            if len(face_locations) > 0:
                if detect_blurry_variance(frame):
                    logging.info('The frame is blurred. Retrying with next frame')
                    continue
                if detect_face_angle_for_face(frame):
                    logging.info('The face seems tilted. Retrying for frontal detection')
                    continue
                match_found, match_index = recognize_faces(frame, face_locations, reference_encodings, face_detect_model)
                if match_found:
                    name = names[match_index]
                    logging.info(f"Face identified as: {name}")
                    log_thread = threading.Thread(target=log_transaction, args=(frame_count, name, face_detect_model,))
                    speech_thread = threading.Thread(target=play_speech, args=(name,))
                    mail_thread = threading.Thread(target=trigger_mail, args=(name, [capture_face_img(frame)]))
                    timer_thread = threading.Thread(target=update_timer_for_user_in_background, args=(name,))
                    speech_thread.start()
                    mail_thread.start()
                    speech_thread.join()
                    mail_thread.join()
                    event_thread.set()
                    timer_thread.start()
                    log_thread.start()
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
