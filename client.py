import socket
import json

class SettlersNetworkClient():
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.socket = None
        self.socket_file = None

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.ip, self.port))
        except socket.error:
            return False
        if self.socket is None:
            return False
        self.socket_file = self.socket.makefile('r+')
        return True

    def send_data(self, data):
        packed_data = json.dumps(data)
        self.socket.send(packed_data + '\n')

        recv_data = self.socket_file.readline()
        recv_data_decoded = json.loads(recv_data)
        return recv_data_decoded

    def disconnect(self):
        self.socket.close()
