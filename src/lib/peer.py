import binascii
from socket import *
from lib.packets import *
from lib.cfg_peers import *
from lib.server import Server


chunks_path = os.path.join(root_path, 'chunks')


class Peer(Server):

    def __init__(self):
        self.Packets = Packets()
        Server.__init__(self)
        print('Done')

    def start_socket(self, client, address):
        while 1:
            # recv the header to know the length the body
            print('\n')
            msg_header = client.recv(8)
            if msg_header:
                # recv the body
                msg_version, msg_type, msg_length, msg_body = self.Packets.recv(
                    client, msg_header)

                if self.Packets.check_format(msg_version, msg_type) is False:
                    self.Packets.send_error(client, INVALID_MESSAGE_FORMAT)
                    print('ERROR: INVALID_MESSAGE_FORMAT')
                elif self.Packets.check_request(msg_type) is False:
                    self.Packets.send_error(client, INVALID_REQUEST)
                    print('ERROR: INVALID_REQUEST')
                else:
                    filename = self.Packets.handle_get_chunk(msg_body)
                    print('GET_CHUNK:', msg_version,
                          msg_type, msg_length, filename)

                    chunk_found = self.check_chunk(filename)
                    if chunk_found is False:
                        self.Packets.send_error(client, CHUNK_NOT_FOUND)
                        print('ERROR: CHUNK_NOT_FOUND')
                    else:
                        chunk_content_length, chunk_content = self.read_chunk(
                            filename)
                        self.Packets.send_chunk(
                            client, msg_body, chunk_content_length, chunk_content)
            else:
                print('Client disconnected with ' +
                      address[0] + ':' + str(address[1]))
                client.close()
                return False

    def check_chunk(self, filename):
        chunk_path = os.path.join(
            chunks_path, self.user, filename + '.bin')
        if not os.path.exists(chunk_path):
            return False
        else:
            return True

    def read_chunk(self, filename):
        chunk_path = os.path.join(
            chunks_path, self.user, filename + '.bin')
        chunk_content_length = os.path.getsize(chunk_path)
        chunk_content = ''
        with open(chunk_path, 'rb') as cf:
            chunk_content = cf.read(chunk_content_length)
        return chunk_content_length, chunk_content
