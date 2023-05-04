import pickle
import struct


def send_socket_msg(conn, type, content=None, debug=False):
    msg = {'type': type, 'content': content}

    packet = pickle.dumps(msg)
    size = len(packet)
    length_in_4_bytes = struct.pack('I', size)

    conn.sendall(length_in_4_bytes)
    conn.sendall(packet)

    if debug:
        print("\n###############")
        print("Sent header size:", size)
        print("Sent packet size:", len(packet))
        print("Sent packet type:", type)
        print("###############\n")


def recv_socket_msg(conn, debug=False):
    length_in_4_bytes = conn.recv(4)
    size = struct.unpack('I', length_in_4_bytes)
    size = size[0]

    # Keep reading the incoming bytes
    # Until all bytes length required are received
    data = bytearray(size)
    pos = 0
    while pos < size:
        n = conn.recv_into(memoryview(data)[pos:])
        pos += n

    if debug:
        print("\n*****************")
        print("Received header size:", size)
        print("Received packet size:", len(data))
        print("*****************\n")

    return pickle.loads(data)
