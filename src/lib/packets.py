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

    def recv(self, client, msg_header):
        # recv 8 bytes
        msg_version, msg_type, msg_length = unpack('<BB2xI', msg_header)
        body_length = (msg_length - 2) * 4
        # recv n bytes
        msg_body = client.recv(body_length)
        return msg_version, msg_type, msg_length, msg_body

    def send(self, sock, msg_version, msg_type, msg_length, msg_body):
        msg_header = pack('<BB2xI', msg_version, msg_type, msg_length)

        # send 8 bytes
        sock.send(msg_header)
        # send n bytes
        if msg_body:
            sock.send(msg_body)

    # D.1 Charlie 3
    def send_discover_tracker(self, sock):
        msg_type = DISCOVER_TRACKER
        msg_length = 2
        self.send(sock, version, msg_type, msg_length, 0)

    # D.2 Tracker 3
    def send_tracker_info(self, sock, ip_address, port_number, tracker_name_length, tracker_name):
        print('')
        # msg_type = DISCOVER_TRACKER
        # msg_length = 2
        # self.send(sock, version, msg_type, msg_length, 0)

    # D.3 Charlie 2
    def send_get_file_info(self, sock):
        msg_type = GET_FILE_INFO
        msg_length = 2
        self.send(sock, version, msg_type, msg_length, 0)

    # D.4 Tracker
    def send_file_info(self, sock, chunks_count, filename, chunks, chunks_peers, peers_info):
        msg_type = FILE_INFO

        filename_length = len(filename)
        msg_body = struct.pack("<HH%ds" % filename_length, chunks_count,
                               filename_length, filename.encode("utf-8"))
        if filename_length % 4 != 0:
            pad_length = (4 - filename_length % 4) % 4
            msg_body += struct.pack("%dx" % pad_length)
        for i in range(len(chunks)):
            chunk_hash = chunks[i]
            peers = chunks_peers[i]
            peers_count = len(peers)
            msg_body += struct.pack('<20BHxx', *chunk_hash, peers_count)
            for peer in peers:
                ip_address = peers_info[peer][0]
                port_number = peers_info[peer][1]
                msg_body += struct.pack('4B', *(int(x)
                                                for x in ip_address.split('.')))
                msg_body += struct.pack('<Hxx', port_number)

        length = 0
        length += 8 + 4 + filename_length + pad_length
        for i in range(len(chunks_peers)):
            length += 20 + 4
            length += 8 * len(chunks_peers[i])
        msg_length = length // 4

        self.send(sock, version, msg_type, msg_length, msg_body)

    # D.5 Charlie
    def send_get_chunk(self, sock, chunk_hash):
        msg_type = GET_CHUNK
        # 2 + 5
        msg_length = 7
        msg_body = pack('<')
        msg_body += pack('B' * 20, *chunk_hash)
        self.send(sock, version, msg_type, msg_length, msg_body)

    # D.6 - Peer
    def send_chunk(self, sock, chunk_hash, chunk_content_length, chunk_content):
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

    # D.7 Peer - Tracker
    def send_error(self, sock, err):
        msg_type = ERROR
        # 2 + 1
        msg_length = 3
        msg_body = pack('<H2x', err)
        self.send(sock, version, msg_type, msg_length, msg_body)

    # Check Formats:
    # Peer
    def check_format(self, msg_version, msg_type):
        if (msg_type >= 0 and msg_type <= 6) and msg_version == version:
            return True
        else:
            return False

    # Peer
    def check_request(self, msg_type):
        if (msg_type == GET_CHUNK):
            return True
        else:
            return False

    # Tracker
    def check_request_GET_FILE_INFO(self, msg_type):
        if (msg_type == GET_FILE_INFO):
            return True
        else:
            return False
