import socket
import argparse

from Server.server_recv_thread import ReceivingThread
from Server.server_cmd_thread import CommandThread
from TF.TfDistributor import TfDistributor

CLIENT_NUM = 2


class Server:
    def __init__(self, recv_port, send_port):
        # Parameters for Sending/Receiving Threads
        self.host = socket.gethostbyname(socket.gethostname())
        self.recv_port = recv_port
        self.send_port = send_port

        # Initialise local value
        self.marker = 0
        self.snapshot_counter = 0
        self.worker_list = []
        self.snapshot_list = []
        self.channel_state_list = []

        # Attach a model distributor
        self.model_distributor = TfDistributor()
        self.model_distributor.set_total_clients(CLIENT_NUM)

        # Mock Incoming Channels
        self.recv_thread = ReceivingThread(self.host, self.recv_port, self)

    def start(self):
        # Thread for listening user input commands
        user_command_thread = CommandThread(self.send_port, self)
        user_command_thread.start()

        self.recv_thread.start()

    # def handle_connection(self, client_socket, addr):
    #     """
    #     Handle each incoming socket connection
    #     """
    #     print("[Connection] Start handling connection...")
    #     self.all_socket_connections.append(client_socket)
    #
    #     # Welcome message
    #     send_socket_msg(client_socket, 'connection', 'Welcome to the server!')
    #
    #     # Keep sending commands to client
    #     while True:
    #         # Receive client response
    #         response = recv_socket_msg(client_socket)
    #
    #         if response['type'] == "Snapshot already taken":
    #             print("[Client - {}] {}".format(addr[0], response['type']))
    #         elif response['type'] == "updated_weights":
    #             received_weights = response['content']
    #             print("[Client - {}] Received pushed new model weights".format(addr[0]))
    #
    #             # If return weights != None, means already collected all model weights
    #             # Returned weights is the new weights, ready to distribute to all
    #             received_weights = self.model_distributor.collect_model_weights(received_weights)
    #             if received_weights is not None:
    #                 self.distribute_model_weights(received_weights)
    #         elif response['type'] == "snapshot_value":
    #             print("[Client - {}] Local values: {}".format(addr[0], response['content']))
    #         else:
    #             print("[Client - {}] Unspecified message: {}".format(addr[0], response))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Mock Worker Nodes in Federated learning")
    parser.add_argument("--recv", type=int, help="Port to Listening on")
    parser.add_argument("--send", type=int, help="Port for requesting connections")

    args = parser.parse_args()

    recv_port = args.recv  # 5999
    send_port = args.send  # 9999

    server = Server(recv_port, send_port)
    server.start()
