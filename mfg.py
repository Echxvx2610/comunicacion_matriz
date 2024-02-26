# mfg.py
# autor: Cristian A. Echevarria Mendoza
import PySimpleGUI as sg
import csv
import os
import time
from datetime import datetime
#monitoreo de archivos
import threading
import watchdog
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from queue import Queue

#importacion de modulo propio
from tools import logger, notificacion 

#Nota : Falta corregir rutas para que archivos esten en el dico H como csv y log, lo demas se ira con la carpeta del proyecto!!!!!!

# Declarar el logger
logger = logger.setup_logger("H:\Temporal\Analisis_matriz\mfg.log")

# .... ::: Funciones de manejo de excepciones ::::: .....
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


# ............ :::::: Funciones para el manejo de archivos :::::: .......
def validar_datos(datos):
    campos_obligatorios = ["-JOB-", "-FAMILIA-", "-SEC-", "-ENSAMBLE-","-PARTE-" ,"-EMPAQUETADO-"]
    for campo in campos_obligatorios:
        if not datos[campo]:
            raise MissingDataError(f"El campo '{campo[1:-1]}' es obligatorio y no puede estar vacío.")

    try:
        # Validar que 'Job' no este vacío
        if not datos["-JOB-"]:
            raise MissingDataError("El campo 'Job' es obligatorio y no puede estar vacío.")
    except ValueError:
        logger.error("El valor de 'Job' debe ser un número entero.")
        raise InvalidDataError("El valor de 'Job' debe ser un número entero.")


    familia = str(datos["-FAMILIA-"])

    if not datos["-ENSAMBLE-"].startswith("003"):
        logger.error("El valor de 'Ensamble' debe comenzar con '003'.")
        raise InvalidDataError("El valor de 'Ensamble' debe comenzar con '003'.")
    
    if not datos["-PARTE-"].startswith("014"):
        logger.error("El valor de 'No.Parte' debe comenzar con '014'.")
        raise InvalidDataError("El valor de 'No.Parte' debe comenzar con '014'.")
    
    if datos["-EMPAQUETADO-"] == "Charola" and not datos["-MATRIZ-"]:
        logger.error("El campo 'Matriz' es obligatorio cuando se selecciona 'Charola' en Empaquetado.")
        raise MissingDataError("El campo 'Matriz' es obligatorio cuando se selecciona 'Charola' en Empaquetado.")

    return datos["-JOB-"],familia, datos["-PARTE-"]

def cargar_datos_desde_csv(csv_file):
    try:
        with open(csv_file, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Saltar encabezados
            return [row for row in reader]
    except FileNotFoundError:
        logger.error(f"El archivo '{csv_file}' no existe.")
        return []

def guardar_datos_en_csv(datos):
    csv_file = r"H:\Temporal\Analisis_matriz\datos_matriz.csv"

    if not os.path.isfile(csv_file):
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Job", "Familia", "Secuencia", "Ensamble","No.Parte" ,"Empaquetado", "Matriz"])

    job, familia,parte = validar_datos(datos)

    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([job, familia, datos["-SEC-"], datos["-ENSAMBLE-"],datos["-PARTE-"],datos["-EMPAQUETADO-"], datos["-MATRIZ-"]])

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

# ..... ::::: Funcion main  ::::: .......
def main():
    sg.theme("DarkGrey14")
    layout = [
        [sg.Image(r'analisis_matriz\img\LOGO_NAVICO_white.png',expand_x=False,expand_y=False,enable_events=True,key='-LOGO-'),sg.Push()],
        [sg.Text("Job", font=("monospace", 12, "bold"), size=(11, 1)), sg.InputText(size=(13, 1), key="-JOB-"),sg.Text("Familia", font=("monospace", 12, "bold"), size=(11, 1)), sg.InputText(size=(13, 1), key="-FAMILIA-")],
        [sg.Text("Secuencia", font=("monospace", 12, "bold"), size=(11, 1)), sg.Combo(["10", "20"], size=(11, 1), key="-SEC-", readonly=True),sg.Text("Ensamble", font=("monospace", 12, "bold"), size=(11, 1)), sg.InputText(size=(13, 1), key="-ENSAMBLE-")],
        [sg.Text("No. Parte", font=("monospace", 12, "bold"), size=(11, 1)), sg.InputText(size=(13, 1), key="-PARTE-"),sg.Text("Empaquetado", font=("monospace", 12, "bold"), size=(11, 1)), sg.Combo(["Rollo", "Charola","N/A"], size=(11, 1), key="-EMPAQUETADO-", readonly=True,enable_events=True)],
        [sg.Text("Matriz", font=("monospace", 12, "bold"), size=(11, 1)), sg.InputText(size=(13, 1), key="-MATRIZ-", default_text="N/A")],
        [sg.Button("Registrar", font=("monospace", 10, "bold"), key="-REGISTRAR-", size=(10, 1)),sg.Button("Editar", font=("monospace", 10, "bold"), key="-EDITAR-", size=(10, 1)),(sg.Button("Eliminar", font=("monospace", 10, "bold"), key="-ELIMINAR-", size=(10, 1))),(sg.Button("Recargar", font=("monospace", 10, "bold"), key="-RECARGAR-", size=(10, 1)))],
        [sg.Table(values=cargar_datos_desde_csv(r"H:\Temporal\Analisis_matriz\datos_matriz.csv"),
                  headings=["Job", "Familia", "Secuencia", "Ensamble","No.Parte","Empaquetado", "Matriz"],
                  auto_size_columns=True,
                  row_colors=[('white', 'silver'), ('white', 'silver'), ('white', 'silver'), ('white', 'silver'), ('white', 'silver')],
                  justification='center',
                  display_row_numbers=False,
                  visible_column_map=[True, True, True, True, True, True, True],
                  header_background_color='#2F4858',
                  selected_row_colors=("white", "green"),
                  num_rows=20,
                  key="-TABLE-")],
        [sg.Multiline(size=(100, 4), key="-LOG-",text_color="white",background_color="black",autoscroll=True,enable_events=True,disabled=True,no_scrollbar=True)],
        [sg.Text("Created by: Cristian Echevarría",font=('Arial',8,'italic'))]
    ]

    window = sg.Window("Matriz de charola L5 - MFG", layout, size=(720, 635), element_justification="center", finalize=True, resizable=False)
    
    # Iniciar el hilo para actualizar la salida en el GUI
    threading.Thread(target=update_output_window, args=(window,), daemon=True).start()

    # Iniciar el hilo para la función run_filemonitor
    threading.Thread(target=run_file_monitor, daemon=True).start()

    texto = open("H:\Temporal\Analisis_matriz\mfg.log", "r")
    window["-LOG-"].update(texto.read())
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED: # si se cierra la ventana se cierra el programa
            break
        
        # Manejo de eventos 
        if event == "-EMPAQUETADO-":
            if values["-EMPAQUETADO-"] == "Rollo" or values["-EMPAQUETADO-"] == "N/A":
                # Si se selecciona "Rollo", se actualiza el campo de matriz con "N/A" y se deshabilita
                window["-MATRIZ-"].update(value="N/A",text_color="black", disabled=True)
            else:
                # Si se selecciona "Charola", se habilita el campo de matriz y se deja vacío
                window["-MATRIZ-"].update(value="", disabled=False)
        
        # Manejo de evento boton "Registrar"
        if event == "-REGISTRAR-":
            confirmacion = sg.popup_yes_no("¿Estás seguro de que deseas registrar estos datos?", title="Confirmación")
            if confirmacion == "Yes":
                try:
                    validar_datos(values)
                    guardar_datos_en_csv(values)
                    sg.popup("Datos guardados correctamente.")
                    #limpiar campos
                    window["-JOB-"].update("")
                    window["-FAMILIA-"].update("")
                    window["-SEC-"].update("")
                    window["-ENSAMBLE-"].update("")
                    window["-PARTE-"].update("")
                    window["-EMPAQUETADO-"].update("")
                    window["-MATRIZ-"].update("N/A")
                    #recargar tabla
                    window["-TABLE-"].update(values=cargar_datos_desde_csv(r"H:\Temporal\Analisis_matriz\datos_matriz.csv"))
                    #window["-LOG-"].print(f"- Datos registrados correctamente hora: \n. {list(values.values())[0:7]} \n")
                    window["-LOG-"].print(f"\n- Datos registrados correctamente modf: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: \n {list(values.values())[0:7]} \n")
                    logger.info(f"-Datos registrados correctamente:\n{list(values.values())[0:7]} \n")
                except ValueError as e:
                    logger.error(f"Error al guardar datos: {str(e)}")
                    sg.popup_error(f"Error al guardar datos:\n{str(e)}")
                except MissingDataError as e:
                    logger.error(f"Faltan datos obligatorios: {str(e)}")
                    sg.popup_error(f"Faltan datos obligatorios:\n{str(e)}")
                except InvalidDataError as e:
                    logger.error(f"Error en los datos: {str(e)}")
                    sg.popup_error(f"Error en los datos:\n{str(e)}")
        
        # Manejo de evento boton "Editar"
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
                        [sg.Button("Guardar Cambios", font=("monospace", 10, "bold"), key="-GUARDAR-")]
                    ]
                    edit_window = sg.Window("Editar Datos", edit_layout, finalize=True)
                    while True:
                        edit_event, edit_values = edit_window.read()
                        if edit_event == sg.WIN_CLOSED:
                            break
                        # Guardar los cambios al presionar el boton "Guardar"
                        if edit_event == "-GUARDAR-":
                            try:
                                new_data = [edit_values["-JOB-"], edit_values["-FAMILIA-"], edit_values["-SEC-"], edit_values["-ENSAMBLE-"], edit_values["-PARTE-"], edit_values["-EMPAQUETADO-"], edit_values["-MATRIZ-"]]
                                guardar_datos_editados_en_csv(selected_row, new_data)
                                sg.popup("Cambios guardados correctamente.")
                                edit_window.close()
                                window["-TABLE-"].update(values=cargar_datos_desde_csv(r'H:\Temporal\Analisis_matriz\datos_matriz.csv'))  # Actualizar la tabla después de editar
                                #window["-LOG-"].update(f"Datos guardados correctamente. {new_data} \n", append=True)
                                window["-LOG-"].print(f"\n- Datos editados correctamente modf: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: \n {new_data} \n")
                                logger.info(f"-Datos editados correctamente:\n{new_data} \n")
                                break
                            except Exception as e:
                                logger.error(f"Error al guardar cambios: {str(e)}")
                                sg.popup_error(f"Error al guardar cambios:\n{str(e)}")
        
        # eliminar registro de tabla
        if event == "-ELIMINAR-":
            selected_rows = values["-TABLE-"]
            if selected_rows:
                selected_row = selected_rows[0]
                if selected_row:
                    respuesta = sg.popup_yes_no("¿Desea eliminar el registro seleccionado?")
                    if respuesta == "Yes":
                        try:
                            # Obtener el índice de la fila seleccionada
                            selected_index = selected_row

                            # Cargar los datos actuales desde el archivo CSV
                            csv_file = r"H:\Temporal\Analisis_matriz\datos_matriz.csv"
                            datos_actuales = cargar_datos_desde_csv(csv_file)

                            # Verificar si el índice seleccionado está dentro de los límites
                            if selected_index < len(datos_actuales):
                                # Eliminar la fila correspondiente al índice seleccionado
                                del datos_actuales[selected_index]

                                # Sobrescribir el archivo CSV con los datos actualizados
                                with open(csv_file, mode='w', newline='') as file:
                                    writer = csv.writer(file)
                                    writer.writerow(["Job", "Familia", "Secuencia", "Ensamble", "No.Parte","Empaquetado", "Matriz"])
                                    writer.writerows(datos_actuales)
                                    
                                # Actualizar la tabla con los datos actualizados
                                window["-TABLE-"].update(values=datos_actuales)
                                sg.popup("Registro eliminado correctamente.")
                                
                                # Imprimir en el Multiline que se han eliminado los datos seleccionados
                                window["-LOG-"].print(f"\n - Datos eliminados modf: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} \n {datos_actuales[selected_index]} \n")
                                logger.info(f"-Datos eliminados correctamente:\n{datos_actuales[selected_index]} \n")
                            else:
                                logger.error("No se puede eliminar la fila seleccionada. La fila no existe. \n")
                                sg.popup_error("No se puede eliminar la fila seleccionada. La fila no existe.")
                        except Exception as e:
                            logger.error(f"Error al eliminar el registro: {str(e)} \n")
            else:
                sg.popup_error("No se ha seleccionado ninguna fila para eliminar.")
                
        if event == "-UPDATE_OUTPUT-":
            # lanzar notificacion
            notificacion.mostrar_notificacion_con_sonido(title='Analisis de la Matriz MFG', message=values[event], sound_file=r'analisis_matriz\sound\soft-notice-146623.wav')
            window["-TABLE-"].update(values=cargar_datos_desde_csv(r'H:\Temporal\Analisis_matriz\datos_matriz.csv'))
            # imprimir datos modificados
            print(values[event])
            #window["-LOG-"].print(f"\n - Datos modificados modf: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} \n {values[event]} \n")
            #logger.info(f"-Datos modificados correctamente:\n{values[event]} \n")
        elif event == "-RECARGAR-":
            window["-TABLE-"].update(values=cargar_datos_desde_csv(r'H:\Temporal\Analisis_matriz\datos_matriz.csv'))
            
    window.close()
    

if __name__ == "__main__":
    main()