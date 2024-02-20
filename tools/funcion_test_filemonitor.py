import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from queue import Queue
import PySimpleGUI as sg

# Definir una cola para pasar mensajes entre hilos
output_queue = Queue()

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".csv"):
            # Agregar el mensaje a la cola
            output_queue.put(f"Análisis de la matriz ha sido modificado!. Hora: {time.strftime('%H:%M:%S')}")

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

def run_filemonitor():
    start_csv_observer(r"C:\Users\CECHEVARRIAMENDOZA\OneDrive - Brunswick Corporation\Documents\Proyectos_Python\PysimpleGUI\Proyectos\analisis_matriz")



# Función para leer mensajes de la cola y actualizar el Multiline de PySimpleGUI
def update_output_window(window):
    while True:
        message = output_queue.get()  # Obtener mensaje de la cola
        window.write_event_value('-UPDATE_OUTPUT-', message)  # Emitir evento para actualizar el GUI

def main():
    # Función principal
    # for i in range(0, 100):
    #     print(i)
    #     time.sleep(1)
    # Definir el diseño de la interfaz PySimpleGUI
    layout = [
        [sg.Multiline(size=(60, 20), key='-OUTPUT-')],
    ]

    window = sg.Window('File Monitor', layout, finalize=True)

    # Iniciar el hilo para actualizar la salida en el GUI
    threading.Thread(target=update_output_window, args=(window,), daemon=True).start()

    # Iniciar el hilo para la función run_filemonitor
    threading.Thread(target=run_filemonitor, daemon=True).start()

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == '-UPDATE_OUTPUT-':
            window['-OUTPUT-'].print(values[event])

    window.close()

if __name__ == '__main__':
    main()