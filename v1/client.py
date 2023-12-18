import socket
import threading


def listen(socket):
    while True:
        data = socket.recv(1024).decode()
        print('Received from server: ' + str(data))


if __name__ == "__main__":

    client_socket = socket.socket() 
    client_socket.connect((socket.gethostname(), 5500)) 

    listen_thread = threading.Thread(target=listen,args=(client_socket,))
    listen_thread.start()

    message = input(" -> ") 

    while message.lower().strip() != 'exit':
        client_socket.send(message.encode()) 

        message = input(" -> ")

    client_socket.close() 