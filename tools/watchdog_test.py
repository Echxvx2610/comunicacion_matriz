import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MyHandler(FileSystemEventHandler):
    # def on_created(self, event):
    #     if event.is_directory:
    #         print(f"Directorio creado: {event.src_path}")
    #     else:
    #         print(f"Archivo creado: {event.src_path}")

    # def on_deleted(self, event):
    #     if event.is_directory:
    #         print(f"Directorio eliminado: {event.src_path}")
    #     else:
    #         print(f"Archivo eliminado: {event.src_path}")

    def on_modified(self, event):
        if event.is_directory:
            print(f"Directorio modificado: {event.src_path}")
        else:
            print(f"Archivo modificado: {event.src_path}")

    # def on_moved(self, event):
    #     if event.is_directory:
    #         print(f"Directorio movido de {event.src_path} a {event.dest_path}")
    #     else:
    #         print(f"Archivo movido de {event.src_path} a {event.dest_path}")

watched_folder = r"C:\Users\CECHEVARRIAMENDOZA\OneDrive - Brunswick Corporation\Documents\Proyectos_Python\PysimpleGUI\Proyectos\analisis_matriz"

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
