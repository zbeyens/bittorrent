import sys
from socket import *
from lib.packets import *
from lib.cfg_peers import *
import threading


class Server(object):

    def __init__(self, user):
        cfg_peers = CfgPeers()
        self.ip_address, self.port_number = cfg_peers.read_config_peers(user)
        self.create_socket()
        # self.read_chuncks(user)
        print('Done')

    def read_chunks(self, user):
        chunks_path = os.path.join(root_path, 'chunks', user)
        # NOTE: not finished, for Ziyad
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

    def create_socket(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        # Include IP headers
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.socket.bind((self.ip_address, self.port_number))
        self.listen_socket()

    def listen_socket(self):
        self.Packets = Packets()
        print('Listening on port', self.port_number)
        self.socket.listen(10)
        while True:
            client, address = self.socket.accept()
            print('ho')
            print('Client connected with ' +
                  address[0] + ':' + str(address[1]))
            # timeout after 60 seconds of inactivity
            # client.settimeout(60)
            threading.Thread(target=self.start_socket,
                             args=(client, address)).start()

    def start_socket(self, client, address):

        while 1:
            # recv the header to know the length the body

            msg_header = client.recv(4)
            print('he')
            if msg_header:
                # recv the body
                msg_version, msg_type, msg_length, msg_body = self.Packets.recv(
                    client, msg_header)

                # NOTE: should we send only one error message (in this order of
                # priority)?
                if self.Packets.check_format(msg_version, msg_type, msg_length, msg_body) is False:
                    # • If the request is malformed (invalid message format), they will send back an ERROR (see
                    # Appendix D.7) message with the error code
                    # INVALID_MESSAGE_FORMAT.
                    self.Packets.sendError(client, INVALID_MESSAGE_FORMAT)
                    print('1')
                elif self.Packets.check_request(msg_type) is False:
                    self.Packets.sendError(client, INVALID_REQUEST)
                    print('2')
                else:
                    print('...')
                    # NOTE: la suite pour Ziyad
                    # • If the chunk cannot be found (look to the directory content), they will send back an
                    # ERROR (see Appendix D.7) message with the error code CHUNK_NOT_FOUND.
                    # • Otherwise, they will send back a CHUNK (see Appendix D.6) message with the content
                    # obtained from the file.
            else:
                print('Client disconnected with ' +
                      address[0] + ':' + str(address[1]))
                client.close()
                return False
