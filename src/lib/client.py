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
        merge_chunks = MergeChunks()

    def create_sockets(self):
        self.Packets = Packets()
        self.chunks_content = []
        self.sockets = {}
        for peer in self.peerList:
            if peer == "tracker":
                continue
            self.sockets[peer] = socket(AF_INET, SOCK_STREAM)
            print((self.peerList[peer][0], self.peerList[peer][1]))
            self.sockets[peer].connect(
                (self.peerList[peer][0], self.peerList[peer][1]))

    def start_sockets(self):
        ths = []
        for i in range(len(self.chunks)):
            self.start(i)
            # th = Thread(target=self.start, args=[i])
            # th.daemon = True
            # th.start()
            # ths.append(th)
        # wait all the threads have finished
        for t in ths:
            t.join()
        # ths = []
        # th1 = Thread(target=self.start, args=[range(len(self.chunks) // 2)])
        # th2 = Thread(target=self.start, args=[range(
        #     len(self.chunks) // 2, len(self.chunks))])
        #
        # th1.daemon = True
        # th1.start()
        # ths.append(th1)
        # th2.daemon = True
        # th2.start()
        # ths.append(th2)
        # # wait all the threads have finished
        # for t in ths:
        #     t.join()

    def start(self, i):
        chunk_hash = self.chunks[i]
        chunk_peers = self.chunks_peers[i]
        print ('ham', chunk_peers)
        for peer in chunk_peers:
            print('\n' + str(i), peer)
            if self.get_chunk(peer, chunk_hash) is True:
                break

    def get_chunk(self, peer, chunk_hash):
        sock = self.sockets[peer]
        # req
        self.Packets.send_get_chunk(sock, chunk_hash)
        print('Sent:', binascii.hexlify(chunk_hash).decode())

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
        print('ham2',self.chunks_peers)
        Client.__init__(self)

class Client2(Client):
    def __init__(self):
        self.filename = ''
        self.chunks_info = 0
        self.create_socket()
        self.start_socket()
        self.peerList,self.chunks,self.chunks_peers, self.chunks_count = self.parse_info()
        Client.__init__(self)

    def create_socket(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect((self.ip_address, self.port_number))
        print('connected to',self.ip_address,'on port',self.port_number)
    def start_socket(self):
        self.Packets.send_get_file_info(self.socket)
        print('sent get_fileinfo')
        msg_header = self.socket.recv(8)
        if len(msg_header) == 0:
            self.socket.close()
            return False
            # test
        print('header:',msg_header)
        msg_version, msg_type, msg_length, msg_body = self.Packets.recv(self.socket, msg_header)
        print('body:',msg_body)
        print ('File info received, length =', len(msg_body))
        self.filename, self.chunks_info = self.Packets.handle_file_info(msg_body)
        print ("receive fileinfo-> filename = ",self.filename)
        self.socket.close()
        print("socket closed")

    def parse_info(self):
        peers_set = {}
        chunks = {}
        chunks_peers = {}
        if len(self.chunks_info) != 0:
            i = 0
            j=0
            for chunk in self.chunks_info:
                chunks[i] = chunk[0]
                peers = chunk[1]
                chunks_peers[i] = []

                for peer in peers:
                    if peer not in peers_set.values():
                        peers_set[str(j)] = peer
                        j+=1
                for peer in peers_set:
                    if peers_set[peer] in peers:
                        chunks_peers[i].append(peer)
                i += 1
        return peers_set,chunks,chunks_peers,len(chunks)


class Client21(Client2):
    def __init__(self):
        cfg = CfgPeers()
        self.Packets = Packets()
        self.ip_address, self.port_number = cfg.read_config_peers('tracker')
        Client2.__init__(self)

class Client3(Client2):
    def __init__(self):
        self.addr = ('<broadcast>',9000)
        self.Packets = Packets()
        self.broadcasting()
        Client2.__init__(self)
    def broadcasting(self):
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.Packets.send_discover_tracker(self.sock, self.addr)
        print('discovertracker sending')
        #print('socket created')
        #print('ready to broadcast')
        self.sock2 = socket(AF_INET, SOCK_DGRAM)
        self.sock2.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.sock2.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock2.bind(('', 9000))
        #print('socket created')

        msg_header, addr= self.sock2.recvfrom(8)
        if len(msg_header) == 0:
            self.socket.close()
            return False
            # test
        print('header:',msg_header)
        msg_version, msg_type, msg_length, msg_body, self.addr = self.Packets.recvfrom(msg_header)
        print('body:',msg_body)
        self.ip_address, self.port_number, self.tracker_name, self.tracker_name_length = self.Packets.handle_tracker_info(msg_body)
        self.udpsock.close()
        print("socket closed")
