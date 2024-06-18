import cv2
import logging
import numpy as np
import face_recognition as fr
from mtcnn import MTCNN
from modules.config_reader import read_config

config = read_config()


def calculate_face_angle(left_eye_center, right_eye_center):
    eye_delta = right_eye_center - left_eye_center
    angle = np.arctan2(eye_delta[1], eye_delta[0]) * 180.0 / np.pi
    return angle


def detect_blurry_variance(frame):
    is_face_blurred = False
    blur_threshold = int(config['face_config']['img-blur-threshold-percentage'])
    variance = cv2.Laplacian(frame, cv2.CV_64F).var()
    if variance < blur_threshold:
        is_face_blurred = True
        logging.info("Face is blurred or not properly detected. Please stand still for better detection")
    else:
        logging.debug("Face is clear.")
    return is_face_blurred


def detect_face_angle_for_face(frame):
    list_of_face_angles = []
    # rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # Detect facial landmarks
    face_landmarks_list = fr.face_landmarks(frame)

    for face_landmarks in face_landmarks_list:
        # Extract the coordinates of the left eye, right eye, and nose tip
        left_eye = face_landmarks['left_eye']
        right_eye = face_landmarks['right_eye']

        if len(left_eye) == 0 or len(right_eye) == 0:
            list_of_face_angles.append(True)
            logging.warning("One or both eyes not detected.")
            continue

        # Compute the center points of the eyes
        left_eye_center = np.mean(left_eye, axis=0)
        right_eye_center = np.mean(right_eye, axis=0)

        # Calculate the angle between the eyes
        # eye_delta_x = right_eye_center[0] - left_eye_center[0]
        # eye_delta_y = right_eye_center[1] - left_eye_center[1]
        # angle = np.arctan2(eye_delta_y, eye_delta_x) * 180.0 / np.pi
        angle = calculate_face_angle(left_eye_center, right_eye_center)
        logging.debug(f'Face tilt angle: {angle:.2f} degrees')

        # Determine if the face is tilted
        if abs(angle) > int(config['face_config']['img-tilt-threshold-angle']):  # You can adjust the threshold angle as needed
            logging.info("Face is tilted.")
            list_of_face_angles.append(True)
        else:
            logging.debug("Face is frontal.")
            list_of_face_angles.append(False)
    num_true = list_of_face_angles.count(True)
    num_false = list_of_face_angles.count(False)
    return num_true >= num_false


def detect_face_locations(image, model):
    face_locations = None
    match model:
        case 'mtcnn':
            detector = MTCNN()
            frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            faces = detector.detect_faces(frame)
            # detect_face_angle(faces)
            face_locations = [
                (face['box'][1], face['box'][0] + face['box'][2], face['box'][1] + face['box'][3], face['box'][0])
                for face in faces]
        case 'cascade':
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            faces = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml').detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            face_locations = []
            for (x, y, w, h) in faces:
                face_locations.append((y, x + w, y + h, x))
        case 'VNoU':
            # small_frame = cv2.resize(image, (0, 0), fx=0.5, fy=0.5)
            rgb_frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_locations = fr.face_locations(rgb_frame)
        case _:
            face_locations = []
    return face_locations


def recognize_faces(frame, face_locations, reference_encodings, model):
    match model:
        case 'cascade':
            # small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        case _:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = frame[:, :, ::]
    face_encodings = fr.face_encodings(frame, known_face_locations=face_locations, num_jitters=1)
    for face_encoding in face_encodings:
        if face_encodings:
            logging.info('Face detected in frame')
            matches = fr.compare_faces(reference_encodings, face_encoding)
            face_distances = fr.face_distance(reference_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if best_match_index > len(matches):
                logging.error(f'Error in face image in backend. Please change backend images')
                return False, None
            if matches[best_match_index]:
                return True, best_match_index
    return False, None
