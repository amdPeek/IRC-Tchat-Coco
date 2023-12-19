import socket
import threading
import sys

listening = True

def listen(socket):
    while True:
        data = socket.recv(1024).decode()
        if not data: 
            listening = False
            return
        print(str(data))

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("usage : client.py <nickname>")
    else:
        client_socket = socket.socket() 
        client_socket.connect((socket.gethostname(), 5500)) 

        listen_thread = threading.Thread(target=listen,args=(client_socket,))
        listen_thread.start()

        #setting up the params

        message = input("") 

        while message.lower().strip() != 'exit' and listening :
            client_socket.send(message.encode()) 
            message = input("")
            

        client_socket.close() 