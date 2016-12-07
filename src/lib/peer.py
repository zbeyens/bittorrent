import sys
from socket import *
from lib.packets import *
from lib.cfg_peers import *
from lib.server import Server


chunks_path = os.path.join(root_path, 'chunks')

class Peer(Server):

    def __init__(self, user):
        Peer.__init__(self, user)
        print('Done')

    def check_chunk(self, filename):
        chunk_path = os.path.join(chunks_path, self.user, filename + '.bin')
        if not os.path.exists(chunk_path):
            return False
        else:
            return True

    def read_chunk(self, filename):
        chunk_path = os.path.join(chunks_path, self.user, filename + '.bin')
        chunk_content_length = os.path.getsize(chunk_path)
        chunk_content = ''
        with open(chunk_path, 'rb') as cf:
            chunk_content = cf.read(chunk_content_length)
        return chunk_content_length, chunk_content

