import PySimpleGUI as sg
import csv
import os

class MissingDataError(Exception):
    pass

class InvalidDataError(Exception):
    pass

def main():
    sg.theme("reddit")

    layout = [
        [sg.Image(r'analisis_matriz\img\LOGO_NAVICO_1_90-black.png',expand_x=False,expand_y=True,enable_events=True,key='-LOGO-'),sg.Push()],
        [sg.Text("Job", font=("monospace", 12, "bold"), size=(11, 1)), sg.InputText(size=(13, 1), key="-JOB-")],
        [sg.Text("Familia", font=("monospace", 12, "bold"), size=(11, 1)), sg.InputText(size=(13, 1), key="-FAMILIA-")],
        [sg.Text("Secuencia", font=("monospace", 12, "bold"), size=(11, 1)), sg.Combo(["10", "20"], size=(11, 1), key="-SEC-", readonly=True)],
        [sg.Text("Ensamble", font=("monospace", 12, "bold"), size=(11, 1)), sg.InputText(size=(13, 1), key="-ENSAMBLE-")],
        [sg.Text("Empaquetado", font=("monospace", 12, "bold"), size=(11, 1)), sg.Combo(["Rollo", "Charola"], size=(11, 1), key="-EMPAQUETADO-", readonly=True)],
        [sg.Text("Matriz", font=("monospace", 12, "bold"), size=(11, 1)), sg.InputText(size=(13, 1), key="-MATRIZ-")],
        [sg.Button("Registrar", font=("monospace", 10, "bold"), key="-REGISTRAR-", size=(10, 1)),
         sg.Button("Editar", font=("monospace", 10, "bold"), size=(10, 1),key="-EDITAR-"),
         sg.Button("Cargar", font=("monospace", 10, "bold"), size=(10, 1),key="-CARGAR-")],
        [sg.Text("", key="-SELECTED_ROW-", visible=False)],
        [sg.Table(values=[], headings=["Job", "Familia", "Secuencia", "Ensamble", "Empaquetado", "Matriz"],
                  auto_size_columns=False,
                  row_colors=[('white', 'silver'), ('white', 'silver'), ('white', 'silver'), ('white', 'silver'), ('white', 'silver')],
                  justification='center',
                  display_row_numbers=False,
                  num_rows=50,
                  key="-TABLE-")]
    ]

    window = sg.Window("Matriz de charola L5", layout, size=(700, 500), element_justification="center", finalize=True, resizable=False)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        if event == "-REGISTRAR-":
            try:
                validar_datos(values)
                guardar_datos_en_csv(values)
                sg.popup("Datos guardados correctamente.")
                window["-TABLE-"].update(values=cargar_datos_desde_csv("datos_matriz.csv"))  # Actualizar la tabla después de registrar
            except ValueError as e:
                sg.popup_error(f"Error al guardar datos:\n {str(e)}")
            except MissingDataError as e:
                sg.popup_error(f"Faltan datos obligatorios:\n {str(e)}")
            except InvalidDataError as e:
                sg.popup_error(f"Error en los datos:\n {str(e)}")

        if event == "-CARGAR-":
            window["-TABLE-"].update(values=cargar_datos_desde_csv("datos_matriz.csv"))

        if event == "-TABLE-":
            selected_rows = values["-TABLE-"]
            if selected_rows:
                selected_row = selected_rows[0]
                cargar_datos_seleccionados_en_ventana_principal(window, selected_row)

    window.close()

def validar_datos(datos):
    campos_obligatorios = ["-JOB-", "-FAMILIA-", "-SEC-", "-ENSAMBLE-", "-EMPAQUETADO-", "-MATRIZ-"]
    for campo in campos_obligatorios:
        if not datos[campo]:
            raise MissingDataError(f"El campo '{campo[1:-1]}' es obligatorio y no puede estar vacío.")

    try:
        job = int(datos["-JOB-"])
    except ValueError:
        raise InvalidDataError("El valor de 'Job' debe ser un número entero.")

    familia = str(datos["-FAMILIA-"])

    if not datos["-ENSAMBLE-"].startswith("003"):
        raise InvalidDataError("El valor de 'Ensamble' debe comenzar con '003'.")

    return job, familia

def guardar_datos_en_csv(datos):
    csv_file = "datos_matriz.csv"

    if not os.path.isfile(csv_file):
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Job", "Familia", "Secuencia", "Ensamble", "Empaquetado", "Matriz"])

    job, familia = validar_datos(datos)

    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([job, familia, datos["-SEC-"], datos["-ENSAMBLE-"], datos["-EMPAQUETADO-"], datos["-MATRIZ-"]])

def cargar_datos_desde_csv(csv_file):
    try:
        with open(csv_file, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Saltar encabezados
            return [row for row in reader]
    except FileNotFoundError:
        return []

def cargar_datos_seleccionados_en_ventana_principal(window, selected_row):
    csv_file = "datos_matriz.csv"
    datos = cargar_datos_desde_csv(csv_file)

    if selected_row < len(datos):
        window["-JOB-"].update(value=datos[selected_row][0])
        window["-FAMILIA-"].update(value=datos[selected_row][1])
        window["-SEC-"].update(value=datos[selected_row][2])
        window["-ENSAMBLE-"].update(value=datos[selected_row][3])
        window["-EMPAQUETADO-"].update(value=datos[selected_row][4])
        window["-MATRIZ-"].update(value=datos[selected_row][5])

if __name__ == "__main__":
    main()
