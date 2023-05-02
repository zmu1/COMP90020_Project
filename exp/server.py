import threading
import socket
import time

import util


class Server:
    def __init__(self):
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
        msg_content = 'Welcome to the server!' + "\r\n"
        welcome_msg = util.construct_msg("message", msg_content)
        client_socket.send(welcome_msg)

        # Keep sending commands to client
        while True:
            # Request to take snapshot
            print("Request to take snapshot...")
            snapshot_msg = util.construct_msg("snapshot", "record your state now")
            client_socket.send(snapshot_msg)

            # Receive client response
            res = client_socket.recv(1024)
            response = util.parse_msg(res)

            if response["type"] == "state_recorded":
                print(response["content"])
            elif response["type"] == "state":
                print("Local value from {}: {}".format(addr, response["content"]))

            time.sleep(5)

    def run(self):
        while True:
            # Establish client connection
            client_socket, addr = self.server_socket.accept()
            print("Connected to: %s" % str(addr))

            # Thread-per-Connection
            client_thread = threading.Thread(target=self.handle_connection, args=(client_socket, addr))
            client_thread.start()


server = Server()
server.run()