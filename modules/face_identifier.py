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


def encode_face(tuple_data=None):
    input_video_src = 0 if os.getenv('CAMERA_INDEX') is None else os.getenv('CAMERA_INDEX')
    input_video_src = int(input_video_src) if re.fullmatch(r"\d+", str(input_video_src)) else input_video_src
    video_capture = cv2.VideoCapture(input_video_src or 0)
    logging.info(f'CAMERA_INDEX is set as {"default Web Cam/Camera Source" if str(input_video_src).isnumeric() else "link" + input_video_src}')
    while True:
        update_valid_till_for_expired()
        identified = None
        ret, frame = video_capture.read()
        if not (video_capture.isOpened() or frame or ret):
            logging.debug('Video capture not processed correctly. Retrying....')
            encode_face(tuple_data)
        rgb_frame = frame[:, :, ::]
        face_locations = fr.face_locations(rgb_frame, model='cnn' if os.getenv('HIGH_QUALITY_ENCODING') is not None else 'hog')
        face_encodings = fr.face_encodings(rgb_frame, face_locations)
        # for line in read_file():
        for row in get_data():
            IMG_BLOB = row[2]
            img = convert_binary_to_img(IMG_BLOB, f'{os.getenv("PROJECT_PATH") or ""}data/test{row[0]}.jpg')
            input_image = fr.load_image_file(img)
            image_face_encoding = fr.face_encodings(input_image)[0]
            known_face_encoding = [image_face_encoding]
            known_face_names = [row[1]]

            for(top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = fr.compare_faces(known_face_encoding, face_encoding, tolerance=0.50)

                default_name = 'Unknown Face'
                face_distances = fr.face_distance(known_face_encoding, face_encoding)
                match_index = np.argmin(face_distances)

                if matches[match_index]:
                    name = known_face_names[match_index]
                    identified = play_speech(name)
                    update_timer_for_user_in_background(name)
                else:
                    capture_unknown_face_img(frame)
                    name = default_name

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)

                font = cv2.FONT_ITALIC

                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            cv2.imshow('face detection', frame)
            remove_file(img)
            if identified:
                break
        delete_similar_images(f'{os.getenv("PROJECT_PATH") or ""}captured/')
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        #play_speech(name)

    video_capture.release()
    # cv2.destroyAllWindows()


def update_timer_for_user_in_background(name, valid_for_seconds=os.getenv('VOICE_EXPIRY_SECONDS') or 30):
    current_time = time.time()
    timestamp = datetime.datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S')
    valid_till_timestamp = datetime.datetime.fromtimestamp(int(current_time) + valid_for_seconds).strftime('%Y-%m-%d %H:%M:%S')
    _id = fetch_table_data_in_tuples('', query_data.ID_FOR_NAME % name)[0][0]
    id_found = False
    try:
        fetch_table_data_in_tuples('', query_data.ALL_FOR_ID % _id)[0][0]
        id_found = True
    except Exception as err:
        logging.error(f'ignore {err}')
    if not id_found:
        populate_identification_record(_id, True, timestamp, valid_till_timestamp)
    elif not int(current_time) <= convert_into_epoch(str(fetch_table_data_in_tuples('', query_data.VALID_TILL_FOR_ID % _id)[0][0])):
        update_table(update_data.UPDATE_TIMESTAMP_WITH_IDENTIFIER % (0, valid_till_timestamp, _id))


def update_valid_till_for_expired():
    try:
        header, rows = fetch_table_data(Tables.IDENTIFICATION_RECORDS)
        for row in rows:
            update_table(update_data.UPDATE_BOOL_FOR_ID % (0 if int(time.time()) >= convert_into_epoch(str(row[3])) else 1, int(row[0])))
    except Exception as err:
        logging.error(err)


def capture_unknown_face_img(frame, filepath=f'{os.getenv("PROJECT_PATH") or ""}captured/'):
    file_name = re.sub("[^\w]", "_", datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    cv2.imwrite(f"{filepath}NewPicture_{file_name}.jpg", frame)
    logging.info(f"unidentified person's screen shot has been saved as NewPicture_{file_name}.jpg")


def delete_similar_images(filepath):
    image_list = Load_Data().from_folder(folder_list=[filepath])

    for index in range(len(image_list) - 1):
        img1 = cv2.imread(image_list[index])
        img2 = cv2.imread(image_list[index + 1])

        # convert the images to grayscale
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        h, w = img1.shape
        diff = cv2.subtract(img1, img2)
        err = np.sum(diff**2)
        mse = err/(float(h*w))
        if int(mse) < (int(os.getenv('IMG_SIMILARITY_PERCENT_FOR_DELETE')) if os.getenv('IMG_SIMILARITY_PERCENT_FOR_DELETE') is not None else 30):
            logging.debug(f'Deleting img : {image_list[index]}')
            os.remove(image_list[index])
