import sys
import configparser
from socket import *
from lib.packets import *
from lib.cfg import *

chunks_path = os.path.join(root_path, 'chunks')


class Client(object):

    def __init__(self, user):
        self.read_config_peers(user)
        self.socket_connect()
        self.socket_recv()
        print('Done')

    def read_config_peers(self, user):
        config = configparser.ConfigParser()
        config.read(peers_path)
        self.ip_address = config.get(user, 'ip_address')
        self.port_number = config.getint(user, 'port_number')

    def read_chunks(self, user):
        # NOTE: not finished, for Hamza
        # with open(os.path.join(chunks_path, peername, chunk_hash + '.bin'), 'wb') as cf:
            # cf.read(chunk_content)

        # tests...
        files = [f for f in os.listdir(chunks_path) if os.path.isfile(f)]
        for fle in files:
            print('yo')
            with open(fle) as f:
                print(f.readlines())
        print('ok')
        # with open(filename, 'rb') as f:
        #     sock.sendall(f.read())

    def socket_connect(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect((self.ip_address, self.port_number))

    def socket_recv(self):
        self.Packets = Packets()

        while 1:
            # test
            msg_body = input('enter:')
            self.Packets.send(self.socket, version, 6,
                              len(msg_body), msg_body.encode())

            # recv the header to know the length the body
            msg_header = self.socket.recv(4)
            # recv the body
            msg_version, msg_type, msg_length, msg_body = self.Packets.recv(
                self.socket, msg_header)

            # NOTE: should we send only one error message (in this order of
            # priority)?
            if self.Packets.check_format(msg_version, msg_type, msg_length, msg_body) is False:
                # • If the request is malformed (invalid message format), they will send back an ERROR (see
                # Appendix D.7) message with the error code
                # INVALID_MESSAGE_FORMAT.
                self.Packets.sendError(self.socket, INVALID_MESSAGE_FORMAT)
                print('1')
            elif self.Packets.check_request(msg_type) is False:
                self.Packets.sendError(self.socket, INVALID_REQUEST)
                print('2')
            else:
                # NOTE: la suite pour Hamza
                # • If the chunk cannot be found (look to the directory content), they will send back an
                # ERROR (see Appendix D.7) message with the error code CHUNK_NOT_FOUND.
                # • Otherwise, they will send back a CHUNK (see Appendix D.6) message with the content
                # obtained from the file.
                print('la suite pour Hamza')

        self.socket.close()
