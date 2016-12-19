from ctypes import *
import time
import struct
from socket import *
from math import *
from lib.packets import *
from lib.cfg_peers import *
from lib.server import *
from lib.cfg_chunks import *


class Tracker(Server):

    def __init__(self):
        cfg = CfgPeers()
        cfg2 = CfgChunks()
        self.Packets = Packets()
        self.tracker_name = 'tracker'

        self.own_ip_address, self.own_port_number = cfg.read_config_peers(
            'tracker')

        self.tracker_name_length = len(self.tracker_name)

        self.addr_broad = ('<broadcast>', 9000)

        self.create_socket_udp()
        # self.start_socket_udp()

        self.peers_info = cfg.read_config_peers_all()
        self.chunks, self.chunks_peers, self.chunks_count, self.filename = cfg2.read_config_chunks()
        self.user = self.tracker_name
        Server.__init__(self)

    def create_socket_udp(self):
        self.UDPSock = socket(AF_INET, SOCK_DGRAM)
        self.UDPSock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.UDPSock.bind(('', 9000))
        th = threading.Thread(target=self.start_socket_udp)
        th.daemon = True
        th.start()
        print('UDP socket created')

    def start_socket_udp(self):
        while True:
            msg_header, addr = self.UDPSock.recvfrom(8)
            print('Received broadcast from', addr)
            if msg_header:
                msg_version, msg_type, msg_length, msg_body = self.Packets.recvfrom(
                    self.UDPSock, msg_header)
                if self.Packets.check_format(msg_version, msg_type) is False:
                    self.Packets.send_error_to(
                        self.UDPSock, INVALID_MESSAGE_FORMAT, addr)
                    print('ERROR: INVALID_MESSAGE_FORMAT')
                elif self.Packets.check_request_tracker_info(msg_type) is False:
                    self.Packets.send_error_to(
                        self.UDPSock, INVALID_REQUEST, addr)
                    print('ERROR: INVALID_REQUEST')
                else:
                    self.Packets.send_tracker_info(
                        self.UDPSock, self.own_ip_address, self.own_port_number, self.tracker_name_length, self.tracker_name, addr)
                    # self.UDPSock.close()
                    # break
            else:
                print('UDP-tracker-server closed')
                self.UDPSock.close()
                return False

    def start_socket(self, client, address):
        while 1:
            # recv the header to know the length the body
            msg_header = client.recv(8)
            if msg_header:
                msg_version, msg_type, msg_length, msg_body = self.Packets.recv(
                    client, msg_header)
                if self.Packets.check_format(msg_version, msg_type) is False:
                    self.Packets.send_error(client, INVALID_MESSAGE_FORMAT)
                    print('ERROR: INVALID_MESSAGE_FORMAT')
                elif self.Packets.check_request_get_file_info(msg_type) is False:
                    self.Packets.send_error(client, INVALID_REQUEST)
                    print('ERROR: INVALID_REQUEST')
                else:
                    self.Packets.send_file_info(
                        client, self.chunks_count, self.filename, self.chunks, self.chunks_peers, self.peers_info)
            else:
                print('Client disconnected with ' +
                      address[0] + ':' + str(address[1]) + '\n')
                client.close()
                return False
if __name__ == '__main__':
    Tracker()
