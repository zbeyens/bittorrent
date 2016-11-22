from struct import *

version = 1

DISCOVER_TRACKER = 0
TRACKER_INFO = 1
GET_FILE_INFO = 2
FILE_INFO = 3
GET_CHUNK = 4
CHUNK = 5
ERROR = 6
# Error codes:
INVALID_MESSAGE_FORMAT = 0
INVALID_REQUEST = 1
CHUNK_NOT_FOUND = 2


class Packets():

    def send(self, sock, msg_version, msg_type, msg_length, msg_body):
        msg_header = pack('<BBH', msg_version, msg_type, msg_length)
        print(msg_header, msg_length)
        # NOTE: or should we send in only one message ?
        sock.send(msg_header)
        sock.send(msg_body)

    def sendError(self, sock, err):
        msg_body = pack('<H2x', INVALID_MESSAGE_FORMAT)
        msg_length = 4
        msg_type = err
        self.send(sock, version, msg_type, msg_length, msg_body)

    def recv(self, client, msg_header):
        msg_version, msg_type, msg_length = unpack('<BBH', msg_header)
        print(msg_version, msg_type, msg_length)
        msg_body = client.recv(msg_length).decode()
        print(msg_body, 'received')
        return msg_version, msg_type, msg_length, msg_body

    def check_format(self, msg_version, msg_type, msg_length, msg_body):
        # NOTE: is it enough?
        if (msg_type >= 0 and msg_type <= 6) and msg_version == version and msg_length % 4 == 0:
            return True
        else:
            return False

    def check_request(self, msg_type):
        if (msg_type == GET_CHUNK):
            return True
        else:
            return False
