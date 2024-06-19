import cv2
import re
import time
import logging
import os
import numpy as np
from datetime import datetime
from DeepImageSearch import Load_Data
from modules.config_reader import read_config

config = read_config()


def capture_face_img(frame, filepath=config['files']['save-unknown-image-filepath']):
    file_name = re.sub("[^\w]", "_",
                       datetime.fromtimestamp(time.time()).strftime(config['app_default']['timestamp-format']))
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
