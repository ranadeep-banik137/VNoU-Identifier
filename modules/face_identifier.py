import threading
import cv2
import os
import time
import logging
import face_recognition as fr
import numpy as np
from modules.face_readers import detect_blurry_variance, detect_face_locations, get_face_distance_threshold
from modules.speech import play_speech
from modules.data_cache import process_db_data, get_cache, is_user_eligible_for_announcement, update_user_identification_cache, update_frame_counts, cache_frame_data
from modules.config_reader import read_config
from modules.app_logger import log_transaction, log_unknown_notification
from modules.triggers import trigger_mail
from modules.file_handler import save_img_to_local, capture_face_img_with_face_marked_positions

config = read_config()


class _LatestFrameGrabber:
    def __init__(self, cap):
        self._cap = cap
        self._lock = threading.Lock()
        self._frame = None
        self._ret = False
        self._stopped = threading.Event()
        self._thread = threading.Thread(target=self._loop, daemon=True, name="frame-grabber")

    def start(self):
        self._thread.start()
        return self

    def stop(self):
        self._stopped.set()
        try:
            self._thread.join(timeout=2.0)
        except Exception:
            pass

    def read_latest(self):
        with self._lock:
            if self._frame is None:
                return False, None
            return self._ret, self._frame.copy()

    def _loop(self):
        # Continuously read frames so decode/network I/O doesn't block recognition.
        # Keeping only the newest frame prevents latency buildup on streams.
        while not self._stopped.is_set():
            ret, frame = self._cap.read()
            with self._lock:
                self._ret = ret
                self._frame = frame if ret else None
            if not ret:
                # Avoid a tight loop if the stream stalls.
                time.sleep(0.02)


def _crop_roi(frame, top, right, bottom, left, pad=12):
    height, width = frame.shape[:2]
    top = max(0, top - pad)
    left = max(0, left - pad)
    bottom = min(height, bottom + pad)
    right = min(width, right + pad)
    if bottom <= top or right <= left:
        return None
    return frame[top:bottom, left:right]

def _scale_locations(face_locations, inv_scale):
    if inv_scale == 1.0:
        return face_locations
    scaled = []
    for (top, right, bottom, left) in face_locations:
        scaled.append(
            (
                int(round(top * inv_scale)),
                int(round(right * inv_scale)),
                int(round(bottom * inv_scale)),
                int(round(left * inv_scale)),
            )
        )
    return scaled


def _limit_faces_by_size(face_locations, max_faces):
    if not max_faces or max_faces <= 0 or len(face_locations) <= max_faces:
        return face_locations

    sized = []
    for loc in face_locations:
        top, right, bottom, left = loc
        area = max(0, bottom - top) * max(0, right - left)
        sized.append((area, loc))
    sized.sort(key=lambda x: x[0], reverse=True)
    return [loc for _, loc in sized[:max_faces]]


def _match_face_encodings(face_encodings, reference_encodings_np, threshold):
    results = []
    if reference_encodings_np is None or reference_encodings_np.size == 0:
        for _ in face_encodings:
            results.append((False, None, None))
        return results

    for encoding in face_encodings:
        distances = fr.face_distance(reference_encodings_np, encoding)
        best_index = int(np.argmin(distances))
        best_distance = float(distances[best_index])
        results.append((best_distance < threshold, best_index, best_distance))
    return results


def _start_db_cache_refresher(stop_event, interval_seconds=2.0):
    def _loop():
        while not stop_event.is_set():
            try:
                process_db_data()
            except Exception:
                logging.exception("process_db_data() failed in background refresh loop")
            stop_event.wait(interval_seconds)

    t = threading.Thread(target=_loop, daemon=True, name="db-cache-refresher")
    t.start()
    return t


def run_face_recognition():
    face_config = config['face_recognition']
    input_video_src = str(os.getenv('CAMERA_INDEX', face_config['camera-index']))
    save_img = os.getenv('SAVE_UNKNOWN_FACE_IMAGE', face_config['capture-unknown-face'])
    face_detect_model = os.getenv('FACE_RECOGNITION_MODEL', face_config['face-recognition-model'])
    frame_rate = int(os.getenv('FRAME_RATE_RANGE', face_config['frame-rate-range']))  # Adjust this value to balance performance and accuracy
    encoding_jitters = int(os.getenv('ENCODING_JITTERS', 0))
    max_faces_per_frame = int(os.getenv('MAX_FACES_PER_FRAME', 0))
    face_upsample_times = int(os.getenv('FACE_UPSAMPLE_TIMES', 0))
    downscale_default = 0.5 if str(face_detect_model).lower() == 'vnou' else 1.0
    frame_downscale = float(os.getenv('FRAME_DOWNSCALE', downscale_default))
    frame_downscale = 1.0 if frame_downscale <= 0 else frame_downscale
    check_blur_before_announce = str(os.getenv('CHECK_BLUR_BEFORE_ANNOUNCE', 'true')).lower() in ('1', 'true', 'yes')
    profile_every = int(os.getenv('PROFILE_EVERY_N_FRAMES', 0))
    capture_width = int(os.getenv('CAPTURE_WIDTH', 0))
    capture_height = int(os.getenv('CAPTURE_HEIGHT', 0))
    cap = cv2.VideoCapture(input_video_src if not input_video_src.isdigit() else int(input_video_src))
    try:
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    except Exception:
        pass
    if capture_width > 0:
        try:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, capture_width)
        except Exception:
            pass
    if capture_height > 0:
        try:
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, capture_height)
        except Exception:
            pass
    logging.info(
        f'CAMERA_INDEX is set as {"default Web Cam/Camera Source" if str(input_video_src).isdigit() and int(input_video_src) == 0 else "link " + str(input_video_src)}')
    logging.info(f'Frames will be processed every {frame_rate} frames')
    logging.info(f'FRAME_DOWNSCALE={frame_downscale}, FACE_UPSAMPLE_TIMES={face_upsample_times}, ENCODING_JITTERS={encoding_jitters}')
    frame_count = 0
    frame_fail_count = 0

    # Prime cache once on startup, then refresh in the background.
    process_db_data()
    stop_event = threading.Event()
    cache_refresh_interval = float(os.getenv('CACHE_REFRESH_INTERVAL_SECONDS', 2.0))
    _start_db_cache_refresher(stop_event, interval_seconds=cache_refresh_interval)
    grabber = _LatestFrameGrabber(cap).start()
    reference_encodings_np = None
    reference_encodings_len = -1
    threshold = get_face_distance_threshold()
    while True:
        log_unknown_notification(frame_number=frame_count, model=face_detect_model)
        ret, frame = grabber.read_latest()
        frame_count += 1
        update_frame_counts(frame_count)
        if frame_count % frame_rate != 0:
            logging.warning(f'Index frame {frame_count} skipped')
            cache_frame_data(frame_number=frame_count, is_detected=False, is_unknown_img_saved=False, img_path=None, reason='SKIP')
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue
        if ret:
            user_ids, reference_encodings, names = get_cache()
            if len(reference_encodings) != reference_encodings_len:
                reference_encodings_len = len(reference_encodings)
                reference_encodings_np = np.asarray(reference_encodings) if reference_encodings_len > 0 else None

            unknown_saved_this_frame = False
            saved_img_path = None

            start_t = time.perf_counter()
            proc_frame = frame
            inv_scale = 1.0
            if frame_downscale != 1.0:
                proc_frame = cv2.resize(frame, (0, 0), fx=frame_downscale, fy=frame_downscale, interpolation=cv2.INTER_LINEAR)
                inv_scale = 1.0 / frame_downscale

            if str(face_detect_model).lower() == 'vnou':
                proc_rgb = cv2.cvtColor(proc_frame, cv2.COLOR_BGR2RGB)
                face_locations_small = fr.face_locations(proc_rgb, number_of_times_to_upsample=face_upsample_times, model='hog')
            else:
                face_locations_small = detect_face_locations(proc_frame, face_detect_model)
                proc_rgb = cv2.cvtColor(proc_frame, cv2.COLOR_BGR2RGB) if face_locations_small else None
            face_locations_small = face_locations_small or []

            face_locations_small = _limit_faces_by_size(face_locations_small, max_faces_per_frame)
            face_locations = _scale_locations(face_locations_small, inv_scale)
            face_detected = len(face_locations) > 0
            if face_detected:
                face_encodings = fr.face_encodings(proc_rgb, known_face_locations=face_locations_small, num_jitters=encoding_jitters)
                match_results = _match_face_encodings(face_encodings, reference_encodings_np, threshold)
                usable = min(len(face_locations), len(match_results))
                any_recognized = False
                any_unidentified = False
                for i in range(usable):
                    match_found, match_index, _distance = match_results[i]
                    top, right, bottom, left = face_locations[i]
                    if match_found and match_index is not None:
                        any_recognized = True
                        name = names[match_index] if match_index < len(names) else 'Unknown'
                        user_id = user_ids[match_index] if match_index < len(user_ids) else None
                        logging.info(f"Face identified as: {name}")
                        if user_id is not None:
                            is_eligible_for_announcement = is_user_eligible_for_announcement(user_id)
                            face_quality_ok = True
                            if check_blur_before_announce:
                                roi = _crop_roi(frame, top, right, bottom, left)
                                face_quality_ok = (roi is not None) and (not detect_blurry_variance(roi))
                            if is_eligible_for_announcement and face_quality_ok:
                                speech_thread = threading.Thread(target=play_speech, args=(name,), daemon=True)
                                mail_img = capture_face_img_with_face_marked_positions(frame.copy(), name, top, right, bottom, left)
                                mail_thread = threading.Thread(target=trigger_mail, args=(user_id, name, [mail_img]), daemon=True)
                                speech_thread.start()
                                mail_thread.start()
                            update_user_identification_cache(user_id)
                            log_thread = threading.Thread(
                                target=log_transaction,
                                args=(frame_count, user_id, name, face_detect_model, is_eligible_for_announcement,),
                                daemon=True,
                            )
                            log_thread.start()
                    else:
                        any_unidentified = True
                        if not unknown_saved_this_frame:
                            unknown_saved_this_frame, saved_img_path = save_img_to_local(frame, save_img)

                if len(face_locations) > usable:
                    any_unidentified = True

                if any_recognized:
                    cache_frame_data(frame_number=frame_count, is_detected=True, is_unknown_img_saved=False, img_path=None)
                else:
                    cache_frame_data(
                        frame_number=frame_count,
                        is_detected=True,
                        is_unknown_img_saved=unknown_saved_this_frame,
                        img_path=saved_img_path,
                        reason='UNIDENTIFIED' if any_unidentified else 'NIL',
                    )
            else:
                logging.info('No face detected')
                cache_frame_data(frame_number=frame_count, is_detected=face_detected, is_unknown_img_saved=False, img_path=None, reason='NIL')
            if profile_every and frame_count % profile_every == 0:
                elapsed_ms = (time.perf_counter() - start_t) * 1000.0
                logging.info(f'Perf: frame={frame_count}, ms={elapsed_ms:.1f}, faces={len(face_locations)}')
        else:
            frame_fail_count += 1
            cache_frame_data(frame_number=frame_count, is_detected=False, is_unknown_img_saved=False, img_path=None, reason='INVALID')
            if frame_fail_count > int(os.getenv('FRAME_MAX_RESET_COUNT', face_config['frame-max-reset-seconds'])):
                time.sleep(0.5)  # Wait for 1 second
                logging.error(f'Frame loading timed out after {frame_fail_count} seconds')
                break
            logging.warning('Frame not loaded correctly. Loading next frame..')

    stop_event.set()
    grabber.stop()
    cap.release()
