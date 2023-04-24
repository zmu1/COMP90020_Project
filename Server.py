import socket
from server import server_comm_thread


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

    def run(self):
        while True:
            # establish client connection
            client_socket, addr = self.server_socket.accept()
            print("Connected to: %s" % str(addr))

            # Thread-per-Connection
            comm_thread = server_comm_thread.ServerCommThread(client_socket)
            comm_thread.run()


server = Server()
server.run()
