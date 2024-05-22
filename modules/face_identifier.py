import cv2
import os
import re
import time
import datetime
import logging
import numpy as np
import face_recognition as fr
from modules.speech import play_speech
from modules.database import fetch_table_data_in_tuples, populate_identification_record, update_table, fetch_table_data
from modules.data_reader import convert_binary_to_img, remove_file
from modules.data_cache import get_data
from constants.db_constansts import query_data, update_data, Tables
from modules.date_time_converter import convert_into_epoch
from DeepImageSearch import Load_Data


def encode_face():
    input_video_src = int(os.getenv('CAMERA_INDEX', "0"))
    video_capture = cv2.VideoCapture(input_video_src or 0)
    logging.info(
        f'CAMERA_INDEX is set as {"default Web Cam/Camera Source" if input_video_src == 0 else "link " + str(input_video_src)}')

    process_every_n_frames = int(
        os.getenv('FRAME_RATE_RANGE', "5"))  # Adjust this value to balance performance and accuracy
    frame_count = 0

    while True:
        update_valid_till_for_expired()
        identified = False
        ret, frame = video_capture.read()

        if not ret:
            logging.debug('Failed to capture video frame. Retrying....')
            continue

        # Lower the resolution to improve performance
        frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_frame = frame[:, :, ::]  # Convert BGR to RGB

        frame_count += 1
        if frame_count % process_every_n_frames != 0:
            # cv2.imshow('face detection', frame)
            logging.warning('Frame out of bound warning')
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        face_locations = fr.face_locations(rgb_frame,
                                           model=os.getenv('FACE_RECOGNITION_MODEL', 'hog'))  # Use HOG for speed
        logging.debug(f'Face locations: {face_locations}')

        if not face_locations:
            # cv2.imshow('face detection', frame)
            logging.warning('face locations out of bound warning')
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        face_encodings = fr.face_encodings(rgb_frame, face_locations)
        logging.debug(f'Face encodings: {face_encodings}')

        for row in get_data():
            binary_img = row[2]
            img = convert_binary_to_img(binary_img, f'{os.getenv("PROJECT_PATH") or ""}data/test{row[0]}.jpg')
            input_image = fr.load_image_file(img)
            image_face_encodings = fr.face_encodings(input_image)
            if not image_face_encodings:
                logging.warning(f'No face encodings found in image {img}')
                continue
            image_face_encoding = image_face_encodings[0]
            known_face_encoding = [image_face_encoding]
            known_face_names = [row[1]]

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = fr.compare_faces(known_face_encoding, face_encoding, tolerance=0.50)

                default_name = 'Unknown Face'
                face_distances = fr.face_distance(known_face_encoding, face_encoding)
                match_index = np.argmin(face_distances)

                if matches[match_index]:
                    name = known_face_names[match_index]
                    identified = play_speech(name)
                    update_timer_for_user_in_background(name)
                else:
                    if os.getenv('SAVE_UNKNOWN_FACE_IMAGE'):
                        capture_unknown_face_img(frame)
                    # name = default_name

                # Ensure rectangle and text positions are within the frame boundaries
                # cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                # cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)

                # font = cv2.FONT_ITALIC
                # cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            remove_file(img)
            if identified:
                break

        delete_similar_images(f'{os.getenv("PROJECT_PATH") or ""}captured/')

        # cv2.imshow('face detection', frame)
        logging.warning('Frame out of bound warning')
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    # cv2.destroyAllWindows()


def update_timer_for_user_in_background(name, valid_for_seconds=int(os.getenv('VOICE_EXPIRY_SECONDS', "30"))):
    current_time = time.time()
    timestamp = datetime.datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S')
    valid_till_timestamp = datetime.datetime.fromtimestamp(int(current_time) + valid_for_seconds).strftime(
        '%Y-%m-%d %H:%M:%S')
    _id = fetch_table_data_in_tuples('', query_data.ID_FOR_NAME % name)[0][0]
    id_found = False
    try:
        fetch_table_data_in_tuples('', query_data.ALL_FOR_ID % _id)[0][0]
        id_found = True
    except Exception as err:
        logging.error(f'ignore {err}')
    if not id_found:
        populate_identification_record(_id, True, timestamp, valid_till_timestamp)
    elif not int(current_time) <= convert_into_epoch(
            str(fetch_table_data_in_tuples('', query_data.VALID_TILL_FOR_ID % _id)[0][0])):
        update_table(update_data.UPDATE_TIMESTAMP_WITH_IDENTIFIER % (0, valid_till_timestamp, _id))


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
    cv2.imwrite(f"{filepath}NewPicture_{file_name}.jpg", frame)
    logging.debug(f"unidentified person's screen shot has been saved as NewPicture_{file_name}.jpg")


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
        similarity_threshold = int(os.getenv('IMG_SIMILARITY_PERCENT_FOR_DELETE', 30))

        logging.debug(f'MSE for images {image_list[index]} and {image_list[index + 1]}: {mse}')

        if mse < similarity_threshold:
            logging.debug(f'Deleting similar image: {image_list[index]}')
            os.remove(image_list[index])
