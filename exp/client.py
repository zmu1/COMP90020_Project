import threading
import socket
import time

import util


class Client:
    def __init__(self):
        # Initialise local value
        self.foo_var = 0
        self.marker_received = 0

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
            reply = self.server_socket.recv(1024)
            cmd = util.parse_msg(reply)

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

    def run(self):
        # Thread for ML training
        train_thread = threading.Thread(target=self.train)
        train_thread.start()

        # Thread for handling server commands
        server_thread = threading.Thread(target=self.listen_command)
        server_thread.start()


client = Client()
client.run()
