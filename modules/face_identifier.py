import threading
import cv2
import os
import time
import logging
from modules.data_transfer import transfer_data_to_database
from modules.face_readers import detect_face_angle_for_face, detect_blurry_variance, recognize_faces, detect_face_locations
from modules.speech import play_speech
from modules.data_cache import process_db_data, get_cache, is_user_eligible_for_announcement, update_user_identification_cache, update_frame_counts
from modules.config_reader import read_config
from modules.app_logger import log_transaction, log_unknown_notification
from modules.triggers import trigger_mail
from modules.file_handler import capture_face_img, capture_face_img_with_face_marked_positions

config = read_config()


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
    process_db_data()
    while True:
        transfer_data_to_database()
        threading.Thread(target=process_db_data()).start()
        user_ids, reference_encodings, names = get_cache()
        # threading.Thread(target=update_valid_till_for_expired).start()
        ret, frame = cap.read()
        frame_count += 1
        update_frame_counts(frame_count)
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
                face_match_index_list = recognize_faces(frame, face_locations, reference_encodings, face_detect_model)
                for (match_found, match_index), face in zip(face_match_index_list, face_locations):
                    top, right, bottom, left = face
                    if match_found and not detect_blurry_variance(face):
                        name = names[match_index]
                        user_id = user_ids[match_index]
                        logging.info(f"Face identified as: {name}")
                        is_eligible_for_announcement = is_user_eligible_for_announcement(user_id)
                        if is_eligible_for_announcement:
                            speech_thread = threading.Thread(target=play_speech, args=(name,))
                            mail_thread = threading.Thread(target=trigger_mail, args=(user_id, name, [capture_face_img_with_face_marked_positions(frame, name, top, right, bottom, left)]))
                            speech_thread.start()
                            mail_thread.start()
                            speech_thread.join()
                            mail_thread.join()
                        update_user_identification_cache(user_id)
                        log_thread = threading.Thread(target=log_transaction,
                                                      args=(frame_count, user_id, name, face_detect_model, is_eligible_for_announcement,))
                        log_thread.start()
                        continue
                    else:
                        saved_img = None
                        save_img = os.getenv('SAVE_UNKNOWN_FACE_IMAGE', face_config['capture-unknown-face'])
                        if save_img:
                            saved_img = capture_face_img(frame)
                        threading.Thread(target=log_unknown_notification, args=(frame_count, face_detect_model, True, save_img, saved_img,)).start()
            else:
                logging.info('No face detected')
                threading.Thread(target=log_unknown_notification, args=(frame_count, face_detect_model, False, False, None,)).start()
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
    cap.release()
