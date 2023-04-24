import threading
import socket


class ServerCommThread(threading.Thread):
    def __init__(self, client_socket):
        threading.Thread.__init__(self)
        self.client_socket = client_socket

    def run(self):
        while True:
            msg = 'Welcome to the server!' + "\r\n"
            self.client_socket.send(msg.encode('utf-8'))

            new_msg = self.client_socket.recv(1024)

            if msg:
                print(new_msg.decode('utf-8'))

        self.client_socket.close()