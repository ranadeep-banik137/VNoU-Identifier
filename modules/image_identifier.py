import threading
import cv2
import os
import re
import time
import datetime
import logging
import numpy as np
import face_recognition as fr
from mtcnn import MTCNN
from modules.speech import play_speech
from modules.database import fetch_table_data_in_tuples, populate_identification_record, update_table, fetch_table_data
from modules.data_cache import process_db_data
from constants.db_constansts import query_data, update_data, Tables
from modules.date_time_converter import convert_into_epoch
from DeepImageSearch import Load_Data


def detect_faces_with_haarcascade(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    faces = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml').detectMultiScale(gray,
                                                                                                                  scaleFactor=1.1,
                                                                                                                  minNeighbors=5,
                                                                                                                  minSize=(
                                                                                                                  30,
                                                                                                                  30))
    return faces


def detect_faces_with_mtcnn(image):
    detector = MTCNN()
    faces = detector.detect_faces(image)
    face_locations = [(face['box'][1], face['box'][0] + face['box'][2], face['box'][1] + face['box'][3], face['box'][0]) for face in faces]
    return face_locations


def recognize_faces_with_faces(frame, faces, reference_encodings):
    rgb_frame = frame[:, :, ::]
    for (x, y, w, h) in faces:
        face_image = rgb_frame[y:y+w, x:x+h]
        face_encodings = fr.face_encodings(face_image)
        if face_encodings:
            face_encoding = face_encodings[0]
            logging.info('Face detected in frame')
            matches = fr.compare_faces(reference_encodings, face_encoding)
            if True in matches:
                return True, matches.index(True)
    return False, None


def recognize_faces_with_face_locations(frame, face_locations, reference_encodings):
    rgb_frame = frame[:, :, ::]
    face_encodings = fr.face_encodings(rgb_frame, face_locations) if face_locations else fr.face_encodings(rgb_frame)
    for face_encoding in face_encodings:
        if face_encodings:
            logging.info('Face detected in frame')
            matches = fr.compare_faces(reference_encodings, face_encoding)
            face_distances = fr.face_distance(reference_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                return True, best_match_index
            # if True in matches:
            #    return True, matches.index(True)
    return False, None


face_recognizers = {
    'cnn': recognize_faces_with_face_locations,
    'other': recognize_faces_with_faces
}

face_detector = {
    'cnn' : detect_faces_with_mtcnn,
    'other' : detect_faces_with_haarcascade
}

def run_face_recognition():
    input_video_src = os.getenv('CAMERA_INDEX', '0')
    cap = cv2.VideoCapture(input_video_src if not input_video_src.isdigit() else int(input_video_src))
    logging.info(
        f'CAMERA_INDEX is set as {"default Web Cam/Camera Source" if input_video_src == 0 else "link " + str(input_video_src)}')

    process_every_n_frames = int(
        os.getenv('FRAME_RATE_RANGE', "5"))  # Adjust this value to balance performance and accuracy
    logging.info(f'Frames will be skipped every {process_every_n_frames} seconds')
    frame_count = 0

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
            face_detect_model = os.getenv('FACE_RECOGNITION_MODEL', 'cnn')
            face_locations = face_detector[face_detect_model](frame)
            if face_locations:
                match_found, match_index = face_recognizers[face_detect_model](frame, face_locations, reference_encodings)
                if match_found:
                    name = names[match_index]
                    logging.info(f"Face identified as: {name}")
                    threading.Thread(target=play_speech, args=(name,)).start()
                    threading.Thread(target=update_timer_for_user_in_background, args=(name,)).start()
                    continue
                else:
                    if os.getenv('SAVE_UNKNOWN_FACE_IMAGE', True):
                        capture_unknown_face_img(frame)
            else:
                logging.info('No face detected')
                continue

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            logging.warning('Frame not loaded correctly. Loading next frame..')
            continue
    threading.Thread(target=delete_similar_images, args=(f'{os.getenv("PROJECT_PATH") or ""}captured/',)).start()
    cap.release()


def update_timer_for_user_in_background(name, valid_for_seconds=int(os.getenv('VOICE_EXPIRY_SECONDS', "30"))):
    current_time = time.time()
    timestamp = datetime.datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S')
    valid_till_timestamp = datetime.datetime.fromtimestamp(int(current_time) + valid_for_seconds).strftime(
        '%Y-%m-%d %H:%M:%S')
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
        update_table(update_data.UPDATE_ALL_TIMESTAMPS_WITH_IDENTIFIER % (0, valid_till_timestamp, timestamp, (visit_count + 1), _id))
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


def capture_unknown_face_img(frame, filepath=f'{os.getenv("PROJECT_PATH") or ""}captured/'):
    file_name = re.sub("[^\w]", "_", datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    cv2.imwrite(f"{filepath}VNoU_{file_name}.jpg", frame)
    logging.debug(f"unidentified person's screen shot has been saved as VNoU_{file_name}.jpg")


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
        similarity_threshold = int(os.getenv('IMG_SIMILARITY_PERCENT_FOR_DELETE', 20))

        logging.debug(f'MSE for images {image_list[index]} and {image_list[index + 1]}: {mse}')

        if mse < similarity_threshold:
            logging.debug(f'Deleting similar image: {image_list[index]}')
            os.remove(image_list[index])
