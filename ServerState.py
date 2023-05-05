class ServerState:
    def __init__(self, server):
        # Server config
        self.host = server.host
        self.port = server.port

        # Existing connections
        self.all_socket_connections = server.all_socket_connections

        self.model_distributor = server.model_distributor

    def check(self):
        print(self.host, self.port)
        print(self.all_socket_connections)
