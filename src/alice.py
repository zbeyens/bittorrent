import os
import sys
import configparser
from socket import *

root_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
chunks_path = os.path.join(root_path, 'chunks')
config_path = os.path.join(root_path, 'config')
peers_path = os.path.join(config_path, 'peers.ini')


class Alice:

    def __init__(self):
        user = 'alice'
        self.read_config_peers(user)
        # self.read_chunks(user)
        self.connect_server()
        print('Done')

    def read_config_peers(self, user):
        config = configparser.ConfigParser()
        config.read(peers_path)
        self.ip_address = config.get(user, 'ip_address')
        self.port_number = config.getint(user, 'port_number')
        print(self.port_number)

    def read_chunks(self, user):
        # with open(os.path.join(chunks_path, peername, chunk_hash + '.bin'), 'wb') as cf:
            # cf.read(chunk_content)
        files = [f for f in os.listdir(chunks_path) if os.path.isfile(f)]
        for fle in files:
            print('yo')
            with open(fle) as f:
                print(f.readlines())
        print('ok')

    def connect_server(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect((self.ip_address, self.port_number))

        while 1:
            sentence = input('enter:')
            self.socket.send(sentence.encode())
            servSentence = self.socket.recv(1024)
            print(servSentence.decode())
        self.socket.close()

if __name__ == '__main__':
    Alice()
