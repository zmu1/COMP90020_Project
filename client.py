import socket

# create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# get local host name and port number
host = socket.gethostname()
port = 9999

# connect to the server
client_socket.connect((host, port))

# receive the message
msg = client_socket.recv(1024)

client_socket.close()

print(msg.decode('utf-8'))
