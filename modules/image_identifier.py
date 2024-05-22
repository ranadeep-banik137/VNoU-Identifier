import threading
import queue
import face_recognition as fr
import cv2
import os
import time
import logging
import numpy as np
from modules.speech import play_speech
from modules.data_reader import convert_binary_to_img
from modules.data_cache import get_data

# Define a global variable to control the process
stop_event = threading.Event()

# Define a queue to hold pictures
picture_queue = queue.Queue()

# Function to generate pictures
def picture_producer():
    video_capture = cv2.VideoCapture(0)
    process_every_n_frames = int(os.getenv('FRAME_RATE_RANGE', "5"))
    frame_count = 0
    counter = 0
    while not stop_event.is_set():
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to capture frame from camera.")
            break

        frame_count += 1
        if frame_count % process_every_n_frames == 0:
            face_locations = fr.face_locations(frame,
                                           model=os.getenv('FACE_RECOGNITION_MODEL', 'hog'))
            if not face_locations:
                #cv2.imshow('face detection', frame)
                print('No face locations')
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue
            face_encodings = fr.face_encodings(frame, face_locations)
            if face_encodings:
                picture_queue.put(zip(face_locations, face_encodings))
                print(f"Produced picture with face encodings.")
        time.sleep(0.1)
    video_capture.release()

# Function to consume pictures
def picture_consumer():
    while not stop_event.is_set():
        try:
            cam_face_encodings = picture_queue.get(timeout=1)
            print('Picture fetched from queue')
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

                for (top, right, bottom, left), face_encoding in cam_face_encodings:
                    matches = fr.compare_faces(known_face_encoding, face_encoding, tolerance=0.50)
                    default_name = 'Unknown Face'
                    face_distances = fr.face_distance(known_face_encoding, face_encoding)
                    match_index = np.argmin(face_distances)

                    if matches[match_index]:
                        name = known_face_names[match_index]
                        identified = play_speech(name)
                        # update_timer_for_user_in_background(name)
                    else:
                        # capture_unknown_face_img(frame)
                        name = default_name
                #remove_file(img)

            picture_queue.task_done()
        except queue.Empty:
            print('The queue is empty, continue to the next iteration')
        except Exception as e:
            print(f'Error: {e}')

# Main method
def main():
    producer_thread = threading.Thread(target=picture_producer)
    consumer_thread = threading.Thread(target=picture_consumer)

    producer_thread.start()
    consumer_thread.start()

    input("Press Enter to stop...")
    stop_event.set()

    producer_thread.join()
    consumer_thread.join()

def compare_faces(image_path1, image_path2):
    image1 = fr.load_image_file(image_path1)
    face_locations1 = fr.face_locations(image1)
    face_encodings1 = fr.face_encodings(image1, face_locations1)
    if len(face_encodings1) == 0:
        print(f"No faces found in the first image: {image_path1}")
        return False

    image2 = fr.load_image_file(image_path2)
    face_locations2 = fr.face_locations(image2)
    face_encodings2 = fr.face_encodings(image2, face_locations2)
    if len(face_encodings2) == 0:
        print(f"No faces found in the second image: {image_path2}")
        return False

    face_encoding1 = face_encodings1[0]
    face_encoding2 = face_encodings2[0]

    results = fr.compare_faces([face_encoding1], face_encoding2)
    face_distance = fr.face_distance([face_encoding1], face_encoding2)
    return results[0], face_distance[0]

def is_match(img1, img2):
    are_same_person, distance = compare_faces(img1, img2)
    if are_same_person:
        print(f"The faces in the images are of the same person (distance: {distance}).")
    else:
        print(f"The faces in the images are not of the same person (distance: {distance}).")
    return are_same_person

if __name__ == "__main__":
    main()
