import argparse
import socket

from Client.client_send_thread import SendingThread
from Client.client_recv_thread import ReceivingThread
from Client.client_train_thread import TrainingThread


class Client:
    def __init__(self, server_host, recv_port, send_port):
        self.client_host = socket.gethostbyname(socket.gethostname())
        self.server_host = server_host
        self.recv_port = recv_port
        self.send_port = send_port

        self.initialization = 0
        self.foo_var = 0

        self.foo_array = [1, 2, 3, 4, 5]

        self.marker = 0
        self.incoming_messages = []  # Msg in the channel
        self.channel_state = []  # For recording channel state

        # Incoming Channel
        self.recv_thread = ReceivingThread(self.client_host, self.recv_port, self)
        self.recv_thread.start()

        # Outgoing Channel
        self.send_thread = SendingThread(self.server_host, self.send_port, self, "initialization")
        self.send_thread.start()
        self.send_thread.join()

        # Mock training
        self.train_thread = TrainingThread(self)

    def initialize_snapshot(self):
        if self.marker != 0:
            return
        else:
            self.send_thread = SendingThread(self.server_host, self.send_port, self, "init_snapshot")
            self.send_thread.start()
            self.send_thread.join()

            self.marker = 1

    def start(self):
        self.train_thread.start()


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
