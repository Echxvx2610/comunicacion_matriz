# mfg.py
import PySimpleGUI as sg
import csv
import os
import socket
from tools import logger
import threading
import watchdog
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer



# Declarar el logger
logger = logger.setup_logger("analisis_matriz\mfg.log")

class MissingDataError(Exception):
    pass

class InvalidDataError(Exception):
    pass

#................ Funciones de conexión entre apps con watchdog ................

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
        raise InvalidDataError("El valor de 'Job' debe ser un número entero.")

    familia = str(datos["-FAMILIA-"])

    if not datos["-ENSAMBLE-"].startswith("003"):
        raise InvalidDataError("El valor de 'Ensamble' debe comenzar con '003'.")
    
    if not datos["-PARTE-"].startswith("014"):
        raise InvalidDataError("El valor de 'No.Parte' debe comenzar con '014'.")
    
    if datos["-EMPAQUETADO-"] == "Charola" and not datos["-MATRIZ-"]:
        raise MissingDataError("El campo 'Matriz' es obligatorio cuando se selecciona 'Charola' en Empaquetado.")

    return datos["-JOB-"],familia, datos["-PARTE-"]

def cargar_datos_desde_csv(csv_file):
    try:
        with open(csv_file, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Saltar encabezados
            return [row for row in reader]
    except FileNotFoundError:
        return []

def guardar_datos_en_csv(datos):
    csv_file = r"C:\Users\CECHEVARRIAMENDOZA\OneDrive - Brunswick Corporation\Documents\Proyectos_Python\PysimpleGUI\Proyectos\analisis_matriz\datos_matriz.csv"

    if not os.path.isfile(csv_file):
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Job", "Familia", "Secuencia", "Ensamble","No.Parte" ,"Empaquetado", "Matriz"])

    job, familia,parte = validar_datos(datos)

    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([job, familia, datos["-SEC-"], datos["-ENSAMBLE-"],datos["-PARTE-"],datos["-EMPAQUETADO-"], datos["-MATRIZ-"]])

def guardar_datos_editados_en_csv(selected_row, new_data):
    csv_file = r"C:\Users\CECHEVARRIAMENDOZA\OneDrive - Brunswick Corporation\Documents\Proyectos_Python\PysimpleGUI\Proyectos\analisis_matriz\datos_matriz.csv"
    datos_actuales = cargar_datos_desde_csv(csv_file)

    if selected_row < len(datos_actuales):
        datos_actuales[selected_row] = new_data
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Job", "Familia", "Secuencia", "Ensamble", "No.Parte","Empaquetado", "Matriz"])
            writer.writerows(datos_actuales)
    else:
        raise ValueError(f"No se puede editar la fila {selected_row}. La fila seleccionada no existe.")

# ..... ::::: Funcion main  ::::: .......
def main():
    sg.theme("DarkGrey14")
    layout = [
        [sg.Text("Job", font=("monospace", 12, "bold"), size=(11, 1)), sg.InputText(size=(13, 1), key="-JOB-"),sg.Text("Familia", font=("monospace", 12, "bold"), size=(11, 1)), sg.InputText(size=(13, 1), key="-FAMILIA-")],
        [sg.Text("Secuencia", font=("monospace", 12, "bold"), size=(11, 1)), sg.Combo(["10", "20"], size=(11, 1), key="-SEC-", readonly=True),sg.Text("Ensamble", font=("monospace", 12, "bold"), size=(11, 1)), sg.InputText(size=(13, 1), key="-ENSAMBLE-")],
        [sg.Text("No. Parte", font=("monospace", 12, "bold"), size=(11, 1)), sg.InputText(size=(13, 1), key="-PARTE-"),sg.Text("Empaquetado", font=("monospace", 12, "bold"), size=(11, 1)), sg.Combo(["Rollo", "Charola","N/A"], size=(11, 1), key="-EMPAQUETADO-", readonly=True,enable_events=True)],
        [sg.Text("Matriz", font=("monospace", 12, "bold"), size=(11, 1)), sg.InputText(size=(13, 1), key="-MATRIZ-", default_text="N/A")],
        [sg.Button("Registrar", font=("monospace", 10, "bold"), key="-REGISTRAR-", size=(10, 1)),sg.Button("Editar", font=("monospace", 10, "bold"), key="-EDITAR-", size=(10, 1)),sg.Button("Recargar", font=("monospace", 10, "bold"), key="-RECARGAR-", size=(10, 1))],
        [sg.Table(values=cargar_datos_desde_csv(r"C:\Users\CECHEVARRIAMENDOZA\OneDrive - Brunswick Corporation\Documents\Proyectos_Python\PysimpleGUI\Proyectos\analisis_matriz\datos_matriz.csv"),
                  headings=["Job", "Familia", "Secuencia", "Ensamble","No.Parte","Empaquetado", "Matriz"],
                  auto_size_columns=True,
                  row_colors=[('white', 'silver'), ('white', 'silver'), ('white', 'silver'), ('white', 'silver'), ('white', 'silver')],
                  justification='center',
                  display_row_numbers=False,
                  visible_column_map=[True, True, True, True, True, True, True],
                  header_background_color='#2F4858',
                  selected_row_colors=("white", "green"),
                  num_rows=20,
                  key="-TABLE-"),],
        [sg.Multiline(size=(100, 10), key="-LOG-", autoscroll=True,enable_events=True,disabled=True)]
    ]

    window = sg.Window("Matriz de charola L5 - MFG", layout, size=(720, 600), element_justification="center", finalize=True, resizable=False)
    try:
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
                        window["-TABLE-"].update(values=cargar_datos_desde_csv(r"C:\Users\CECHEVARRIAMENDOZA\OneDrive - Brunswick Corporation\Documents\Proyectos_Python\PysimpleGUI\Proyectos\analisis_matriz\datos_matriz.csv"))
                        window["-LOG-"].update(f"Datos guardados correctamente: {values} \n", append=True)
                    except ValueError as e:
                        sg.popup_error(f"Error al guardar datos:\n {str(e)}")
                    except MissingDataError as e:
                        sg.popup_error(f"Faltan datos obligatorios:\n {str(e)}")
                    except InvalidDataError as e:
                        sg.popup_error(f"Error en los datos:\n {str(e)}")
            # Manejo de evento boton "Editar"
            if event == "-EDITAR-":
                selected_rows = values["-TABLE-"]
                if selected_rows:
                    selected_row = selected_rows[0]
                    if selected_row:
                        # Obtener los datos de la fila seleccionada
                        selected_data = cargar_datos_desde_csv(r"C:\Users\CECHEVARRIAMENDOZA\OneDrive - Brunswick Corporation\Documents\Proyectos_Python\PysimpleGUI\Proyectos\analisis_matriz\datos_matriz.csv")[selected_row]
                        # Crear una nueva ventana para editar los datos
                        edit_layout = [
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
                                    window["-TABLE-"].update(values=cargar_datos_desde_csv(r"C:\Users\CECHEVARRIAMENDOZA\OneDrive - Brunswick Corporation\Documents\Proyectos_Python\PysimpleGUI\Proyectos\analisis_matriz\datos_matriz.csv"))  # Actualizar la tabla después de editar
                                    window["-LOG-"].update(f"Datos guardados correctamente. {new_data} \n", append=True)
                                    break
                                except Exception as e:
                                    sg.popup_error(f"Error al guardar cambios:\n{str(e)}")
                
            if event == "-RECARGAR-":
                #recargar tabla
                window["-TABLE-"].update(values=cargar_datos_desde_csv(r"C:\Users\CECHEVARRIAMENDOZA\OneDrive - Brunswick Corporation\Documents\Proyectos_Python\PysimpleGUI\Proyectos\analisis_matriz\datos_matriz.csv"))
    finally:
        window.close()
    

if __name__ == "__main__":
    main()