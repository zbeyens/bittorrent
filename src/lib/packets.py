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
        msg_header = pack('<BB2xI', msg_version, msg_type, msg_length)

        # send 8 bytes
        sock.send(msg_header)
        # send n bytes
        sock.send(msg_body)

    def sendError(self, sock, err):
        msg_type = ERROR
        # 2 + 1
        msg_length = 3
        msg_body = pack('<H2x', err)
        self.send(sock, version, msg_type, msg_length, msg_body)

    def sendChunk(self, sock, chunk_hash, chunk_content_length, chunk_content):
        msg_type = CHUNK
        chunk_content_pad = (4 - chunk_content_length % 4) % 4
        # 2 + 5 + 1 + n
        msg_length = 8 + (chunk_content_length + chunk_content_pad) // 4
        msg_body = pack('<')
        msg_body += pack('B' * 20, *chunk_hash)
        msg_body += pack('I', chunk_content_length)
        msg_body += pack('%dB' % chunk_content_length, *chunk_content)
        msg_body += pack('%dx' % chunk_content_pad)
        self.send(sock, version, msg_type, msg_length, msg_body)

    def recv(self, client, msg_header):
        # recv 8 bytes
        msg_version, msg_type, msg_length = unpack('<BB2xI', msg_header)
        body_length = (msg_length - 2) * 4
        # recv n bytes
        msg_body = client.recv(body_length)
        return msg_version, msg_type, msg_length, msg_body

    # def getBody(self, isEncoded, client, msg_header):
    #     if isEncoded is True:
    #         client.recv(msg_length).decode()
    #     else:
    #         client.recv(msg_length)

    def check_format(self, msg_version, msg_type):
        # NOTE: is it enough?
        if (msg_type >= 0 and msg_type <= 6) and msg_version == version:
            return True
        else:
            return False

    def check_request(self, msg_type):
        if (msg_type == GET_CHUNK):
            return True
        else:
            return False
