from socket import *
from packets import *
from cfg_peers import *


# ALICE, BOB, TRACKER
class Client:

    def __init__(self, serverName):
        cfg = cfgPeers()
        self.ip_address, self.port_number = cfg.read_config_peers(serverName)

    def create_socket(self):
        self.Packets = Packets()
        self.socket = socket(AF_INET, SOCK_STREAM)
        # NOTE: have to multithread (cf server.py)
        self.socket.connect((self.ip_address, self.port_number))
        self.start_socket()


class ClientV1(Client):

    def __init__(self):
        # NOTE: use cfg_peers
        Client.__init__('Alice')
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
            self.Packets.send(self.socket, version, GET_CHUNK, msg_length, msg_body)


class ClientV2(Client):

    def __init__(self, tracker):
        # NOTE: use cfg_peers
        self.length = 2
        Client.__init__(tracker)
        self.create_socket()

    def start_socket(self):
        try:
            while 1:
                # test
                msg_body=""
                self.Packets.send(self.socket, version,GET_FILE_INFO, self.length, msg_body.encode())
                msg_header = self.socket.recv(8)
                if len(msg_header) == 0:
                    self.socket.close()
                    break
                # test
                self.msg_version, self.msg_type, self.msg_length, self.msg_body = self.Packets.recv(self.socket, msg_header)
        finally:
            self.socket.close()



if __name__ == '__main__':
    Client()
