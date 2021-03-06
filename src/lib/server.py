from socket import *
from lib.cfg_peers import *
import threading


class Server:

    def __init__(self):
        cfg_peers = CfgPeers()
        self.ip_address, self.port_number = cfg_peers.read_config_peers(
            self.user)
        # self.user in tracker!
        self.create_socket()

    def create_socket(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        # Include IP headers
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.socket.bind((self.ip_address, self.port_number))
        self.listen_socket()

    def listen_socket(self):
        print('Listening on port', self.port_number)
        self.socket.listen(10)
        while True:
            client, address = self.socket.accept()
            print('Client connected with ' +
                  address[0] + ':' + str(address[1]))
            # timeout after 60 seconds of inactivity
            # client.settimeout(60)
            th = threading.Thread(target=self.start_socket,
                                  args=(client, address))
            th.daemon = True
            th.start()

    def start_socket(self):
        pass
