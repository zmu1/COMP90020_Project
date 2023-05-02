import threading
import socket
import time

from TfModel import TfModel


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
            self.model.preprocess_data(self.dataset_path)
            self.model.train_model()

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
            msg = self.server_socket.recv(1024)
            if msg:
                print("Command:", msg.decode('utf-8'))

            if msg.decode('utf-8') == 'snapshot':
                if self.marker_received == 0:
                    self.marker_received = 1
                    print("Ready to take snapshot...")

                    # Check current values during training
                    # Return key values as snapshot response
                    epoch, weights, loss, accuracy = self.check_local_state()
                    snapshot_value = "Current epoch: {}, loss: {}, accuracy: {}".format(epoch, loss, accuracy)
                    self.server_socket.send(snapshot_value.encode('utf-8'))

                else:
                    reply = "Snapshot already taken"
                    self.server_socket.send(reply.encode('utf-8'))

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


client = Client()
client.run()
