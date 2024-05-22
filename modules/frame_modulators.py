import numpy as np

frame_shape = None


def fetch_frame(frame_bytes):
    frame = np.frombuffer(frame_bytes, dtype=np.uint8).reshape(frame_shape)
    return frame


def cache_frame(frame):
    global frame_shape
    if frame is not None:
        frame_shape = frame.shape
    return frame.tobytes()
