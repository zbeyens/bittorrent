from ctypes import *
import struct
from math import *
from lib.packets import Packets
from lib.cfg_peers import CfgPeers
from lib.server import Server
from lib.cfg_chunks import CfgChunks


class Tracker:
    def __init__(self):
        cfg = CfgPeers()
        cfg2 = CfgChunks()
        self.ip_address_peers = cfg.read_config_peers_all()
        self.chunks, self.chunks_peers, self.chunks_count, self.filename = cfg2.read_config_chunks()
        self.msg = self.get_fileinfo()
        self.msg_2 = self.get_file_info_2()



    def get_fileinfo(self):
        filename_length = len(self.filename)
        msg_body = struct.pack("<HH%ds" % filename_length,self.chunks_count,filename_length,self.filename.encode("utf-8"))
        if filename_length%4 != 0:
            pad_length = 4 - filename_length%4
            msg_body += struct.pack("%dx" % pad_length)
        for i in range(len(self.chunks)):
            peers = self.chunks_peers[i]
            msg_body += struct.pack('<20BHxx', *self.chunks[i],len(peers))
            for peer in peers:
                ip = self.ip_address_peers[peer][0]
                msg_body += struct.pack('4B', *(int(x) for x in ip.split('.')))
                msg_body += struct.pack('<Hxx',self.ip_address_peers[peer][1])
        return msg_body


    def get_file_info_2(self):
        l = 0
        msg_length = self.message_length()
        msg = create_string_buffer(msg_length)
        filename_length = len(self.filename)
        struct.pack_into("<HH%ds" % filename_length, msg, l, self.chunks_count, filename_length, self.filename.encode("utf-8"));l += 4 + filename_length;
        if filename_length%4 != 0:
            pad_length = 4 - filename_length%4
            struct.pack_into("%dx" % pad_length,l); l += pad_length
        for i in range(len(self.chunks)):
            peers = self.chunks_peers[i]
            struct.pack_into('<20BHxx',msg,l, *self.chunks[i], len(peers));l += 24;
            for peer in peers:
                struct.pack_into('4B', *(int(x) for x in (self.ip_address_peers[peer][0]).split('.')));l += 4;
                struct.pack_into('<Hxx',msg ,l ,self.ip_address_peers[peer][1]);l += 4;
        return msg

    def message_length(self):
        l = 0
        l += 4+len(self.filename)+(4+20)*self.chunks_count
        if len(self.filename) % 4 != 0:
            l += (4 - len(self.filename)%4)
        for i in range(len(self.chunks_peers)):
            l += 8*len(self.chunks_peers[i])

        return l

    def length_in_dwords(self):
        L = self.message_length()
        D = ceil((L+8)/4)
        return D


class ServerTracker(Server):

    def __init__(self):
        self.tracker = Tracker()
        self.version = 1
        self.type = 3
        self.length = self.tracker.length_in_dwords()
        Server.__init__(self,'tracker')

    def start_socket(self, client, address):
        try:
            while 1:
                #recv the header to know the length the body
                msg_header = client.recv(8)
                if msg_header:
                    msg_version, msg_type, msg_length, msg_body = self.Packets.recv(client, msg_header)
                    if self.Packets.check_format(msg_version, msg_type) is False:
                        self.Packets.sendError(client, INVALID_MESSAGE_FORMAT)
                        print('ERROR: INVALID_MESSAGE_FORMAT')
                    elif self.Packets.check_request_GET_FILE_INFO(self, msg_type) is False:
                        self.Packets.sendError(client, INVALID_REQUEST)
                        print('ERROR: INVALID_REQUEST')
                    else:
                        self.Packets.send(self, self.sock, self.version, self.type, self.length, self.tracker.msg_2)
                else:
                    print('Client disconnected with ' +address[0] + ':' + str(address[1]))
                    client.close()
                    break
        finally:
            self.client.close()