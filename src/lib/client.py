from socket import *
from lib.packets import *
from lib.cfg_peers import *
from lib.cfg_chunks import *
from merge_chunks import *
from threading import *


# ALICE, BOB, TRACKER
class Client:

    def __init__(self):
        self.create_sockets()
        self.start_sockets()
        self.write_chunks()

    def create_sockets(self):
        self.Packets = Packets()
        self.chunks_content = []
        self.sockets = {}
        for peer in self.peerList:
            if peer == "tracker":
                continue
            self.sockets[peer] = socket(AF_INET, SOCK_STREAM)
            self.sockets[peer].connect(
                (self.peerList[peer][0], self.peerList[peer][1]))
            print('\nConnected to', (self.peerList[
                  peer][0], self.peerList[peer][1]))

    def start_sockets(self):
        for i in range(len(self.chunks)):
            self.start(i)
        # end
        for peer in self.peerList:
            if peer == "tracker":
                continue
            self.sockets[peer].close()
            print('TCP-' + peer + ' socket closed')

    def start(self, i):
        chunk_hash = self.chunks[i]
        chunk_peers = self.chunks_peers[i]
        for peer in chunk_peers:
            print('\n' + str(i), peer)
            if self.get_chunk(peer, chunk_hash) is True:
                break

    def get_chunk(self, peer, chunk_hash):
        sock = self.sockets[peer]
        # req
        self.Packets.send_get_chunk(sock, chunk_hash)

        # res
        msg_header = sock.recv(8)
        if len(msg_header) == 0:
            sock.close()
            return False
        msg_version, msg_type, msg_length, msg_body = self.Packets.recv(
            sock, msg_header)

        if self.Packets.check_chunk(msg_type) is True:
            rchunk_hash, chunk_content = self.Packets.handle_chunk(msg_body)
            self.chunks_content.append((rchunk_hash, chunk_content))
            return True
        else:
            self.Packets.handle_error(msg_body)
            return False

    def write_chunks(self):
        for chunk in self.chunks_content:
            chunk_path = os.path.join(
                chunks_path, 'charlie', chunk[0] + '.bin')
            with open(chunk_path, 'wb') as cf:
                cf.write(chunk[1])


class Client1(Client):

    def __init__(self):
        cfg_peers = CfgPeers()
        cfg_chunks = CfgChunks()
        self.peerList = cfg_peers.read_config_peers_all()
        self.chunks, self.chunks_peers, self.chunks_count, self.filename = cfg_chunks.read_config_chunks()
        Client.__init__(self)
        merge_chunks = MergeChunks()


class Client2(Client):

    def __init__(self):
        self.filename = ''
        self.chunks_info = 0
        self.create_socket()
        self.start_socket()
        self.peerList, self.chunks, self.chunks_peers, self.chunks_count = self.parse_info()
        Client.__init__(self)
        self.create_config_file
        merge_chunks = MergeChunks()

    def create_socket(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        print('\nConnected to tracker:', self.ip_address,
              'on port', self.port_number)
        self.socket.connect((self.ip_address, self.port_number))

    def start_socket(self):
        self.Packets.send_get_file_info(self.socket)
        msg_header = self.socket.recv(8)
        if len(msg_header) == 0:
            self.socket.close()
            return False
            # test
        msg_version, msg_type, msg_length, msg_body = self.Packets.recv(
            self.socket, msg_header)
        self.filename, self.chunks_info = self.Packets.handle_file_info(
            msg_body)
        self.socket.close()
        print("TCP-tracker socket closed")

    def parse_info(self):
        peers_set = {}
        chunks = {}
        chunks_peers = {}
        if len(self.chunks_info) != 0:
            i = 0
            j = 0
            for chunk in self.chunks_info:
                chunks[i] = chunk[0]
                peers = chunk[1]
                chunks_peers[i] = []

                for peer in peers:
                    if peer not in peers_set.values():
                        peers_set[str(j)] = peer
                        j += 1
                for peer in peers_set:
                    if peers_set[peer] in peers:
                        chunks_peers[i].append(peer)
                i += 1
        return peers_set, chunks, chunks_peers, len(chunks)

    def create_config_file(self):
        config = configparser.ConfigParser()
        config.add_section('description')
        config.set('description', 'filename', self.filename)
        config.set('description', 'chunks_count', str(len(self.chunks)))
        config.add_section('chunks')
        for (i, chunk_hash) in enumerate(self.chunks):
            config.set('chunks', str(i), chunk_hash)
        config.add_section('chunks_peers')
        for (i, peers) in enumerate(self.chunks_peers):
            config.set('chunks_peers', str(i), ', '.join(peers))
        with open(os.path.join(config_path, 'file.ini'), 'w') as f:
            config.write(f)


class Client21(Client2):

    def __init__(self):
        cfg = CfgPeers()
        self.Packets = Packets()
        # self.ip_address, self.port_number = cfg.read_config_peers('tracker')
        # print(self.ip_address, self.port_number)
        self.ip_address = '164.15.76.104'
        self.port_number = 8000
        Client2.__init__(self)


class Client3(Client2):

    def __init__(self):
        self.addr = ('<broadcast>', 9000)
        self.Packets = Packets()
        self.broadcasting()
        Client2.__init__(self)

    def broadcasting(self):

        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.Packets.send_discover_tracker(self.sock, self.addr)
        print('Discovering the tracker...', self.addr)
        msg_header, addr2 = self.sock.recvfrom(8)
        if len(msg_header) == 0:
            self.sock.close()
            return False
            # test
        msg_version, msg_type, msg_length, msg_body = self.Packets.recvfrom(
            self.sock, msg_header)
        self.ip_address, self.port_number, self.tracker_name, self.tracker_name_length = self.Packets.handle_tracker_info(
            msg_body)
        self.sock.close()
        print("UDP-broadcast socket closed")
