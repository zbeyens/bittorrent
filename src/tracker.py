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
        config = configparser.ConfigParser()
        config.read(chunks_path)
        #chunks_number = config.getint('Description','chunks_count')
        self.chunks = []
        self.chunks_peer = []
        for (id,chunk_hash) in config.items('chunks'):
            id=int(id)
            self.chunks.append(id, chunk_hash)
        for (id, peers) in config.items('chunks_peer'):
            id = int(id)
            list_peer = peers.split(',')
            self.chunks_peer.append(id, list_peer)


