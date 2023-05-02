import threading
import socket
import time
import queue

import util


class Client:
    def __init__(self):
        # Initialise local value
        self.foo_var = 0
        self.marker_received = 0
        self.channel_queue = queue.Queue()

        # Create a socket object
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Get local host name and port number
        self.host = socket.gethostname()
        self.port = 5999

        # Connect to the server
        self.server_socket.connect((self.host, self.port))

    def train(self):
        """
        Simulate ML training process
        """
        while True:
            self.foo_var += 1
            if self.foo_var % 5 == 0:
                print("Training progress:", self.foo_var)

            if self.foo_var % 12 == 0:
                self.marker_received = 0

            time.sleep(1)

    def listen_command(self):
        """
        Keep listening to commands from server
        """
        print("Ready for new commands...")

        while True:
            # receive the message
            msg = self.server_socket.recv(1024)
            self.channel_queue.put(msg)

            print(list(self.channel_queue.queue))

    def handle_command(self):
        while True:
            if self.channel_queue:
                first_item = self.channel_queue.get()
                cmd = util.parse_msg(first_item)

                if cmd:
                    if cmd["type"] == "message":
                        print(cmd["content"])

                    elif cmd["type"] == "snapshot":
                        # First Marker
                        if self.marker_received == 0:
                            self.marker_received = 1

                            print("Ready to take snapshot... local value:", self.foo_var)
                            snapshot_value = str(self.foo_var)

                            reply = util.construct_msg("state", snapshot_value)
                            self.server_socket.send(reply)

                        # State already recorded
                        else:
                            reply = util.construct_msg("state_recorded", "own state has been recorded")
                            self.server_socket.send(reply)

            time.sleep(5)

    def run(self):
        # Thread for ML training
        train_thread = threading.Thread(target=self.train)
        train_thread.start()

        # Thread for receiving server commands
        server_thread = threading.Thread(target=self.listen_command)
        server_thread.start()

        # Thread for handling commands
        handling_thread = threading.Thread(target=self.handle_command)
        handling_thread.start()


client = Client()
client.run()
