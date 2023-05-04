import socket
import threading
import time

import util


class ReceivingThread(threading.Thread):
    def __init__(self, host, port, server_instance):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.channel_msg = []
        self.server_instance = server_instance

    def handle_connection(self, client_socket, addr):
        client_msg = client_socket.recv(1024)
        received_msg = util.parse_msg(client_msg)

        self.channel_msg.append(received_msg)

        first_out = self.channel_msg.pop()
        if first_out:
            if first_out["type"] == "initialization":
                self.server_instance.worker_list.append(addr[0])
                self.server_instance.snapshot_list.append({"worker": addr[0],
                                                           "value:": [],
                                                           "channel_state": []})

                self.server_instance.channel_state_list.append({"worker": addr[0],
                                                                "channel_msg": []})
                # print(self.server_instance.worker_list)
                print("------Received from ({}:{}) -> {}------\n".format(addr[0], addr[1], received_msg["content"]))

                welcome_msg = util.construct_msg("welcome", "Welcome to the server!")
                client_socket.send(welcome_msg)

            elif first_out["type"] == "init_snapshot" and self.server_instance.marker == 0:
                for i in range(len(self.server_instance.snapshot_list)):
                    if self.server_instance.snapshot_list[i].get("worker") == addr[0]:
                        self.server_instance.snapshot_list[i].update({"value": received_msg["content"]})

                for i in range(len(self.server_instance.channel_state_list)):
                    if self.server_instance.channel_state_list[i].get("worker") == addr[0]:
                        self.server_instance.channel_state_list[i].update({"channel_msg": received_msg["content"]})

                print("------Snapshot from ({}:{}) -> {}------\n".format(addr[0], addr[1], received_msg["content"]))

                reply = util.construct_msg("snapshot_reply", "Snapshot Initialized")
                client_socket.send(reply)

                forwarding_thread = SendingThread(self.host, 9999, self.server_instance, "marker")
                forwarding_thread.start()
                forwarding_thread.join()

                self.server_instance.snapshot_counter += 1
                self.server_instance.marker = 1

        client_socket.close()

    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)

        print("------Listening on ({}:{})------\n".format(self.host, self.port))

        while True:
            client_socket, addr = server_socket.accept()
            print("------Accepted connection from ({}:{})------\n".format(addr[0], addr[1]))

            client_thread = threading.Thread(target=self.handle_connection, args=(client_socket, addr))
            client_thread.start()


class SendingThread(threading.Thread):
    def __init__(self, host, port, server_instance, cmd):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.server_instance = server_instance
        self.cmd = cmd

    def run(self):
        for client_ip in self.server_instance.worker_list:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((client_ip, 9999))

            if self.cmd == "marker":
                snapshot_msg = util.construct_msg(self.cmd, "Server Has Recorded Local State")
                client_socket.send(snapshot_msg)

            elif self.cmd == "init_snapshot" and self.server_instance.marker == 0:
                print("------From ({}:{}) -> Snapshot Initialized------\n".format(self.host, self.port))
                snapshot_msg = util.construct_msg(self.cmd, "Record Local State")
                client_socket.send(snapshot_msg)

            elif self.cmd == "terminate":
                terminate_msg = util.construct_msg(self.cmd, "Snapshot Finished")
                client_socket.send(terminate_msg)

                # Reset for next snapshot
                self.server_instance.marker = 0
                self.server_instance.snapshot_counter = 0
                self.server_instance.snapshot_list = []

            client_msg = client_socket.recv(1024)
            if client_msg:
                received_msg = util.parse_msg(client_msg)

                if received_msg:
                    if received_msg["type"] == "state_recorded":
                        for i in range(len(self.server_instance.snapshot_list)):
                            if self.server_instance.snapshot_list[i].get("worker") == client_ip:
                                self.server_instance.snapshot_list[i].update({"value": received_msg["content"]})

                        self.server_instance.snapshot_counter += 1
                        print("------Received from ({}:{}) -> {}------\n".format(self.host, self.port,
                                                                                 received_msg["content"]))
                    elif received_msg["type"] == "snapshot_already_taken":
                        for i in range(len(self.server_instance.snapshot_list)):
                            if self.server_instance.snapshot_list[i].get("worker") == client_ip:
                                self.server_instance.snapshot_list[i].update({"channel_state": received_msg["content"]})

                        self.server_instance.snapshot_counter += 1
                        print("------Received from ({}:{}) -> {}------\n".format(self.host, self.port,
                                                                                 received_msg["content"]))

                    elif received_msg["type"] == "terminate_reply":
                        print("------Received from ({}:{}) -> {}------\n".format(self.host, self.port,
                                                                                 received_msg["content"]))

            if self.server_instance.snapshot_counter == 1:
                terminate_thread = SendingThread(self.host, 9999, self.server_instance, "terminate")
                terminate_thread.start()
                terminate_thread.join()

            if client_socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR) != 0:
                client_socket.close()


class Server:
    def __init__(self):
        self.marker = 0
        self.snapshot_counter = 0
        self.worker_list = []
        self.snapshot_list = []
        self.channel_state_list = []

        # Mock Incoming Channels
        self.recv_thread = ReceivingThread("localhost", 5999, self)

    def initialize_snapshot(self):
        if self.marker != 0:
            return
        else:
            send_thread = SendingThread("localhost", 9999, self, "init_snapshot")
            send_thread.start()
            send_thread.join()

            self.marker = 1

    def start(self):
        self.recv_thread.start()

        # server initialize snapshot algorithm
        time.sleep(10)
        self.initialize_snapshot()

        # self.send_thread.start()


server = Server()
server.start()
