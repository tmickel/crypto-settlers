import socket
import json

class SettlersNetworkClient():
    def __init__(self, ip, port, signature_verify):
        self.ip = ip
        self.port = port
        self.socket = None
        self.socket_file = None
        self.signature_verify = signature_verify

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

    def send_key(self):
        self.send_data({'public_key': self.signature_verify.get_public_key()})

    def send_data(self, data):
        packed_data = json.dumps(data)
        signature = self.signature_verify.sign(packed_data)

        message = {'message': packed_data, 'signature': signature}
        send_message = json.dumps(message)

        self.socket.send(send_message + '\n')

        recv_data = self.socket_file.readline()
        recv_data_decoded = json.loads(recv_data)
        if (type(recv_data_decoded) != dict or 'success' not in recv_data_decoded or
            recv_data_decoded['success'] != True):
            print "Server returned an error"
            return False
        return True

    def disconnect(self):
        self.socket.close()
