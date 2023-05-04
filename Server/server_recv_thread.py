import socket
import threading
import util
from Server.server_send_thread import SendingThread


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

                welcome_msg = util.construct_msg("welcome", "Welcome to the Server!")
                client_socket.sendall(welcome_msg)

            elif first_out["type"] == "init_snapshot" and self.server_instance.marker == 0:
                for i in range(len(self.server_instance.snapshot_list)):
                    if self.server_instance.snapshot_list[i].get("worker") == addr[0]:
                        self.server_instance.snapshot_list[i].update({"value": received_msg["content"]})

                for i in range(len(self.server_instance.channel_state_list)):
                    if self.server_instance.channel_state_list[i].get("worker") == addr[0]:
                        self.server_instance.channel_state_list[i].update({"channel_msg": received_msg["content"]})

                print("------Snapshot from ({}:{}) -> {}------\n".format(addr[0], addr[1], received_msg["content"]))

                reply = util.construct_msg("snapshot_reply", "Snapshot Initialized")
                client_socket.sendall(reply)

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