import socket 
import threading
import rsa
import os


public_key,private_key=rsa.newkeys(1024)
public_parnet = None


choice = input("do you want to host (1) or to connect (2): ")

if choice == '1':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost',2610)) #server.bind(('ip',port)) con fines de practica utilice el local host
    server.listen()
    
    client, _ = server.accept()
    client.send(public_key.save_pkcs1("PEM"))
    public_parnet = rsa.PublicKey.load_pkcs1(client.recv(1024))
elif choice == '2':
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost',2610)) #recordar que en ip va el ip publico de ambas partes del chat
    public_parnet = rsa.PublicKey.load_pkcs1(client.recv(1024))
    client.send(public_key.save_pkcs1("PEM"))
    
else:
    exit()
    
def sending_messages(c):
    while True:
        message = input("")
        c.send(rsa.encrypt(message.encode(),public_parnet))
        print('You: ' + message)

def receiving_messages(c):
    while True:
        print('Partnet: ' + rsa.decrypt(c.recv(1024),private_key).decode())
        

thred_sending = threading.Thread(target=sending_messages, args=(client,)).start()
thred_receiving = threading.Thread(target=receiving_messages, args=(client,)).start()

       