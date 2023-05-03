import threading
import socket
import time

from CommHelper import send_socket_msg, recv_socket_msg
from TfDistributor import TfDistributor

CLIENT_NUM = 3


class Server:
    def __init__(self):
        # Attach a model distributor
        self.model_distributor = TfDistributor()
        self.model_distributor.set_total_clients(CLIENT_NUM)

        # Create a socket object
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Get local host name and port number
        self.host = socket.gethostname()
        self.port = 5999

        # Bind the port
        self.server_socket.bind((self.host, self.port))

        # Set the maximum number of connections, after which the queue is full
        self.server_socket.listen(5)

    def handle_connection(self, client_socket, addr):
        """
        Handle each incoming socket connection
        """
        print("Start handling connection...")

        # Welcome message
        send_socket_msg(client_socket, 'welcome', 'Welcome to the server!')

        # Keep sending commands to client
        while True:
            time.sleep(2)

            # Request to take snapshot
            print("Request to take snapshot...")
            command = "snapshot"
            send_socket_msg(client_socket, 'command', command)

            # Receive client response
            response = recv_socket_msg(client_socket)

            if response['type'] == "Snapshot already taken":
                print(response['type'])
            elif response['type'] == "updated_weights":
                received_weights = response['content']
                print("Received weights from client", addr)
                self.model_distributor.collect_model_weights(received_weights)
            elif response['type'] == "snapshot_value":
                print("Local value from {}: {}".format(addr, response['content']))
            else:
                print(response)

            time.sleep(5)

    def run(self):
        print("Ready to accept incoming connections...")

        while True:
            # Establish client connection
            client_socket, addr = self.server_socket.accept()
            print("Connected to: %s" % str(addr))

            # Thread-per-Connection
            client_thread = threading.Thread(target=self.handle_connection, args=(client_socket, addr))
            client_thread.start()


server = Server()
server.run()
