import threading
import socket
import time

from CommHelper import send_socket_msg, recv_socket_msg
from TfDistributor import TfDistributor

CLIENT_NUM = 2


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

        self.all_socket_connections = []

    def handle_connection(self, client_socket, addr):
        """
        Handle each incoming socket connection
        """
        print("Start handling connection...")
        self.all_socket_connections.append(client_socket)

        # Welcome message
        send_socket_msg(client_socket, 'welcome', 'Welcome to the server!')

        # Keep sending commands to client
        while True:
            # Receive client response
            response = recv_socket_msg(client_socket)

            if response['type'] == "Snapshot already taken":
                print(response['type'])
            elif response['type'] == "updated_weights":
                received_weights = response['content']
                print("Received weights from client", addr)

                # If return weights != None, means already collected all model weights
                # Returned weights is the new weights, ready to distribute to all
                received_weights = self.model_distributor.collect_model_weights(received_weights)
                if received_weights is not None:
                    self.distribute_model_weights(received_weights)
            elif response['type'] == "snapshot_value":
                print("Local value from {}: {}".format(addr, response['content']))
            else:
                print(response)

    def distribute_model_weights(self, new_weights):
        # Send merged new model weights to all connected clients
        for conn in self.all_socket_connections:
            send_socket_msg(conn, "updated_weights", new_weights)

    def handle_user_command(self):
        while True:
            user_input = input("> ")

            if user_input == 'snapshot':
                print("User command: snapshot")
                self.send_command(user_input)
            elif user_input == 'finish':
                print("User command: stop training")
                self.send_command(user_input)
            else:
                print("Unrecognised user command")

    def send_command(self, command, to_all=True):
        if to_all:
            for client_socket in self.all_socket_connections:
                send_socket_msg(client_socket, 'command', command)


    def run(self):
        print("Ready to accept incoming connections...")

        # Thread for listening user input commands
        user_command_thread = threading.Thread(target=self.handle_user_command, daemon=True)
        user_command_thread.start()

        while True:
            # Establish client connection
            client_socket, addr = self.server_socket.accept()
            print("Connected to: %s" % str(addr))

            # Thread-per-Connection
            client_thread = threading.Thread(target=self.handle_connection, args=(client_socket, addr))
            client_thread.start()


server = Server()
server.run()
