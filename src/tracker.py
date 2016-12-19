from ctypes import *
import time
import struct
from socket import *
from math import *
from lib.packets import *
from lib.cfg_peers import *
from lib.server import *
from lib.cfg_chunks import *
"""
        # self.msg = self.get_fileinfo()
        # self.msg_2 = self.get_file_info_2()

    # def get_fileinfo(self):
    #     filename_length = len(self.filename)
    #     msg_body = struct.pack("<HH%ds" % filename_length, self.chunks_count,
    #                            filename_length, self.filename.encode("utf-8"))
    #     if filename_length % 4 != 0:
    #         pad_length = 4 - filename_length % 4
    #         msg_body += struct.pack("%dx" % pad_length)
    #     for i in range(len(self.chunks)):
    #         peers = self.chunks_peers[i]
    #         msg_body += struct.pack('<20BHxx', *self.chunks[i], len(peers))
    #         for peer in peers:
    #             ip = self.peers_info[peer][0]
    #             msg_body += struct.pack('4B', *(int(x) for x in ip.split('.')))
    #             msg_body += struct.pack('<Hxx', self.peers_info[peer][1])
    #     return msg_body

    # def get_file_info_2(self):
    #     l = 0
    #     msg_length = self.message_length()
    #     msg = create_string_buffer(msg_length)
    #     filename_length = len(self.filename)
    #     struct.pack_into("<HH%ds" % filename_length, msg, l, self.chunks_count,
    #                      filename_length, self.filename.encode("utf-8"))
    #     l += 4 + filename_length
    #     if filename_length % 4 != 0:
    #         pad_length = 4 - filename_length % 4
    #         struct.pack_into("%dx" % pad_length, l)
    #         l += pad_length
    #     for i in range(len(self.chunks)):
    #         peers = self.chunks_peers[i]
    #         struct.pack_into('<20BHxx', msg, l, *self.chunks[i], len(peers))
    #         l += 24
    #         for peer in peers:
    #             struct.pack_into(
    #                 '4B', *(int(x) for x in (self.peers_info[peer][0]).split('.')))
    #             l += 4
    #             struct.pack_into(
    #                 '<Hxx', msg, l, self.peers_info[peer][1])
    #             l += 4
    #     return msg

    # def message_length(self):
    #     l = 0
    #     l += 4 + len(self.filename) + (4 + 20) * self.chunks_count
    #     if len(self.filename) % 4 != 0:
    #         l += (4 - len(self.filename) % 4)
    #     for i in range(len(self.chunks_peers)):
    #         l += 8 * len(self.chunks_peers[i])
    #
    #     return l
    #
    # def length_in_dwords(self):
    #     L = self.message_length()
    #     D = ceil((L + 8) / 4)
    #     return D
"""

class Tracker(Server):

    def __init__(self):
        cfg = CfgPeers()
        cfg2 = CfgChunks()
        self.Packets = Packets()
        self.tracker_name = 'tracker'

        self.own_ip_address,self.own_port_number = cfg.read_config_peers('tracker')

        self.tracker_name_length = len(self.tracker_name)

        self.addr_broad =('<broadcast>',9000)

        self.create_socket_udp()
        self.start_socket_udp()

        self.peers_info = cfg.read_config_peers_all()
        self.chunks, self.chunks_peers, self.chunks_count, self.filename = cfg2.read_config_chunks()
        self.user = self.tracker_name
        Server.__init__(self)
    def create_socket_udp(self):
        self.UDPSock = socket(AF_INET,SOCK_DGRAM)
        self.UDPSock.setsockopt(SOL_SOCKET,SO_BROADCAST, 1)
        self.UDPSock.bind(('', 9000))
        print('socket created')


    def start_socket_udp (self):
        while True:
            msg_header, addr = self.UDPSock.recvfrom(8)
            print(' received header:',msg_header,addr)
            print(msg_header,addr)
            if msg_header:
                msg_version, msg_type, msg_length, msg_body = self.Packets.recvfrom(self.UDPSock, msg_header)
                print('type=',msg_type)
                if self.Packets.check_format(msg_version, msg_type) is False:
                    self.Packets.send_error_to(self.UDPSock, INVALID_MESSAGE_FORMAT, addr)
                    print('ERROR: INVALID_MESSAGE_FORMAT')
                elif self.Packets.check_request_tracker_info(msg_type) is False:
                    self.Packets.send_error_to(self.UDPSock, INVALID_REQUEST,addr)
                    print('ERROR: INVALID_REQUEST')
                else:
                    self.Packets.send_tracker_info(self.UDPSock,
                        self.own_ip_address, self.own_port_number, self.tracker_name_length, self.tracker_name, addr)
                    break

        else:
            print('udp server disconnected')
            self.UDPSock.close()
            return False



    def start_socket(self, client, address):
        while 1:
            # recv the header to know the length the body
            msg_header = client.recv(8)
            if msg_header:
                msg_version, msg_type, msg_length, msg_body = self.Packets.recv(
                    client, msg_header)
                print('header:',msg_header)
                if self.Packets.check_format(msg_version, msg_type) is False:
                    self.Packets.send_error(client, INVALID_MESSAGE_FORMAT)
                    print('ERROR: INVALID_MESSAGE_FORMAT')
                elif self.Packets.check_request_get_file_info(msg_type) is False:
                    self.Packets.send_error(client, INVALID_REQUEST)
                    print('ERROR: INVALID_REQUEST')
                else:
                    self.Packets.send_file_info(client, self.chunks_count, self.filename, self.chunks, self.chunks_peers, self.peers_info)
                    # self.Packets.send(
                    # self, self.sock, self.version, self.type, self.length,
                    # self.tracker.msg_2)
            else:
                print('Client disconnected with ' +
                      address[0] + ':' + str(address[1]))
                client.close()
                return False
if __name__ == '__main__':
    Tracker()
