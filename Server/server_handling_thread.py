import threading

from CommHelper import send_socket_msg, recv_socket_msg
from Server.server_send_thread import SendingThread


class HandlingThread(threading.Thread):
    def __init__(self, host, port, client_socket, addr, server_instance):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.client_socket = client_socket
        self.addr = addr
        self.server_instance = server_instance

        self.channel_msg = []

    def run(self):
        self.handle_connection(self.client_socket, self.addr, self.server_instance)

    def distribute_model_weights(self, new_weights):
        for worker_ip in self.server_instance.worker_list:
            send_thread = SendingThread(worker_ip, self.port, self.server_instance,
                                        "update_weights", new_weights)
            send_thread.start()

        print("[Log] New model weights distributed to all successfully!")
        # print("=================================================\n")

    def handle_connection(self, client_socket, addr, server_instance):
        client_msg = recv_socket_msg(client_socket)
        self.channel_msg.append(client_msg)

        first_out = self.channel_msg.pop()
        if first_out:
            if first_out["type"] == "initialization":
                server_instance.worker_list.append(addr[0])
                server_instance.snapshot_list.append({"worker": addr[0],
                                                      "value:": [],
                                                      "channel_state": []})

                server_instance.channel_state_list.append({"worker": addr[0],
                                                           "channel_msg": []})
                # print(self.server_instance.worker_list)
                print("[Message] Received from ({}:{}) -> {}\n".format(addr[0], addr[1], first_out["content"]))

                # welcome_msg = util.construct_msg("welcome", "Welcome to the Server!")
                # client_socket.sendall(welcome_msg)

                send_socket_msg(client_socket, "welcome", "Welcome to the Server!")

            elif first_out['type'] == "update_weights":
                received_weights = first_out['content']
                print("[Log] Received new model weights from ({}:{})".format(addr[0], addr[1]))

                # If return weights != None, means already collected all model weights
                # Returned weights is the new weights, ready to distribute to all
                received_weights = self.server_instance.model_distributor.collect_model_weights(received_weights)

                if received_weights is not None:
                    self.distribute_model_weights(received_weights)

                send_socket_msg(client_socket, "weights_reply", "New Weights received!")

            # elif first_out["type"] == "init_snapshot" and server_instance.marker == 0:
            #     for i in range(len(server_instance.snapshot_list)):
            #         if server_instance.snapshot_list[i].get("worker") == addr[0]:
            #             server_instance.snapshot_list[i].update({"value": received_msg["content"]})
            #
            #     for i in range(len(server_instance.channel_state_list)):
            #         if server_instance.channel_state_list[i].get("worker") == addr[0]:
            #             server_instance.channel_state_list[i].update({"channel_msg": received_msg["content"]})
            #
            #     print("------Snapshot from ({}:{}) -> {}------\n".format(addr[0], addr[1], received_msg["content"]))
            #
            #     reply = util.construct_msg("snapshot_reply", "Snapshot Initialized")
            #     client_socket.sendall(reply)
            #
            #     forwarding_thread = SendingThread(self.host, self.port, server_instance, "marker")
            #     forwarding_thread.start()
            #     forwarding_thread.join()
            #
            #     server_instance.snapshot_counter += 1
            #     server_instance.marker = 1

        client_socket.close()
