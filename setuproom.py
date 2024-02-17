import PySimpleGUI as sg
import csv
import os
import logger


#  Cargar datos desde el archivo CSV
csv_file = r"C:\Users\CECHEVARRIAMENDOZA\OneDrive - Brunswick Corporation\Documents\Proyectos_Python\PysimpleGUI\Proyectos\analisis_matriz\datos_matriz.csv"
logger = logger.setup_logger("analisis_matriz\setuproom.log")

class MissingDataError(Exception):
    pass

class InvalidDataError(Exception):
    pass



#........... ::::: Funciones para conexion entre app:::::::............




# ..............:::::: Funciones de manejo de archivos :::::::.............
def cargar_datos_desde_csv(csv_file):
    try:
        with open(csv_file, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Saltar encabezados
            return [row for row in reader]
    except FileNotFoundError:
        return []

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

def main():
    sg.theme("DarkGrey14")

    layout = [
        [sg.Table(values=cargar_datos_desde_csv(r"C:\Users\CECHEVARRIAMENDOZA\OneDrive - Brunswick Corporation\Documents\Proyectos_Python\PysimpleGUI\Proyectos\analisis_matriz\datos_matriz.csv"),
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
        [sg.Button("Editar", font=("monospace", 10, "bold"), size=(10, 1), key="-EDITAR-"),
         sg.Button("Refrescar", font=("monospace", 10, "bold"), size=(10, 1), key="-REFRESCAR-")]
    ]

    window = sg.Window("Matriz de charola L5 - SETUP", layout, size=(720, 400), element_justification="center", finalize=True, resizable=False)

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
                        if edit_event == "-GUARDAR-":
                            try:
                                new_data = [edit_values["-JOB-"], edit_values["-FAMILIA-"], edit_values["-SEC-"], edit_values["-ENSAMBLE-"], edit_values["-PARTE-"], edit_values["-EMPAQUETADO-"], edit_values["-MATRIZ-"]]
                                guardar_datos_editados_en_csv(selected_row, new_data)
                                sg.popup("Cambios guardados correctamente.")
                                edit_window.close()
                                window["-TABLE-"].update(values=cargar_datos_desde_csv(r"C:\Users\CECHEVARRIAMENDOZA\OneDrive - Brunswick Corporation\Documents\Proyectos_Python\PysimpleGUI\Proyectos\analisis_matriz\datos_matriz.csv"))  # Actualizar la tabla después de editar
                                break
                            except Exception as e:
                                sg.popup_error(f"Error al guardar cambios:\n{str(e)}")

        if event == "-REFRESCAR-":
            window["-TABLE-"].update(values=cargar_datos_desde_csv(r"C:\Users\CECHEVARRIAMENDOZA\OneDrive - Brunswick Corporation\Documents\Proyectos_Python\PysimpleGUI\Proyectos\analisis_matriz\datos_matriz.csv"))

    window.close()

if __name__ == "__main__":
    main()
