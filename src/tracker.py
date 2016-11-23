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
        config = configparser.ConfigParser()
        config.read(peers_path)
        self.ip_address = config.get('tracker', 'ip_address')
        self.port_number = config.getint('tracker', 'port_number')

    def read_config_chunks(self):
        self.chunks = {}
        self.chunks_peers = {}
        config = configparser.ConfigParser()
        config.read(chunks_path)
        #chunks_number = config.getint('Description','chunks_count')
        for (id_chunk, chunk_hash) in config.items('chunks'):
            id_chunk = int(id_chunk)
            self.chunks[id_chunk]=chunk_hash
        for (id_chunk_peer, peers) in config.items('chunks_peer'):
            id_chunk_peer = int(id_chunk_peer)
            list_peers = peers.split(',')
            self.chunks_peers[id_chunk_peer] = list_peers
    """
    def listen(self):
    """

