import threading
import socket

from Client.client_handling_thread import HandlingThread


class ReceivingThread(threading.Thread):
    def __init__(self, host, port, client_instance):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.client_instance = client_instance

    # def handle_connection(self, client_socket, addr):
    #     client_msg = client_socket.recv(1024)
    #     received_msg = util.parse_msg(client_msg)
    #
    #     self.client_instance.incoming_messages.append(received_msg)
    #
    #     first_out = self.client_instance.incoming_messages.pop()
    #     if first_out:
    #         if first_out["type"] == "welcome":
    #             print("------Received from ({}:{}) -> {}------\n".format(addr[0], addr[1], received_msg["content"]))
    #
    #         # elif first_out["type"] == "marker":
    #         #     print("------Received from ({}:{}) -> {}------\n".format(addr[0], addr[1], received_msg["content"]))
    #         #
    #         #     if self.client_instance.marker == 0:
    #         #         snapshot_msg = util.construct_msg("state_recorded", str(self.client_instance.foo_var))
    #         #         client_socket.send(snapshot_msg)
    #         #     else:
    #         #         self.client_instance.channel_state = self.client_instance.incoming_messages
    #         #
    #         #         reply = util.construct_msg("snapshot_already_taken", str(self.client_instance.incoming_messages))
    #         #         client_socket.send(reply)
    #
    #         elif first_out["type"] == "marker":
    #             print("------Received from ({}:{}) -> {}------\n".format(addr[0], addr[1], received_msg["content"]))
    #
    #             if self.client_instance.marker == 0:
    #                 # snapshot_msg = util.construct_msg("state_recorded", str(self.client_instance.foo_var))
    #                 snapshot_msg = util.construct_msg("state_recorded", str(self.client_instance.foo_array))
    #                 client_socket.send(snapshot_msg)
    #             else:
    #                 self.client_instance.channel_state = self.client_instance.incoming_messages
    #
    #                 reply = util.construct_msg("snapshot_already_taken", str(self.client_instance.incoming_messages))
    #                 client_socket.send(reply)
    #
    #         elif first_out["type"] == "terminate":
    #             print("------Received from ({}:{}) -> {}------\n".format(addr[0], addr[1], received_msg["content"]))
    #
    #             terminate_reply = util.construct_msg("terminate_reply", "Algorithm Terminated")
    #             client_socket.send(terminate_reply)
    #
    #             self.client_instance.initialization = 0
    #             self.client_instance.foo_var = 0
    #             self.client_instance.marker = 0
    #             self.client_instance.incoming_messages = []  # Msg in the channel
    #             self.client_instance.channel_state = []  # Record Channel State
    #
    #     # client_socket.close()

    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)

        print("[Log] Client Listening on ({}:{}))\n".format(self.host, self.port))

        while True:
            client_socket, addr = server_socket.accept()
            print("[Connection] Client accepted connection from ({}:{})\n".format(addr[0], addr[1]))

            client_thread = HandlingThread(self.host, self.port, client_socket, addr, self.client_instance)
            client_thread.start()
