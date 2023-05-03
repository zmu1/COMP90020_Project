import threading
import socket
import time
import pickle
import json
import struct

from TfModel import TfModel, Status


class Client:
    def __init__(self):
        # Initialise local value
        self.marker_received = 0
        self.dataset_path = "ml/credit_batch_1.csv"

        # Create a socket object
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Get local host name and port number
        self.host = socket.gethostname()
        self.port = 5999

        # Connect to the server
        self.server_socket.connect((self.host, self.port))

        # Initialise tensorflow model
        self.model = TfModel()

    def check_local_state(self):
        epoch = self.model.check_current_progress()
        weights = self.model.check_current_weights()
        loss, accuracy = self.model.check_current_performance()

        return epoch, weights, loss, accuracy

    def train(self):
        """
        Simulate ML training process
        """
        while True:
            if self.model.status == Status.IDLE:
                self.model.preprocess_data(self.dataset_path)
                self.model.train_model()
                self.send_model_weights()
            elif self.model.status == Status.WAITING_FOR_UPDATES:
                print("Client status: WAITING_FOR_UPDATES")
                time.sleep(3)

            # if self.foo_var % 12 == 0:
            #     self.marker_received = 0

            # time.sleep(1)

    def listen_command(self):
        """
        Keep listening to commands from server
        """
        print("Ready for new commands...")

        while True:
            # receive the message
            msg = self.recv_socket_msg(self.server_socket)
            if msg['type'] == 'command':
                print("Command:", msg['content'])

            if msg['type'] == 'command' and msg['content'] == 'snapshot':
                if self.marker_received == 0:
                    self.marker_received = 1
                    print("Ready to take snapshot...")

                    # Check current values during training
                    # Return key values as snapshot response
                    epoch, weights, loss, accuracy = self.check_local_state()
                    snapshot_value = "Current epoch: {}, loss: {}, accuracy: {}".format(epoch, loss, accuracy)

                    # socket_packet = pickle.dumps({'type': 'snapshot_value', 'content': snapshot_value})
                    # self.server_socket.send(socket_packet)
                    self.send_socket_msg(self.server_socket, 'snapshot_value', snapshot_value)
                else:
                    reply = "Snapshot already taken"
                    socket_packet = pickle.dumps({'type': reply})
                    # self.server_socket.send(socket_packet)
                    self.send_socket_msg(self.server_socket, 'Snapshot already taken')

            else:
                print(msg)

            # if msg.decode('utf-8') == 'snapshot':
            #     print("Ready to take snapshot... local value:", self.foo_var)
            #     snapshot_value = str(self.foo_var)
            #     self.server_socket.send(snapshot_value.encode('utf-8'))

    def run(self):
        # Thread for ML training
        train_thread = threading.Thread(target=self.train)
        train_thread.start()

        # Thread for handling server commands
        server_thread = threading.Thread(target=self.listen_command)
        server_thread.start()

    def send_model_weights(self):
        model_weights = self.model.check_current_weights()
        # self.server_socket.send("Updated weights".encode('utf-8'))
        # self.server_socket.send(pickle.dumps(model_weights))

        # socket_packet = pickle.dumps({'type': 'updated_weights', 'content': model_weights})
        # self.server_socket.send(socket_packet)
        self.send_socket_msg(self.server_socket, 'updated_weights', model_weights)

        print("Sent updated weights")

    def receive_model_weights(self, updated_weights):
        self.model.receive_updated_weights(updated_weights)

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


client = Client()
client.run()
