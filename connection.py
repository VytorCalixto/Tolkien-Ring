import socket, select
import message
# Recommended for queues on python doc
from collections import deque
import logging

logging.basicConfig(filename='tolkien.log', level=logging.DEBUG)

# links interessantes:
# http://www.bogotobogo.com/python/python_network_programming_tcp_server_client_chat_server_chat_client_select.php
# https://pymotw.com/2/select/index.html#module-select
# https://pymotw.com/2/socket/udp.html

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
        return select.select(self.input_sockets, self.output_sockets, self.monitor_sockets,0)

    def send_handshake(self, sock, addr, port=1337):
        handshake = message.makeHandshake(port)
        logging.debug("Criando handshake")
        logging.debug(handshake.getMessage())
        self.messages[sock].append((handshake.getMessage(), addr))

    def ack_handshake(self, sock, addr, host):
        ack = message.makeAckHandshake(host)
        logging.debug("Criando ack_handshake")
        logging.debug(ack.getMessage())
        self.messages[sock].append((ack.getMessage(), addr))

    def send_token(self, sock, addr):
        token = message.makeToken()
        logging.debug("Gerando token para enviar")
        self.messages[sock].append((token.getMessage(), addr))

    def put_message(self, sock, msg, addr):
        self.messages[sock].append((msg, addr))
        logging.debug(self.messages)

    def send_message(self, sock):
        # * -> expands tuple as arguments
        sock.sendto(*(self.messages[sock].popleft()))
        logging.debug(self.messages)

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
        print("lol")
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
