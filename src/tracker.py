from ctypes import *
import struct
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
        self.read_config_chunks()
        msg = self.get_fileinfo()



    def get_fileinfo (self):
        filename_length = len(self.filename)
        msg_body = struct.pack("<HH%ds" % filename_length,self.chunks_count,filename_length,self.filename.encode("utf-8"))
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
        version = '1'
        msg_type = '3'
        msg_length = self.message_length()
        msg = create_string_buffer(msg_length + 4)
        struct.pack_into('<BBxxI',msg, l, version, msg_type, msg_length);l+=4;
        filename_length = len(self.filename)
        struct.pack_into("<HH%ds" % filename_length, msg, l, self.chunks_count, filename_length, self.filename.encode("utf-8"));l += 4 + filename_length;
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
        for i in range(len(self.chunks_peers)):
            l += 8*len(self.chunks_peers[i])
        return l


class ServerTracker(Server):
    def __init__(self):
        Server.__init__(self,'tracker')