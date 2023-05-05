import threading
import socket

from CommHelper import send_socket_msg, recv_socket_msg


class SendingThread(threading.Thread):
    def __init__(self, host, port, client_instance, cmd, content):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.client_instance = client_instance
        self.cmd = cmd
        self.content = content

    def run(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host, self.port))

        print("[Connection] Client Connected to ({}:{})".format(self.host, self.port))

        if self.cmd == "initialization" and self.client_instance.initialization == 0:
            # init_msg = util.construct_msg(self.cmd, "Worker Node Initialization")
            # client_socket.sendall(init_msg)

            send_socket_msg(client_socket, self.cmd, self.content)

        elif self.cmd == "update_weights":
            print("[Log] Client sending new weights to ({}:{})".format(self.host, self.port))
            send_socket_msg(client_socket, self.cmd, self.content)

        # elif self.cmd == "init_snapshot" and self.client_instance.marker == 0:
        #     snapshot_msg = util.construct_msg(self.cmd, str(self.client_instance.foo_var))
        #     client_socket.sendall(snapshot_msg)

        # server_msg = client_socket.recv(1024)
        # if server_msg:
        #     received_msg = util.parse_msg(server_msg)

        server_msg = recv_socket_msg(client_socket)
        if server_msg:
            if server_msg["type"] == "welcome":
                print("[Message] Received from ({}:{}) -> {}\n".format(self.host, self.port,
                                                                       server_msg["content"]))
                self.client_instance.initialization = 1

            elif server_msg["type"] == "weights_reply":
                print("[Message] Received from ({}:{}) -> {}\n".format(self.host, self.port,
                                                                       server_msg["content"]))

            elif server_msg["type"] == "snapshot_reply":
                print("------Received from ({}:{}) -> {}------\n".format(self.host, self.port,
                                                                         server_msg["content"]))

                self.client_instance.incoming_messages = []  # Msg in the channel
                self.client_instance.channel_state = []  # Record Channel State

        client_socket.close()
