import socket
import threading
import time

import util


class SendingThread(threading.Thread):
    def __init__(self, host, port, server_instance, cmd):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.server_instance = server_instance
        self.cmd = cmd

    def run(self):
        # for client_ip in self.server_instance.worker_list:
        client_ip = self.host
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((client_ip, 9999))

        if self.cmd == "marker":
            snapshot_msg = util.construct_msg(self.cmd, "Server Has Recorded Local State")
            client_socket.sendall(snapshot_msg)

        elif self.cmd == "init_snapshot" and self.server_instance.marker == 0:
            print("------From ({}:{}) -> Snapshot Initialized------\n".format(self.host, self.port))
            snapshot_msg = util.construct_msg(self.cmd, "Record Local State")
            client_socket.sendall(snapshot_msg)

        elif self.cmd == "terminate":
            terminate_msg = util.construct_msg(self.cmd, "Snapshot Finished")
            client_socket.sendall(terminate_msg)

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

        print("\n\n\n", self.server_instance.snapshot_counter)
        if self.server_instance.snapshot_counter == 2:
            terminate_thread = SendingThread(self.host, 9999, self.server_instance, "terminate")
            terminate_thread.start()
            terminate_thread.join()

        if client_socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR) != 0:
            client_socket.close()