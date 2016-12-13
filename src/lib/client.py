from socket import *
from lib.packets import *
from lib.cfg_peers import *
from threading import *


# ALICE, BOB, TRACKER
class Client:

    def __init__(self):
        cfg = CfgPeers()
        cfg2 = CfgChunks()
        self.peers_ip_port = cfg.read_config_peers_all()
        self.chunks, self.chunks_peers, self.chunks_count, self.filename = cfg2.read_config_chunks()
        self.read_config_chunks()
        self.create_sockets()
        self.start_sockets()

    def create_sockets(self):
        self.Packets = Packets()
        self.sockets = {}
        for i in range(len(self.peers_ip_port)):
            names = config_p.sections()

            self.sockets[names[i]] = socket(AF_INET, SOCK_STREAM)
            self.sockets[i].connect(
                (self.peers_ip_port[i][0], self.peers_ip_port[i][1]))
        # NOTE: have to multithread (cf server.py)
        # for i in range(len(self.peers_ip_port)):
        #     th = threading.Thread(target=self.start_socket, args=(self.socket))
        #     th.daemon = True
        #     th.start()

    def start_sockets(self, socket):
        for i in range(len(self.chunks_peers)):

    def


class ClientV1(Client):

    def __init__(self):
        Client.__init__()
        self.create_socket()

    def start_socket(self):

        while 1:
            # test
            msg_body = input('enter:')
            self.Packets.send(self.socket, version, 6,
                              len(msg_body), msg_body.encode())

            msg_header = self.socket.recv(8)

            if len(msg_header) == 0:
                self.socket.close()
                break

            # test
            msg_version, msg_type, msg_length, msg_body = self.Packets.recv(
                self.socket, msg_header)

            # test, should send GET_CHUNK
            self.Packets.send(self.socket, version,
                              GET_CHUNK, msg_length, msg_body)


class ClientV2(Client):

    def __init__(self, tracker):
        # NOTE: use cfg_peers
        self.version = 1
        self.type = 2
        self.length = 2
        Client.__init__(tracker)
        self.create_socket()

    def start_socket(self):
        while 1:
            # test
            msg_body = 'ok'
            self.Packets.send(self.socket, self.version,
                              self.type, self.length, msg_body.encode())
            msg_header = self.socket.recv(8)
            if len(msg_header) == 0:
                self.socket.close()
                break
            # test
            msg_version, msg_type, msg_length, msg_body = self.Packets.recv(
                self.socket, msg_header)


if __name__ == '__main__':
    Client()
