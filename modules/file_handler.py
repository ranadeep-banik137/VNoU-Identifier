import cv2
import re
import time
import logging
import os
import numpy as np
from datetime import datetime
from DeepImageSearch import Load_Data
from modules.config_reader import read_config
from modules.data_reader import make_dir_if_not_exist

config = read_config()


def capture_face_img(frame, filepath=config['files']['save-unknown-image-filepath'], img_name=None):
    file_name = re.sub("[^\w]", "_",
                       datetime.fromtimestamp(time.time()).strftime(config['app_default']['timestamp-format']))
    write_file_name = f"{filepath}VNoU_{file_name}.jpg" if img_name is None else f"{filepath}{img_name}"
    make_dir_if_not_exist(write_file_name)
    cv2.imwrite(write_file_name, frame)
    logging.debug(f"unidentified person's screen shot has been saved as VNoU_{file_name}.jpg")
    return write_file_name


def capture_face_img_with_face_marked(frame, name, face_locations):
    for face_location in face_locations:
        top, right, bottom, left = face_location

        # Draw rectangle around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 155, 255), 2)
        # landmarks = fr.face_landmarks(frame, [face_location])
        # for facial_feature in landmarks[0].keys():
        #    for point in landmarks[0][facial_feature]:
        #        cv2.circle(frame, point, 0.5, (0, 155, 255), 0.5)  # Green circles for facial landmarks
        cv2.putText(frame, name, (left, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 155, 255), 2)
    _, buffer = cv2.imencode('.jpg', frame)
    image_data = buffer.tobytes()
    image_name = f"VNoU_{name}.jpg"
    if config['mail']['save-image-to-local']:
        capture_face_img(frame, img_name=image_name)
    return image_data, image_name


def delete_similar_images(filepath=config['files']['save-unknown-image-filepath']):
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
