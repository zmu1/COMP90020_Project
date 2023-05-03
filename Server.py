import threading
import socket
import time
import pickle
import json
import struct

from TfDistributor import TfDistributor


class Server:
    def __init__(self):
        # Attach a model distributor
        self.model_distributor = TfDistributor()

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
        # socket_packet = pickle.dumps({'type': 'welcome', 'content': 'Welcome to the server!' + "\r\n"})
        # client_socket.send(socket_packet)
        self.send_socket_msg(client_socket, 'welcome', 'Welcome to the server!')

        # Keep sending commands to client
        while True:
            time.sleep(2)

            # Request to take snapshot
            print("Request to take snapshot...")
            command = "snapshot"
            # socket_packet = pickle.dumps({'type': 'command', 'content': command})
            # client_socket.send(socket_packet)
            self.send_socket_msg(client_socket, 'command', command)

            # Receive client response
            response = self.recv_socket_msg(client_socket)

            if response['type'] == "Snapshot already taken":
                print(response['type'])
            elif response['type'] == "updated_weights":
                received_weights = response['content']
                self.model_distributor.collect_model_weights(received_weights)
                print("Received weights from client", addr)
                print(received_weights)
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

    def send_socket_msg(self, conn, type, content=None):
        msg = {'type': type, 'content': content}

        packet = pickle.dumps(msg)
        length_in_4_bytes = struct.pack('I', len(packet))
        packet = length_in_4_bytes + packet

        conn.send(packet)

    def recv_socket_msg(self, conn):
        length_in_4_bytes = conn.recv(4)
        size = struct.unpack('I', length_in_4_bytes)
        size = size[0]
        data = conn.recv(size)

        return pickle.loads(data)


server = Server()
server.run()
