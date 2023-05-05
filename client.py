import socket
import argparse

from Client.client_send_thread import SendingThread
from Client.client_recv_thread import ReceivingThread
from Client.client_train_thread import TrainingThread
from TF.TfModel import TfModel


class Client:
    def __init__(self, server_host, recv_port, send_port):
        # Parameters for Sending/Receiving Threads
        self.client_host = socket.gethostbyname(socket.gethostname())
        self.server_host = server_host
        self.recv_port = recv_port
        self.send_port = send_port

        # Initialise local value
        self.dataset_path = "ml/credit_batch_1.csv"
        self.initialization = 0
        self.marker = 0
        self.incoming_messages = []  # Msg in the channel
        self.channel_state = []  # For recording channel state

        # Incoming Channel
        self.recv_thread = ReceivingThread(self.client_host, self.recv_port, self)
        self.recv_thread.start()

        # Outgoing Channel
        self.send_thread = SendingThread(self.server_host, self.send_port, self,
                                         "initialization", "Worker Node Initialization")
        self.send_thread.start()
        self.send_thread.join()

        # Initialise tensorflow model
        self.model = TfModel()

        # ML training
        self.train_thread = TrainingThread(self.server_host, self.send_port, self)

    def start(self):
        self.train_thread.start()

    # def listen_command(self):
    #     """
    #     Keep listening to commands from server
    #     """
    #     print("Ready for new commands...")
    #
    #     while True:
    #         # receive the message
    #         msg = recv_socket_msg(self.server_socket)
    #         if msg['type'] == 'command':
    #             print("\n[Command] {}".format(msg['content']))
    #
    #             if msg['content'] == 'snapshot':
    #                 if self.marker == 0:
    #                     # self.marker_received = 1
    #                     print("Ready to take snapshot...")
    #
    #                     # Check current values during training
    #                     # Return key values as snapshot response
    #                     epoch, weights, loss, accuracy = self.check_local_state()
    #                     snapshot_value = "Current epoch: {}, loss: {}, accuracy: {}".format(epoch, loss, accuracy)
    #
    #                     send_socket_msg(self.server_socket, 'snapshot_value', snapshot_value)
    #                 else:
    #                     send_socket_msg(self.server_socket, 'Snapshot already taken')
    #             elif msg['content'] == 'finish':
    #                 self.model.finish_training()
    #
    #         # Received merged new model weights from server
    #         # Continue next round training
    #         elif msg['type'] == 'updated_weights':
    #             self.model.receive_updated_weights(msg['content'])
    #         elif msg['type'] == 'connection':
    #             print("[Connection] {}".format(msg['content']))
    #         else:
    #             print(msg)

    # def receive_model_weights(self, updated_weights):
    #     self.model.receive_updated_weights(updated_weights)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Mock Worker Nodes in Federated learning")
    parser.add_argument("--server", type=str, help="IP Address of server nod")
    parser.add_argument("--recv", type=int, help="Port to Listening on")
    parser.add_argument("--send", type=int, help="Port for requesting connections")

    args = parser.parse_args()

    server_host = args.server
    recv_port = args.recv  # 9999
    send_port = args.send  # 5999

    client = Client(server_host, recv_port, send_port)
    client.start()
