import pickle
import struct

def send_socket_msg(conn, type, content=None):
    msg = {'type': type, 'content': content}

    packet = pickle.dumps(msg)
    length_in_4_bytes = struct.pack('I', len(packet))
    packet = length_in_4_bytes + packet

    conn.send(packet)


def recv_socket_msg(conn):
    length_in_4_bytes = conn.recv(4)
    size = struct.unpack('I', length_in_4_bytes)
    size = size[0]
    data = conn.recv(size)

    return pickle.loads(data)