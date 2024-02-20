
#Variables
host = '172.27.182.132'
port = 8000
#Se importa el módulo
import socket
import os
 
#Creación de un objeto socket (lado cliente)
obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
#Conexión con el servidor. Parametros: IP (puede ser del tipo 192.168.1.1 o localhost), Puerto
obj.connect((host, port))
print("Conectado al servidor")
 
#Creamos un bucle para retener la conexion
while True:
    #Instanciamos una entrada de datos para que el cliente pueda enviar mensajes
    mens = input("Mensaje desde Cliente a Servidor >> ")
 
    #Con el método send, enviamos el mensaje
    obj.send(mens.encode())
    
    #recibimos los datos del servidor y visualizamos
    data = obj.recv(1024)
    print(data.decode())
    
#Cerramos la instancia del objeto servidor
obj.close()

#Imprimimos la palabra Adios para cuando se cierre la conexion
print("Conexión cerrada")