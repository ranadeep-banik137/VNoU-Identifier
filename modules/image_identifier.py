import threading
import cv2
import os
import re
import time
import datetime
import logging
import numpy as np
from modules.face_readers import detect_face_angle_for_face, detect_blurry_variance, recognize_faces, detect_face_locations
from modules.speech import play_speech
from modules.database import fetch_table_data_in_tuples, populate_identification_record, update_table, fetch_table_data
from modules.data_cache import process_db_data
from constants.db_constansts import query_data, update_data, Tables
from modules.date_time_converter import convert_into_epoch
from DeepImageSearch import Load_Data
from modules.config_reader import read_config
from modules.app_logger import log_transaction
from modules.triggers import trigger_mail

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
                    mail_thread = threading.Thread(target=trigger_mail, args=(name, [capture_unknown_face_img(frame)]))
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
                        capture_unknown_face_img(frame)
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


def update_timer_for_user_in_background(name, valid_for_seconds=int(
        os.getenv('VOICE_EXPIRY_SECONDS', config['face_recognition']['voice-command-expiry']))):
    current_time = time.time()
    timestamp = datetime.datetime.fromtimestamp(current_time).strftime(config['app_default']['timestamp-format'])
    valid_till_timestamp = datetime.datetime.fromtimestamp(int(current_time) + valid_for_seconds).strftime(
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


def capture_unknown_face_img(frame, filepath=config['files']['save-unknown-image-filepath']):
    file_name = re.sub("[^\w]", "_",
                       datetime.datetime.fromtimestamp(time.time()).strftime(config['app_default']['timestamp-format']))
    write_file_name = f"{filepath}VNoU_{file_name}.jpg"
    cv2.imwrite(f"{filepath}VNoU_{file_name}.jpg", frame)
    logging.debug(f"unidentified person's screen shot has been saved as VNoU_{file_name}.jpg")
    return write_file_name


def delete_similar_images(filepath):
    image_list = Load_Data().from_folder(folder_list=[filepath])

    # Sort image_list to ensure consistent order
    image_list.sort()

    for index in range(len(image_list) - 1):
        img1 = cv2.imread(image_list[index])
        img2 = cv2.imread(image_list[index + 1])

        if img1 is None or img2 is None:
            logging.warning(f'One of the images could not be loaded: {image_list[index]} or {image_list[index + 1]}')
            continue

        if img1.shape != img2.shape:
            logging.warning(f'Image shapes do not match: {img1.shape} vs {img2.shape}')
            continue

        # Convert the images to grayscale
        img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        # Check the dimensions after conversion
        if img1_gray.shape != img2_gray.shape:
            logging.warning(f'Grayscale image shapes do not match: {img1_gray.shape} vs {img2_gray.shape}')
            continue

        diff = cv2.subtract(img1_gray, img2_gray)
        err = np.sum(diff ** 2)
        mse = err / (float(img1_gray.shape[0] * img1_gray.shape[1]))
        similarity_threshold = int(os.getenv('IMG_SIMILARITY_PERCENT_FOR_DELETE',
                                             config['face_recognition']['delete-img-similarity-percentage']))

        logging.debug(f'MSE for images {image_list[index]} and {image_list[index + 1]}: {mse}')

        if mse < similarity_threshold:
            logging.debug(f'Deleting similar image: {image_list[index]}')
            os.remove(image_list[index])
