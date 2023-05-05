import socket
import threading

from Server.server_handling_thread import HandlingThread


class ReceivingThread(threading.Thread):
    def __init__(self, host, port, server_instance):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.server_instance = server_instance

    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)

        print("[Log] Server listening on ({}:{})\n".format(self.host, self.port))

        while True:
            client_socket, addr = server_socket.accept()
            print("[Connection] Server accepted connection from ({}:{})\n".format(addr[0], addr[1]))

            client_thread = HandlingThread(self.host, self.port, client_socket, addr, self.server_instance)
            client_thread.start()
