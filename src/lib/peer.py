import binascii
from socket import *
from lib.packets import *
from lib.cfg_peers import *
from lib.server import Server


chunks_path = os.path.join(root_path, 'chunks')


class Peer(Server):

    def __init__(self, user):
        Peer.__init__(self, user)
        print('Done')

    def check_chunk(self, filename):
        chunk_path = os.path.join(chunks_path, self.user, filename + '.bin')
        if not os.path.exists(chunk_path):
            return False
        else:
            return True

    def read_chunk(self, filename):
        chunk_path = os.path.join(chunks_path, self.user, filename + '.bin')
        chunk_content_length = os.path.getsize(chunk_path)
        chunk_content = ''
        with open(chunk_path, 'rb') as cf:
            chunk_content = cf.read(chunk_content_length)
        return chunk_content_length, chunk_content

    def start_socket(self, client, address):
        while 1:
            # recv the header to know the length the body
            # msg_header = client.recv(8)
            msg_header = 1
            if msg_header:
                # recv the body
                # msg_version, msg_type, msg_length, msg_body = self.Packets.recv(
                #     client, msg_header)
                msg_version = 1
                msg_type = 4
                msg_length = 7
                msg_body = binascii.unhexlify(
                    '17ca281aa5b956e096bbdabfbb11f96ebd4d9e76')

                if self.Packets.check_format(msg_version, msg_type) is False:
                    # • If the request is malformed (invalid message format),
                    # they will send back an ERROR (see
                    # Appendix D.7) message with the error code
                    # INVALID_MESSAGE_FORMAT.
                    self.Packets.sendError(client, INVALID_MESSAGE_FORMAT)
                    print('ERROR: INVALID_MESSAGE_FORMAT')
                elif self.Packets.check_request(msg_type) is False:
                    self.Packets.sendError(client, INVALID_REQUEST)
                    print('ERROR: INVALID_REQUEST')
                else:
                    filename = binascii.hexlify(msg_body).decode()
                    chunk_found = self.check_chunk(filename)
                    if chunk_found is False:
                        # • If the chunk cannot be found (look to the directory
                        # content), they will send back an
                        # ERROR (see Appendix D.7) message with the error code
                        # CHUNK_NOT_FOUND.
                        self.Packets.sendError(client, CHUNK_NOT_FOUND)
                        print('ERROR: CHUNK_NOT_FOUND')
                    else:
                        # • Otherwise, they will send back a CHUNK (see
                        # Appendix D.6) message with the content
                        # obtained from the file.
                        chunk_content_length, chunk_content = self.read_chunk(
                            filename)
                        self.Packets.sendChunk(
                            client, msg_body, chunk_content_length, chunk_content)
                return False
            else:
                print('Client disconnected with ' +
                      address[0] + ':' + str(address[1]))
                client.close()
                return False
