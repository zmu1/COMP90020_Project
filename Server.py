import threading
import socket
import time

from CommHelper import send_socket_msg, recv_socket_msg
from ServerState import ServerState
from TfDistributor import TfDistributor

CLIENT_NUM = 2


class Server:
    def __init__(self):
        # Create a socket object
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Get local host name and port number
        self.host = socket.gethostname()
        self.port = 5999

        # Bind the port
        self.server_socket.bind((self.host, self.port))

        # Set the maximum number of connections, after which the queue is full
        self.server_socket.listen(5)
        self.all_socket_connections = []

        # Attach a model distributor
        self.model_distributor = TfDistributor()
        self.model_distributor.set_total_clients(CLIENT_NUM)

        # Snapshot attributes
        self.local_state_recorded = False
        self.local_state = None
        self.channel_state = None
        self.channel_recording_status = None

    def handle_connection(self, client_socket, addr):
        """
        Handle each incoming socket connection
        """
        print("[Connection] Start handling connection...")
        self.all_socket_connections.append((client_socket, addr))

        # Welcome message
        send_socket_msg(client_socket, 'connection', 'Welcome to the server!')

        # Keep listening to response from client
        while True:
            # Receive client response
            response = recv_socket_msg(client_socket)

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
                        print("\n[Snapshot] All clients have recorded their states")
                        print("[Snapshot] Initiate local states collection...")
                        self.initiate_snapshot_collection()

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
        # Step 1 - record own local state
        print("\n[Snapshot] Step 1")
        self.record_local_state()

        # Step 2 - start recording incoming messages
        print("\n[Snapshot] Step 2")
        self.start_incoming_recording()

        # Step 3 - send marker messages to all
        print("\n[Snapshot] Step 3")
        self.broadcast_snapshot_message('marker')

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
        # Broadcast to collect local states
        self.broadcast_snapshot_message('collect')
        # reset snapshot related attributed

    def run(self):
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


server = Server()
server.run()
