import threading
import socket
import argparse
import time

from CommHelper import send_socket_msg, recv_socket_msg
from ServerState import ServerState
from TfDistributor import TfDistributor

CLIENT_NUM = 2


class Server:
    def __init__(self, port):
        # Create a socket object
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Get local host name and port number
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = port

        # Bind the port
        self.server_socket.bind((self.host, self.port))

        # Set the maximum number of connections, after which the queue is full
        self.server_socket.listen(5)
        self.all_socket_connections = []

        # Attach a model distributor
        self.model_distributor = TfDistributor()
        self.model_distributor.set_total_clients(CLIENT_NUM)

        # Buffer message queue for each client
        self.buffer_message = {}

        # Snapshot attributes
        self.local_state_recorded = False
        self.local_state = None
        self.channel_state = {}
        self.channel_recording_status = {}
        self.collected_snapshot = []

    def store_buffer_message(self, client_socket, addr):
        ip = addr[0]

        print("Buffer thread running for", ip)

        # Keep listening to response from client
        while True:
            # Put incoming messages into buffer queue
            message = recv_socket_msg(client_socket)
            if ip in self.buffer_message.keys():
                self.buffer_message[ip].append(message)
            else:
                self.buffer_message[ip] = [message]

            # Snapshot not started
            # Skip channel recording
            if len(self.channel_recording_status.keys()) == 0:
                continue

            # If recording for the channel
            if self.channel_recording_status[ip]:

                # Return marker received
                # End of channel recording
                if self.local_state_recorded and message['type'] == 'snapshot' and message['content'] == 'marker':
                    continue

                if ip in self.channel_state.keys():
                    self.channel_state[ip].append(message)
                else:
                    self.channel_state[ip] = [message]

            # print("New incoming message from", ip)
            # self.check_channel_state()

    def handle_connection(self, client_socket, addr):
        """
        Handle each incoming socket connection
        """
        # Register the client connection
        print("[Connection] Start handling connection...")
        self.all_socket_connections.append((client_socket, addr))
        self.buffer_message[addr[0]] = []

        # Thread to buffer incoming messages
        buffer_thread = threading.Thread(target=self.store_buffer_message, args=(client_socket, addr))
        buffer_thread.start()

        # Welcome message
        send_socket_msg(client_socket, 'connection', 'Welcome to the server!')

        # Queue to buffer incoming messages
        message_queue = self.buffer_message[addr[0]]

        # Keep processing buffered message
        while True:
            # No new message, skip
            if len(message_queue) == 0:
                time.sleep(0.1)
                continue

            # Get the next message
            response = message_queue.pop()

            if response['type'] == "snapshot":
                # Received marker message
                if response['content'] == 'marker':
                    print("\n[Snapshot] [Client - {}] Marker message received".format(addr[0]))

                    # Condition 1 - local state not recorded
                    # Skip (when received, server must have already recorded its local state)
                    if not self.local_state_recorded:
                        # Step 1 - record own local state
                        print("\n[Snapshot] Condition 1 - Ready to record local state")
                        # Step 2 - start recording incoming messages
                        # Step 3 - send marker messages to all (back to server)
                    # Condition 2 - local state recorded
                    else:
                        print("\n[Snapshot] Condition 2 - Local state already recorded")
                        # Step 1 - stop recording incoming messages
                        self.stop_incoming_recording(client_socket, addr)
                        self.check_channel_state()

                    # Check if received marker message from all clients
                    # If received, client channel recording is False
                    if self.all_clients_recorded():
                        self.initiate_snapshot_collection()

            # Received returned local states for collection
            elif response['type'] == "state":
                print("\n[Snapshot] [Client - {}] Local state received".format(addr[0]))
                client_local_state = response['content']
                self.collected_snapshot.append(client_local_state)

                collected_count = len(self.collected_snapshot)
                print("[Snapshot] Received local state count:", collected_count)
                if collected_count == CLIENT_NUM:
                    print("[Snapshot] Collected all client local states")
                    print("=====================================================\n")

            elif response['type'] == "updated_weights":
                received_weights = response['content']
                print("[Client - {}] Received pushed new model weights".format(addr[0]))

                # If return weights != None, means already collected all model weights
                # Returned weights is the new weights, ready to distribute to all
                received_weights = self.model_distributor.collect_model_weights(received_weights)
                if received_weights is not None:
                    self.distribute_model_weights(received_weights)
            elif response['type'] == "check_value":
                print("[Client - {}] Local values: {}".format(addr[0], response['content']))
            else:
                print("[Client - {}] Unspecified message: {}".format(addr[0], response))

    def distribute_model_weights(self, new_weights):
        # Send merged new model weights to all connected clients
        for client_socket, addr in self.all_socket_connections:
            send_socket_msg(client_socket, "updated_weights", new_weights)
        print("New model weights distributed to all successfully!")
        print("=================================================\n")

    def handle_user_command(self):
        while True:
            user_input = input()

            if user_input == 'snapshot':
                print("\nUser command: snapshot")
                self.initialise_snapshot()
            elif user_input == 'summary':
                print("\nUser command: summary")
                self.show_snapshot_summary()
            elif user_input == 'check':
                print("\nUser command: check")
                self.send_command(user_input)
            elif user_input == 'finish':
                print("\nUser command: stop training")
                self.send_command(user_input)
            else:
                print("\nUnrecognised user command")

    def send_command(self, command, to_all=True):
        if to_all:
            for client_socket, addr in self.all_socket_connections:
                send_socket_msg(client_socket, 'command', command)

    def initialise_snapshot(self):
        print("\n======== Initiate Chandy-Lamport Snapshot ==========")
        # Step 1 - record own local state
        print("[Snapshot] Step 1")
        self.record_local_state()

        # Step 2 - start recording incoming messages
        print("\n[Snapshot] Step 2")
        self.start_incoming_recording()

        # Step 3 - send marker messages to all
        print("\n[Snapshot] Step 3")
        self.broadcast_snapshot_message('marker')
        print("====================================================\n")

    def record_local_state(self):
        print("[Snapshot] Start recording local state")
        self.local_state = ServerState(self)
        self.local_state_recorded = True
        print("[Snapshot] Local state recorded successfully")

    def start_incoming_recording(self):
        print("[Snapshot] Start recording incoming messages")

        # Initialise channel state
        self.channel_state = {}
        self.channel_recording_status = {}
        for client_socket, addr in self.all_socket_connections:
            self.channel_recording_status[addr[0]] = True
            self.channel_state[addr[0]] = []
            print("[Snapshot] Start recording channel from {}".format(addr[0]))

        self.check_channel_state()

    def broadcast_snapshot_message(self, content):
        for client_socket, addr in self.all_socket_connections:
            send_socket_msg(client_socket, 'snapshot', content)

        if content == 'marker':
            print("[Snapshot] Marker messages are sent")
        elif content == 'collect':
            print("[Snapshot] Collect messages are sent")

    def stop_incoming_recording(self, client_socket, addr):
        self.channel_recording_status[addr[0]] = False
        print("[Snapshot] Stop recording incoming messages from {}".format(addr[0]))

    def check_channel_state(self):
        for client_ip in self.channel_state.keys():
            print("[Snapshot] Channel state from {} : {}".format(client_ip, self.channel_state[client_ip]))

    def all_clients_recorded(self):
        for client_ip in self.channel_recording_status.keys():
            if self.channel_recording_status[client_ip]:
                return False
        return True

    def initiate_snapshot_collection(self):
        print("\n======== Initiate Local State Collection ==========")
        print("[Snapshot] All clients have recorded their states")
        print("[Snapshot] Initiate local states collection...")
        # Broadcast to collect local states
        self.broadcast_snapshot_message('collect')

    def show_snapshot_summary(self):
        print("\n================ Snapshot Summary =================")
        if len(self.collected_snapshot) != CLIENT_NUM:
            print("[Summary] Snapshot not yet available...")
            print("=====================================================\n")
            return

        # Show server local state
        self.local_state.show_state_summary()

        # Show client local states
        for client_local_state in self.collected_snapshot:
            print("-----")
            client_local_state.show_state_summary()
        print("=====================================================\n")

        # Reset snapshot related attributed
        self.snapshot_reset()

    def snapshot_reset(self):
        # Reset snapshot attributes
        self.local_state_recorded = False
        self.local_state = None
        self.channel_state = None
        self.channel_recording_status = {}
        self.collected_snapshot = []

        # Inform clients to reset too
        self.broadcast_snapshot_message('reset')
        print("[Snapshot] Reset snapshot attributes")

    def start(self):
        print("[Connection] Ready to accept incoming connections...")

        # Thread for listening user input commands
        user_command_thread = threading.Thread(target=self.handle_user_command, daemon=True)
        user_command_thread.start()

        while True:
            # Establish client connection
            client_socket, addr = self.server_socket.accept()
            print("[Connection] Connected to: %s" % str(addr))

            # Thread-per-Connection
            client_thread = threading.Thread(target=self.handle_connection, args=(client_socket, addr))
            client_thread.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Mock Worker Nodes in Federated learning")
    parser.add_argument("--port", type=int, help="Port used for communication")

    args = parser.parse_args()

    port = args.port

    server = Server(port)
    server.start()
