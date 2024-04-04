# setuproom.py
# autor: Cristian A. Echevarria Mendoza
import PySimpleGUI as sg
import csv
import os
from tools import logger, alerta
#monitoreo de archivos
import threading
import watchdog
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from queue import Queue
import time

#Nota : Falta corregir rutas para que archivos esten en el dico H como csv y log, lo demas se ira con la carpeta del proyecto!!!!!
 
#  Cargar datos desde el archivo CSV
csv_file = r"H:\Temporal\Analisis_matriz\datos_matriz.csv"
logger = logger.setup_logger("H:\Temporal\Analisis_matriz\mfg.log")


class MissingDataError(Exception):
    pass

class InvalidDataError(Exception):
    pass

#................ Funciones de conexión entre apps con watchdog ................
# Definir una cola para pasar mensajes entre hilos
output_queue = Queue()

# Variable global para almacenar el tiempo del ultimo evento
last_event_time = 0

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global last_event_time
        # Verificar si ha pasado suficiente tiempo desde el último evento
        current_time = time.time()
        if current_time - last_event_time < 2:  # Ignorar eventos dentro de un intervalo de 2 segundos
            return
        last_event_time = current_time
        
        if event.src_path.endswith(".csv"):
            # Verificar si el mensaje ya está en la cola
            message = f"Análisis de la matriz ha sido modificado!. Hora: {time.strftime('%H:%M:%S')}"
            if message not in output_queue.queue:
                output_queue.put(message)

def start_csv_observer(watched_folder):                      
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=watched_folder, recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info(f"Se ha interrumpido el monitoreo de archivos.{ time.strftime('%H:%M:%S') }")
        observer.stop()
    observer.join()        

def run_file_monitor():
    start_csv_observer(r"H:\Temporal\Analisis_matriz")



# Función para leer mensajes de la cola y actualizar el Multiline de PySimpleGUI
def update_output_window(window):
    while True:
        message = output_queue.get()  # Obtener mensaje de la cola
        window.write_event_value('-UPDATE_OUTPUT-', message)  # Emitir evento para actualizar el GUI

# ..............:::::: Funciones de manejo de archivos :::::::.............
def cargar_datos_desde_csv(csv_file):
    try:
        with open(csv_file, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Saltar encabezados
            return [row for row in reader]
    except FileNotFoundError:
        logger.error(f"El archivo '{csv_file}' no existe.")
        return []

def guardar_datos_editados_en_csv(selected_row, new_data):
    csv_file = r"H:\Temporal\Analisis_matriz\datos_matriz.csv"
    datos_actuales = cargar_datos_desde_csv(csv_file)

    if selected_row < len(datos_actuales):
        datos_actuales[selected_row] = new_data
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Job", "Familia", "Secuencia", "Ensamble", "No.Parte","Empaquetado", "Matriz"])
            writer.writerows(datos_actuales)
    else:
        logger.error(f"No se puede editar la fila {selected_row}. La fila seleccionada no existe.")
        raise ValueError(f"No se puede editar la fila {selected_row}. La fila seleccionada no existe.")

def main():
    sg.theme("DarkGrey14")

    layout = [
        [sg.Image(r'analisis_matriz\img\LOGO_NAVICO_white.png',expand_x=False,expand_y=False,enable_events=True,key='-LOGO-'),sg.Push()],
        [sg.Table(values=cargar_datos_desde_csv(r'H:\Temporal\Analisis_matriz\datos_matriz.csv'),
                  headings=["Job", "Familia", "Secuencia", "Ensamble","No.Parte", "Empaquetado", "Matriz"],
                  auto_size_columns=True,
                  row_colors=[('white', 'silver'), ('white', 'silver'), ('white', 'silver'), ('white', 'silver'), ('white', 'silver')],
                  justification='center',
                  display_row_numbers=False,
                  num_rows=20,
                  visible_column_map=[True, True, True, True, True, True, True],
                  selected_row_colors=('white', 'green'),
                  header_background_color='#2F4858',
                  key="-TABLE-")],
        [sg.Multiline(size=(118, 7), key="-LOG-",text_color="white",background_color="black",autoscroll=True,enable_events=True,disabled=True,no_scrollbar=False)],
        [sg.Button("Editar", font=("monospace", 10, "bold"), size=(10, 1), key="-EDITAR-"),
         sg.Button("Refrescar", font=("monospace", 10, "bold"), size=(10, 1), key="-REFRESCAR-")],
        [sg.Text("Created by: Cristian Echevarría",font=('Arial',8,'italic'))]
    ]

    window = sg.Window("Matriz de charola L5 - SETUP", layout,icon=r"analisis_matriz\img\data-analytics_2340033.ico", size=(700, 570), element_justification="center", finalize=True, resizable=False)

    # Iniciar el hilo para actualizar la salida en el GUI
    threading.Thread(target=update_output_window, args=(window,), daemon=True).start()

    # Iniciar el hilo para la función run_filemonitor
    threading.Thread(target=run_file_monitor, daemon=True).start()
    
    
    texto = open("H:\Temporal\Analisis_matriz\mfg.log", "r")
    window["-LOG-"].update(texto.read())
    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        if event == "-EDITAR-":
            selected_rows = values["-TABLE-"]
            if selected_rows:
                selected_row = selected_rows[0]
                if selected_row:
                    # Obtener los datos de la fila seleccionada
                    selected_data = cargar_datos_desde_csv(r'H:\Temporal\Analisis_matriz\datos_matriz.csv')[selected_row]
                    # Crear una nueva ventana para editar los datos
                    edit_layout = [
                        [sg.Image(r'analisis_matriz\img\LOGO_NAVICO_white.png',expand_x=False,expand_y=False,enable_events=True,key='-LOGO-'),sg.Push()],
                        [sg.Text("Job", font=("monospace", 12, "bold"), size=(11, 1)), sg.InputText(selected_data[0], size=(13, 1), key="-JOB-")],
                        [sg.Text("Familia", font=("monospace", 12, "bold"), size=(11, 1)), sg.InputText(selected_data[1], size=(13, 1), key="-FAMILIA-")],
                        [sg.Text("Secuencia", font=("monospace", 12, "bold"), size=(11, 1)), sg.Combo(["10", "20"], default_value=selected_data[2], size=(11, 1), key="-SEC-", readonly=True)],
                        [sg.Text("Ensamble", font=("monospace", 12, "bold"), size=(11, 1)), sg.InputText(selected_data[3], size=(13, 1), key="-ENSAMBLE-")],
                        [sg.Text("No.Parte",font=("monospace", 12, "bold"), size=(11, 1)), sg.InputText(selected_data[4], size=(13, 1), key="-PARTE-")],
                        [sg.Text("Empaquetado", font=("monospace", 12, "bold"), size=(11, 1)), sg.Combo(["Rollo", "Charola"], default_value=selected_data[5], size=(11, 1), key="-EMPAQUETADO-", readonly=True)],
                        [sg.Text("Matriz", font=("monospace", 12, "bold"), size=(11, 1)), sg.InputText(selected_data[6], size=(13, 1), key="-MATRIZ-")],
                        [sg.Button("Guardar Cambios", font=("monospace", 10, "bold"), key="-GUARDAR-")],
                        [sg.Text("Created by: Cristian Echevarría",font=('Arial',8,'italic'))]
                    ]
                    edit_window = sg.Window("Editar Datos", edit_layout, finalize=True)
                    while True:
                        edit_event, edit_values = edit_window.read()
                        if edit_event == sg.WIN_CLOSED:
                            break
                        if edit_event == "-GUARDAR-":
                            try:
                                new_data = [edit_values["-JOB-"], edit_values["-FAMILIA-"], edit_values["-SEC-"], edit_values["-ENSAMBLE-"], edit_values["-PARTE-"], edit_values["-EMPAQUETADO-"], edit_values["-MATRIZ-"]]
                                guardar_datos_editados_en_csv(selected_row, new_data)
                                sg.popup("Cambios guardados correctamente.")
                                edit_window.close()
                                window["-TABLE-"].update(values=cargar_datos_desde_csv(r"H:\Temporal\Analisis_matriz\datos_matriz.csv"))  # Actualizar la tabla después de editar
                                logger.info(f"- Datos editados por Setup Room:\n {new_data} \n")
                                break
                            except Exception as e:
                                logger.error(f"Error al guardar cambios:\n{str(e)}")
                                sg.popup_error(f"Error al guardar cambios:\n{str(e)}")

        if event == "-REFRESCAR-":
            window["-TABLE-"].update(values=cargar_datos_desde_csv(r"H:\Temporal\Analisis_matriz\datos_matriz.csv"))
        
        if event == "-UPDATE_OUTPUT-":
            # lanzar notificacion
            alerta.mostrar_notificacion_con_sonido(title='Analisis de la Matriz MFG', message=values[event], sound_file=r'analisis_matriz\sound\soft-notice-146623.wav')
            window["-TABLE-"].update(values=cargar_datos_desde_csv(r'H:\Temporal\Analisis_matriz\datos_matriz.csv'))
            new_text = open("H:\Temporal\Analisis_matriz\mfg.log", "r")
            window["-LOG-"].update(new_text.read())
            
            
    window.close()

if __name__ == "__main__":
    main()
