import time
from watchdog.observers import Observer
from modules.event_data_handler import ImageHandler


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    path = "gui/uploads/"  # Use your actual path here
    event_handler = ImageHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
