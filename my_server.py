
#Se importa el módulo
import socket
import os

#instanciamos un objeto para trabajar con el socket
ser = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
#Puerto y servidor que debe escuchar
ser.bind(("172.27.182.132", 8000))
 
#Aceptamos conexiones entrantes con el metodo listen. Por parámetro las conexiones simutáneas.
ser.listen(1)
 
#Instanciamos un objeto cli (socket cliente) para recibir datos
cli, addr = ser.accept()

while True:

    #Recibimos el mensaje, con el metodo recv recibimos datos. Por parametro la cantidad de bytes para recibir
    recibido = cli.recv(1024).decode()
    #Si se reciben datos nos muestra la IP y el mensaje recibido
    print ("Recibo conexion de la IP: " + str(addr[0]) + " Puerto: " + str(addr[1]))
    #print("Mensaje recibido: " + recibido.decode('utf-8'))
    
    #Mostramos en el servidor el mensaje que hemos recibido
    mensaje_recib = "Mensaje recibido por el Cliente>> " + str(recibido)
    print(mensaje_recib,'\n')

    #Devolvemos el mensaje al cliente
    #opcion 1
    mensaje = 'Su mensaje ha sido recibido'
    cli.send(mensaje.encode())
    
    #opcion2
    #text = 'Mensaje recibido del cliente<<: ' + str(recibido)
    #cli.send(text.encode())
    
    
#Cerramos la instancia del socket cliente y servidor
cli.close()
ser.close()

print("Conexiones cerradas")