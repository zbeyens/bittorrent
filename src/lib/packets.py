from struct import *
import binascii
import math

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

    def recv(self, sock, msg_header):
        # recv 8 bytes
        msg_version, msg_type, msg_length = unpack('<BB2xI', msg_header)
        body_length = (msg_length - 2) * 4
        # recv n bytes
        msg_body = self.recvall(sock, body_length)
        print('Received:', msg_version, msg_type, msg_length)
        return msg_version, msg_type, msg_length, msg_body

    def recvfrom (self,sock,msg_header):
        msg_version, msg_type, msg_length = unpack('<BB2xI', msg_header)
        body_length = (msg_length - 2) * 4
        msg_body = self.recvallfrom(sock, body_length)
        print('Received:', msg_version, msg_type, msg_length)
        return msg_version, msg_type, msg_length, msg_body

    def recvallfrom(self, sock, n):
        msg_body = ''.encode()
        while len(msg_body) < n:
            print (msg_body)
            packet,addr = sock.recvfrom(n - len(msg_body))
            if not packet:
                return None
            msg_body += packet
        return msg_body

    def recvall(self, sock, n):
        # Packets sent can be divided: we could need multiple recv
        # Helper function to recv n bytes or return None if EOF is hit
        msg_body = ''.encode()
        while len(msg_body) < n:
            packet = sock.recv(n - len(msg_body))
            if not packet:
                return None
            msg_body += packet
        return msg_body

    def send(self, sock, msg_version, msg_type, msg_length, msg_body):
        msg_header = pack('<BB2xI', msg_version, msg_type, msg_length)

        # send 8 bytes
        sock.send(msg_header)
        # send n bytes
        if msg_body:
            sock.send(msg_body)

    def sendto(self, sock, msg_version, msg_type, msg_length, msg_body,addr):
        msg_header = pack('<BB2xI', msg_version, msg_type, msg_length)
        print ('hham', msg_header)
        # send 8 bytes
        sock.sendto(msg_header,addr)
        # send n bytes
        if msg_body:
            sock.sendto(msg_body,addr)


    # D.1 Charlie 3
    def send_discover_tracker(self, sock, addr):
        msg_type = DISCOVER_TRACKER
        msg_length = 2
        print (addr)
        self.sendto(sock, version, msg_type, msg_length, 0, addr)

    # D.2 Tracker 3
    def send_tracker_info(self, sock, ip_address, port_number, tracker_name_length, tracker_name, addr):
        msg_body = pack('<')
        msg_body += pack('4B', *(int(x) for x in ip_address.split('.')))
        msg_body += pack('H', port_number)
        msg_body += pack('H', tracker_name_length)
        pad_length = (4-tracker_name_length%4)%4
        msg_body += pack('%ds' % tracker_name_length,tracker_name.encode("utf-8"))
        msg_body += pack('%dx' % pad_length)
        msg_type = TRACKER_INFO
        msg_length = math.ceil(len(msg_body)/4) + 2
        self.sendto(sock, version, msg_type, msg_length, msg_body,addr)


    # D.3 Charlie 2
    def send_get_file_info(self, sock):
        msg_type = GET_FILE_INFO
        msg_length = 2
        self.send(sock, version, msg_type, msg_length, 0)

    def handle_tracker_info(self, msg_body):
        ip_adress_brut = unpack('4B',msg_body[0:4])
        ip_address = self.table2ip(ip_adress_brut)
        port_number, tracker_name_length = unpack('<HH',msg_body[4:8])
        tracker_nameb = unpack ('%ds'% tracker_name_length , msg_body[8:8 + tracker_name_length])
        tracker_name = tracker_nameb[0].decode()
        return ip_address, port_number, tracker_name, tracker_name_length


    # D.4 Tracker
    def send_file_info(self, sock, chunks_count, filename, chunks, chunks_peers, peers_info):
        msg_type = FILE_INFO

        filename_length = len(filename)
        pad_length = (4 - filename_length % 4) % 4
        msg_body = pack('<')
        msg_body +=  pack('H',chunks_count)
        msg_body +=  pack('H',filename_length)
        msg_body += pack('%ds' % filename_length, filename.encode("utf-8"))
        msg_body += pack('%dx' % pad_length)

        for i in range(chunks_count):
            chunk_hash = chunks[i]
            peers = chunks_peers[i]
            peers_count = len(peers)
            msg_body += pack('20B', *chunk_hash)
            msg_body += pack('H', peers_count)
            msg_body += pack('xx')
            # msg_body += pack
            for peer in peers:
                ip_address = peers_info[peer][0]
                port_number = peers_info[peer][1]
                msg_body += pack('4B', *(int(x) for x in ip_address.split('.')))
                msg_body += pack('H', port_number)
                msg_body += pack('xx')

        msg_length = len(msg_body)
        msg_length = math.ceil(msg_length/4) + 2

        self.send(sock, version, msg_type, msg_length, msg_body)

    # D.5 Charlie
    def send_get_chunk(self, sock, chunk_hash):
        msg_type = GET_CHUNK
        # 2 + 5
        msg_length = 7
        msg_body = pack('<')
        msg_body += pack('B' * 20, *chunk_hash)
        self.send(sock, version, msg_type, msg_length, msg_body)

    def handle_get_chunk(self, msg_body):
        filename = binascii.hexlify(msg_body).decode()
        return filename

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
        print('CHUNK sent:', len(msg_body))
        self.send(sock, version, msg_type, msg_length, msg_body)

    def handle_chunk(self, msg_body):
        
        body = unpack("<20BI", msg_body[:24])
        rchunk_hash = binascii.hexlify(bytearray(body[:20])).decode()
        chunk_content_length = body[20]
        body = unpack("<%dB" % chunk_content_length,
                      msg_body[24:24 + chunk_content_length])
        chunk_content = bytearray(body)
        print('CHUNK')
        return rchunk_hash, chunk_content

    def handle_file_info(self,msg_body):

        chunks_count,filename_length= unpack('<HH',msg_body[0:4])
        print(chunks_count)
        print(filename_length)
        pad_length = (4 - filename_length%4)%4
        filename = unpack ('%ds'% filename_length , msg_body[4:4 + filename_length])
        filename = filename[0].decode()
        n = 4 + filename_length
        print(filename)
        n += pad_length
        chunks_info = []
        for i in range(chunks_count):
            chunk_hash_b = unpack('20B',msg_body[n:n+20]); n += 20
            chunk_hash = bytearray(chunk_hash_b)
            peers_count= unpack('H', msg_body[n:n+2]);n+=4
            peers_count=peers_count[0]
            print(peers_count)
            peers_info = []
            for j in  range(peers_count):
                ip_adress_brut = unpack('4B',msg_body[n:n+4]);n+=4
                #print(ip_adress_brut
                ip_address = self.table2ip(ip_adress_brut)
                port_number = unpack('H',msg_body[n:n+2]);n+=4
                port_number = port_number[0]
                #print(ip_address)
                #print (port_number)
                peers_info.append((ip_address,port_number))
            chunks_info.append((chunk_hash,peers_info))
        print(filename,chunks_info)
        return filename, chunks_info

    def table2ip(self,table):
        ip = ''
        if len(table) == 4 or len(table) == 6:
            for i in range(len(table)):
                if i == len(table) - 1:
                    ip = ip + str(table[i])
                else:
                    ip = ip + str(table[i]) + '.'
        return ip



    # D.7 Peer - Tracker
    def send_error(self, sock, err):
        msg_type = ERROR
        # 2 + 1
        msg_length = 3
        msg_body = pack('<H2x', err)
        self.send(sock, version, msg_type, msg_length, msg_body)


    def handle_error(self, msg_body):
        body = unpack('<H', msg_body[:2])
        if body[0] == INVALID_MESSAGE_FORMAT:
            print('INVALID_MESSAGE_FORMAT')
        elif body[0] == INVALID_REQUEST:
            print('INVALID_REQUEST')
        elif body[0] == CHUNK_NOT_FOUND:
            print('CHUNK_NOT_FOUND')
    def send_error_to(self, sock, err, addr):
        msg_type = ERROR
        # 2 + 1
        msg_length = 3
        msg_body = pack('<H2x', err)
        self.sendto(sock, version, msg_type, msg_length, msg_body, addr)
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
    def check_request_get_file_info(self, msg_type):
        if (msg_type == GET_FILE_INFO):
            return True
        else:
            return False

    # Charlie
    def check_chunk(self, msg_type):
        if msg_type == ERROR:
            return False
        else:
            return True
    #tracker2
    def check_request_tracker_info(self, msg_type):
        if (msg_type == DISCOVER_TRACKER):
            return True
        else:
            return False
