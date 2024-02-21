import logging
import os

def setup_logger(log_file):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Crear un formateador de registro (yyyy MM dd - HH:MM:SS - Level - Message)
    #formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
    
    # Crear un manejador para escribir los registros en un archivo
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Agregar el manejador al logger
    logger.addHandler(file_handler)

    # Cambiar los permisos del archivo de registro para que sea de solo lectura para otros usuarios
    os.chmod(log_file, 0o644)  # Esto permite escritura por el propietario y lectura por otros
    
    # solo escribir por el propietario
    #os.chmod(log_file, 0o666)

    return logger
