import sys
import configparser
from socket import *
from lib.packets import *
from lib.cfg import *


class Tracker:

    def __init__(self):
        self.read_config_peers()
        self.read_config_chunks()

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
        #chunks_number = config.getint('Description','chunks_count')
        for (id_chunk, chunk_hash) in config.items('chunks'):
            id_chunk = int(id_chunk)
            self.chunks[id_chunk] = chunk_hash
        for (id_chunk_peer, peers) in config.items('chunks_peer'):
            id_chunk_peer = int(id_chunk_peer)
            list_peers = peers.split(',')
            self.chunks_peers[id_chunk_peer] = list_peers

    def create_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def bind(self):
        self.sock.bind(('', self.port_peers['tracker'][1]))

