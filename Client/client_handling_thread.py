import threading

from CommHelper import send_socket_msg, recv_socket_msg


class HandlingThread(threading.Thread):
    def __init__(self, host, port, client_socket, addr, client_instance):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.client_socket = client_socket
        self.addr = addr
        self.client_instance = client_instance

    def run(self):
        self.handle_connection(self.client_socket, self.addr)

    def handle_connection(self, client_socket, addr):
        client_msg = recv_socket_msg(client_socket)
        self.client_instance.incoming_messages.append(client_msg)

        first_out = self.client_instance.incoming_messages.pop()
        if first_out:
            if first_out["type"] == "update_weights":
                print("[Log] Client received updated weights from ({}:{})".format(addr[0], addr[1]))
                self.client_instance.model.receive_updated_weights(first_out['content'])

                send_socket_msg(client_socket, "weights_reply", "New weights received")

            elif first_out["type"] == "marker":
                if self.client_instance.marker == 0:
                    self.client_instance.marker = 1
                    print("[Log] Client ready to take snapshot")

                    epoch, weights, loss, accuracy = self.client_instance.train_thread.check_local_state()
                    snapshot_value = "[Snapshot] Current epoch: {}, loss: {}, accuracy: {}".format(epoch, loss, accuracy)

                    send_socket_msg(client_socket, 'snapshot_value', snapshot_value)

                else:
                    print("[Log] Client has already taken snapshot")
                    send_socket_msg(client_socket, "snapshot_reply", 'Snapshot already taken')

            elif first_out["type"] == "finish":
                print("[Log] Received User Command -> Stop Training")
                self.client_instance.model.finish_training()

            # elif first_out["type"] == "marker":
            #     print("------Received from ({}:{}) -> {}------\n".format(addr[0], addr[1], received_msg["content"]))
            #
            #     if self.client_instance.marker == 0:
            #         # snapshot_msg = util.construct_msg("state_recorded", str(self.client_instance.foo_var))
            #         snapshot_msg = util.construct_msg("state_recorded", str(self.client_instance.foo_array))
            #         client_socket.send(snapshot_msg)
            #     else:
            #         self.client_instance.channel_state = self.client_instance.incoming_messages
            #
            #         reply = util.construct_msg("snapshot_already_taken", str(self.client_instance.incoming_messages))
            #         client_socket.send(reply)
            #
            # elif first_out["type"] == "terminate":
            #     print("------Received from ({}:{}) -> {}------\n".format(addr[0], addr[1], received_msg["content"]))
            #
            #     terminate_reply = util.construct_msg("terminate_reply", "Algorithm Terminated")
            #     client_socket.send(terminate_reply)
            #
            #     self.client_instance.initialization = 0
            #     self.client_instance.foo_var = 0
            #     self.client_instance.marker = 0
            #     self.client_instance.incoming_messages = []  # Msg in the channel
            #     self.client_instance.channel_state = []  # Record Channel State

        # client_socket.close()


