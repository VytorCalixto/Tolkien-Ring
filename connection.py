import socket, select
# Recommended for queues on python doc
from collections import deque

class Connection(object):

    def __init__(self):
        self._input_sockets = []
        self._output_sockets = []
        self._monitor_sockets = []
        self.messages = {}

    def open_socket(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((host, port))
        s.setblocking(False)
        return s

    def poll(self):
        return select.select(self._input_sockets, self._output_sockets, self._monitor_sockets,0)

    def send_handshake(self, sock, addr):
        self.put_message(sock,"handshake", addr)

    def ack_handshake(self, sock, addr):
        self.put_message(sock,"ok", addr)

    def put_message(self, sock, msg, addr):
        self.messages[sock].append((msg, addr))

    def send_message(self, sock):
        # * -> expands tuple as arguments
        sock.sendto(*(self.messages[sock].popleft()))

    def has_message(self, sock):
        return bool(self.messages[sock])

    def add_output_socket(self, sock):
        if sock not in self._output_sockets:
            self._output_sockets.append(sock)
            self.messages[sock] = deque()

    @property
    def input_sockets(self):
        return self._input_sockets

    @input_sockets.setter
    def input_sockets(self, value):
        self._input_sockets = value

    @property
    def output_sockets(self):
        return self._output_sockets

    @output_sockets.setter
    def output_sockets(self, value):
        self._output_sockets = value
        for s in value:
            print(s)
            self.messages[s] = deque()

    @property
    def monitor_sockets(self):
        return self._monitor_sockets

    @monitor_sockets.setter
    def monitor_sockets(self, value):
        self._monitor_sockets = value