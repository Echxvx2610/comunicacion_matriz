import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MyHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if event.src_path.endswith(".csv"):
                print(f"El archivo {event.src_path} ha sido modificado.")

def start_csv_observer(watched_folder):                      
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=watched_folder, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()    


