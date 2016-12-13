from socket import *
from lib.packets import *
from lib.cfg_peers import *
from threading import *


# ALICE, BOB, TRACKER
class Client:

    def __init__(self):
        cfg = CfgPeers()
        cfg2 = CfgChunks()
        self.chunks_content = []
        self.peerList = cfg.read_config_peers_all()
        self.chunks, self.chunks_peers, self.chunks_count, self.filename = cfg2.read_config_chunks()
        self.read_config_chunks()
        self.create_sockets()
        self.start_sockets()

    def create_sockets(self):
        self.Packets = Packets()
        self.sockets = {}
        for peer in self.peerList:
            if peer = "tracker":
                continue
            self.sockets[peer] = socket(AF_INET, SOCK_STREAM)
            self.sockets[peer].connect(
                (self.peerList[peer][0], self.peerList[peer][1]))
        # NOTE: have to multithread (cf server.py)
        # for i in range(len(self.peerList)):
        #     th = threading.Thread(target=self.start_socket, args=(self.socket))
        #     th.daemon = True
        #     th.start()

    def start_sockets(self):
        for i in range(len(self.chunks)):
            chk_hash = chunks[i]
            chk_peers = chunks_peers[i]
            for peer in chk_peers:
                if self.get_chunk(peer, chk_hash) is False:
                    break

    def get_chunk(self, peer, chk_hash):
        sock = self.sockets[peer]
        self.Packets.send_get_chunk(sock, chk_hash)
        msg_header = sock.recv(8)
        if len(msg_header) == 0:
            sock.close()
            return False
        msg_version, msg_type, msg_length, msg_body = self.Packets.recv(
            sock, msg_header)
        if self.Packets.check_chunk(msg_type) is True:
            body = unpack("<20BI", msg_body[:24])
            chunk_hash = body[0]
            chunk_content_length = body[1]
            body = unpack("<20BI%dB" % chunk_content_length,
                          msg_body[:24 + chunk_content_length])
            self.chunks_content.append(body[2])
            return True
        else:
            return False


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
