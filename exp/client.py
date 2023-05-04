import socket
import threading
import time

import util


class ReceivingThread(threading.Thread):
    def __init__(self, host, port, client_instance):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.client_instance = client_instance

    def handle_connection(self, client_socket, addr):
        client_msg = client_socket.recv(1024)
        received_msg = util.parse_msg(client_msg)

        self.client_instance.incoming_messages.append(received_msg)

        first_out = self.client_instance.incoming_messages.pop()
        if first_out:
            if first_out["type"] == "marker":
                print("------Received from ({}:{}) -> {}------\n".format(addr[0], addr[1], received_msg["content"]))

                if self.client_instance.marker == 0:
                    snapshot_msg = util.construct_msg("state_recorded", str(self.client_instance.foo_var))
                    client_socket.send(snapshot_msg)
                else:
                    self.client_instance.channel_state = self.client_instance.incoming_messages

                    reply = util.construct_msg("snapshot_already_taken", str(self.client_instance.incoming_messages))
                    client_socket.send(reply)

            elif first_out["type"] == "init_snapshot":
                print("------Received from ({}:{}) -> {}------\n".format(addr[0], addr[1], received_msg["content"]))

                if self.client_instance.marker == 0:
                    # snapshot_msg = util.construct_msg("state_recorded", str(self.client_instance.foo_var))
                    snapshot_msg = util.construct_msg("state_recorded", str(self.client_instance.foo_array))
                    client_socket.send(snapshot_msg)
                else:
                    self.client_instance.channel_state = self.client_instance.incoming_messages

                    reply = util.construct_msg("snapshot_already_taken", str(self.client_instance.incoming_messages))
                    client_socket.send(reply)

            elif first_out["type"] == "terminate":
                print("------Received from ({}:{}) -> {}------\n".format(addr[0], addr[1], received_msg["content"]))

                terminate_reply = util.construct_msg("terminate_reply", "Algorithm Terminated")
                client_socket.send(terminate_reply)

                self.client_instance.initialization = 0
                self.client_instance.foo_var = 0
                self.client_instance.marker = 0
                self.client_instance.incoming_messages = []  # Msg in the channel
                self.client_instance.channel_state = []  # Record Channel State

        client_socket.close()

    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)

        print("------Listening on ({}:{})------)".format(self.host, self.port))

        while True:
            client_socket, addr = server_socket.accept()
            print("------Accepted connection from ({}:{})------\n".format(addr[0], addr[1]))

            client_thread = threading.Thread(target=self.handle_connection, args=(client_socket, addr))
            client_thread.start()


class SendingThread(threading.Thread):
    def __init__(self, host, port, client_instance, cmd):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.client_instance = client_instance
        self.cmd = cmd

    def run(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host, self.port))

        print("\n------Connected to ({}:{})------\n".format(self.host, self.port))

        if self.cmd == "initialization" and self.client_instance.initialization == 0:
            init_msg = util.construct_msg(self.cmd, "Worker Node Initialization")
            client_socket.send(init_msg)
        elif self.cmd == "init_snapshot" and self.client_instance.marker == 0:
            snapshot_msg = util.construct_msg(self.cmd, str(self.client_instance.foo_var))
            client_socket.send(snapshot_msg)

        server_msg = client_socket.recv(1024)
        if server_msg:
            received_msg = util.parse_msg(server_msg)

            if received_msg:
                if received_msg["type"] == "welcome":
                    print("------Received from ({}:{}) -> {}------\n".format(self.host, self.port,
                                                                             received_msg["content"]))
                    self.client_instance.initialization = 1
                elif received_msg["type"] == "snapshot_reply":
                    print("------Received from ({}:{}) -> {}------\n".format(self.host, self.port,
                                                                             received_msg["content"]))

                    self.client_instance.incoming_messages = []  # Msg in the channel
                    self.client_instance.channel_state = []  # Record Channel State

        client_socket.close()


class TrainingThread(threading.Thread):
    def __init__(self, client_instance):
        threading.Thread.__init__(self)
        self.client_instance = client_instance

    def train(self):
        """
        Simulate ML training process
        """
        print("------Training Started------")

        while self.client_instance.foo_var < 5:
            self.client_instance.foo_var += 1
            print("------Training progress: {}------".format(self.client_instance.foo_var))

            time.sleep(1)

    def run(self):
        self.train()
        # self.client_instance.initialize_snapshot()


class Client:
    def __init__(self):
        self.initialization = 0
        self.foo_var = 0

        self.foo_array = [1, 2, 3, 4, 5]

        self.marker = 0
        self.incoming_messages = []  # Msg in the channel
        self.channel_state = []  # For recording channel state

        # Incoming Channel
        self.recv_thread = ReceivingThread("localhost", 9999, self)
        self.recv_thread.start()

        # Outgoing Channel
        self.send_thread = SendingThread("localhost", 5999, self, "initialization")
        self.send_thread.start()
        self.send_thread.join()

        # Mock training
        self.train_thread = TrainingThread(self)

    def initialize_snapshot(self):
        if self.marker != 0:
            return
        else:
            self.send_thread = SendingThread("localhost", 5999, self, "init_snapshot")
            self.send_thread.start()
            self.send_thread.join()

            self.marker = 1

    def start(self):
        self.train_thread.start()


client = Client()
client.start()
