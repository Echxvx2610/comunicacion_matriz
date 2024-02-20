from file_monitor import CSVHandler
from watchdog.observers import Observer
import os

if __name__ == "__main__":
    # Ruta al archivo CSV que deseas monitorear
    csv_file = r"C:\Users\CECHEVARRIAMENDOZA\OneDrive - Brunswick Corporation\Documents\Proyectos_Python\PysimpleGUI\Proyectos\analisis_matriz\datos_matriz.csv"

    # Crear un observador y adjuntar el manejador de eventos
    observer = Observer()
    event_handler = CSVHandler(filename=os.path.basename(csv_file))
    observer.schedule(event_handler, path=os.path.dirname(csv_file), recursive=False)

    # Iniciar el observador
    observer.start()

    try:
        while True:
            pass  # Mantener el script en ejecución para que el observador funcione en segundo plano
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
