class ServerState:
    def __init__(self, server):
        # Server config
        self.host = server.host
        self.port = server.port
        self.ip = server.host

        # Existing connections
        self.all_socket_connections = server.all_socket_connections

        self.model_distributor = server.model_distributor

    def check(self):
        print(self.host, self.port)
        print(self.all_socket_connections)

    def show_state_summary(self):
        print("[Summary] Server - {}".format(self.ip))
        print("Connected client count:", len(self.all_socket_connections))
        print("Connected clients:", [conn[1][0] for conn in self.all_socket_connections])

