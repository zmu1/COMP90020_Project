import threading
import socket
import time


class Server:
    def __init__(self):
        # create a socket object
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # get local host name and port number
        self.host = socket.gethostname()
        self.port = 5999

        # bind the port
        self.server_socket.bind((self.host, self.port))

        # set the maximum number of connections, after which the queue is full
        self.server_socket.listen(5)

    def handle_connection(self, client_socket):
        print("Start handling connection...")

        msg = 'Welcome to the server!' + "\r\n"
        client_socket.send(msg.encode('utf-8'))

        while True:
            print("Request to take snapshot...")
            msg = "snapshot"
            client_socket.send(msg.encode('utf-8'))

            # receive the message
            response = client_socket.recv(1024)
            if response:
                print("Response:", response.decode('utf-8'))
            time.sleep(3)

    def run(self):
        while True:
            # establish client connection
            client_socket, addr = self.server_socket.accept()
            print("Connected to: %s" % str(addr))

            # Thread-per-Connection
            client_thread = threading.Thread(target=self.handle_connection, args=(client_socket,))
            client_thread.start()


server = Server()
server.run()