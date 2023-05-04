import threading
import socket
import time

from CommHelper import send_socket_msg, recv_socket_msg
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

                if self.model.status != Status.COMPLETE:
                    self.send_model_weights()
            elif self.model.status == Status.WAITING_FOR_UPDATES:
                print("Client status: WAITING_FOR_UPDATES")
                time.sleep(3)
            elif self.model.status == Status.COMPLETE:
                print("\nClient status: **COMPLETE**")
                break

    def listen_command(self):
        """
        Keep listening to commands from server
        """
        print("Ready for new commands...")

        while True:
            # receive the message
            msg = recv_socket_msg(self.server_socket)
            if msg['type'] == 'command':
                print("\nCommand:", msg['content'])

                if msg['content'] == 'snapshot':
                    if self.marker_received == 0:
                        # self.marker_received = 1
                        print("Ready to take snapshot...")

                        # Check current values during training
                        # Return key values as snapshot response
                        epoch, weights, loss, accuracy = self.check_local_state()
                        snapshot_value = "Current epoch: {}, loss: {}, accuracy: {}".format(epoch, loss, accuracy)

                        send_socket_msg(self.server_socket, 'snapshot_value', snapshot_value)
                    else:
                        send_socket_msg(self.server_socket, 'Snapshot already taken')
                elif msg['content'] == 'finish':
                    self.model.finish_training()

            # Received merged new model weights from server
            # Continue next round training
            elif msg['type'] == 'updated_weights':
                self.model.receive_updated_weights(msg['content'])
            else:
                print(msg)

    def run(self):
        # Thread for ML training
        train_thread = threading.Thread(target=self.train)
        train_thread.start()

        # Thread for handling server commands
        server_thread = threading.Thread(target=self.listen_command)
        server_thread.start()

    def send_model_weights(self):
        model_weights = self.model.check_current_weights()
        send_socket_msg(self.server_socket, 'updated_weights', model_weights)

        print("Sent updated weights")

    def receive_model_weights(self, updated_weights):
        self.model.receive_updated_weights(updated_weights)


client = Client()
client.run()
