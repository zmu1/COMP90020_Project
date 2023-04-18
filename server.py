import socket

# create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# get local host name and port number
host = socket.gethostname()
port = 9999

# bind the port
server_socket.bind((host, port))

# set the maximum number of connections, after which the queue is full
server_socket.listen(5)

while True:
    # establish client connection
    client_socket, addr = server_socket.accept()

    print("Connected to: %s" % str(addr))

    msg = 'Welcome to the server!' + "\r\n"
    client_socket.send(msg.encode('utf-8'))

    client_socket.close()
