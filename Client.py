import threading
import socket
import argparse
import time

from CommHelper import send_socket_msg, recv_socket_msg
from TfModel import TfModel, Status
from ClientState import ClientState


class Client:
    def __init__(self, server_host, port):
        # Create a socket object
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Get local host name and port number
        self.host = server_host
        self.port = port
        self.ip = socket.gethostbyname(socket.gethostname())

        # Connect to the server
        self.server_socket.connect((self.host, self.port))

        # Initialise tensorflow model
        self.dataset_path = "ml/credit_batch_1.csv"
        self.model = TfModel()

        # Buffer message queue for each client
        self.buffer_message = []

        # Snapshot attributes
        self.local_state_recorded = False
        self.local_state = None
        self.channel_state = []

    def check_current_value(self):
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
                print("[Status]: WAITING_FOR_UPDATES")
                time.sleep(3)
            elif self.model.status == Status.COMPLETE:
                print("\n[Status]: **COMPLETE**")
                break

    def store_buffer_message(self, server_socket):
        print("Buffer thread running for", self.ip)

        # Keep listening to response from client
        while True:
            # Put incoming messages into buffer queue
            message = recv_socket_msg(server_socket)
            self.buffer_message.append(message)

            # Snapshot not started
            # Skip channel recording
            # if len(self.channel_recording_status.keys()) == 0:
            #     continue

            # If recording for the channel
            if not self.local_state_recorded:

                # Return marker received
                # End of channel recording
                if message['type'] == 'snapshot' and message['content'] == 'marker':
                    self.local_state_recorded = True
                    continue

                self.channel_state.append(message)
                #
                # if ip in self.channel_state.keys():
                #     self.channel_state[ip].append(message)
                # else:
                #     self.channel_state[ip] = [message]

            # print("New incoming message from", ip)
            # self.check_channel_state()

    def listen_command(self):
        """
        Keep listening to commands from server
        """
        print("Ready for new commands...")

        # Thread to buffer incoming messages
        buffer_thread = threading.Thread(target=self.store_buffer_message, args=(self.server_socket))
        buffer_thread.start()

        # Queue to buffer incoming messages
        message_queue = self.buffer_message

        while True:
            # receive the message
            # msg = recv_socket_msg(self.server_socket)

            # No new message, skip
            if len(message_queue) == 0:
                time.sleep(0.1)
                continue

            # Get the next message
            msg = message_queue.pop()

            # Handle chandy-lamport snapshot
            if msg['type'] == 'snapshot':
                print("\n[Snapshot] {}".format(msg['content']))

                # Received marker message
                if msg['content'] == 'marker':
                    print("Marker message received")

                    # Condition 1 - local state not recorded
                    if not self.local_state_recorded:
                        # Step 1 - record own local state
                        print("\n[Snapshot] Condition 1 - Ready to record local state")
                        self.record_local_state()
                        self.local_state_recorded = True

                        self.check_local_state()

                        # Step 2 - start recording incoming messages
                        # Skip

                        # Step 3 - send marker messages to all (back to server)
                        send_socket_msg(self.server_socket, 'snapshot', 'marker')

                    # Condition 2 - local state recorded
                    else:
                        print("\n[Snapshot] Condition 2 - Local state already recorded")
                        # Step 1 - stop recording incoming messages
                        # Skip

                # Received collect message
                # Snapshot collection
                elif msg['content'] == 'collect':
                    print("\n[Snapshot] Snapshot collection stage")
                    self.send_local_state()

                # Reset for next snapshot
                elif msg['content'] == 'reset':
                    print("\n[Snapshot] Reset for next snapshot")
                    self.snapshot_reset()

            # User command operations
            elif msg['type'] == 'command':
                print("\n[Command] {}".format(msg['content']))

                if msg['content'] == 'check':
                    # Check current values during training
                    # Return key values as snapshot response
                    epoch, weights, loss, accuracy = self.check_current_value()
                    snapshot_value = "Current epoch: {}, loss: {}, accuracy: {}".format(epoch, loss, accuracy)

                    send_socket_msg(self.server_socket, 'check_value', snapshot_value)
                elif msg['content'] == 'finish':
                    self.model.finish_training()

            # Received merged new model weights from server
            # Continue next round training
            elif msg['type'] == 'updated_weights':
                self.model.receive_updated_weights(msg['content'])
            elif msg['type'] == 'connection':
                print("[Connection] {}".format(msg['content']))
            else:
                print(msg)

    def start(self):
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

    def record_local_state(self):
        print("[Snapshot] Start recording local state")
        self.local_state = ClientState(self)
        self.local_state_recorded = True
        print("[Snapshot] Local state recorded successfully")

    def check_local_state(self):
        print("[Snapshot] Check local state")
        self.local_state.check_model()

    def send_local_state(self):
        send_socket_msg(self.server_socket, 'state', self.local_state)
        print("\n[Snapshot] Send back local state recorded")

    def snapshot_reset(self):
        # Reset snapshot attributes
        self.local_state_recorded = False
        self.local_state = None
        self.channel_state = []
        print("[Snapshot] Reset snapshot attributes")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Mock Worker Nodes in Federated learning")
    parser.add_argument("--server", type=str, help="IP address of server nod")
    parser.add_argument("--port", type=int, help="Port used for communication")

    args = parser.parse_args()

    server_host = args.server
    port = args.port

    client = Client(server_host, port)
    client.start()
