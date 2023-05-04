import threading
import socket
import util


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
            client_socket.sendall(init_msg)
        elif self.cmd == "init_snapshot" and self.client_instance.marker == 0:
            snapshot_msg = util.construct_msg(self.cmd, str(self.client_instance.foo_var))
            client_socket.sendall(snapshot_msg)

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