import time
import socket
import argparse

from Server.server_send_thread import SendingThread
from Server.server_recv_thread import ReceivingThread


class Server:
    def __init__(self, recv_port, send_port):
        self.host = socket.gethostbyname(socket.gethostname())
        self.recv_port = recv_port
        self.send_port = send_port

        self.marker = 0
        self.snapshot_counter = 0
        self.worker_list = []
        self.snapshot_list = []
        self.channel_state_list = []

        # Mock Incoming Channels
        self.recv_thread = ReceivingThread(self.host, self.recv_port, self)

    def initialize_snapshot(self):
        if self.marker != 0:
            return
        else:
            for worker_ip in self.worker_list:
                send_thread = SendingThread(worker_ip, self.send_port, self, "init_snapshot")
                send_thread.start()
                send_thread.join()

                if self.marker == 0:
                    self.marker = 1

    def start(self):
        self.recv_thread.start()

        # Server initialize snapshot algorithm
        time.sleep(15)
        self.initialize_snapshot()

        # self.send_thread.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Mock Worker Nodes in Federated learning")
    parser.add_argument("--recv", type=int, help="Port to Listening on")
    parser.add_argument("--send", type=int, help="Port for requesting connections")

    args = parser.parse_args()

    recv_port = args.recv  # 5999
    send_port = args.send  # 9999

    server = Server(recv_port, send_port)
    server.start()
