import socket
import threading
import time
import os

def receive(connection, mode):

    global stop_connection

    while True:

        try:

            msg = connection.recv(1024)

            if mode == 'server':
                print(f"\nClient {connection.getpeername()[0]} : ", msg.decode('utf-8'))
            else:
                print("\nServer : ", msg.decode('utf-8'))
                
        except:

            stop_connection = True   
            break

def sending(connection, mode):

    global stop_connection

    while True:

        if mode == 'server':
            msg = input("\nServer : ")
        else:
            msg = input("\nClient : ")
            
        if msg == '' or msg == 'exit' or msg == '\n':
            stop_connection = True
            break

        connection.send(msg.encode('utf-8'))

while True:

    try:
        host = input("Enter host: ")
        socket.gethostbyname(host)
        break
    except socket.gaierror:
        print("Invalid host, try again")

port = int(input("Enter port: "))

stop_connection = False

while True:

    mode = input("Enter mode (client or server): ")

    if mode == "client":

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        print("Client connection established with host " +
            host + " on port " + str(port))
        send_thread = threading.Thread(target=sending, args=(sock,mode,))
        receive_thread = threading.Thread(target=receive, args=(sock,mode,))
        send_thread.start()
        receive_thread.start()
        break

    elif mode == "server":

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen(1)
        print("Server is up and running on host " + host + " on port " + str(port))
        conn, addr = sock.accept()
        print("Connection accepted with client " + str(addr))
        send_thread = threading.Thread(target=sending, args=(conn,mode,))
        receive_thread = threading.Thread(target=receive, args=(conn,mode,))
        send_thread.start()
        receive_thread.start()
        break

    else:

        print("Invalid mode")
        continue

    

while True:

    if stop_connection:
        
        print("\nConnection closed")
        send_thread.join(1)
        receive_thread.join(1)
        os._exit(0)

    time.sleep(1)
