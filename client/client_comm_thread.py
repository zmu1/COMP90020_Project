import threading
import socket
import time


class ClientCommThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.foo_var = 0

        # create a socket object
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # get local host name and port number
        self.host = socket.gethostname()
        self.port = 5999

        # connect to the server
        self.server_socket.connect((self.host, self.port))

    def run(self):
        while True:
            # receive the message
            msg = self.server_socket.recv(1024)
            if msg:
                print(msg.decode('utf-8'))

            new_msg = str(self.foo_var)
            self.server_socket.send(new_msg.encode('utf-8'))
            time.sleep(1)

        self.client_socket.close()