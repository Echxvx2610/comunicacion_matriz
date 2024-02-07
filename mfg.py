# mfg.py
import PySimpleGUI as sg
import csv
import os
import socket

# MFG (servidor de Socket)
HOST = "localhost"  # direccion IP del servidor
PORT = 65432       # puerto de escucha del servidor


class MissingDataError(Exception):
    pass

class InvalidDataError(Exception):
    pass

def enviar_notificacion(cambio):
    # Función para enviar una notificación sobre un cambio en el archivo CSV a todos los clientes conectados
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                print('Conexión establecida desde:', addr)
                conn.sendall(cambio.encode())



def validar_datos(datos):
    campos_obligatorios = ["-JOB-", "-FAMILIA-", "-SEC-", "-ENSAMBLE-", "-EMPAQUETADO-"]
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

    if datos["-EMPAQUETADO-"] == "Charola" and not datos["-MATRIZ-"]:
        raise MissingDataError("El campo 'Matriz' es obligatorio cuando se selecciona 'Charola' en Empaquetado.")

    return job, familia

def guardar_datos_en_csv(datos):
    csv_file = r"C:\Users\CECHEVARRIAMENDOZA\OneDrive - Brunswick Corporation\Documents\Proyectos_Python\PysimpleGUI\Proyectos\analisis_matriz\datos_matriz.csv"

    if not os.path.isfile(csv_file):
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Job", "Familia", "Secuencia", "Ensamble", "Empaquetado", "Matriz"])

    job, familia = validar_datos(datos)

    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([job, familia, datos["-SEC-"], datos["-ENSAMBLE-"], datos["-EMPAQUETADO-"], datos["-MATRIZ-"]])

def main():
    sg.theme("reddit")

    layout = [
        [sg.Text("Job", font=("monospace", 12, "bold"), size=(11, 1)), sg.InputText(size=(13, 1), key="-JOB-")],
        [sg.Text("Familia", font=("monospace", 12, "bold"), size=(11, 1)), sg.InputText(size=(13, 1), key="-FAMILIA-")],
        [sg.Text("Secuencia", font=("monospace", 12, "bold"), size=(11, 1)), sg.Combo(["10", "20"], size=(11, 1), key="-SEC-", readonly=True)],
        [sg.Text("Ensamble", font=("monospace", 12, "bold"), size=(11, 1)), sg.InputText(size=(13, 1), key="-ENSAMBLE-")],
        [sg.Text("Empaquetado", font=("monospace", 12, "bold"), size=(11, 1)), sg.Combo(["Rollo", "Charola"], size=(11, 1), key="-EMPAQUETADO-", readonly=True,enable_events=True)],
        [sg.Text("Matriz", font=("monospace", 12, "bold"), size=(11, 1)), sg.InputText(size=(13, 1), key="-MATRIZ-", default_text="N/A")],
        [sg.Button("Registrar", font=("monospace", 10, "bold"), key="-REGISTRAR-", size=(10, 1))]
    ]

    window = sg.Window("Matriz de charola L5 - MFG", layout, size=(400, 300), element_justification="center", finalize=True, resizable=False)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        if event == "-EMPAQUETADO-":
            if values["-EMPAQUETADO-"] == "Rollo":
                # Si se selecciona "Rollo", se actualiza el campo de matriz con "N/A" y se deshabilita
                window["-MATRIZ-"].update(value="N/A", disabled=True)
            else:
                # Si se selecciona "Charola", se habilita el campo de matriz y se deja vacío
                window["-MATRIZ-"].update(value="", disabled=False)

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
                    window["-EMPAQUETADO-"].update("")
                    window["-MATRIZ-"].update("N/A")
                except ValueError as e:
                    sg.popup_error(f"Error al guardar datos:\n {str(e)}")
                except MissingDataError as e:
                    sg.popup_error(f"Faltan datos obligatorios:\n {str(e)}")
                except InvalidDataError as e:
                    sg.popup_error(f"Error en los datos:\n {str(e)}")

    window.close()

if __name__ == "__main__":
    main()
