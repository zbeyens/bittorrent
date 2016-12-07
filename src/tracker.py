import binascii
from lib.packets import Packet
from ctypes import *
import struct
import configparser
from lib.packets import *
from lib.cfg import *
from lib.server import Server

class Tracker:

    def __init__(self):
        self.read_config_peers()
        self.read_config_chunks()
        msg = self.get_fileinfo()
        self.create_socket()
        self.bind()
        Packet.send(self.sock,'1','3',len(msg),msg)

    def read_config_peers(self):
        config_p = configparser.ConfigParser()
        config_p.read(peers_path)
        self.ports_peers = {}
        self.ip_address_peers = {}
        for each_section in config_p.sections():
            p = config_p.getint(each_section,'port_number')
            i = config_p.get(each_section,'ip_address')
            self.ip_address_peers[each_section] = (i, p)

    def read_config_chunks(self):
        self.chunks = {}
        self.chunks_peers = {}
        config = configparser.ConfigParser()
        config.read(chunks_path)
        self.filename = config.get('description', 'filename')
        self.chunks_count = config.getint('Description','chunks_count')
        for (id_chunk, chunk_hash) in config.items('chunks'):
            id_chunk = int(id_chunk)
            self.chunks[id_chunk] = binascii.a2b_hex(chunk_hash)
        for (id_chunk_peer, peers) in config.items('chunks_peer'):
            id_chunk_peer = int(id_chunk_peer)
            list_peers = peers.split(',')
            self.chunks_peers[id_chunk_peer] = list_peers

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
        pass


